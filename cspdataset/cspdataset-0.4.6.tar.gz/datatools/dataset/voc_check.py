#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2021/9/1 11:07
# @Author  : xgy
# @Site    : 
# @File    : voc_check.py
# @Software: PyCharm
# @python version: 3.7.4
"""
import argparse
import os
import xml.etree.ElementTree as ET
from loguru import logger
from datatools.util.check import CheckDataset

# import shutil


class CheckVOC(CheckDataset):
    dataset_type = "VOC"

    def __init__(self, dataset_dir, labels=None, output_dir=None):
        super().__init__(dataset_dir, labels, output_dir)
        self.img_dir = os.path.join(self.dir, "JPEGImages")

    # 判断标注数据(.xml)是否存在错误
    def is_anno_break(self):
        # anno_break_dir = os.path.join(self.output_dir, "anno_break")
        size_error_txt = os.path.join(self.output_dir, "size_error.txt")
        box_error_txt = os.path.join(self.output_dir, "box_error.txt")
        no_obj_txt = os.path.join(self.output_dir, "no_object_error.txt")
        cls_error_txt = os.path.join(self.output_dir, "cls_error.txt")
        error_list_txt = os.path.join(self.output_dir, "error_list.txt")

        # 删除旧文件
        if os.path.exists(size_error_txt):
            os.remove(size_error_txt)
        if os.path.exists(box_error_txt):
            os.remove(box_error_txt)
        if os.path.exists(no_obj_txt):
            os.remove(no_obj_txt)
        if os.path.exists(cls_error_txt):
            os.remove(cls_error_txt)
        if os.path.exists(error_list_txt):
            os.remove(error_list_txt)

        for xml in os.listdir(self.anno_dir):
            flag_size = True
            flag_cls = True
            flag_no_obj = True
            flag_box = True

            xml_name = os.path.splitext(xml)[0]
            xml_path = os.path.join(self.anno_dir, xml)
            tree = ET.parse(xml_path)
            annotation = tree.getroot()  # 获取根节点， Element类

            # 图片尺寸为0判断
            size = annotation.find("size")
            if not size:
                flag_size = False
                width = None
                height = None
            else:
                width = size.find("width")
                height = size.find("height")
                if int(width.text) == 0 or int(height.text) == 0 or width is None or height is None:
                    flag_size = False
                    # dst_xml_path = os.path.join(anno_break_dir, xml_name + "_" + "size_error" + ".xml")
                    # shutil.copy(xml_path, dst_xml_path)
            if not flag_size:
                with open(size_error_txt, "a+", encoding="utf-8") as fw:
                    fw.write(xml_name)
                    fw.write("\n")

            # 判断 object 节点相关字段
            # 判断有无 object 节点
            obj_flag = annotation.find("object")
            if obj_flag:
                for obj in annotation.iter('object'):
                    cls = obj.find('name').text

                    # 类别错误判断
                    if cls not in self.labels:
                        flag_cls = False
                        # dst_xml_path = os.path.join(anno_break_dir, xml_name + "_" + "cls_error" + ".xml")
                        # shutil.copy(xml_path, dst_xml_path)
                        # with open(cls_error_txt, "a+", encoding="utf-8") as fw:
                        #     fw.write(xml_name)
                        #     fw.write("\n")

                    # box 坐标值错误判断
                    bndbox = obj.find('bndbox')
                    if not bndbox:
                        # 无 bndbox 节点
                        flag_box = False
                    else:
                        try:
                            # 无 xmin 等节点
                            xmin = int(bndbox.find('xmin').text)
                            ymin = int(bndbox.find('ymin').text)
                            xmax = int(bndbox.find('xmax').text)
                            ymax = int(bndbox.find('ymax').text)
                        except ValueError:
                            flag_box = False
                        else:
                            if width.text and height.text:
                                # 坐标值 错误
                                if xmin < 0 or xmax < 0 or ymin < 0 or ymax < 0 or xmin >= xmax or ymin >= ymax or xmax > int(width.text) or ymax > int(height.text):
                                    flag_box = False
                            if width is None and height is None:
                                if any(item < 0 for item in [xmin, ymin, xmax, ymax]) or xmin >= xmax or ymin >= ymax:
                                    flag_box = False

                if not flag_box and not flag_cls:
                    with open(box_error_txt, "a+", encoding="utf-8") as fw:
                        fw.write(xml_name)
                        fw.write("\n")
                    with open(cls_error_txt, "a+", encoding="utf-8") as fw:
                        fw.write(xml_name)
                        fw.write("\n")

                if not flag_box and flag_cls:
                    with open(box_error_txt, "a+", encoding="utf-8") as fw:
                        fw.write(xml_name)
                        fw.write("\n")

                if flag_box and not flag_cls:
                    with open(cls_error_txt, "a+", encoding="utf-8") as fw:
                        fw.write(xml_name)
                        fw.write("\n")

            else:
                flag_no_obj = False
                with open(no_obj_txt, "a+", encoding="utf-8") as fw:
                    fw.write(xml_name)
                    fw.write("\n")

            if not flag_size or not flag_cls or not flag_no_obj or not flag_box:
                with open(error_list_txt, "a+", encoding="utf-8") as fw:
                    fw.write(xml_name)
                    fw.write("\n")
        if os.path.exists(error_list_txt):
            logger.info("the error annotation name has been save to the {}".format(error_list_txt))
        else:
            print("there are not error annotations")


def get_labels(label_file):
    labels = []
    with open(label_file, "r", encoding="utf-8") as fr:
        txt_list = fr.readlines()
        for index, item in enumerate(txt_list):
            item_list = item.split(" ")
            labels.append(item_list[0].replace("\n", ""))

    return labels


def get_args():
    parser = argparse.ArgumentParser(description="checking voc dataset")
    parser.add_argument("--voc_dir", help="Directory path to voc.", type=str, default='C:/Users/xgy/Desktop/voc_coco/voctest1')
    parser.add_argument("--labels", help="label.txt.", type=str, default='C:/Users/xgy/Desktop/voc_coco/voctest1/label.txt')
    parser.add_argument("--out_path", help="Directory path of result.", type=str, default='C:/Users/xgy/Desktop/voc_coco/voctest1/check_output')
    args = parser.parse_args()
    return args


def main(voc_dir, labels_file, out_path):
    labels = get_labels(labels_file)
    voc_data_set = CheckVOC(voc_dir, labels, out_path)

    voc_data_set.is_anno_break()
    voc_data_set.is_img_break()


if __name__ == '__main__':
    print("start")
    args = get_args()
    main(args.voc_dir, args.labels, args.out_path)
