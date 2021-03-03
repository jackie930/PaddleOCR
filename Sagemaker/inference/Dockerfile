FROM paddlepaddle/paddle:2.0.0rc1-gpu-cuda10.1-cudnn7

ENV LANG=en_US.utf8
ENV LANG=C.UTF-8

ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/program:${PATH}"

##########################################################################################
# SageMaker requirements
##########################################################################################
RUN pip3.7 install --upgrade pip

## install flask
RUN pip3.7 install networkx==2.3 flask gevent gunicorn boto3

RUN pip3.7 install paddlepaddle-gpu==2.0rc1

#add folder
RUN git clone https://github.com/jackie930/PaddleOCR.git /PaddleOCR

#download model
RUN mkdir inference/
RUN cd inference/
RUN wget -P ./inference/ https://paddleocr.bj.bcebos.com/dygraph_v2.0/ch/ch_ppocr_mobile_v2.0_det_infer.tar && tar -xf ch_ppocr_mobile_v2.0_det_infer.tar && rm -rf ch_ppocr_mobile_v2.0_det_infer.tar
RUN wget -P ./inference/ https://paddleocr.bj.bcebos.com/dygraph_v2.0/ch/ch_ppocr_mobile_v2.0_cls_infer.tar && tar -xf ch_ppocr_mobile_v2.0_cls_infer.tar && rm -rf ch_ppocr_mobile_v2.0_cls_infer.tar
RUN wget -P ./inference/ https://paddleocr.bj.bcebos.com/dygraph_v2.0/ch/ch_ppocr_mobile_v2.0_rec_infer.tar && tar -xf ch_ppocr_mobile_v2.0_rec_infer.tar && rm -rf ch_ppocr_mobile_v2.0_rec_infer.tar

RUN pip3.7 install -r /PaddleOCR/requirements.txt

### Install nginx notebook
RUN apt-get -y update && apt-get install -y --no-install-recommends \
         wget \
         nginx \
         ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log
RUN ln -sf /dev/stderr /var/log/nginx/error.log

# Set up the program in the image
COPY * /opt/program/
COPY ./pretrained_model/* /opt/program/
WORKDIR /opt/program

ENTRYPOINT ["python", "serve.py"]

