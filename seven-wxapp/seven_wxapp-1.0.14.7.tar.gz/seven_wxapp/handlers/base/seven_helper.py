# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-04-22 14:32:40
:LastEditTime: 2021-04-14 09:29:51
:LastEditors: HuangJingCan
:description: 常用帮助类
"""
from seven_framework import *
import random
import hashlib
import datetime


class SevenHelper:
    """
    :description: 常用帮助类
    :last_editors: HuangJingCan
    """
    @classmethod
    def merge_dict_list(self, source_dict_list, source_key, merge_dict_list, merge_key, merge_columns_names):
        """
        :description: 两个字典列表合并
        :param source_dict_list：源字典表
        :param source_key：源表用来关联的字段
        :param merge_dict_list：需要合并的字典表
        :param merge_key：需要合并的字典表用来关联的字段
        :param merge_columns_names：需要合并的字典表中需要展示的字段
        :return: 
        :last_editors: HuangJingCan
        """
        result = []
        for source_dict in source_dict_list:
            info_list = [i for i in merge_dict_list if source_dict[source_key] != "" and i[merge_key] == source_dict[source_key]]
            if info_list:
                list_key = list(merge_columns_names.split(","))
                source_dict = dict(source_dict, **dict.fromkeys(list_key))
                for item in list_key:
                    source_dict[item] = info_list[0].get(item)
            else:
                list1 = list(merge_columns_names.split(","))
                source_dict = dict(source_dict, **dict.fromkeys(list1))
            result.append(source_dict)
        return result

    @classmethod
    def get_now_int(self, hours=0):
        """
        :description: 获取整形的时间 格式为yyyyMMddHHmmss，如2009年12月27日9点10分10秒表示为20091227091010
        :return:
        :last_editors: HuangJianYi
        """
        now_date = (datetime.datetime.now() + datetime.timedelta(hours=hours))
        return int(int(now_date.strftime('%Y%m%d%H%M%S')))

    @classmethod
    def get_now_day_int(self, hours=0):
        """
        :description: 获取整形的天20200506
        :return:
        :last_editors: HuangJianYi
        """
        now_date = (datetime.datetime.now() + datetime.timedelta(hours=hours))
        now_day = int(TimeHelper.datetime_to_format_time(now_date, "%Y%m%d"))
        return now_day

    @classmethod
    def get_now_month_int(self, hours=0):
        """
        :description: 获取整形的月202005
        :return:
        :last_editors: HuangJianYi
        """
        now_date = (datetime.datetime.now() + datetime.timedelta(hours=hours))
        now_month = int(TimeHelper.datetime_to_format_time(now_date, "%Y%m"))
        return now_month

    @classmethod
    def get_random(self, num, many):
        """
        :description: 获取随机数
        :param num：位数
        :param many：个数
        :return: str
        :last_editors: HuangJianYi
        """
        result = ""
        for x in range(many):
            s = ""
            for i in range(num):
                # n=1 生成数字  n=2 生成字母
                n = random.randint(1, 2)
                if n == 1:
                    numb = random.randint(0, 9)
                    s += str(numb)
                else:
                    nn = random.randint(1, 2)
                    cc = random.randint(1, 26)
                    if nn == 1:
                        numb = chr(64 + cc)
                        s += numb
                    else:
                        numb = chr(96 + cc)
                        s += numb
            result += s
        return result

    @classmethod
    def is_ip(self, ip_str):
        """
        :description: 判断是否IP地址
        :param ip_str: ip串
        :return:
        :last_editors: HuangJianYi
        """
        p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
        if p.match(str(ip_str)):
            return True
        return False

    @classmethod
    def get_condition_by_str_list(self, field_name, str_list):
        """
        :description: 根据str_list返回查询条件
        :param field_name: 字段名
        :param str_list: 字符串数组
        :return: 
        :last_editors: HuangJianYi
        """
        if not str_list:
            return ""
        list_str = ','.join(["'%s'" % str(item) for item in str_list])
        return f"{field_name} IN({list_str})"

    @classmethod
    def get_condition_by_int_list(self, field_name, int_list=None):
        '''
        :description: 根据int_list返回查询条件
        :param field_name:字段名
        :param int_list:整形数组
        :return: str
        :last_editors: HuangJianYi
        '''
        if not int_list:
            return ""
        list_str = str(int_list).strip('[').strip(']')
        return f"{field_name} IN({list_str})"

    @classmethod
    def get_page_count(self, page_size, record_count):
        """
        @description: 计算页数
        @param page_size：页大小
        @param record_count：总记录数
        @return: 页数
        @last_editors: HuangJingCan
        """
        page_count = record_count / page_size + 1
        if page_size == 0:
            page_count = 0
        if record_count % page_size == 0:
            page_count = record_count / page_size
        page_count = int(page_count)
        return page_count

    @classmethod
    def create_order_id(self, ran=5):
        """
        :description: 生成订单号
        :param ran：随机数位数，默认5位随机数（0-5）
        :return: 25位的订单号
        :last_editors: HuangJianYi
        """
        ran_num = ""
        if ran == 1:
            ran_num = random.randint(0, 9)
        elif ran == 2:
            ran_num = random.randint(10, 99)
        elif ran == 3:
            ran_num = random.randint(100, 999)
        elif ran == 4:
            ran_num = random.randint(1000, 9999)
        elif ran == 5:
            ran_num = random.randint(10000, 99999)
        # cur_time = TimeHelper.get_now_format_time('%Y%m%d%H%M%S%f')
        cur_time = TimeHelper.get_now_timestamp(True)
        order_id = str(cur_time) + str(ran_num)
        return order_id