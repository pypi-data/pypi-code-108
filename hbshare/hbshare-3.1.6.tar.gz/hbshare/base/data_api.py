# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Pro数据接口 
Created on 2020/06/15
@author: meng.lv
@group : hbshare
"""

import simplejson as json
from functools import partial
import requests


class DataApi:

    __token = ''
    __base_url = 'https://data.howbuy.com'

    def __init__(self, token, timeout=300):
        """
        Parameters
        ----------
        token: str
            API接口TOKEN，用于用户认证
        """
        self.__token = token
        if timeout and timeout > 600:
            # 最大600
            timeout = 600
        self.__timeout = timeout

    def query(self, url, method='get', post_data={}):
        headers = {
            "token": self.__token,
            "Referer": 'hbshare'
        }

        if method == 'get':
            res = requests.get(url, headers=headers, timeout=self.__timeout)
        else:
            res = requests.post(url, json=post_data, headers=headers, timeout=self.__timeout)
        if res.status_code != 200:
            res.raise_for_status()
        result = json.loads(res.text)
        return result

    def get(self, url):
        headers = {
            "token": self.__token,
            "Referer": 'hbshare'
        }

        res = requests.get(url, headers=headers, timeout=self.__timeout)

        return res.text

    def __getattr__(self, name):
        return partial(self.query, name)

    def __str__(self):
        return u"%s, %s" % (self.__base_url, self.__token)
