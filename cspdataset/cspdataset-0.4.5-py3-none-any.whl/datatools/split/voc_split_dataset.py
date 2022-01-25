#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2021/9/9 10:36
# @Author  : xgy
# @Site    : 
# @File    : voc_split_dataset.py
# @Software: PyCharm
# @python version: 3.7.4
"""
import os
import shutil
import random
import argparse
from loguru import logger


def voc_split_dataset(vod_dir, ratios=None):
    if ratios is None:
        trainval_ratio = 0.9
    else:
        trainval_ratio = get_percent(ratios)

    dir_before = os.path.split(vod_dir)[0]

    dir_test = os.path.join(dir_before, "voc_test")
    test_Annonations = os.path.join(dir_test, "Annotations")
    test_JPEGImages = os.path.join(dir_test, "JPEGImages")
    txt_ImageSets = os.path.join(dir_test, "ImageSets/Main")
    os.makedirs(dir_test, exist_ok=True)
    os.makedirs(test_Annonations, exist_ok=True)
    os.makedirs(test_JPEGImages, exist_ok=True)
    os.makedirs(txt_ImageSets, exist_ok=True)

    xml_dir = os.path.join(vod_dir, 'Annotations')
    img_dir = os.path.join(vod_dir, 'JPEGImages')

    txtsavepath = os.path.join(vod_dir, 'ImageSets/Main')
    os.makedirs(txt_ImageSets, exist_ok=True)

    total_xml = os.listdir(xml_dir)

    num = len(total_xml)
    list_ids = range(num)
    tv = int(num * trainval_ratio)
    trainval = random.sample(list_ids, tv)

    if os.path.exists(os.path.join(txtsavepath, "trainval.txt")):
        os.remove(os.path.join(txtsavepath, "trainval.txt"))
    ftrainval = open(os.path.join(vod_dir, 'ImageSets/Main/trainval.txt'), 'w', encoding='utf-8')
    ftest = open(os.path.join(dir_test, 'ImageSets/Main/test.txt'), 'w', encoding='utf-8')

    for i in list_ids:
        name = total_xml[i][:-4]
        if i in trainval:
            ftrainval.write(name)
            ftrainval.write("\n")
        else:
            ftest.write(name)
            ftest.write("\n")

            src_xml = os.path.join(xml_dir, name + ".xml")
            dst_xml = os.path.join(test_Annonations, name + ".xml")
            shutil.move(src_xml, dst_xml)

            for suffix in [".jpg", ".JPG", ".PNG", ".png"]:
                test_img_name = name + suffix
                src_img = os.path.join(img_dir, test_img_name)
                if os.path.exists(src_img):
                    dst_img = os.path.join(test_JPEGImages, test_img_name)
                    shutil.move(src_img, dst_img)

    ftrainval.close()
    ftest.close()

    logger.info("the split result files saved in {}".format(dir_test))


def get_percent(percents):
    assert len(percents) == 1, "need one float num"
    for item in percents:
        # print(item)
        if not isinstance(item, float) and 0 <= float(item) <= 1:
            raise ValueError("切分比例必须为 [0,1] 之间的浮点数 [0.9]")
    try:
        trainval_percent = percents[0]
    except:
        # 命令行能输入浮点数
        raise ValueError('设置的分割比例格式错误 eg. --xxx_ratio 0.9 0.8')

    return trainval_percent


def get_args():
    parser = argparse.ArgumentParser(description='voc datasets split to new voc_test.')
    parser.add_argument('--voc_path', type=str, default=None, help="voc数据目录")
    parser.add_argument("--division_ratio", help="数据集分割比例.", type=float, default=[0.9], nargs='+')
    args = parser.parse_args()

    return args


def main(voc_path, division_ratio):
    voc_split_dataset(voc_path, division_ratio)


if __name__ == '__main__':
    print("start")

    params = get_args()
    main(params.voc_path, params.division_ratio)
