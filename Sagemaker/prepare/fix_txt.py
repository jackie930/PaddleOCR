def fix(i):
    with open(i, "r") as f:
        data = f.readlines()
    if i=='./train_data/train/labels.txt':
        data = ['train/'+i for i in data]
        f = open("./train_data/rec_gt_train.txt", "w")
        for line in data:
            x = line.split(' ')
            line = '\t'.join(x)
            f.write(line)
            print (line)
        f.close()
    else:
        data = ['test/' + i.replace(' ', '\t') for i in data]
        f = open("./train_data/rec_gt_test.txt", "w")
        for line in data:
            x = line.split(' ')
            line = '\t'.join(x)
            f.write(line)
            print (line)
        f.close()

def main():
    for i in ['./train_data/train/labels.txt','./train_data/test/labels.txt']:
        fix(i)
    print ("process finished!")

if __name__ == '__main__':
    main()