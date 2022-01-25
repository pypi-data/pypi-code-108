# -*- coding: utf-8 -*-
'''
Created on 2021-8-27

@author: zhys513(254851907@qq.com)
'''
import os
from xml.etree.ElementTree import ElementTree, Element


def gen_size(width_str, height_str, depth_str='3'):
    size = Element('size')

    depth = Element('depth')
    depth.text = depth_str

    width = Element('width')
    width.text = width_str

    height = Element('height')
    height.text = height_str

    size.append(depth)
    size.append(width)
    size.append(height)

    return size


def gen_source(database_str='Unknown'):
    source = Element('source')

    database = Element('database')
    database.text = database_str

    source.append(database)

    return source


def gen_object(name_str, xmin, ymin, xmax, ymax, truncated_str='0', difficult_str='0', pose_str='Unspecified'):
    name = Element('name')
    name.text = str(name_str)

    pose = Element('pose')
    pose.text = pose_str

    truncated = Element('truncated')
    truncated.text = truncated_str

    difficult = Element('difficult')
    difficult.text = difficult_str
     
    xmin_e = Element('xmin')
    xmin_e.text = str(xmin)

    ymin_e = Element('ymin')
    ymin_e.text = str(ymin)

    xmax_e = Element('xmax')
    xmax_e.text = str(xmax)

    ymax_e = Element('ymax')
    ymax_e.text = str(ymax)

    bndbox = Element('bndbox')
    bndbox.append(xmin_e)
    bndbox.append(ymin_e)
    bndbox.append(xmax_e)
    bndbox.append(ymax_e)
    
    oo_e = Element('object')
    oo_e.append(name) 
    oo_e.append(pose) 
    oo_e.append(truncated) 
    oo_e.append(difficult) 
    oo_e.append(bndbox) 
    return oo_e


# 格式化
def __indent(elem, level=0):
    i = "\n" + level*"\t"
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "\t"
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            __indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def gen_voc_xml(boxes: list, file_path, img_w, img_h, out_file):
    tree = ElementTree()
    annotation = Element('annotation')

    path = Element('path')
    path.text = file_path

    folder = Element('folder')
    folder.text = "JPEGImages"

    filename = Element('filename')
    filename.text = os.path.basename(file_path)

    img_w = str(img_w)
    img_h = str(img_h)
    size = gen_size(img_w, img_h)
    source = gen_source()

    segmented = Element('segmented')
    segmented.text = "0"

    annotation.append(path)
    annotation.append(folder)
    annotation.append(filename)
    annotation.append(size)
    annotation.append(source)
    annotation.append(segmented)

    for index, box in enumerate(boxes):
        object_item = gen_object(box["category"], box["xmin"], box["ymin"], box["xmax"], box["ymax"],)
        annotation.append(object_item)

    __indent(annotation)
    tree._setroot(annotation)
    tree.write(out_file, encoding="utf-8")

    return


if __name__ == '__main__':
    gen_voc_xml()

