# -*- coding:utf-8 -*- 
"""
pro init 
Created on 2018/07/01
@author: Jimmy Liu
@group : tushare.pro
@contact: jimmysoa@sina.cn
"""
from hbshare.base import data_api, upass


def hb_api(token='',timeout=300):
    """
    初始化pro API,第一次可以通过ts.set_token('your token')来记录自己的token凭证，临时token可以通过本参数传入
    """
    if token == '' or token is None:
        token = upass.get_token()
    if token is not None and token != '':
        pro = data_api.DataApi(token,timeout)
        return pro
    else:
        raise Exception('api init error.') 

