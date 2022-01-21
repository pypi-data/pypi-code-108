#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/1/14 10:25 上午
# @Author  : lance.txl
# @Site    : 
# @File    : date_utils.py
# @Software: PyCharm

from datetime import datetime,timedelta

def get_date_tag():
    """
    获取一个时间tag
    :return:
    """
    now = datetime.now()
    s = now.strftime("%Y%m%d-%H%M")
    return s
if __name__ == '__main__':
    get_date_tag()
