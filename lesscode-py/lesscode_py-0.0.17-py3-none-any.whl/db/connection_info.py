# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2021/11/25 9:52 上午
# Copyright (C) 2021 The lesscode Team

class ConnectionInfo:
    """
    数据库连接信息对象
    """

    def __init__(self, dialect, host, port, password, user=None, db_name=None, name=None, params=None, min_size=3,
                 max_size=10, enable=True, async_enable=True):
        # 数据库dialect类型
        self.dialect = dialect
        # 连接池名称
        if name:
            self.name = name
        else:
            self.name = dialect
        # 主机地址
        self.host = host
        # 端口号
        self.port = port
        # 用户名
        self.user = user
        # 密码
        self.password = password
        # 数据库名称
        self.db_name = db_name
        # 额外参数
        self.params = params
        # 最小数
        self.min_size = min_size
        # 最大数
        self.max_size = max_size
        # 是否启用
        self.enable = enable
        # 是否启用异步
        self.async_enable = async_enable
