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
