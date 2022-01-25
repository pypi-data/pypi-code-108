#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2021/9/16 10:54
# @Author  : xgy
# @Site    : 
# @File    : xml2platform.py
# @Software: PyCharm
# @python version: 3.7.4
"""
import json
import os
import argparse
import xml.etree.ElementTree as ET
from loguru import logger

img_types = [".jpg", ".JPG", ".png", ".PNG", ".JPEG"]


def xml2platform(xml_dir, img_dir, json_file):
    result_series = []
    num_id = 0
    for root, _, files in os.walk(xml_dir):
        for xml_item in files:

            xml_name = os.path.splitext(xml_item)[0]
            xml_path = os.path.join(root, xml_item)

            img_hz = None
            for img_ex in img_types:
                if os.path.exists(os.path.join(img_dir, xml_name + img_ex)):
                    # img_path = os.path.join(img_dir, xml_name + img_ex)
                    img_hz = img_ex
                    # 认为有且只有一个名为 xml_name 的图片文件
                    break

            if not img_hz:
                logger.info("can not find img {} {} in {}".format(xml_name, img_types, img_dir))
                continue
            else:
                # logger.info("xml_path: {}".format(xml_path))
                tree = ET.parse(xml_path)
                annotation = tree.getroot()
                for obj in annotation.findall("object"):
                    category = obj.find("name").text
                    # print(category)
                    bndbox = obj.find("bndbox")
                    xmin = bndbox.find("xmin").text
                    ymin = bndbox.find("ymin").text
                    xmax = bndbox.find("xmax").text
                    ymax = bndbox.find("ymax").text

                    # print("xmin, ymin, xmax, ymax: {} {} {} {}".format(xmin, ymin, xmax, ymax))

                    item_dict = {"id": num_id,
                                 "filename": xml_name + img_hz,
                                 "category": category,
                                 "score": "",
                                 "bndbox": {"xmin": xmin,
                                            "ymin": ymin,
                                            "xmax": xmax,
                                            "ymax": ymax}}
                    result_series.append(item_dict)
                    num_id += 1

    with open(json_file, "w", encoding="utf-8") as fw:
        json.dump(result_series, fw, ensure_ascii=False, indent=4)


def get_args():
    parser = argparse.ArgumentParser(description="transform xml to json that submit to platform")
    parser.add_argument("--xml_dir", help="the path of json that submit to platform", required=True, type=str, default=None)
    parser.add_argument("--imgs", help="the dir of imgs that used for eva", required=True, type=str, default=None)
    parser.add_argument("--output_json", help="the folder to save result", type=str, default="./output_xml")
    args = parser.parse_args()

    return args


if __name__ == '__main__':
    print("start")
    args = get_args()
    xml2platform(args.xml_dir, args.imgs, args.output_json)

    # xml_folder = "C:/Users/xgy/Desktop/belt/eva_xml_0916/"
    # img_dir = "C:/Users/xgy/Desktop/belt/eva/JPEGImages/"
    # output_json = "C:/Users/xgy/Desktop/belt/test_xml2json.json"
    # xml2platform(xml_folder, img_dir, output_json)

