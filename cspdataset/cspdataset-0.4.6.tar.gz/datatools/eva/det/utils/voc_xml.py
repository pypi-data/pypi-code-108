# -*- coding: utf-8 -*-
'''
Created on 2021-8-27

@author: zhys513(254851907@qq.com)
'''
from xml.etree.ElementTree import ElementTree, Element


def gen_size(width,height,depth='3'):
    width_e = Element('width') 
    width_e.text = str(width)
    height_e = Element('height')
    height_e.text = str(height)
    depth_e = Element('depth')
    depth_e.text = str(depth)
     
    size_e = Element('size')
    size_e.append(width_e)
    size_e.append(height_e)
    size_e.append(depth_e)
    return size_e
 
def gen_source(database='Unknown'):
    database_e = Element('database') 
    source_e = Element('source') 
    source_e.append(database_e)
    return source_e

def gen_object(name,xmin,ymin,xmax,ymax,truncated='0',difficult='0',pose='Unspecified' ): 
    name_e = Element('name')
    name_e.text = str(name)
    pose_e = Element('pose')
    pose_e.text = pose
    truncated_e = Element('truncated')
    truncated_e.text = truncated
    difficult_e = Element('difficult')
    difficult_e.text = difficult
     
    xmin_e = Element('xmin')
    xmin_e.text = str(xmin) 
    ymin_e = Element('ymin')
    ymin_e.text = str(ymin) 
    xmax_e = Element('xmax')
    xmax_e.text = str(xmax) 
    ymax_e = Element('ymax')
    ymax_e.text = str(ymax)  
    bndbox_e = Element('bndbox')
    bndbox_e.append(xmin_e)
    bndbox_e.append(ymin_e)
    bndbox_e.append(xmax_e)
    bndbox_e.append(ymax_e)
    
    oo_e = Element('object')
    oo_e.append(name_e) 
    oo_e.append(pose_e) 
    oo_e.append(truncated_e) 
    oo_e.append(difficult_e) 
    oo_e.append(bndbox_e) 
     
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


def gen_voc_xml(filename,objects,width,height,output_voc_file_path): 
    tree = ElementTree()
    annotation = Element('annotation')
    folder = Element('folder') 
    annotation.append(folder)
    filename_e = Element('filename') 
    filename_e.text = filename
    annotation.append(filename_e)
    size = gen_size(width,height)
    annotation.append(size)
     
    for obj in objects:
        annotation.append(obj)
     
    source = gen_source()
    annotation.append(source)
    
    __indent(annotation)
    tree._setroot(annotation)   
    
    if output_voc_file_path:
        tree.write(output_voc_file_path,encoding = "utf-8")
        

if __name__ == "__main__": 
    obj = gen_object('test',1,2,3,4)
    gen_voc_xml([obj],11,22,'test.xml')
