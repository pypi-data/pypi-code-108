#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2021/9/2 16:32
# @Author  : xgy
# @Site    : 
# @File    : datatools.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import argparse
from datatools.dataset import coco2voc
from datatools.dataset import coco_check, voc_check, voc2coco
from datatools.split import coco_split, voc_split

# usag = "datatools --split --form coco --data_dir C:/Users/xgy/Desktop/voc_coco/cocotest1 --division_ratio 0.9 0.8"


def get_args():
    parser = argparse.ArgumentParser(description="tools for voc/coco dataset")
    parser.add_argument("--form", help="the form of the dataset", type=str, required=True, default=None,
                        choices=["coco", "COCO", "VOC", "voc"])
    parser.add_argument("--data_dir", help="the dir of the dataset", type=str, required=True, default=None)

    parser.add_argument("--split", action='store_true', default=False, help='Set a switch to split. Usually after the transform operation')
    parser.add_argument("--division_ratio", help="data segmentation ratio", type=float, default=[0.9, 0.8], nargs='+')

    parser.add_argument("--transform", action='store_true', default=False, help='Set a switch to transform')
    # parser.add_argument("--txtname", help="txt file name in ImageSets/Main/'", type=str, default=["trainval"], nargs='+')
    parser.add_argument("--output_transform", help="dir of output that should be different from the data_dir", type=str, default="./output_transform")

    parser.add_argument("--check", action='store_true', default=False, help='Set a switch to check')
    parser.add_argument("--output_check", help="dir for output", type=str, default="./output_check")
    parser.add_argument("--labelfile", help="the labels.txt from the platform", type=str, default=None)

    parser.add_argument("--eva")
    args = parser.parse_args()
    return args


def main():
    args = get_args()

    if args.split:
        if args.form == "VOC" or args.form == "voc":
            voc_split.main(args.data_dir, args.division_ratio)
        if args.form == "COCO" or args.form == "coco":
            coco_split.main(args.data_dir, args.division_ratio)

    if args.transform:
        if args.form == "VOC" or args.form == "voc":
            voc2coco.main(args.data_dir, args.output_transform)
        if args.form == "COCO" or args.form == "coco":
            coco2voc.main(args.data_dir, args.output_transform)

    if args.check:
        if args.form == "VOC" or args.form == "voc":
            voc_check.main(args.data_dir, args.labelfile, args.output_check)
        if args.form == "COCO" or args.form == "coco":
            coco_check.main(args.data_dir, args.output_check)


if __name__ == '__main__':
    print("start")
    main()
