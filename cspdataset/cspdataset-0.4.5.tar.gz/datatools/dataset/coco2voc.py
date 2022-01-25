#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2021/8/30 8:56
# @Author  : xgy
# @Site    :
# @File    : voc_split.py
# @Software: PyCharm
# @python version: 3.7.4
"""
import argparse
import json
import os
import shutil
from loguru import logger
from datatools.util.create_voc_xml import gen_voc_xml

'''
把coco数据集合的所有标注转换到voc格式，不改变图片命名方式，
注意，原来有一些图片是黑白照片，检测出不是 RGB 图像，这样的图像不会被放到新的文件夹中
'''


# 若保存文件夹不存在，创建保存文件夹，若存在，删除重建
def mkr(path):
    if os.path.exists(path):
        pass
        # shutil.rmtree(path)
        # os.mkdir(path)
    else:
        os.makedirs(path, exist_ok=True)


def get_CK5(origin_base_dir, output_voc_dir):
    # if data_types is None:
    #     data_types = ["train"]

    origin_anno_dir = os.path.join(origin_base_dir, 'Annotations')  # 原始的coco的标注存放位置
    data_types = ['train', "test", "val", "trainval"]
    for dataType in data_types:
        origin_Images_dir = os.path.join(origin_base_dir, dataType)
        if os.path.exists(origin_Images_dir):
            dst_ImageSets_txt_dir = os.path.join(output_voc_dir, 'ImageSets', 'Main')  # VOC ImageSets
            dst_Annotations_dir = os.path.join(output_voc_dir, 'Annotations')  # VOC Annotations
            dst_JPEGImages_dir = os.path.join(output_voc_dir, 'JPEGImages')  # VOC JPEGImages
            mkr(dst_ImageSets_txt_dir)
            mkr(dst_Annotations_dir)
            mkr(dst_JPEGImages_dir)

            # 加载 coco 标注数据 train.json
            annFile = '{}.json'.format(dataType)
            annpath = os.path.join(origin_anno_dir, annFile)
            with open(annpath, "r", encoding="utf-8") as fr:
                json_data = json.load(fr)

            # 生成 voc dataType.txt
            dst_ImageSets_txt_path = os.path.join(dst_ImageSets_txt_dir, dataType + '.txt')
            img_filenames = []
            images = json_data["images"]
            for image in images:
                filename = image["file_name"]
                img_filenames.append(filename)
            with open(dst_ImageSets_txt_path, 'a+', encoding='utf-8') as output:
                for item in img_filenames:
                    item_short = os.path.splitext(item)[0]
                    output.write(item_short)
                    output.write('\n')
            print("生成 voc {}.txt 成功".format(dataType))

            # 复制 coco 图片到 voc 图片文件夹
            for ori_img_root, _, ori_files in os.walk(origin_Images_dir):
                for ori_file in ori_files:
                    ori_path = os.path.join(ori_img_root, ori_file)
                    dst_path = os.path.join(dst_JPEGImages_dir, ori_file)
                    shutil.copy(ori_path, dst_path)
            print("复制 coco 图片到 voc 图片文件夹 成功")

            # json 转xml
            json2xml(json_data, dst_Annotations_dir, dst_JPEGImages_dir)
            print("json 转xml 成功")


def json2xml(data, anno_dir, jpg_dir):
    images = data["images"]
    annotations = data["annotations"]
    categories = data["categories"]

    category_dict = {}
    for category in categories:
        category_dict[category["id"]] = category["name"]

    for img in images:
        file_name = img["file_name"]
        img_id = img["id"]
        height = img["height"]
        width = img["width"]

        xml_name = os.path.splitext(file_name)[0] + ".xml"
        xml_path = os.path.join(anno_dir, xml_name)
        jpg_path = os.path.join(jpg_dir, file_name)

        # xml 配置
        xml_boxes = []
        for annotation in annotations:
            image_id = annotation["image_id"]
            if image_id == img_id:
                bbox = annotation["bbox"]
                box = {"xmin": bbox[0] + 1,
                       "ymin": bbox[1] + 1,
                       "xmax": bbox[0] + bbox[2],
                       "ymax": bbox[1] + bbox[3],
                       "category": category_dict[annotation["category_id"]]}
                xml_boxes.append(box)
        gen_voc_xml(xml_boxes, jpg_path, width, height, xml_path)


def get_args():
    parser = argparse.ArgumentParser(description="Convert Pascal COCO annotation to VOC format.")
    parser.add_argument("--origin_base_dir", help="Directory path to coco.", type=str,
                        default='C:/Users/xgy/Desktop/voc_coco/cocotest')
    parser.add_argument("--output_voc_dir", help="Directory path to voc.", type=str,
                        default='C:/Users/xgy/Desktop/voc_coco/voctest')
    # parser.add_argument("--data_types", help="待转换的coco的数据集列表.", type=list,
    #                     default=['train'])  # 'train1','train2','val1',
    args = parser.parse_args()

    return args


def main(origin_base_dir, output_voc_dir):
    assert origin_base_dir != output_voc_dir, "the output voc folder should be different from the original coco folder"

    mkr(output_voc_dir)
    # get_CK5(origin_base_dir, output_voc_dir, data_types)
    get_CK5(origin_base_dir, output_voc_dir)
    logger.info('voc_dir: {}'.format(output_voc_dir))


if __name__ == "__main__":
    # args = get_args()
    # main(args.origin_base_dir, args.output_voc_dir)

    coco_dir = "../../test/coco_eva_clothes_helmet"
    out_voc = "../../test/voc_eva_clothes_helmet"
    main(coco_dir, out_voc)

