#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2021/9/1 8:56
# @Author  : xgy
# @Site    : 
# @File    : voc_split.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import os
import random
import argparse
from loguru import logger


def mkdir(path):
    # 去除特殊字符
    path = path.strip()
    path = path.rstrip("\\")
    # 判断结果
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        return True
    else:
        pass
        return False


def get_percent(percents):
    assert len(percents) == 2, "need two float num"
    for item in percents:
        # print(item)
        if not isinstance(item, float) and 0 <= float(item) <= 1:
            raise ValueError("切分比例必须为 [0,1] 之间的浮点数 [0.9, 0.8]")
    try:
        trainval_percent = percents[0]
        train_percent = percents[1]
    except:
        # todo 命令行能否输入浮点数
        raise ValueError('设置的分割比例格式错误 eg. --xxx_ratio 0.9 0.8')

    return trainval_percent, train_percent


def voc_split(vod_dir, ratios=None):
    if ratios is None:
        trainval_ratio = 0.9
        train_ratio = 0.8
    else:
        trainval_ratio, train_ratio = get_percent(ratios)

    xmlfilepath = os.path.join(vod_dir, 'Annotations')
    txtsavepath = os.path.join(vod_dir, 'ImageSets/Main')
    mkdir(txtsavepath)
    total_xml = os.listdir(xmlfilepath)

    num = len(total_xml)
    list_ids = range(num)
    tv = int(num * trainval_ratio)
    tr = int(tv * train_ratio)
    trainval = random.sample(list_ids, tv)
    train = random.sample(trainval, tr)

    ftrainval = open(os.path.join(vod_dir, 'ImageSets/Main/trainval.txt'), 'w', encoding='utf-8')
    ftest = open(os.path.join(vod_dir, 'ImageSets/Main/test.txt'), 'w', encoding='utf-8')
    ftrain = open(os.path.join(vod_dir, 'ImageSets/Main/train.txt'), 'w', encoding='utf-8')
    fval = open(os.path.join(vod_dir, 'ImageSets/Main/val.txt'), 'w', encoding='utf-8')

    for i in list_ids:
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

    logger.info("the split result files saved in {}".format(os.path.join(vod_dir, 'ImageSets/Main')))


def get_args():
    parser = argparse.ArgumentParser(description='voc datasets split.')
    parser.add_argument('--voc_path', type=str, default=None, help="voc数据目录")
    parser.add_argument("--division_ratio", help="数据集分割比例.", type=float, default=[0.9, 0.8], nargs='+')
    args = parser.parse_args()

    return args


def main(voc_path, division_ratio):
    voc_split(voc_path, division_ratio)


if __name__ == '__main__':
    print("start")
    params = get_args()
    main(params.voc_path, params.division_ratio)
