#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: LiangChao
@email：liangchao@noboauto.com
@desc: 
"""
import os
import sys

from . import py
from .err import ErrorCapture
from .ospath import Path


def parse_root_dirs(path):
    """
    解析给定路径下的根级包目录
    :param path:
    :return:
    """
    packages = []
    if not isinstance(path, Path):
        path = Path(path)

    def search(p):
        recurse_child = True
        for item in p.files('__init__.py'):
            parent = item.parent
            packages.append(parent)
            recurse_child = False
            break
        if recurse_child:
            for item in p.dirs():
                search(item)

    search(path)
    return packages


def check_project(path):
    error_capture = ErrorCapture()
    pkg_dirs = parse_root_dirs(path)
    for _dir in pkg_dirs:
        if _dir in sys.path:
            sys.path.remove(_dir.parent)
            sys.path.insert(0, _dir.parent)
        py.get_object(_dir)
        for path, dirs, files in os.walk(_dir):
            # for d in dirs:
            #     if d.startswith(('_', '.')):
            #         continue
            #     test_name = os.path.join(path, d)
            #     with error_capture():
            #         py.get_object(test_name)
            for f in files:
                if not f.endswith('.py'):
                    continue
                test_name = os.path.join(path, f)
                with error_capture():
                    py.get_object(test_name)

    return error_capture.errors
