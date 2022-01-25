#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2021/9/2 9:31
# @Author  : xgy
# @Site    : 
# @File    : coco_check.py
# @Software: PyCharm
# @python version: 3.7.4
"""
import argparse
import json
import os
from loguru import logger
from datatools.util.check import CheckDataset

# import shutil


class CheckCOCO(CheckDataset):
    dataset_type = "COCO"

    def __init__(self, dataset_dir, labels=None, output_dir=None):
        super().__init__(dataset_dir, labels, output_dir)
        self.img_dir = os.path.join(dataset_dir, "train")

    # 判断标注数据(.json)是否存在错误
    def is_anno_break(self):
        json_path = os.path.join(self.anno_dir, "train.json")
        with open(json_path, "r", encoding="utf-8") as fr:
            json_data = json.load(fr)

        error_all_list = []
        size_error_list = []
        box_error_list = []
        cls_error_list = []

        # img_id: [file_name, w, h] 键值对
        images = json_data["images"]
        img_dict = {}
        for img in images:
            file_name_short = os.path.splitext(img["file_name"])[0]

            height = img.get("height", None)
            width = img.get("width", None)
            img_dict[img["id"]] = [file_name_short, width, height]

            # w, h 为 0 或 不存在
            if not height or not width:
                if file_name_short not in size_error_list:
                    size_error_list.append(file_name_short)
                if file_name_short not in error_all_list:
                    error_all_list.append(file_name_short)

        # 类别 id 列表
        categories = json_data["categories"]
        category_id_list = []
        for category in categories:
            category_id = category["id"]
            category_id_list.append(category_id)

        annotations = json_data["annotations"]
        for anno in annotations:
            image_id = anno["image_id"]
            img_name = img_dict[image_id][0]
            img_w = img_dict[image_id][1]
            img_h = img_dict[image_id][2]

            category_id = anno["category_id"]
            # 非法类别 id
            if category_id not in category_id_list:
                if img_name not in cls_error_list:
                    cls_error_list.append(img_name)
                if img_name not in error_all_list:
                    error_all_list.append(img_name)
            try:
                bbox = anno["bbox"]
                x1, y1, w, h = bbox
                x2 = x1 + w
                y2 = y1 + h
            except Exception:
                # bbox 字段缺失或不完整
                if img_name not in box_error_list:
                    box_error_list.append(img_name)
                if img_name not in error_all_list:
                    error_all_list.append(img_name)
            else:
                # w, h 值正常
                if img_w and img_h:
                    # 坐标值异常
                    if x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0 or x2 <= x1 or y2 <= y1 or x2 > img_w or y2 > img_h:
                        if img_name not in box_error_list:
                            box_error_list.append(img_name)
                        if img_name not in error_all_list:
                            error_all_list.append(img_name)
                # w 值正常， h 异常
                elif img_w and not img_h:
                    if x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0 or x2 <= x1 or y2 <= y1 or x2 > img_w:
                        if img_name not in box_error_list:
                            box_error_list.append(img_name)
                        if img_name not in error_all_list:
                            error_all_list.append(img_name)
                # h 值正常， w 异常
                elif img_h and not img_w:
                    if x1 < 0 or y1 < 0 or x2 < 0 or y2 < 0 or x2 <= x1 or y2 <= y1 or y2 > img_h:
                        if img_name not in box_error_list:
                            box_error_list.append(img_name)
                        if img_name not in error_all_list:
                            error_all_list.append(img_name)

        # 写入对应文件中（.txt）
        result_list = [error_all_list, size_error_list, box_error_list, cls_error_list]
        txt_path_list = [self.error_list_txt, self.size_error_txt, self.box_error_txt, self.cls_error_txt]

        for result, txt_path in zip(result_list, txt_path_list):
            if result:
                with open(txt_path, "a+",  encoding="utf-8") as fw:
                    for result_item in result:
                        fw.write(result_item)
                        fw.write("\n")

        if os.path.exists(self.error_list_txt):
            logger.info("the error annotation name has been save to the {}".format(self.error_list_txt))
        else:
            print("there are not error annotations")


def get_args():
    parser = argparse.ArgumentParser(description="checking voc dataset")
    parser.add_argument("--coco_dir", help="Directory path to voc.", type=str, default='C:/Users/xgy/Desktop/voc_coco/cocotest1')
    parser.add_argument("--labels", help="label.txt.", type=str, default=None)
    parser.add_argument("--out_path", help="Directory path of result.", type=str, default='C:/Users/xgy/Desktop/voc_coco/cocotest1/check_output')
    args = parser.parse_args()
    return args


def main(coco_dir, out_path):

    # labels = get_labels(args.labels)
    coco_data_set = CheckCOCO(dataset_dir=coco_dir,  output_dir=out_path)

    coco_data_set.is_anno_break()
    coco_data_set.is_img_break()


if __name__ == '__main__':
    print("start")
    args = get_args()
    main(args.coco_dir, args.out_path)
