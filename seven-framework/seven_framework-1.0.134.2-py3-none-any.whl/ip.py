# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2021-11-05 10:50:40
:LastEditTime: 2021-11-05 11:41:00
:LastEditors: ChenXiaolei
:Description: IP信息帮助类
"""

from seven_framework import http, json


class IPHelper:
    ip_info_api_url = "https://ps.gao7.com/ip_info"

    @classmethod
    def get_ip_info(self, ip):
        """
        :description: 获取ip地址信息
        :param ip: ip地址
        :return 获取ip地址信息字典 包含国家、省份、城市
        :last_editors: ChenXiaolei
        """
        response = http.HTTPHelper.get(self.ip_info_api_url, params={"ip": ip})

        if not response or response.status_code != 200:
            return None

        ip_info_json = json.loads(response.text)

        if not ip_info_json or "data" not in ip_info_json or not ip_info_json["data"]:
            return None

        ip_info = ip_info_json["data"]

        return ip_info

    @classmethod
    def get_ip_country(self, ip):
        """
        :description: 获取IP归属国家
        :param ip: ip地址
        :return 国家字符串
        :last_editors: ChenXiaolei
        """
        ip_info = self.get_ip_info(ip)

        if not ip_info or "country_name" not in ip_info:
            return ""

        return ip_info["country_name"]

    @classmethod
    def get_ip_region(self, ip):
        """
        :description: 获取IP归属省份
        :param ip: ip地址
        :return 省份字符串
        :last_editors: ChenXiaolei
        """
        ip_info = self.get_ip_info(ip)

        if not ip_info or "region_name" not in ip_info:
            return ""

        return ip_info["region_name"]

    @classmethod
    def get_ip_city(self, ip):
        """
        :description: 获取IP归属城市
        :param ip: ip地址
        :return 城市字符串
        :last_editors: ChenXiaolei
        """
        ip_info = self.get_ip_info(ip)

        if not ip_info or "city_name" not in ip_info:
            return ""

        return ip_info["city_name"]
