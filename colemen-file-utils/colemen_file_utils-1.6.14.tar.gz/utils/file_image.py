# pylint: disable=bare-except
# pylint: disable=line-too-long

'''
    Module for basic image manipulations.
'''

# import subprocess
# import json
# import shutil
# import os

# import ffmpeg
import json
from PIL import Image
from iptcinfo3 import IPTCInfo
# import re
# from pathlib import Path
import utils.file as f
import utils.objectUtils as obj
# import utils.file_read as read
import colemen_string_utils as csu
import colemen_string_utils as strUtils
# from threading import Thread

def genCssMediaScales(src_path,**kwargs):
    sizes = [1600,1400,1200,992,768,576,480]
    for size in sizes:
        scale(src_path, (size, size), keep_proportion=True)

def scale(src_path,size,**kwargs):
    if isinstance(size,(list,tuple)):
        width = size[0]
        height = size[1]
    else:
        print(f"size must be a list or tuple [width,height]")
        return False
    
    
    dst_path = obj.get_kwarg(['dst_path'], False, (str), **kwargs)
    keep_proportion = obj.get_kwarg(['keep_proportion'], True, (bool), **kwargs)

    sizeTuple = (width,height)
    if keep_proportion is True:
        if width > height:
            sizeTuple = (width,width)
        else:
            sizeTuple = (height, height)
            
    fileData = f.get_data(src_path)
    if dst_path is False:
        dst_path = f"{fileData['dir_path']}/{fileData['name_no_ext']}_{sizeTuple[0]}x{sizeTuple[1]}{fileData['extension']}"
    
    image = Image.open(src_path)
    image.thumbnail(sizeTuple, Image.ANTIALIAS)
    image.save(dst_path)

def tags_to_snakecase(file):
    file_array = []
    
    if isinstance(file,(str)):
        file_array = [f.get_data(file)]

    for file in file_array:
        if isinstance(file,(dict)):
            if 'file_path' in file:
                file = get_meta(file['file_path'])
                newTags = []
                for tag in file['iptc_data']['Keywords']:
                    newTags.append(csu.format.to_snake_case(tag))
                    
                file['iptc_data']['Keywords'] = list(set(newTags))
                save(file)
                print(json.dumps(file,indent=4))

def has_tag(file,tag):
    result_array = []
    file_array = _parse_file_obj_list(file)
    for file in file_array:
        if tag in file['iptc_data']['Keywords']:
            result_array.append(file)
    if len(result_array) > 0:
        return True
    return False


def get_meta(file):
    result_array = []
    file_array = _parse_file_obj_list(file)
    for file in file_array:
        # file = f.get_data(file_path)
        file['update_file'] = False
        # im = Image.open(x['file_path'])
        info = IPTCInfo(file['file_path'], force=True)
        # print(info.__dict__.items())
        for k, v in info.__dict__.items():
            # print(f"k: {k}    ::::     v: {v}")
            if k == '_data':
                file['iptc_data'] = formatIPTCData(v)
        if 'iptc_data' not in file:
            file['iptc_data'] = {"Keywords": [], "Description": [], "Contact": []}
        result_array.append(file)
    if len(result_array) == 1:
        return result_array[0]
    return result_array

def save(file):
    file_array = _parse_file_obj_list(file)

    for file in file_array:
        if 'iptc_data' in file:
            info = IPTCInfo(file['file_path'], force=True)
            info['Keywords'] = keywordsToBytes(file['iptc_data']['Keywords'])
            # info['supplemental category'] = file['iptc_data']['supplemental category']
            # info['Contact'] = file['iptc_data']['Contact']
            info.save_as(file['file_path'])
            f.delete(f'{file["file_path"]}~')

def _parse_file_obj_list(file):
    file_array = []
    if isinstance(file, (str)):
        if f.exists(file):
            file_array.append(f.get_data(file))

    if isinstance(file, (list)):
        for i in file:
            if isinstance(i, (str)):
                if f.exists(i):
                    file_array.append(f.get_data(i))
            if isinstance(i, (dict)):
                if 'file_path' in i:
                    file_array.append(i)

    if isinstance(file, (dict)):
        if 'file_path' in file:
            file_array = [file]
            
    return file_array

def formatIPTCData(d):
    data = {}
    if isinstance(d, str) or isinstance(d, bytes):
        return d.decode('utf-8')
    # print(f"d Type: {type(d)}")
    for k, v in d.items():
        if isinstance(v, dict):
            data[k] = formatIPTCData(v)
        if isinstance(v, list):
            nl = []
            for x in v:
                nl.append(formatIPTCData(x))

            key = decodeIPTCKey(k)
            data[key] = nl
        # else:
            # print(f"formatIPTCData: {k} : {v}")
    return data

def add_tag(file, keyword):
    result_array = []
    # Split the keyword by commas if there are any
    if isinstance(keyword,(str)):
        keyword = keyword.split(",")
    # generate a list of file objects from the file argument.
    file_array = _parse_file_obj_list(file)
    # print(f"file_array: ", json.dumps(file_array,indent=4))
    for file in file_array:
        if 'iptc_data' not in file:
            file = get_meta(file)
        # print(f"file: ", json.dumps(file, indent=4))
        iptc = file['iptc_data']
        if 'Keywords' not in iptc:
            iptc['Keywords'] = []

        if isinstance(keyword, list):
            for x in keyword:
                if x not in iptc['Keywords']:
                    iptc['Keywords'].append(x)
        if isinstance(keyword, str):
            if keyword not in iptc['Keywords']:
                iptc['Keywords'].append(keyword)
        if file['iptc_data']['Keywords'] != iptc:
            file['update_file'] = True
        file['iptc_data'] = iptc
        save(file)
        result_array.append(file)
    
    if len(result_array) == 1:
        return result_array[0]
    return result_array

def delete_tag(file, keyword):
    result_array = []
    # Split the keyword by commas if there are any
    if isinstance(keyword, (str)):
        keyword = keyword.split(",")
    # generate a list of file objects from the file argument.
    file_array = _parse_file_obj_list(file)
    # print(f"file_array: ", json.dumps(file_array,indent=4))
    for file in file_array:
        if 'iptc_data' not in file:
            file = get_meta(file)
        # print(f"file: ", json.dumps(file, indent=4))
        iptc = file['iptc_data']
        if 'Keywords' not in iptc:
            iptc['Keywords'] = []

        new_keywords = []
        for k in iptc['Keywords']:
            if k not in keyword:
                new_keywords.append(k)
        iptc['Keywords'] = new_keywords
                
        if file['iptc_data']['Keywords'] != iptc:
            file['update_file'] = True
        file['iptc_data'] = iptc
        save(file)
        result_array.append(file)

    if len(result_array) == 1:
        return result_array[0]
    return result_array



def decodeIPTCKey(n):
    d = {
        "25": "Keywords",
        "20": "supplemental category",
        "118": "Contact",
        "05": "Title",
        "55": "Date Created",
    }
    n = str(n)
    return d[n]

def keywordsToBytes(keys):
    nk = []
    for k in keys:
        nk.append(bytes(k.encode()))
    return nk
