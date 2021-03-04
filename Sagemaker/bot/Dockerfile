FROM tensorflow/tensorflow:1.15.2-gpu-py3

RUN mkdir -p /opt/program

ENV LANG=en_US.utf8
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/program:${PATH}"

ENV PYTHONIOENCODING=utf-8

RUN pip install boto3 -i https://opentuna.cn/pypi/web/simple
RUN pip install Cython -i https://opentuna.cn/pypi/web/simple
RUN pip install opencv-python==3.2.0.8 -i https://opentuna.cn/pypi/web/simple
RUN pip install elasticsearch==7.8.0 -i https://opentuna.cn/pypi/web/simple
RUN pip install easydict -i https://opentuna.cn/pypi/web/simple
RUN pip install glog -i https://opentuna.cn/pypi/web/simple
RUN pip install tqdm==4.44.1 -i https://opentuna.cn/pypi/web/simple


COPY . /opt/program/

WORKDIR /opt/program

CMD ["python", "task.py"]
