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

import shutil
import os
import json
import xml.etree.ElementTree as ET
import argparse
from loguru import logger
from datatools.util.datatool_utils import is_img_exists


START_BOUNDING_BOX_ID = 1
# PRE_DEFINE_CATEGORIES = {'hat': 1, 'head': 2}
# PRE_DEFINE_CATEGORIES = None
img_types = [".jpg", ".JPG", ".JPEG", ".PNG", ".png"]


def get(root, name):
    vars = root.findall(name)
    return vars


def get_and_check(root, name, length):
    vars = root.findall(name)
    if len(vars) == 0:
        raise ValueError("Can not find %s in %s." % (name, root.tag))
    if 0 < length != len(vars):
        raise ValueError(
            "The size of %s is supposed to be %d, but is %d."
            % (name, length, len(vars))
        )
    if length == 1:
        vars = vars[0]
    return vars


def get_categories(xml_files):
    """Generate category name to id mapping from a list of xml files.
    
    Arguments:
        xml_files {list} -- A list of xml file paths.
    
    Returns:
        dict -- category name to id mapping.
    """
    classes_names = []
    for xml_file in xml_files:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for obj_item in root.findall("object"):
            name = obj_item.find("name").text
            if name not in classes_names:
                classes_names.append(name)

    # classes_names.sort()
    return {name: i for i, name in enumerate(classes_names)}


def convert(xml_files, json_path, voc_img_dir):

    json_dict = {"images": [], "type": "instances", "annotations": [], "categories": []}

    categories = get_categories(xml_files)
    bnd_id = START_BOUNDING_BOX_ID
    for i, xml_file in enumerate(xml_files):
        tree = ET.parse(xml_file)
        root = tree.getroot()

        filename = os.path.basename(xml_file).split('.')[0]
        img_type = is_img_exists(voc_img_dir, filename)
        filename = filename + img_type
        # image_id = 100000 + i
        image_id = i
        width = int(root.find("size").find("width").text)
        height = int(root.find("size").find("height").text)
        image = {
            "file_name": filename,
            "height": height,
            "width": width,
            "id": image_id}
        json_dict["images"].append(image)

        for obj in root.findall("object"):
            try:
                bndbox = obj.find("bndbox")
                xmin = int(bndbox.find("xmin").text) - 1
                ymin = int(bndbox.find("ymin").text) - 1
                xmax = int(bndbox.find("xmax").text)
                ymax = int(bndbox.find("ymax").text)
                category_name = obj.find("name").text

                assert xmax > xmin
                assert ymax > ymin
                o_width = abs(xmax - xmin)
                o_height = abs(ymax - ymin)
                ann = {
                    "area": o_width * o_height,
                    "iscrowd": 0,
                    "image_id": image_id,
                    "bbox": [xmin, ymin, o_width, o_height],
                    "category_id": categories[category_name],
                    "id": bnd_id,
                    "ignore": 0,
                    "segmentation": [],
                }
                json_dict["annotations"].append(ann)
                bnd_id = bnd_id + 1
            except:
                print(xml_file)
                logger.error("some errors hanppend in xmin, xmax, ymin, ymax: {} {} {} {}".format(xmin, xmax, ymin, ymax))
                # print("xmin, xmax, ymin, ymax: {} {} {} {}".format(xmin, xmax, ymin, ymax))

    for cate, cid in categories.items():
        cat = {"supercategory": "", "id": cid, "name": cate}
        json_dict["categories"].append(cat)

    with open(json_path, "w", encoding="utf-8") as fw:
        json.dump(json_dict, fw, ensure_ascii=False, indent=4)


def read_txt(filename):
    '''
    读取单个txt文件，文件中包含多行，返回[]
    '''
    with open(filename, encoding='utf-8') as f:
        return f.readlines()


def drop_imageset(folder, xml_folder):
    """
    # 判断是否有 ImageSets/Main/ 文件夹
    # 平台导出数据集有，标准voc没有，需分别处理
    # 没有则需先创建该文件夹并生成trainval.txt
    Args:
        folder:

    Returns:

    """
    data_types = []
    if not os.path.exists(folder):
        os.makedirs(folder)
        trainval_path = os.path.join(folder, "trainval.txt")

        for root, _, files in os.walk(xml_folder):
            for xml_item in files:
                if not xml_item.endswith(".xml"):
                    continue
                xml_name = os.path.splitext(xml_item)[0]

                with open(trainval_path, "a+", encoding="utf-8") as fw:
                    fw.write(xml_name)
                    fw.write("\n")

    for root, _, files in os.walk(folder):
        num_txt = len(files)
        assert num_txt == 1, "there should be only one file in {}".format(folder)
        for txt_item in files:
            txt_name = os.path.splitext(txt_item)[0]
            data_types = [txt_name]
    return data_types


def get_args():
    parser = argparse.ArgumentParser(description="Convert Pascal VOC annotation to COCO format.")
    parser.add_argument("--voc_dir", help="Directory path to voc.", type=str, default='C:/Users/xgy/Desktop/voc_coco/voc')
    parser.add_argument("--out_coco_path", help="Directory path to COCO.", type=str, default='C:/Users/xgy/Desktop/voc_coco/cocotest')
    # parser.add_argument("--data_types", help="ImageSets/main中的txt.", type=list, default=['trainval'])
    args = parser.parse_args()
    return args


def main(voc_dir, out_coco_path):
    assert voc_dir != out_coco_path, "the output coco folder should be different from the original voc folder"

    voc_xml_dir = os.path.join(voc_dir, 'Annotations')
    voc_img_dir = os.path.join(voc_dir, 'JPEGImages')
    voc_txt_dir = os.path.join(voc_dir, 'ImageSets', 'Main')

    # ImageSets/Main/ 含的文件类（test、train、trainval、val）
    data_types = drop_imageset(voc_txt_dir, voc_xml_dir)
    # 若不含任何文件，则默认全部位于 trainval

    coco_json_dir = os.path.join(out_coco_path, 'Annotations')
    os.makedirs(coco_json_dir, exist_ok=True)

    for t in data_types:
        coco_img_dir = os.path.join(out_coco_path, t)
        os.makedirs(coco_img_dir, exist_ok=True)
        xml_files = []
        txt_file = os.path.join(voc_txt_dir, t + '.txt')
        txt_list = read_txt(txt_file)
        for txt in txt_list:
            filename = txt.replace('\n', '')
            xml_file = os.path.join(voc_xml_dir, filename + ".xml")
            xml_files.append(xml_file)
            # 把原始图像复制到目标文件夹
            img_type = is_img_exists(voc_img_dir, filename)
            if img_type:
                img_file = os.path.join(voc_img_dir, filename + img_type)
                to_img_file = os.path.join(coco_img_dir, filename + img_type)
                shutil.copy(img_file, to_img_file)

        print("Number of xml files: {}".format(len(xml_files)))
        # 不限制 txt 文件的名称
        # todo 从 voc 转 coco 时,生成的json，?统一命名为 train.json
        # 1207 修改为依 t 的取值而定
        out_json = os.path.join(coco_json_dir, t + '.json')
        convert(xml_files, out_json, voc_img_dir)
        print("Success: {}".format(out_json))


if __name__ == "__main__":
    # args = get_args()
    # main(args.voc_dir, args.out_coco_path)

    # voc_dir = "C:/Users/xgy/Desktop/eva_scene/eva"
    # out_coco_path = "C:/Users/xgy/Desktop/eva_scene/eva_test_coco"
    # main(voc_dir, out_coco_path)

    voc_dir = "../../test/eva_clothes_helmet/"
    out_coco_path = "../../test/coco_eva_clothes_helmet/"
    main(voc_dir, out_coco_path)
