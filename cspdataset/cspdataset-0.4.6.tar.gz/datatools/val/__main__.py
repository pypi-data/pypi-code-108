# -*- coding: utf-8 -*-
"""
Created on 2022-01-11
@author: cxy(105...@qq.com)
"""

import argparse
import os
import xml.etree.ElementTree as ET
from tqdm import tqdm
from PIL import Image
from loguru import logger


# 数据分析函数 ###########################################
def get_labels(label_file):
    labels = []
    with open(label_file, "r", encoding="utf-8") as fr:
        txt_list = fr.readlines()
        for index, item in enumerate(txt_list):
            item_list = item.split(" ")
            labels.append(item_list[0].replace("\n", ""))

    return labels


def check_img(img_dir, output_dir):
    img_break_txt = output_dir + '/img_error.txt'
    if os.path.exists(img_break_txt):
        os.remove(img_break_txt)
    # 遍历图像，检查是否存在错误
    flag = True
    imgs = os.listdir(img_dir)
    for img in tqdm(imgs):
        img_name = os.path.splitext(img)[0]
        # img_path = os.path.join(img_dir, img)
        img_path = img_dir + '/' + img
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
            # 仅生成 img_error.txt
            with open(img_break_txt, "a+", encoding="utf-8") as fw:
                fw.write(img_name)
                fw.write("\n")
    # 输出检查结果信息
    if not flag:
        logger.info("the error img name has been save to the {}".format(img_break_txt))
    else:
        print("there are not error images")


def check_annotation(xml_file_path, results, labels):
    # xml检查结果路径
    size_error_txt = results + '/size_error.txt'
    box_error_txt = results + '/box_error.txt'
    no_obj_txt = results + '/no_object_error.txt'
    cls_error_txt = results + '/cls_error.txt'
    error_list_txt = results + '/error_list.txt'
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

    # 遍历每个xml文件
    names_xml = os.listdir(xml_file_path)
    for name in tqdm(names_xml):
        if name.endswith('.xml'):
            # 检查标志初始化
            flag_size = True
            flag_cls = True
            flag_no_obj = True
            flag_box = True

            # 获得每份xml文件的根节点
            xml_name = os.path.splitext(name)[0]
            tree = ET.parse(xml_file_path + '/' + name)  # 打开xml文档
            root = tree.getroot()  # 获得root节点

            # 图片尺寸为0判断
            size = root.find("size")
            if not size:
                flag_size = False
                width = None
                height = None
            else:
                width = size.find("width")
                height = size.find("height")
                if int(width.text) == 0 or int(height.text) == 0 or width is None or height is None:
                    flag_size = False
            if not flag_size:
                with open(size_error_txt, "a+", encoding="utf-8") as fw:
                    fw.write(xml_name)
                    fw.write("\n")

            # 判断object节点相关字段
            # 判断有无object节点
            obj_flag = root.find("object")
            if obj_flag:
                for obj in root.iter('object'):
                    cls = obj.find('name').text
                    # 类别错误判断
                    if cls not in labels:
                        flag_cls = False
                    # box坐标值错误判断
                    bndbox = obj.find('bndbox')
                    if not bndbox:
                        # 无bndbox节点
                        flag_box = False
                    else:
                        try:
                            # 无xmin等节点
                            xmin = int(bndbox.find('xmin').text)
                            ymin = int(bndbox.find('ymin').text)
                            xmax = int(bndbox.find('xmax').text)
                            ymax = int(bndbox.find('ymax').text)
                        except ValueError:
                            flag_box = False
                        else:
                            if width.text and height.text:
                                # 坐标值 错误
                                if xmin < 0 or xmax < 0 or ymin < 0 or ymax < 0 or xmin >= xmax or ymin >= ymax or xmax > int(
                                        width.text) or ymax > int(height.text):
                                    flag_box = False
                            if width is None and height is None:
                                if any(item < 0 for item in [xmin, ymin, xmax, ymax]) or xmin >= xmax or ymin >= ymax:
                                    flag_box = False
                # 检查结果输出
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

            # 检查结果汇总输出
            if not flag_size or not flag_cls or not flag_no_obj or not flag_box:
                with open(error_list_txt, "a+", encoding="utf-8") as fw:
                    fw.write(xml_name)
                    fw.write("\n")

    # 所有xml文件检查结果
    if os.path.exists(error_list_txt):
        logger.info("the error annotation name has been save to the {}".format(error_list_txt))
    else:
        print("there are not error annotations")


def analysis_data(xml_file_path):
    # 输入输出路径
    results = os.path.dirname(xml_file_path) + r'/data_report'
    if not os.path.exists(results):
        os.makedirs(results)

    # 检查原始图像是否存在错误
    img_dir = os.path.dirname(xml_file_path) + r'/JPEGImages'
    check_img(img_dir, results)

    # 检查xml文件是否存在错误
    labels_path = os.path.dirname(xml_file_path) + r'/labels.txt'
    labels = get_labels(labels_path)
    check_annotation(xml_file_path, results, labels)

    print('Have finished validation process, the result is in dir: {} !'.format(results))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', type=str, default=None, help='The path of xml files dir !')
    args = parser.parse_args()

    if args.f:
        print('Beginning validate ...... , please wait a moment !')
        analysis_data(args.f)
    else:
        print('You should use this command as follows for help:')
        print('valtools -h')


if __name__ == '__main__':
    print("start")
    main()

