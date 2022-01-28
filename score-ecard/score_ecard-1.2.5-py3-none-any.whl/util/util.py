# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@163.com
Date: 2021-11-5 15:17
Desc:
'''

import sys
import math
import inspect
from functools import wraps
import numpy as np
import time
import logging

# 1.进度条展示 progress_bar(1, 100)
def progress_bar(portion, total, is_pass=True):
    """
    total 总数据大小，portion 已经传送的数据大小
    :param portion: 已经接收的数据量
    :param total: 总数据量
    :return: 接收数据完成，返回True
    """
    if is_pass:
        return True
    part = total / 50  # 1%数据的大小
    count = math.ceil(portion / part)
    sys.stdout.write('\r')
    sys.stdout.write(('[%-50s]%.2f%%' % (('>' * count), portion / total * 100)))
    sys.stdout.flush()

    if portion >= total:
        sys.stdout.write('\n')
        return True
    return False

# 2.获取变量名
def get_retrieve_name(var):
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    list_name = [var_name for var_name, var_val in callers_local_vars if var_val is var]
    return list_name

# 3.计算加权方差
def get_weighted_std(values,weights):
    average = np.average(values, weights=weights)
    variance = np.average((values-average)**2, weights=weights)
    return variance

# 4.计算等频分箱
def get_frequence_blocks(x, box_num=10, drop_duplicates=True):
    '''
        等频分箱
    :param x: dtype=[]
    :param bins: 分箱数量
    :return: 箱边界
    '''
    x=np.sort(x).astype(float)
    len_clocks = int(min(len(x),box_num))
    ind = np.linspace(0, len(x)-1, len_clocks+1).astype(int)
    blocks=np.array(x)[ind].astype(float)
    if drop_duplicates:
        blocks = np.unique(blocks)
    if len(blocks)<2:
        return [-np.inf,np.inf]
    blocks[0] = -np.inf
    blocks[-1] = np.inf
    return blocks.tolist()

# 4.计算等距分箱
def get_distince_blocks(x, box_num=5, drop_duplicates=True):
    '''
        等距分箱
    :param x: dtype=[]
    :param bins: 分箱数量
    :return: 箱边界
    '''
    blocks = np.linspace(min(x), max(x), box_num+1).astype(float)
    if drop_duplicates:
        blocks = np.unique(blocks)
    if len(blocks)<2:
        return [-np.inf,np.inf]
    blocks[0] = -np.inf
    blocks[-1] = np.inf
    return blocks.tolist()

# 5.函数执行时间
def log_run_time(func):
    logging.basicConfig(level='INFO')
    logger = logging.getLogger()
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        if kwargs.get('log', True):
            func_start_time = time.time()
            logger.info('{} Start {}'.format(func_name, time_format(func_start_time)))
        result = func(*args, **kwargs)
        if kwargs.get('log', True):
            func_end_time = time.time()
            func_runtime = func_end_time - func_start_time
            logger.info('{} End {}, Runtime {} S'.format(func_name, time_format(func_end_time), func_runtime))
        return result
    return wrapper

def log_cur_time(info=""):
    logging.basicConfig(level='INFO')
    logger = logging.getLogger()
    lineno = sys._getframe().f_back.f_lineno
    co_name = sys._getframe().f_back.f_code.co_name
    logger.info('{}:lineno_{} Start {}{}'.format(co_name,lineno, time_format(time.time()), info))

def log_step(info):
    logging.basicConfig(level='INFO')
    logger = logging.getLogger()
    logger.info('{} {}'.format(time_format(time.time()),info))

def time_format(time_value):
    local_time = time.localtime(time_value)
    data_head = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    data_secs = (time_value - int(time_value)) * 1000
    time_stamp = "%s.%03d" % (data_head, data_secs)
    return time_stamp