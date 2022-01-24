# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2021-02-19 18:19:25
:LastEditTime: 2021-03-22 18:08:57
:LastEditors: ChenXiaolei
:Description: clickhouse帮助类
"""

import clickhouse_driver


class ClickhouseHelper(clickhouse_driver.Client):
    def __init__(self, *args, **kwargs):
        """
        :description: 初始化Clickhouse连接
        :demo clickhouse_client = ClickhouseHelper(**config.get_value("clickhouse_log_center")).clickhouse_client 
        :demo 配置:    
            {
                "host":"192.168.100.162",
                "port":"9000",
                "database":"log_center",
                "user":"default",
                "password":""
            }
        :return 无
        :last_editors: ChenXiaolei
        """
        self.clickhouse_client = clickhouse_driver.Client(*args, **kwargs)