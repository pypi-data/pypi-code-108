#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import os


def new_report(test_report):
    """
    生成最新的测试报告文件
    :param test_report:
    :return:返回文件
    """
    # 列举test_dir目录下的所有文件，结果以列表形式返回。
    lists = os.listdir(test_report)
    # sort按key的关键字进行排序，lambda的入参fn为lists列表的元素，获取文件的最后修改时间. 最后对lists元素，按文件修改时间大小从小到大排序。
    lists.sort(key=lambda fn: os.path.getmtime(test_report + "/" + fn))
    # 获取最新文件的绝对路径
    file_new = os.path.join(test_report, lists[-1])
    return file_new
