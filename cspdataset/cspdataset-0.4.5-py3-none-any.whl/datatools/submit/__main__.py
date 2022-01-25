#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2021/9/16 16:12
# @Author  : xgy
# @Site    : 
# @File    : __main__.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import argparse
import os.path

from datatools.submit.platform2xml import json2xml
from datatools.submit.xml2platform import xml2platform

# usag = "submitools --form coco --data_dir C:/Users/xgy/Desktop/voc_coco/cocotest1 --img_dir eva/images/folder --output"


def get_args():
    parser = argparse.ArgumentParser(description="tools for submit")
    parser.add_argument("--form", help="the form of the dataset", type=str, required=True, default=None,
                        choices=["json", "xml"])
    parser.add_argument("--data_path", help="the dir of the xml dataset or submit json", type=str, required=True, default=None)
    parser.add_argument("--img_dir", type=str, default=None, help='the folder of imgs which used to eva')
    parser.add_argument("--output", help="the output of result", type=str, required=True)

    args = parser.parse_args()
    return args


def main():
    args = get_args()

    if args.form == "json":
        if not os.path.isfile(args.data_path):
            raise FileNotFoundError("when form is json the data_path should be a file such as eva.json. not {}".format(args.data_path))
        elif not os.path.isdir(args.output):
            raise FileNotFoundError(
                "when form is json the output should be a folder such as eva/xml/. not {}".format(args.output))
        else:
            json2xml(args.data_path, args.imgs, args.output_xml)
    if args.form == "xml":
        if not os.path.isdir(args.data_path):
            raise FileNotFoundError(
                "when form is xml the data_path should be a folder such as eva/xml/. not {}".format(args.data_path))
        elif not os.path.isfile(args.output):
            raise FileNotFoundError(
                "when form is xml the output should be a file such as eva.json. not {}".format(args.output))
        else:
            xml2platform(args.data_path, args.imgs, args.output_xml)


if __name__ == '__main__':
    print("start")
    main()
