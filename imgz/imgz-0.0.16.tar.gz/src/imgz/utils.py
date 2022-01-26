# -*- coding: utf8 -*-

from pathlib import Path

# 图片后缀名
SUFFIX_IMAGE = ['.jpg', '.png', '.jpeg', '.bmp']


def is_image_file(file_path):
    return Path(file_path).suffix.lower() in SUFFIX_IMAGE
