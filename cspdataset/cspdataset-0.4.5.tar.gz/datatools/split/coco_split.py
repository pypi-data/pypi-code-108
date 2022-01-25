#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2021/8/31 8:56
# @Author  : xgy
# @Site    :
# @File    : voc_split.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import os
import shutil
import random
import json
from loguru import logger

'''
把coco数据集合的所有标注按比例切分，可以设置前置对未戴安全帽按比例分布
'''

# import numpy as np
# from functools import reduce
# from terminaltables import AsciiTable
# from pycocotools.coco import  COCO
# 这个包可以从git上下载https://github.com/cocodataset/cocoapi/tree/master/PythonAPI，也可以直接用修改后的coco.py


def coco_split(coco_path, trainval_percent, train_percent, data_types=None):
    """
    coco 数据集切分，需保证该数据集中只存在 Annotation、train 两个文件夹，暂不支持存在多个图片文件夹（如同时存在test、train 图片文件夹，则只会基于 train 作切分）
    Args:
        coco_path:
        trainval_percent:
        train_percent:
        data_types:

    Returns:

    """
    if data_types is None:
        data_types = ["train"]

    ori_Annotations_dir = os.path.join(coco_path, "Annotations")
    ori_Images_dir = os.path.join(coco_path, "train")

    for i, datatype in enumerate(data_types):
        annFile = '{}.json'.format(datatype)
        annpath = os.path.join(coco_path, 'Annotations', annFile)
        data = load_json(annpath)

        images = data["images"]
        categories = data["categories"]
        annotations = data["annotations"]
        coco_type = data["type"]

        # 按序号索引划分比例
        num = len(images)
        list_ids = range(num)
        tv = int(num * trainval_percent)
        tr = int(tv * train_percent)
        trainval = random.sample(list_ids, tv)
        train = random.sample(trainval, tr)

        # 划分 images
        images_class, imgids_class, filename_class = split_images(images, list_ids, trainval, train)

        # 划分 annotations
        annotations_class = split_annotations(annotations, imgids_class)

        # 组装 coco json
        # trainval_json = {"images": images_class[0],
        #                  "type": coco_type,
        #                  "annotations": annotations_class[0],
        #                  "categories": categories}

        train_json = {"images": images_class[1],
                      "type": coco_type,
                      "annotations": annotations_class[1],
                      "categories": categories}
        val_json = {"images": images_class[2],
                    "type": coco_type,
                    "annotations": annotations_class[2],
                    "categories": categories}
        test_json = {"images": images_class[3],
                     "type": coco_type,
                     "annotations": annotations_class[3],
                     "categories": categories}

        # class_json = ["trainval", "train", "val", "test"]
        # list_json = [trainval_json, train_json, val_json, test_json]
        class_json = ["train", "val", "test"]
        list_json = [train_json, val_json, test_json]
        for json_name, json_item in zip(class_json, list_json):
            json_item_path = os.path.join(ori_Annotations_dir, json_name + ".json")
            with open(json_item_path, "w", encoding="utf-8") as fw:
                json.dump(json_item, fw, ensure_ascii=False, indent=4)
        logger.info("the annotations has been splited in to ['trainval.json', 'train.json', 'val.json', 'test.json'] saving in {}".format(ori_Annotations_dir))

        # 划分图片文件夹
        split_im(coco_path, ori_Images_dir, filename_class)
        logger.info("the images has been splited in to ['train', 'val', 'test'] saving in {}".format(os.path.join(coco_path, "Images")))


# 划分 images 字段
def split_images(images, list_ids, trainval, train):
    images_trainval = []
    images_train = []
    images_val = []
    images_test = []

    images_trainval_imgids = []
    images_train_imgids = []
    images_val_imgids = []
    images_test_imgids = []

    images_trainval_filename = []
    images_train_filename = []
    images_val_filename = []
    images_test_filename = []

    for item in list_ids:
        if item in trainval:
            images_trainval.append(images[item])
            images_trainval_imgids.append(images[item]["id"])
            images_trainval_filename.append(images[item]["file_name"])
            if item in train:
                images_train.append(images[item])
                images_train_imgids.append(images[item]["id"])
                images_train_filename.append(images[item]["file_name"])
            else:
                images_val.append(images[item])
                images_val_imgids.append(images[item]["id"])
                images_val_filename.append(images[item]["file_name"])
        else:
            images_test.append(images[item])
            images_test_imgids.append(images[item]["id"])
            images_test_filename.append(images[item]["file_name"])

    images_class = [images_trainval, images_train, images_val, images_test]
    imgids_class = [images_trainval_imgids, images_train_imgids, images_val_imgids, images_test_imgids]
    filename_class = [images_trainval_filename, images_train_filename, images_val_filename, images_test_filename]

    return images_class, imgids_class, filename_class


# 划分 annotations 字段
def split_annotations(annotations, imgids_class):
    annotations_trainval = []
    annotations_train = []
    annotations_val = []
    annotations_test = []

    # 划分 annotations
    for annotation in annotations:
        annotation_img_id = annotation["image_id"]
        if annotation_img_id in imgids_class[0]:
            annotations_trainval.append(annotation)
            if annotation_img_id in imgids_class[1]:
                annotations_train.append(annotation)
            else:
                annotations_val.append(annotation)
        else:
            annotations_test.append(annotation)

    annotations_class = [annotations_trainval, annotations_train, annotations_val, annotations_test]

    return annotations_class


# 划分图片
def split_im(coco_path, ori_Images_dir, filename_class):
    # 划分图片文件夹
    # coco数据集结构调整
    # trainval_img_dir = os.path.join(coco_path, "Images", "trainval")
    # train_img_dir = os.path.join(coco_path, "train")
    val_img_dir = os.path.join(coco_path, "val")
    test_img_dir = os.path.join(coco_path, "test")
    # os.makedirs(trainval_img_dir, exist_ok=True)
    # os.makedirs(train_img_dir, exist_ok=True)
    os.makedirs(val_img_dir, exist_ok=True)
    os.makedirs(test_img_dir, exist_ok=True)

    for ori_Images_root, _, ori_img_files in os.walk(ori_Images_dir):
        for ori_img_file in ori_img_files:
            ori_img_path = os.path.join(ori_Images_root, ori_img_file)
            # if ori_img_file in images_trainval_filename:
            if ori_img_file in filename_class[0]:
                # dst_img_trainval_path = os.path.join(trainval_img_dir, ori_img_file)
                # shutil.copy(ori_img_path, dst_img_trainval_path)
                # if ori_img_file in images_train_filename:
                if ori_img_file in filename_class[1]:
                    pass
                    # dst_img_train_path = os.path.join(train_img_dir, ori_img_file)
                    # shutil.copy(ori_img_path, dst_img_train_path)
                    # shutil.move(ori_img_path, dst_img_train_path)
                else:
                    dst_img_val_path = os.path.join(val_img_dir, ori_img_file)
                    # shutil.copy(ori_img_path, dst_img_val_path)
                    shutil.move(ori_img_path, dst_img_val_path)
            else:
                dst_img_test_path = os.path.join(test_img_dir, ori_img_file)
                # shutil.copy(ori_img_path, dst_img_test_path)
                shutil.move(ori_img_path, dst_img_test_path)


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


def load_json(json_file):
    with open(json_file, "r", encoding="utf-8") as fr:
        json_data = json.load(fr)
    return json_data


def get_args():
    import argparse
    parser = argparse.ArgumentParser(description="Split COCO datasets.")
    parser.add_argument("--coco_path", help="coco 数据集路径.", type=str, default='C:/Users/xgy/Desktop/voc_coco/cocotest3')
    # parser.add_argument("--data_types", help="待合并的coco的数据集列表.", type=list,
    #                     default=['train'])  # 'train1','train2','val1',
    parser.add_argument("--division_ratio", help="数据集分割比例.", type=float, default=[0.9, 0.8], nargs='+')
    parser.add_argument("--seed", help="切分随机种子.", type=int, default=102)
    args = parser.parse_args()

    return args


# def main(coco_path, division_ratio, data_types=None, seed=102):
def main(coco_path, division_ratio, seed=102):
    # if data_types is None:
    #     data_types = ["train"]

    trainval_ratio, train_ratio = get_percent(division_ratio)
    print("the split ratios: trainval {} train {}".format(trainval_ratio, train_ratio))
    random.seed(seed)
    coco_split(coco_path, trainval_ratio, train_ratio)


if __name__ == "__main__":
    args = get_args()
    main(args.coco_path, args.division_ratios)
