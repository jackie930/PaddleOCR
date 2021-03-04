#!/usr/bin/env python
# encoding: utf-8

import os
import sys

import json
from boto3.session import Session
from pprint import pprint

from dependency.main_ocr import ocr

from elasticsearch import Elasticsearch, RequestsHttpConnection
from datetime import datetime

region_name = os.getenv("region_name")
endpoint_name = os.getenv("endpoint_name")
output_s3_bucket = os.getenv("output_s3_bucket")
output_s3_prefix = os.getenv("output_s3_prefix")
elastic_search_host = os.getenv("es_host")
elastic_search_port = os.getenv("es_port")
elastic_search_protocol = os.getenv("es_protocol")
batch_id = os.getenv("batch_id")
job_id = os.getenv("job_id")
elastic_search_index = os.getenv('es_index')


# Hack to print to stderr so it appears in CloudWatch.
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


eprint(
    ">>>> start the job with param - outside es_host-{}, batch_id - {}, region_name-{}, endpoint_name-{},\n \
     output_s3_bucket-{}, output_s3_prefix-{}, es_port-{}, es_protocol-{}, job_id-{}, ".format(
        elastic_search_host, batch_id, region_name, endpoint_name, output_s3_bucket, output_s3_prefix,
        elastic_search_port, elastic_search_protocol, job_id))

print("<<<encode!")
print(sys.getdefaultencoding())

def id_ocr_main(
        input_s3_path_list,
        endpoint_name,
        output_s3_bucket,
        output_s3_prefix,
        region_name
):
    """
 function: save json_files back to s3 (key: file name value: tag label)
    :param input_s3_path_list: 读入s3文件路径list
    :param endpoint_path: 保存名称
    """
    session = Session(region_name=region_name)
    es = __connect_ES()
    s3 = session.client("s3")
    print("start!")

    pprint(input_s3_path_list[:5])
    # exit(0)
    for x in input_s3_path_list:
        print(x)
        s3_path = "s3://{}/{}".format(x["_source"]["bucket"], x["_source"]["file_key"])
        result = {}
        bucket = s3_path.split("/")[2]
        key = "/".join(s3_path.split("/")[3:])
        file_name = s3_path.split("/")[-1]
        print(bucket, key, file_name)
        s3.download_file(Filename=file_name, Key=key, Bucket=bucket)

        # read image
        print("process", s3_path)

        label = invoke_endpoint(session, endpoint_name, bucket,x["_source"]["file_key"])

        result[s3_path] = label
        print (result)

        # save json file
        json_file = file_name.replace(".png", ".json")
        with open(json_file, "w", encoding='utf-8') as fw:  # 建议改为.split('.')
            json.dump(result, fw, ensure_ascii=False)
            print("write json file success!")

        # output to s3
        upload_key=output_s3_prefix+'/'+json_file
        s3.upload_file(Filename=json_file, Key=upload_key, Bucket=output_s3_bucket)
        print("uploaded to s3://{}/{}".format(output_s3_bucket, upload_key))

        # update elasticsearch
        doc_id = x["_id"]
        update_status_by_id(es, doc_id, status="COMPLETED", output=label)

        # delete file locally
        delete_file(json_file)
        delete_file(file_name)


def delete_file(file):
    """
    delete file
    :param file:
    :return:
    """
    if os.path.isfile(file):
        try:
            os.remove(file)
        except:
            pass


def __connect_ES() -> Elasticsearch:
    eprint('Connecting to the ES Endpoint {}:{}'.format(elastic_search_host, elastic_search_port))
    es = None
    print("Using protocol: ", elastic_search_protocol)
    try:
        if elastic_search_protocol == "http":
            eprint (">>> Using http")
            es = Elasticsearch(
                hosts=[{'host': elastic_search_host, 'port': elastic_search_port}],
                # http_auth=awsauth,
                connection_class=RequestsHttpConnection)
        else:
            eprint (">>> Using https")
            es = Elasticsearch(
                hosts=[{'host': elastic_search_host, 'port': elastic_search_port}],
                use_ssl=True
            )

    except Exception as E:
        eprint("Unable to connect to {0}")
        eprint(E)
        exit(3)

    return es

def invoke_endpoint(session, endpoint_name, bucket, image_uri):
    """
 function: use endpoint to infer on one single image
    """
    test_data = {
        'bucket': bucket,
        'image_uri': image_uri,
        'content_type': "application/json",
    }

    payload = json.dumps(test_data)

    runtime = session.client("runtime.sagemaker")
    response = runtime.invoke_endpoint(
        EndpointName=endpoint_name,
        ContentType="application/json",
        Body=payload,  # json.dumps(data),
    )

    outputs = response["Body"].read()
    outputs = outputs.decode("utf-8")
    print(outputs)

    # return str(outputs)
    return outputs

def __search_for_file_list(job_id: str, batch_id: str, status='NOT_STARTED') -> list:
    """
    Fot bot to get their file to process.
    :param job_id: One customer request for bots to process on certain folder is one *job*, and thus have a job_id.
    :param batch_id: Files in one job will spited based on the number of bots. Bot id and batch id is the same.
    :param status: one of "NOT_STARTED, COMPLETED, PROCESSING"
    :return:
    """
    es = __connect_ES()
    query = {  # TODO Would speed up by reduce the result fields
        "size": 10000,
        "query": {
            "bool": {
                "must": [
                    {"match": {"job_id": job_id}},
                    {"match": {"batch_id": batch_id}},
                    {"match": {"status": status}}
                ]
            }
        }
    }
    eprint(">>> going to query: {}".format(query))

    resp = es.search(
        index=elastic_search_index,
        body=query,
        scroll='9s'
    )

    # keep track of pass scroll _id
    old_scroll_id = resp['_scroll_id']
    all_hits = resp['hits']['hits']
    # use a 'while' iterator to loop over document 'hits'
    while len(resp['hits']['hits']):

        # make a request using the Scroll API
        resp = es.scroll(
            scroll_id=old_scroll_id,
            scroll='2s'  # length of time to keep search context
        )

        # check if there's a new scroll ID
        if old_scroll_id != resp['_scroll_id']:
            eprint("NEW SCROLL ID:", resp['_scroll_id'])

        # keep track of pass scroll _id
        old_scroll_id = resp['_scroll_id']

        # eprint the response results
        eprint("\nresponse for index: " + elastic_search_index)
        eprint("_scroll_id:", resp['_scroll_id'])
        eprint('response["hits"]["total"]["value"]:{}'.format(resp["hits"]["total"]))

        # iterate over the document hits for each 'scroll'
        all_hits.extend(resp['hits']['hits'])
    eprint("DOC COUNT:", len(all_hits))

    return all_hits


def update_status_by_id(es, doc_id, status="COMPLETED", output=""):
    resp = es.update(
        index=elastic_search_index,
        id=doc_id,
        body={
            "doc":
                {"status": status,
                 "output": output,
                 "complete_date": datetime.utcnow()
                 }
        },
        doc_type="_doc"
    )
    return resp

if __name__ == "__main__":
    eprint(">>> Start execution.")
    file_list = __search_for_file_list(job_id=job_id, batch_id=batch_id)
    id_ocr_main(file_list,endpoint_name,output_s3_bucket,output_s3_prefix, region_name)
    eprint("<<< Exit.")
    eprint("<<< Exit.")
    exit(0)
    eprint("<<< Exit.")
