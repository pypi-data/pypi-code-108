#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2021/12/3 16:28
# @Author  : xgy
# @Site    : 
# @File    : __main__.py
# @Software: PyCharm
# @python version: 3.7.4
"""
import argparse
from datatools.aug.imgaugments import data_aug


def get_args():
    parser = argparse.ArgumentParser(description="tools for voc/coco dataset")
    parser.add_argument("--aug_config", "-f", help="the config file of aug (yml)", type=str, required=True, default=None)
    parser.add_argument("--data_dir", "-i", help="the folder of data", type=str, required=True, default=None)
    args = parser.parse_args()
    return args


def main():
    args = get_args()

    data_aug(args.aug_config, args.data_dir)


if __name__ == '__main__':
    print("start")
    main()
