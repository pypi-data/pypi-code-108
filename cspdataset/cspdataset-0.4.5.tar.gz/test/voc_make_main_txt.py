import os
import random
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='baseline data striping.') 
    #parser.add_argument('--train_data_path', '-I',type=str, default="e:/opt/local/object_detection/voc",
    parser.add_argument('--train_data_path', '-I',type=str, default="e:/opt/local/object_detection/voc2",
                        help="训练数据目录")
    args = parser.parse_args()
    return args

def mkdir(path):
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")
    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists = os.path.exists(path)
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)
        print(path + ' 创建成功')
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        print(path + ' 目录已存在')
        return False

def imageSets (train_path):
    trainval_percent = 0.8
    train_percent = 0.8
    xmlfilepath = os.path.join(train_path,'Annotations')
    txtsavepath = os.path.join(train_path,'ImageSets/Main')
    mkdir(txtsavepath)
    total_xml = os.listdir(xmlfilepath)

    num=len(total_xml)
    list=range(num)
    tv=int(num*trainval_percent)
    tr=int(tv*train_percent)
    trainval= random.sample(list,tv)
    train=random.sample(trainval,tr)

    ftrainval = open(os.path.join(train_path,'ImageSets/Main/trainval.txt'), 'w',encoding='utf-8')
    ftest = open(os.path.join(train_path,'ImageSets/Main/test.txt'), 'w',encoding='utf-8')
    ftrain = open(os.path.join(train_path,'ImageSets/Main/train.txt'), 'w',encoding='utf-8')
    fval = open(os.path.join(train_path,'ImageSets/Main/val.txt'), 'w',encoding='utf-8')

    for i  in list:
        name = total_xml[i][:-4] + '\n'
        if i in trainval:
            ftrainval.write(name)
            if i in train:
                ftrain.write(name)
            else:
                fval.write(name)
        else:
            ftest.write(name)

    ftrainval.close()
    ftrain.close()
    fval.close()
    ftest .close()

if __name__=="__main__":
    args = parse_args() 
    imageSets(args.train_data_path)