# @Author: chunyang.xu
# @Email:  398745129@qq.com
# @Date:   2020-06-08 16:42:55
# @Last Modified time: 2021-03-26 14:43:20
# @github: https://github.com/longfengpili

# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import logging.handlers
import os
import errno


def mklogdir(path):
    try:
        os.makedirs(path, exist_ok=True)  # Python>3.2
    except TypeError:
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise


class MakeFileHandler(logging.handlers.TimedRotatingFileHandler):
    def __init__(self, filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False, atTime=None):
        mklogdir(os.path.dirname(filename))
        super(MakeFileHandler, self).__init__(filename, when, interval, backupCount, encoding, delay, utc, atTime)
