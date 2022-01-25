#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2021/8/31 16:30
# @Author  : xgy
# @Site    : 
# @File    : test_split.py
# @Software: PyCharm
# @python version: 3.7.4
"""
import os
import shutil
import xml.etree.ElementTree as ET

test_dir = "C:/Users/xgy/Desktop/voc_coco/cocotest3/Images/train"

train_imgs = ["00aa601a430543b9a7b202f30b47320a.jpg", "00d64fd120dc4e4fb265b3231d4d427f.jpg"]
test_imgs = ["00baa6ca705849e49bc4589488efa33b.jpg", "00aac17e02ff4437a32fe054510eb634.jpg"]


if __name__ == '__main__':
    print("start")

    # for root, _, files in os.walk(test_dir):
    #     for file in files:
    #         print(file)
    #         ori_path = os.path.join(root, file)
    #         if file in test_imgs:
    #             dst_path = os.path.join("C:/Users/xgy/Desktop/voc_coco/cocotest3/Images/test", file)
    #             shutil.move(ori_path, dst_path)

    # total_xml = os.listdir("C:/Users/xgy/Desktop/voc_coco/voctest1/Annotations")
    # for item in total_xml:
    #     img_path = os.path.join("C:/Users/xgy/Desktop/voc_coco/voctest1/Annotations", item)

    test_dict = {"w": 0}

    test_w = test_dict.get("w", None)
    if not test_w and test_w != 0:
        print("success")
