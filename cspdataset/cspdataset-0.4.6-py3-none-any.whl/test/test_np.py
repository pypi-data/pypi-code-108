#!/usr/bin/env python
# encoding: utf-8
"""
# @Time    : 2021/9/10 14:59
# @Author  : xgy
# @Site    : 
# @File    : test_np.py
# @Software: PyCharm
# @python version: 3.7.4
"""

import numpy as np

x = np.array([[[1, 1, 1, 1, 1, 1, 1], [2, 2, 2, 2, 2, 2, 2], [3, 3, 3, 3, 3, 3, 3], [4, 4, 4, 4, 4, 4, 4]]])


if __name__ == '__main__':
    shape_test = np.shape(x)
    test = x[0][0][0]
    print("start")
