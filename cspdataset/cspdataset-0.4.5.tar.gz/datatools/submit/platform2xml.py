#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2021/9/15 17:23
# @Author  : xgy
# @Site    : 
# @File    : platform2xml.py
# @Software: PyCharm
# @python version: 3.7.4
"""
import json
import os
import cv2
from tqdm import tqdm
import argparse
# import html

from datatools.util.create_voc_xml import gen_voc_xml
from datatools.util.datatool_utils import is_img_exists

"""
平台评估用json转xml
"""


def json2xml(json_file, img_dir, xml_dir="./output"):
    if not os.path.exists(xml_dir):
        os.makedirs(xml_dir)
    with open(json_file, "r", encoding="utf-8") as fr:
        json_data = json.load(fr)

    file_dict = {}
    for index, item in enumerate(json_data):
        file_name = item["filename"]
        if not file_dict.get(file_name, []):
            file_dict[file_name] = [item]
        else:
            file_dict[file_name].append(item)

    for img_name, pre_info in tqdm(file_dict.items()):
        img_name_suff = os.path.splitext(img_name)[0]
        img_type = is_img_exists(img_dir, img_name_suff)

        try:
            img_path = os.path.join(img_dir, img_name_suff + img_type)
            img = cv2.imread(img_path)
            img_w, img_h, _ = img.shape
        except AttributeError:
            print("can not open {}".format(img_path))
            continue

        xml_boxes = []
        for info in pre_info:
            box = {"category": info["category"],
                   "xmin": info["bndbox"]["xmin"],
                   "ymin": info["bndbox"]["ymin"],
                   "xmax": info["bndbox"]["xmax"],
                   "ymax": info["bndbox"]["ymax"]}
            xml_boxes.append(box)

        out_file = os.path.join(xml_dir, img_name_suff + ".xml")
        gen_voc_xml(xml_boxes, img_path, img_w, img_h, out_file)


def get_args():
    parser = argparse.ArgumentParser(description="transform json that submit to platform to xml which is the standard of voc")
    parser.add_argument("--json", help="the path of json that submit to platform", required=True, type=str, default=None)
    parser.add_argument("--imgs", help="the dir of imgs that used for eva", required=True, type=str, default=None)
    parser.add_argument("--output_xml", help="the folder to save result", type=str, default="./output_xml")
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    print("start")
    args = get_args()
    json2xml(args.json, args.imgs, args.output_xml)

    # eva_json = "C:/Users/xgy/Desktop/belt/result_paddlex_belt_eva.json"
    # eva_img = "C:/Users/xgy/Desktop/belt/eva/JPEGImages/"
    # output_dir = "C:/Users/xgy/Desktop/belt/eva_xml/"
    # json2xml(eva_json, eva_img, xml_dir=output_dir)
