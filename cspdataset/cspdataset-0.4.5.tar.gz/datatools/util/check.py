#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2021/9/2 9:34
# @Author  : xgy
# @Site    : 
# @File    : check.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import os
from PIL import Image
from loguru import logger

# import xml.etree.ElementTree as ET
# import shutil
# import argparse


class CheckDataset:
    dataset_type = None

    def __init__(self, dataset_dir, labels=None, output_dir=None):
        self.dir = dataset_dir
        self.anno_dir = os.path.join(self.dir, "Annotations")
        # self.anno_dir = None
        # self.img_dir = os.path.join(self.dir, "JPEGImages")
        self.img_dir = None
        if not output_dir:
            self.output_dir = os.path.join(self.dir, "check_output")
            os.makedirs(self.output_dir, exist_ok=True)
        else:
            self.output_dir = output_dir
            os.makedirs(self.output_dir, exist_ok=True)
        self._is_img_break = None
        self._is_anno_break = None
        self.labels = labels
        self._is_error_txt = None

        self.size_error_txt = os.path.join(self.output_dir, "size_error.txt")
        self.box_error_txt = os.path.join(self.output_dir, "box_error.txt")
        self.no_obj_txt = os.path.join(self.output_dir, "no_object_error.txt")
        self.cls_error_txt = os.path.join(self.output_dir, "cls_error.txt")
        self.error_list_txt = os.path.join(self.output_dir, "error_list.txt")
        self.img_break_txt = os.path.join(self.output_dir, "img_error.txt")

        # 删除旧文件
        if os.path.exists(self.size_error_txt):
            os.remove(self.size_error_txt)
        if os.path.exists(self.box_error_txt):
            os.remove(self.box_error_txt)
        if os.path.exists(self.no_obj_txt):
            os.remove(self.no_obj_txt)
        if os.path.exists(self.cls_error_txt):
            os.remove(self.cls_error_txt)
        if os.path.exists(self.error_list_txt):
            os.remove(self.error_list_txt)
        if os.path.exists(self.img_break_txt):
            os.remove(self.img_break_txt)

    # 判断图片是否损坏
    # 输出包含错误文件名的 .txt 文件
    def is_img_break(self):
        flag = True
        # img_break_txt = os.path.join(self.output_dir, "img_error.txt")

        for img in os.listdir(self.img_dir):
            img_name = os.path.splitext(img)[0]

            img_path = os.path.join(self.img_dir, img)
            file_size = os.path.getsize(img_path)
            file_size = round(file_size / float(1024 * 1024), 2)
            if file_size == 0:
                flag = False
            else:
                try:
                    img = Image.open(img_path)
                    img.verify()
                except OSError("the img load fail"):
                    flag = False

            if not flag:
                # 移动问题文件
                # break_dir = os.path.join(self.output_dir, "img_break")
                # if not os.path.exists(break_dir):
                #     os.makedirs(break_dir)
                # img_dst_path = os.path.join(break_dir, img)
                # # 问题图片对应 xml 标注文件
                # corr_xml_src_path = os.path.join(self.anno_dir, img_name + ".xml")
                # corr_xml_dst_path = os.path.join(break_dir, img_name + ".xml")
                #
                # shutil.copy(img_path, img_dst_path)
                # shutil.move(corr_xml_src_path, corr_xml_dst_path)

                # 仅生成 img_error.txt
                with open(self.img_break_txt, "a+", encoding="utf-8") as fw:
                    fw.write(img_name)
                    fw.write("\n")
        if not flag:
            logger.info("the error img name has been save to the {}".format(self.img_break_txt))
        else:
            print("there are not error images")
        self._is_img_break = flag


if __name__ == '__main__':
    print("start")
