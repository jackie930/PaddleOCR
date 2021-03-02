# Version: 2.0.0
#first clone the repo and prepared prepare the data
#here if china region, then below
FROM paddlepaddle/paddle:2.0.0rc1-gpu-cuda10.1-cudnn7

# PaddleOCR base on Python3.7
RUN pip3.7 install --upgrade pip -i https://mirror.baidu.com/pypi/simple

RUN pip3.7 install paddlehub --upgrade -i https://mirror.baidu.com/pypi/simple

#add download pretrained model
RUN git clone https://github.com/jackie930/PaddleOCR.git && cd /PaddleOCR && wget -P ./pretrain_models/ https://paddleocr.bj.bcebos.com/dygraph_v2.0/ch/ch_ppocr_mobile_v2.0_rec_pre.tar && cd pretrain_models && tar -xf ch_ppocr_mobile_v2.0_rec_pre.tar && rm -rf ch_ppocr_mobile_v2.0_rec_pre.tar

COPY /train_data /PaddleOCR

WORKDIR /PaddleOCR
