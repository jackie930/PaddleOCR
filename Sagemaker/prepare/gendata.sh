echo $#  '生成中文数据集'
if [ $# -ne 1 ]
then
    echo "Usage: wrong "
    exit
fi

BASE_DIR="./train_data/"

if [ ! -d ${BASE_DIR} ];then
mkdir ${BASE_DIR}
fi

if [ ! -d ${BASE_DIR}"images" ]
then
    mkdir ${BASE_DIR}"images"
    mkdir ${BASE_DIR}"images/train"
    mkdir ${BASE_DIR}"images/valid"
fi

echo "start --------- generate  image --"
TOTAL_COUNT=$(wc -l './data/test.txt' | awk '{print $1}')

echo 'val_rate: ' $1 ' count ' ${TOTAL_COUNT}

val_count=`echo "scale=0; ${TOTAL_COUNT} * $1" | bc`
val_count=`echo $val_count | awk -F. '{print $1}'`

echo 'total  count: '  ${TOTAL_COUNT}
echo 'test   count: '  ${val_count}

train_count=$[TOTAL_COUNT - $val_count]

echo 'train  count: '  ${train_count}

head -n ${train_count} './data/test.txt'  > ${BASE_DIR}'train.txt'
tail -n ${val_count}   './data/test.txt'  > ${BASE_DIR}'valid.txt'

trdg \
-c $train_count -l cn -i ${BASE_DIR}'train.txt' -na 2 \
--output_dir ${BASE_DIR}"train" -ft "./font/香港标准宋体繁体.ttc"

trdg \
-c $val_count -l cn -i ${BASE_DIR}'valid.txt' -na 2 \
--output_dir ${BASE_DIR}"test" -ft "./font/香港标准宋体繁体.ttc"

#prepare folder
