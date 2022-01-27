#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2021/2/8 3:26 下午
# @Author  : zhengyu.0985
# @FileName: http_sender_module.py
# @Software: PyCharm

import requests


class HttpSender(object):
    get_response = ""
    post_response = ""
    hostname = ""  # 公有的类属性
    __cookies = {}  # 私有的类属性

    # def __init__(self):
    #     print("HttpSender Default Constructor has been called.")

    def __init__(self, hostname, headers=None):
        print("HttpSender Parameter Constructor has been called.")
        self.hostname = hostname
        self.headers = headers  # self.headers的这个headers是实例属性，可以用实例直接方法。
        print("self.headers = {0}".format(self.headers))

    def set_headers(self, headers):
        self.headers = headers
        print("成员方法设置请求头：self.headers = {0}".format(self.headers))
        print("self.headers = {0}".format(self.headers))

    # 类方法，用classmethod来进行修饰
    # 注：类方法和实例方法同名，则类方法会覆盖实例方法。所以改个名字。
    @classmethod
    # def set_headers(cls, headers):
    def set_cls_headers(cls, headers):
        cls.headers = headers
        print("类方法设置请求头：cls.headers = {0}".format(cls.headers))

    def send_get_request(self, full_get_url):
        self.get_response = requests.get(full_get_url, headers=self.headers)
        print("响应：", self.get_response.text)

    def send_get_request_by_suburi(self, sub_uri, input_params):
        full_url = self.hostname + sub_uri
        self.get_response = requests.get(full_url, params=input_params, headers=self.headers)
        print("full_url = %s" % self.get_response.url)

    def send_post_request(self, full_post_url, param_data=None):
        self.post_response = requests.post(full_post_url, param_data, headers=self.headers)

    def send_json_post_request(self, full_post_url, json_data=None):
        self.post_response = requests.post(full_post_url, json=json_data, headers=self.headers)
        print("响应={0}".format(self.post_response.text))

    # 静态方法
    @staticmethod
    def send_json_post_request_with_headers_cookies(self, full_post_url, json_data=None, header_data=None, cookie_data=None):
        # 在静态方法中引用类属性的话，必须通过类实例对象来引用
        # print(self.hostname)
        self.post_response = requests.post(full_post_url, json=json_data, headers=header_data, cookies=cookie_data)

    def send_json_post_request_by_suburi(self, sub_uri, json_data=None):
        full_url = self.hostname + sub_uri
        print("full_url={0}".format(full_url))
        print("json_data={0}".format(json_data))
        self.post_response = requests.post(full_url, json=json_data, headers=self.headers)

# *args 和 **kwargs 都代表 1个 或 多个 参数的意思。*args 传入tuple 类型的无名参数，而 **kwargs 传入的参数是 dict 类型.
# 可变参数 (Variable Argument) 的方法：使用*args和**kwargs语法。# 其中，*args是可变的positional arguments列表，**kwargs是可变的keyword arguments列表。
# 并且，*args必须位于**kwargs之前，因为positional arguments必须位于keyword arguments之前。

#
# r = requests.get("http://www.baidu.com")
# print(r.text)
