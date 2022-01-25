#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2021/8/30 17:01
# @Author  : xgy
# @Site    : 
# @File    : test_xml.py
# @Software: PyCharm
# @python version: 3.7.4
"""

xml_path = "C:/Users/xgy/Desktop/voc_coco/voc/Annotations/00aa601a430543b9a7b202f30b47320a.xml"

import xml.etree.ElementTree as ET


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


tree = ET.parse(xml_path)
root = tree.getroot()
# for member in root.findall("size"):
#     # print(member.find("name").text)
#     print(member[0].text)

# size = get_and_check(root, "size", 1)
# width = int(get_and_check(size, "width", 1).text)
# width = int(root.find("size").find("width").text)
#
# for obj in root.findall("object"):
#     # try:
#     bndbox = obj.find("bndbox")
#     xmin = int(bndbox.find("xmin").text) - 1
#     print(xmin)

if __name__ == '__main__':
    print("start")
