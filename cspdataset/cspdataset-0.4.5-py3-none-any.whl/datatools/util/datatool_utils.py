#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2021/9/17 9:55
# @Author  : xgy
# @Site    : 
# @File    : datatool_utils.py
# @Software: PyCharm
# @python version: 3.7.4
"""
import os
# import shutil

from loguru import logger

img_types = [".jpg", ".JPG", ".JPEG", ".PNG", ".png"]


def is_img_exists(img_dir, img_name):
    flag_img_exists = False
    for img_type in img_types:
        img_file = os.path.join(img_dir, img_name + img_type)
        if os.path.exists(img_file):
            return img_type
    if not flag_img_exists:
        logger.warning("can not find img {} {} in {}".format(img_name, img_types, img_dir))
        return flag_img_exists


if __name__ == '__main__':
    print("start")
