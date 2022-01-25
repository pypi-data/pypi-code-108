# -*- coding: utf-8 -*-
"""
Created on 2021-9-30
@author: cxy(105...@qq.com)
"""

import shutil
import argparse
import json
import os
import yaml
import matplotlib.pyplot as plt
from matplotlib.pyplot import MultipleLocator
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import parse
from tqdm import tqdm


# 融合相关函数 ###########################################
def __indent(elem, level=0):
    i = "\n" + level * "\t"
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "\t"
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            __indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def fusing(hole_path, arm_path, out_path, confidence_labels_list):
    for hole_xml in os.listdir(hole_path):
        # 将同名xml合并
        if os.path.exists(os.path.join(arm_path, hole_xml)):
            # print('fusing', hole_xml)
            tree_hole = parse(os.path.join(hole_path, hole_xml))
            root_hole = tree_hole.getroot()  # annotation

            new_hole = tree_hole

            tree_arm = parse(os.path.join(arm_path, hole_xml))
            root_arm = tree_arm.getroot()  # annotation

            objects = tree_arm.findall('object')
            for j in range(len(objects)):
                # 改动起始 忽略与原始标注重复的标签
                box_name = objects[j].find('name').text
                if len(confidence_labels_list) != 0:
                    if box_name in confidence_labels_list:
                        continue
                # 改动截止
                root_hole.append(objects[j])
            __indent(root_hole)
            new_hole.write(out_path + '/' + hole_xml)  # join拼接报错
        # 不同名xml复制
        else:
            # print('copying', hole_xml)
            shutil.copy(os.path.join(hole_path, hole_xml), out_path)

    # 将不同名xml复制
    for arm_xml in os.listdir(arm_path):
        if not os.path.exists(os.path.join(out_path, arm_xml)):
            # print('copying')
            shutil.copy(os.path.join(arm_path, arm_xml), out_path)


def fusing_xml(dataset, annotations_list, dir_path, confidence_labels):
    # 全局变量
    dir_path = dir_path + '/fused'
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    base_path = dir_path + '/' + dataset
    # print('base_path: {}'.format(base_path))
    # print('annotations_list: {}'.format(annotations_list))
    if not os.path.exists(base_path):
        os.mkdir(base_path)
    out_path = 'Nothing has fused !'
    i = 0
    confidence_labels_list = []

    # 当前数据集的置信标签列表
    if dataset in confidence_labels.keys():
        confidence_labels_list = confidence_labels[dataset]

    # 原始标注文件排第一个
    # annotations_list = ['belt_ori', 'belt_glove', 'belt_clothes', 'belt_helmet']

    for i in range(len(annotations_list) - 1):
        if i == 0:
            hole_path = annotations_list[i]
            arm_path = annotations_list[i + 1]
            out_path = base_path + '/Annotations' + str(i + 2)
            if not os.path.exists(out_path):
                os.mkdir(out_path)
        else:
            hole_path = out_path
            arm_path = annotations_list[i + 1]
            out_path = base_path + '/Annotations' + str(i + 2)
            if not os.path.exists(out_path):
                os.mkdir(out_path)

        fusing(hole_path, arm_path, out_path, confidence_labels_list)

    if len(annotations_list) - 1 == 0:
        print('Only one xml dir, not need fusing !')
    else:
        print('{} xml dirs have fused !'.format(i + 2))

    # print('out_path: {}'.format(out_path))
    return out_path


def filter_labels(xmls_path, labels_list):
    results_path = xmls_path + r'_filter'
    if not os.path.exists(results_path):
        os.mkdir(results_path)

    names_xml = os.listdir(xmls_path)
    count = 0

    for name in names_xml:
        if name.endswith('.xml'):
            objects_list = []
            count += 1
            # 打开xml文档
            tree = ET.parse(xmls_path + '/' + name)
            # 获得root节点
            root = tree.getroot()

            for object in root.findall('object'):
                box_name = object.find('name').text
                if box_name not in labels_list:
                    root.remove(object)

            # 保存修改后的xml文件
            tree.write(results_path + '/' + name)

    return results_path


# 融合主函数(基于数据集) ###################################
def fuse_filter_xml_datasets(dir_path, filter_labels_dict):
    print('The input dir : {}'.format(dir_path))
    annotations_list = os.listdir(dir_path)
    dir_path_ori = dir_path
    # 全局变量
    dir_path = dir_path + '/fused'
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    i = 0
    base_path = dir_path
    out_path = 'Nothing has fused !'
    confidence_labels_list = []

    for i in range(len(annotations_list) - 1):
        if i == 0:
            hole_path = dir_path_ori + '/' + annotations_list[i]
            if annotations_list[i] in filter_labels_dict.keys():
                hole_path = filter_labels(hole_path, filter_labels_dict[annotations_list[i]])

            arm_path = dir_path_ori + '/' + annotations_list[i + 1]
            if annotations_list[i + 1] in filter_labels_dict.keys():
                arm_path = filter_labels(arm_path, filter_labels_dict[annotations_list[i + 1]])

            out_path = base_path + '/Annotations' + str(i + 2)
            if not os.path.exists(out_path):
                os.mkdir(out_path)
        else:
            hole_path = out_path

            arm_path = dir_path_ori + '/' + annotations_list[i + 1]
            if annotations_list[i + 1] in filter_labels_dict.keys():
                arm_path = filter_labels(arm_path, filter_labels_dict[annotations_list[i + 1]])

            out_path = base_path + '/Annotations' + str(i + 2)
            if not os.path.exists(out_path):
                os.mkdir(out_path)

        fusing(hole_path, arm_path, out_path, confidence_labels_list)

    if len(annotations_list) - 1 == 0:
        print('Only one xml dir, not need fusing !')
    else:
        print('{} xml dirs have fused !'.format(i + 2))

    print('Have finished all process, the final result is in dir: {} !'.format(out_path))
    print('********************************************************************************')

    return out_path


# 过滤相关函数 ###########################################
def handle(box_name, bndbox):
    dot = r'.'
    if dot in bndbox.find('xmin').text:
        xmin = float(bndbox.find('xmin').text)
        xmax = float(bndbox.find('xmax').text)
        ymin = float(bndbox.find('ymin').text)
        ymax = float(bndbox.find('ymax').text)
    else:
        xmin = int(bndbox.find('xmin').text)
        xmax = int(bndbox.find('xmax').text)
        ymin = int(bndbox.find('ymin').text)
        ymax = int(bndbox.find('ymax').text)

    return [box_name, xmin, xmax, ymin, ymax]


def filter_xml(Annotations):
    results = Annotations + '_filter'
    if not os.path.exists(results):
        os.makedirs(results)

    names_xml = os.listdir(Annotations)
    count = 0

    for name in names_xml:
        if name.endswith('.xml'):
            objects_list = []
            count += 1
            # 打开xml文档
            tree = ET.parse(Annotations + '/' + name)
            # 获得root节点
            root = tree.getroot()
            # # 获取原始图像的宽和高
            # img_size = root.find('size')
            # img_width = int(img_size.find('width').text)
            # img_height = int(img_size.find('height').text)

            # # 将xml中filename元素中的值后缀统一为.jpg
            # filename = root.find('filename').text
            # if filename.endswith('jpg'):
            #     pass
            # else:
            #     filename_split = filename.split('.')
            #     new_name = filename_split[0] + '.jpg'
            #     root.find('filename').text = new_name
            #     print('{0}: Have changed xml_file \' {1} \' name to \' {2} \' !'.format(count, filename, new_name))

            # # 先将原始标注数据的标签存入objects_list
            # for object in root.findall('object'):
            #     box_name = object.find('name').text
            #     bndbox = object.find('bndbox')
            #     dot = r'.'
            #     if dot in bndbox.find('xmin').text:
            #         continue
            #     else:
            #         object_list = handle(box_name, bndbox)
            #         objects_list.append(object_list)

            # # 预处理
            # for object in root.findall('object'):
            #     box_name = object.find('name').text
            #     bndbox = object.find('bndbox')
            #     # 将目标框的坐标值转为整型
            #     dot = r'.'
            #     if dot in bndbox.find('xmin').text:
            #         xmin = bndbox.find('xmin').text
            #         split = xmin.split('.')
            #         bndbox.find('xmin').text = split[0]
            #         xmax = bndbox.find('xmax').text
            #         split = xmax.split('.')
            #         bndbox.find('xmax').text = split[0]
            #         ymin = bndbox.find('ymin').text
            #         split = ymin.split('.')
            #         bndbox.find('ymin').text = split[0]
            #         ymax = bndbox.find('ymax').text
            #         split = ymax.split('.')
            #         bndbox.find('ymax').text = split[0]
            #     # 将长或高大于图像大小的目标框剔除
            #     if (int(bndbox.find('xmax').text) > img_width) or (int(bndbox.find('ymax').text) > img_height) or \
            #             (int(bndbox.find('xmin').text) < 0) or (int(bndbox.find('ymin').text) < 0):
            #         root.remove(object)
            #         print('Removing bigger than image_size box \'{0}\' of {1} !'.format(box_name, name))

            # 筛选每个目标框看是否符合相应要求
            for object in root.findall('object'):
                box_name = object.find('name').text
                bndbox = object.find('bndbox')
                find_flag = False

                # 将目标框的坐标值转为整型
                dot = r'.'
                if dot in bndbox.find('xmin').text:
                    xmin = bndbox.find('xmin').text
                    split = xmin.split('.')
                    bndbox.find('xmin').text = split[0]
                    xmax = bndbox.find('xmax').text
                    split = xmax.split('.')
                    bndbox.find('xmax').text = split[0]
                    ymin = bndbox.find('ymin').text
                    split = ymin.split('.')
                    bndbox.find('ymin').text = split[0]
                    ymax = bndbox.find('ymax').text
                    split = ymax.split('.')
                    bndbox.find('ymax').text = split[0]

                # 将长或高小于12的目标框直接剔除(上一段注释代码执行则支持处理浮点坐标)
                if (int(bndbox.find('xmax').text) - int(bndbox.find('xmin').text) < 12) or \
                        (int(bndbox.find('ymax').text) - int(bndbox.find('ymin').text) < 12):
                    root.remove(object)
                    # print('{0}: Removing small box \'{1}\' of {2} !'.format(count, box_name, name))
                # 进一步过滤与已存在目标框相似的目标框
                else:
                    object_list = handle(box_name, bndbox)
                    object_num = len(objects_list)
                    k_point = 0

                    for k in range(object_num):
                        if object_list[0] == objects_list[k][0]:
                            # 两框无交集
                            if (object_list[1] >= objects_list[k][2]) or (object_list[2] <= objects_list[k][1]) or \
                                    (object_list[3] >= objects_list[k][4]) or (object_list[4] <= objects_list[k][3]):
                                continue
                            # 原始标注数据中的目标框全部保留，上下左右全部相等的一定是预先加入列表的原始框，预测框几乎不可能
                            elif (object_list[1] == objects_list[k][1]) and (object_list[2] == objects_list[k][2]) and \
                                    (object_list[3] == objects_list[k][3]) and (object_list[4] == objects_list[k][4]):
                                continue
                            # 两框相交且水平或垂直方向边界波动50像素范围内的判定为相似，进行剔除
                            elif ((abs(object_list[1] - objects_list[k][1]) < 50) and (
                                    abs(object_list[2] - objects_list[k][2]) < 50)) or \
                                    ((abs(object_list[3] - objects_list[k][3]) < 50) and (
                                            abs(object_list[4] - objects_list[k][4]) < 50)):
                                root.remove(object)
                                find_flag = True
                                k_point = k
                                break
                            # 两框相交且水平或垂直方向重复达70%则判断为相似，进行剔除
                            else:
                                x_1 = min(object_list[2], objects_list[k][2]) - max(object_list[1], objects_list[k][1])
                                x_2 = objects_list[k][2] - objects_list[k][1]
                                y_1 = min(object_list[4], objects_list[k][4]) - max(object_list[3], objects_list[k][3])
                                y_2 = objects_list[k][4] - objects_list[k][3]
                                if (x_1 / x_2 >= 0.7) or (y_1 / y_2 >= 0.7):
                                    root.remove(object)
                                    find_flag = True
                                    k_point = k
                                    break

                    if find_flag and (k_point == object_num - 1):
                        pass
                        # print('{0}: Removing similar box \'{1}\' of {2}, and it has been find in last !'.format(count, box_name, name))
                    elif find_flag:
                        pass
                        # print('{0}: Removing similar box \'{1}\' of {2} !'.format(count, box_name, name))
                    else:
                        objects_list.append(object_list)

            # 保存修改后的xml文件
            tree.write(results + '/' + name)
            del objects_list

    print('Have handled {} xml files !'.format(count))

    return results


# 目标框平移函数 #########################################
def trans_box(xml_file_path, information_list):
    # 输入输出路径
    results = os.path.dirname(xml_file_path) + r'/trans_box_results'
    if not os.path.exists(results):
        os.makedirs(results)

    # 遍历每个xml文件
    count = 0
    names_xml = os.listdir(xml_file_path)
    for name in names_xml:
        if name.endswith('.xml'):
            count += 1
            tree = ET.parse(xml_file_path + '/' + name)  # 打开xml文档
            root = tree.getroot()  # 获得root节点

            # 图像的原始高度
            img_size = root.find('size')
            img_height = img_size.find('height').text
            height = int(img_height)
            img_width = img_size.find('width').text
            width = int(img_width)

            # 遍历每个object
            for object in root.findall('object'):
                box_name = object.find('name').text
                # 多组平移操作
                for information in information_list:
                    # 获取平移方向、百分比、标签名列表信息
                    orientation = information['orientation']
                    percentage = information['percentage']
                    box_name_list = information['box_name_list']
                    # 单组平移操作
                    if orientation == 'left':
                        if box_name in box_name_list:
                            bndbox = object.find('bndbox')
                            dot = r'.'
                            if dot in bndbox.find('xmin').text:
                                xmin = bndbox.find('xmin').text
                                min_split = xmin.split('.')
                                x_min = int(min_split[0])
                                xmax = bndbox.find('xmax').text
                                max_split = xmax.split('.')
                                x_max = int(max_split[0])

                                down_pixel = int((x_max - x_min) * percentage)

                                if (x_min - down_pixel) > 0:
                                    bndbox.find('xmin').text = str(x_min - down_pixel) + r'.' + min_split[1]
                                else:
                                    bndbox.find('xmin').text = r'0.' + min_split[1]

                                bndbox.find('xmax').text = str(x_max - down_pixel) + r'.' + max_split[1]
                            else:
                                xmin = bndbox.find('xmin').text
                                x_min = int(xmin)
                                xmax = bndbox.find('xmax').text
                                x_max = int(xmax)

                                down_pixel = int((x_max - x_min) * percentage)

                                if (x_min - down_pixel) > 0:
                                    bndbox.find('xmin').text = str(x_min - down_pixel)
                                else:
                                    bndbox.find('xmin').text = r'0'

                                bndbox.find('xmax').text = str(x_max - down_pixel)
                            print('{0} Have left \' {1} \' box {2}% !'.format(count, box_name, int(percentage * 100)))
                    elif orientation == 'right':
                        if box_name in box_name_list:
                            bndbox = object.find('bndbox')
                            dot = r'.'
                            if dot in bndbox.find('xmin').text:
                                xmin = bndbox.find('xmin').text
                                min_split = xmin.split('.')
                                x_min = int(min_split[0])
                                xmax = bndbox.find('xmax').text
                                max_split = xmax.split('.')
                                x_max = int(max_split[0])

                                down_pixel = int((x_max - x_min) * percentage)

                                if (x_max + down_pixel) < width:
                                    bndbox.find('xmax').text = str(x_max + down_pixel) + r'.' + min_split[1]
                                else:
                                    bndbox.find('xmax').text = str(width)

                                bndbox.find('xmin').text = str(x_min + down_pixel) + r'.' + max_split[1]
                            else:
                                xmin = bndbox.find('xmin').text
                                x_min = int(xmin)
                                xmax = bndbox.find('xmax').text
                                x_max = int(xmax)

                                down_pixel = int((x_max - x_min) * percentage)

                                if (x_max + down_pixel) < width:
                                    bndbox.find('xmax').text = str(x_max + down_pixel)
                                else:
                                    bndbox.find('xmax').text = str(width)

                                bndbox.find('xmin').text = str(x_min + down_pixel)
                            print('{0} Have right \' {1} \' box {2}% !'.format(count, box_name, int(percentage * 100)))
                    elif orientation == 'up':
                        if box_name in box_name_list:
                            bndbox = object.find('bndbox')
                            dot = r'.'
                            if dot in bndbox.find('ymin').text:
                                ymin = bndbox.find('ymin').text
                                min_split = ymin.split('.')
                                y_min = int(min_split[0])
                                ymax = bndbox.find('ymax').text
                                max_split = ymax.split('.')
                                y_max = int(max_split[0])

                                down_pixel = int((y_max - y_min) * percentage)

                                if (y_min - down_pixel) > 0:
                                    bndbox.find('ymin').text = str(y_min - down_pixel) + r'.' + min_split[1]
                                else:
                                    bndbox.find('ymin').text = r'0.' + min_split[1]

                                bndbox.find('ymax').text = str(y_max - down_pixel) + r'.' + max_split[1]
                            else:
                                ymin = bndbox.find('ymin').text
                                y_min = int(ymin)
                                ymax = bndbox.find('ymax').text
                                y_max = int(ymax)

                                down_pixel = int((y_max - y_min) * percentage)

                                if (y_min - down_pixel) > 0:
                                    bndbox.find('ymin').text = str(y_min - down_pixel)
                                else:
                                    bndbox.find('ymin').text = r'0'

                                bndbox.find('ymax').text = str(y_max - down_pixel)
                            print('{0} Have up \' {1} \' box {2}% !'.format(count, box_name, int(percentage * 100)))
                    elif orientation == 'down':
                        if box_name in box_name_list:
                            bndbox = object.find('bndbox')
                            dot = r'.'
                            if dot in bndbox.find('ymin').text:
                                ymin = bndbox.find('ymin').text
                                min_split = ymin.split('.')
                                y_min = int(min_split[0])
                                ymax = bndbox.find('ymax').text
                                max_split = ymax.split('.')
                                y_max = int(max_split[0])

                                down_pixel = int((y_max - y_min) * percentage)

                                if (y_max + down_pixel) < height:
                                    bndbox.find('ymax').text = str(y_max + down_pixel) + r'.' + min_split[1]
                                else:
                                    bndbox.find('ymax').text = str(height)

                                bndbox.find('ymin').text = str(y_min + down_pixel) + r'.' + max_split[1]
                            else:
                                ymin = bndbox.find('ymin').text
                                y_min = int(ymin)
                                ymax = bndbox.find('ymax').text
                                y_max = int(ymax)

                                down_pixel = int((y_max - y_min) * percentage)

                                if (y_max + down_pixel) < height:
                                    bndbox.find('ymax').text = str(y_max + down_pixel)
                                else:
                                    bndbox.find('ymax').text = str(height)

                                bndbox.find('ymin').text = str(y_min + down_pixel)
                            print('{0} Have down \' {1} \' box {2}% !'.format(count, box_name, int(percentage * 100)))
                    else:
                        print('The value of \'orientation\' is not correct !')
                        print('The value should be in [left, right, up, down] !')

            # 保存修改后的xml文件
            tree.write(results + '/' + name)

    # 打印最终处理的xml文件数
    print('Have handled {} xml files !'.format(count))


# 数据分析函数 ###########################################
def analysis_data(xml_file_path):
    # 输入输出路径
    results = os.path.dirname(xml_file_path) + r'/data_report'
    if not os.path.exists(results):
        os.makedirs(results)

    # 相关变量
    count = 0
    objects_name = []
    objects_num = {}
    images_size_w = []
    images_size_h = []
    images_size_ratio = []
    boxes_size_w = []
    boxes_size_h = []
    boxes_size_ratio = []

    # 遍历每个xml文件
    names_xml = os.listdir(xml_file_path)
    for name in tqdm(names_xml):
        if name.endswith('.xml'):
            # 获得每份xml文件的根节点
            count += 1
            tree = ET.parse(xml_file_path + '/' + name)  # 打开xml文档
            root = tree.getroot()  # 获得root节点

            # 图像长宽信息
            img_size = root.find('size')
            img_height = img_size.find('height').text
            height = int(img_height)
            img_width = img_size.find('width').text
            width = int(img_width)
            images_size_w.append(width)
            images_size_h.append(height)
            images_size_ratio.append(height/width)

            # 遍历每个object，获取目标框长宽信息、各类标签目标框数
            for object in root.findall('object'):
                # 各类标签个数累计
                object_name = object.find('name').text
                if object_name not in objects_name:
                    objects_name.append(object_name)
                    objects_num[object_name] = 1
                else:
                    objects_num[object_name] += 1

                # 目标框长宽信息
                bndbox = object.find('bndbox')
                dot = r'.'
                if dot in bndbox.find('xmin').text:
                    xmin = bndbox.find('xmin').text
                    min_split = xmin.split('.')
                    x_min = int(min_split[0])
                    xmax = bndbox.find('xmax').text
                    max_split = xmax.split('.')
                    x_max = int(max_split[0])
                    ymin = bndbox.find('ymin').text
                    min_split = ymin.split('.')
                    y_min = int(min_split[0])
                    ymax = bndbox.find('ymax').text
                    max_split = ymax.split('.')
                    y_max = int(max_split[0])
                    # 目标框宽高
                    box_width = x_max - x_min
                    box_height = y_max - y_min
                else:
                    xmin = bndbox.find('xmin').text
                    x_min = int(xmin)
                    xmax = bndbox.find('xmax').text
                    x_max = int(xmax)
                    ymin = bndbox.find('ymin').text
                    y_min = int(ymin)
                    ymax = bndbox.find('ymax').text
                    y_max = int(ymax)
                    # 目标框宽高
                    box_width = x_max - x_min
                    box_height = y_max - y_min
                boxes_size_w.append(box_width)
                boxes_size_h.append(box_height)
                boxes_size_ratio.append(box_height/box_width)

    # 保存输出每类标签目标框个数信息文档
    with open(results + '/labels_and_num.json', "w", encoding="utf-8") as fj:
        json.dump(objects_num, fj, ensure_ascii=False, indent=1)

    dpi = 15
    # 散点图(图像) ###########################################labelrotation=90
    plt.figure(figsize=(80, 40))
    plt.xlabel('Width', fontsize=80)
    plt.ylabel('Height', fontsize=80)
    plt.title('Images', fontsize=100)
    plt.tick_params(which='both', direction='inout', pad=30, width=5, length=15, labelsize=50)
    x_major_locator = MultipleLocator(500)
    ax = plt.gca()
    ax.xaxis.set_major_locator(x_major_locator)
    plt.scatter(images_size_w, images_size_h, c='r')
    plt.savefig(results + '/images.png', dpi=dpi)

    # 图像宽度分布
    num_bins = (max(images_size_w) - min(images_size_w)) // 200 + 1  # 柱状条个数
    plt.figure(figsize=(80, 40))
    plt.xlabel('Width', fontsize=80)
    plt.ylabel('Number', fontsize=80)
    plt.title('Distribution of Width about Images', fontsize=100)
    plt.tick_params(which='both', direction='inout', pad=30, width=5, length=15, labelsize=50)
    x_major_locator = MultipleLocator(200)
    ax = plt.gca()
    ax.xaxis.set_major_locator(x_major_locator)
    plt.hist(images_size_w, num_bins, facecolor='red', alpha=0.5)
    plt.savefig(results + '/images_width.png', dpi=dpi)

    # 图像高度分布
    num_bins = (max(images_size_h) - min(images_size_h)) // 200 + 1  # 柱状条个数
    plt.figure(figsize=(80, 40))
    plt.xlabel('Height', fontsize=80)
    plt.ylabel('Number', fontsize=80)
    plt.title('Distribution of Height about Images', fontsize=100)
    plt.tick_params(which='both', direction='inout', pad=30, width=5, length=15, labelsize=50)
    x_major_locator = MultipleLocator(200)
    ax = plt.gca()
    ax.xaxis.set_major_locator(x_major_locator)
    plt.hist(images_size_h, num_bins, facecolor='red', alpha=0.5)
    plt.savefig(results + '/images_height.png', dpi=dpi)

    # 图像高/宽比分布
    num_bins = 20
    plt.figure(figsize=(80, 40))
    plt.xlabel('Height', fontsize=80)
    plt.ylabel('Number', fontsize=80)
    plt.title('Distribution of Ratio(Height/Width) about Images', fontsize=100)
    plt.tick_params(which='both', direction='inout', pad=30, width=5, length=15, labelsize=50)
    x_major_locator = MultipleLocator(0.1)
    ax = plt.gca()
    ax.xaxis.set_major_locator(x_major_locator)
    plt.hist(images_size_ratio, num_bins, facecolor='red', alpha=0.5)
    plt.savefig(results + '/images_ratio.png', dpi=dpi)

    # 散点图(目标框) ##########################################
    plt.figure(figsize=(80, 40))
    plt.xlabel('Width', fontsize=80)
    plt.ylabel('Height', fontsize=80)
    plt.title('Boxes', fontsize=100)
    plt.tick_params(which='both', direction='inout', pad=30, width=5, length=15, labelsize=50)
    x_major_locator = MultipleLocator(500)
    ax = plt.gca()
    ax.xaxis.set_major_locator(x_major_locator)
    plt.scatter(boxes_size_w, boxes_size_h, c='b')
    plt.savefig(results + '/boxes.png', dpi=dpi)

    # 目标框宽度分布
    num_bins = (max(boxes_size_w) - min(boxes_size_w)) // 200 + 1  # 柱状条个数
    plt.figure(figsize=(80, 40))
    plt.xlabel('Width', fontsize=80)
    plt.ylabel('Number', fontsize=80)
    plt.title('Distribution of Width about Boxes', fontsize=100)
    plt.tick_params(which='both', direction='inout', pad=30, width=5, length=15, labelsize=50)
    x_major_locator = MultipleLocator(200)
    ax = plt.gca()
    ax.xaxis.set_major_locator(x_major_locator)
    plt.hist(boxes_size_w, num_bins, facecolor='blue', alpha=0.5)
    plt.savefig(results + '/boxes_width.png', dpi=dpi)

    # 目标框高度分布
    num_bins = (max(boxes_size_h) - min(boxes_size_h)) // 200 + 1  # 柱状条个数
    plt.figure(figsize=(80, 40))
    plt.xlabel('Height', fontsize=80)
    plt.ylabel('Number', fontsize=80)
    plt.title('Distribution of Height about Boxes', fontsize=100)
    plt.tick_params(which='both', direction='inout', pad=30, width=5, length=15, labelsize=50)
    x_major_locator = MultipleLocator(200)
    ax = plt.gca()
    ax.xaxis.set_major_locator(x_major_locator)
    plt.hist(boxes_size_h, num_bins, facecolor='blue', alpha=0.5)
    plt.savefig(results + '/boxes_height.png', dpi=dpi)

    # 目标框高/宽比分布
    num_bins = 30
    plt.figure(figsize=(80, 40))
    plt.xlabel('Height', fontsize=80)
    plt.ylabel('Number', fontsize=80)
    plt.title('Distribution of Ratio(Height/Width) about Boxes', fontsize=100)
    plt.tick_params(which='both', direction='inout', pad=30, width=5, length=15, labelsize=50)
    x_major_locator = MultipleLocator(0.4)
    ax = plt.gca()
    ax.xaxis.set_major_locator(x_major_locator)
    plt.hist(boxes_size_ratio, num_bins, facecolor='blue', alpha=0.5)
    plt.savefig(results + '/boxes_ratio.png', dpi=dpi)

    print('Have finished EDA process, the result is in dir: {} !'.format(results))


# 融合主函数(基于模型) ####################################
def fuse_filter_xml(dir_path, confidence_labels_of_datasets):
    final_return_dir = ''

    print('The input dir : {}'.format(dir_path))
    flag_data = True
    models = os.listdir(dir_path)
    # 检查每个模型目录下的数据集个数是否符合要求
    for model in models:
        model_path = dir_path + '/' + model
        model_datasets = os.listdir(model_path)
        if len(model_datasets) != len(models):
            flag_data = False
            print('The number of datasets is incorrect in dir: {} !'.format(model_path))
            break
    # 数据的组织结构正确则开始后续的操作
    if flag_data:
        models_path = []
        for model in models:
            model_path = dir_path + '/' + model
            models_path.append(model_path)
        model_datasets = os.listdir(models_path[0])
        datasets_fuse_dir = []

        datasets_num = len(model_datasets)
        print('datasets_num: {}'.format(datasets_num))

        # 以数据集为单位，对不同模型在该数据集下的标注数据进行融合
        # i 数据集索引
        for i in range(datasets_num):
            datasets_path = []
            first_dataset_list = []

            # j 模型索引
            for j in range(datasets_num):
                if model_datasets[i] in models_path[j]:
                    first_dataset_list.append(models_path[j] + '/' + model_datasets[i])
                else:
                    datasets_path.append(models_path[j] + '/' + model_datasets[i])
            datasets_path = first_dataset_list + datasets_path

            # 替换标注数据文件夹路径中所有的'\'为'/'
            for k in range(len(datasets_path)):
                datasets_path[k].replace('\\', '/')
            print('################################################################################')
            print('Fusing the {0}th dataset from these dir: \n{1}'.format(i + 1, datasets_path))

            dataset_fuse_dir = fusing_xml(model_datasets[i], datasets_path, dir_path, confidence_labels_of_datasets)
            datasets_fuse_dir.append(dataset_fuse_dir)

            del first_dataset_list
            del datasets_path

        # 所有数据集的标注数据进行融合
        print('################################################################################')
        print('Fusing the all dataset from these dir: \n{}'.format(datasets_fuse_dir))
        final_fuse_dir = fusing_xml('final_xml', datasets_fuse_dir, dir_path, confidence_labels_of_datasets)
        print('The final fusing result is in dir: {}'.format(final_fuse_dir))

        # 对最终融合结果进行过滤
        print('################################################################################')
        print('Begin filtering the final fusing result !')
        final_fuse_dir = filter_xml(final_fuse_dir)
        print('Have finished all process, the final result is in dir: {} !'.format(final_fuse_dir))
        print('********************************************************************************')
        final_return_dir = final_fuse_dir

    return final_return_dir


# 原main函数
# def main():
#     parser = argparse.ArgumentParser()
#     parser.add_argument('-p', type=str, default=None, help='The path of yaml file !')
#     args = parser.parse_args()
#
#     # 仅需传入yaml配置文件所在位置即可
#     if args.p:
#         print('################################################################################')
#         print('Reading yaml file......')
#         with open(args.p, 'r', encoding='utf-8') as f:
#             yaml_dict = yaml.safe_load(f)
#         print('Finish reading, the information of yaml file is as follows: ')
#         print(yaml_dict)
#
#         # 融合、标签平移、EDA
#         path = ''
#         if yaml_dict['fuse_filter']:  # 融合操作
#             # 选择融合方式以及是否开启标签平移
#             if yaml_dict['mode'] == 'model':
#                 xml_path = yaml_dict['xml_path']
#                 repeated_labels_of_datasets = yaml_dict['repeated_labels']
#                 path = fuse_filter_xml(xml_path, repeated_labels_of_datasets)
#                 if yaml_dict['translate']:
#                     groups_list = yaml_dict['trans_box']
#                     trans_box(path, groups_list)
#                 if yaml_dict['eda']:
#                     analysis_data(path)
#             elif yaml_dict['mode'] == 'dataset':
#                 xml_path = yaml_dict['xml_path']
#                 used_labels_of_datasets = yaml_dict['used_labels']
#                 path = fuse_filter_xml_datasets(xml_path, used_labels_of_datasets)
#                 if yaml_dict['translate']:
#                     groups_list = yaml_dict['trans_box']
#                     trans_box(path, groups_list)
#                 if yaml_dict['eda']:
#                     analysis_data(path)
#             else:
#                 print(r'The value of \'mode\' has not been specified correctly in yaml file !')
#                 print(r'The value of \'mode\' can be in [model, dataset] !')
#         elif yaml_dict['translate']:  # 仅标签平移操作
#             path = yaml_dict['trans_box_path']
#             groups_list = yaml_dict['trans_box']
#             trans_box(path, groups_list)
#         elif yaml_dict['eda']:  # 仅EDA操作
#             path = yaml_dict['eda_path']
#             analysis_data(path)
#         else:
#             print('Do nothing !')
#
#         # 各标签相关信息统计报告
#         pass
#     else:
#         print('You should use this script as follows for help: ')
#         print('edatools -h')


# 仅开放eda操作的main函数
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', type=str, default=None, help='The path of xml files dir !')
    args = parser.parse_args()

    if args.f:
        print('Beginning analysis ...... , please wait a moment !')
        analysis_data(args.f)
    else:
        print('You should use this command as follows for help:')
        print('edatools -h')


if __name__ == '__main__':
    print("start")
    main()

