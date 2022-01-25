#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   file_tool.py    
@Contact :   mitiandameng@gmail.com
@License :   (C)Copyright 2020-2021, TianZhiXiang.
@Software:   PyCharm
@Modify Time      @Author    @Version    @Description
------------      -------    --------    -----------
2021-12-17 13:40     douly      1.0         file_tool
"""
# import lib
import os


def get_latest_file_in_dir(path):
    """
    文件夹中最新生成的文件,不包含文件夹和最新修改的文件
    :param path: 目标文件夹
    :return: 最新生成文件的完整路径, 生成时间戳
    """

    latest_tm = 0
    latest_file = ''
    for root, _, files in os.walk(path):
        for f in files:
            t_path = os.path.join(root, f)
            t = os.path.getctime(t_path)
            if t > latest_tm:
                latest_tm = t
                latest_file = t_path

    return latest_file, latest_tm