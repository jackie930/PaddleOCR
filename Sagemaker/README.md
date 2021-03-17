## 

基于sagemaker的ocr任务

目录结构

```
#bot
bot--|--build_and_push.sh 用于构建账户所在region的ecr镜像
     |--build_and_push-all-regions.sh 用于构建账户全部region的ecr镜像（只用于生产环境）
     |--Dockerfile
     |--task.py(执行主程序)
     |--ecr-policy.py 控制镜像iam权限

#inference是使用 pretrained 模型构建镜像，并可直接用于创建sagemaker endpoint
inference-｜...

#inference是使用 finetuned 模型构建镜像，并可直接用于创建sagemaker endpoint
inference-finetune  -｜...

```

具体的操作步骤指南，可以参考workshop文档中对应章节。


简化版如下：

### 准备训练数据
```shell script
#use environment
source activate python3
cd Sagemaker/prepare/
# install dependency
pip install trdg==1.6.0
#run 
cd ~/PaddleOCR/Sagemaker/prepare/
bash gendata.sh 0.2

#copy the data to target folder
cp -r train_data ~/PaddleOCR/deploy/docker/hubserving/gpu/
```

### 训练模型
首先，我们需要构建镜像。注意，这里使用的基础镜像比较大（22g），请确保您的空间足够。
```shell script
cd ~/PaddleOCR/deploy/docker/hubserving/gpu/
docker build . -t paddle --no-cache
```

验证docker创建成功
```shell script
docker images
#你可以看到列出了一个paddle的镜像，大小为25.8GB
```

启动并进入容器
```shell script
sudo nvidia-docker run --name paddlev0 -v $PWD:/paddle --shm-size=64G --network=host -it paddle /bin/bash
```

训练
```shell script
python3.7 -m paddle.distributed.launch --gpus '0' tools/train.py -c ./configs/rec/ch_ppocr_v2.0/rec_chinese_lite_train_v2.0_jackie.yml
```

### 模型部署


确保当前在docker镜像中运行。如果没有可以使用如下指令进入到*正在运行*的Docker。

```shell script
docker exec -it paddlev0 /bin/bash
```

然后执行下面的指令来转换模型。
```shell script
python3.7 tools/export_model.py \
-c configs/rec/ch_ppocr_v2.0/rec_chinese_lite_train_v2.0.yml \
-o Global.pretrained_model=./pretrain_models/ch_ppocr_mobile_v2.0_rec_pre/best_accuracy \
Global.load_static_weights=False \
Global.save_inference_dir=./inference/rec_crnn/
```

可以看到，在目录 ./inference/rec_crnn/中，生成了三个用于推理的模型文件：inference.pdiparams  inference.pdiparams.info  inference.pdmodel。

输入`exit`从Docker环境中退出来。

```shell script
#将模型文件拷贝出来
docker cp paddlev0:/PaddleOCR/inference/rec_crnn ~/PaddleOCR/Sagemaker/inference-finetune/ 
```

先配置默认的Region。
```shell script
aws configure
```

构建Docker Image并推送到ECR。
```shell script
cd ~/PaddleOCR/Sagemaker/inference-finetune
bash build_and_push.sh
```
这里可以看到已经生成了对应的image

获取ecr路径

```
aws ecr describe-repositories --repository-names paddle_crnn
```
获取其中的`repositoryUri`, 这个URL是后面需要使用的ECR路径。

创建Amazon Sagemaker endpoint
```shell script
python ~/PaddleOCR/Sagemaker/inference/create_endpoint.py \
--endpoint_ecr_image_path [your built ecr path] \
--endpoint_name ocr-endpoint-paddlev2 \
--instance_type ml.g4dn.2xlarge
```

Endpoint启动需要7分钟左右，这时去SageMaker控制台查看，可以发现Endpoint已经成功自启动。

测试`Amazon Sagemaker endpoint`
备注：这里需要指定测试用的图片的s3桶地址和图片名称。

```python
import boto3
from botocore.config import Config
from sagemaker.session import Session

config = Config(
    read_timeout=120,
    retries={
        'max_attempts': 0
    }
)

from boto3.session import Session
import json

bucket = 'bot-ocr-test-bucket'
image_uri = '1.png'
test_data = {
    'bucket' : bucket,
    'image_uri' : image_uri,
    'content_type': "application/json",
}
payload = json.dumps(test_data)
print(payload)

sagemaker_runtime_client = boto3.client('sagemaker-runtime', config=config)
session = Session(sagemaker_runtime_client)

#     runtime = session.client("runtime.sagemaker",config=config)
response = sagemaker_runtime_client.invoke_endpoint(
    EndpointName='ocr-endpoint-paddlev2',
    ContentType="application/json",
    Body=payload)

result = json.loads(response["Body"].read())
print (result)
```

先替换代码中的`img_uri`,`bucket`为测试图片，然后将上面的脚本保存成`test-ocr.py`，并在Server上执行，可以看到结果如下图。

