# pylint: disable=bare-except
# pylint: disable=line-too-long

'''
    Module for basic image manipulations.
'''

# import subprocess
# import json
# import shutil
import os
import ffmpeg
from PIL import Image, UnidentifiedImageError
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


