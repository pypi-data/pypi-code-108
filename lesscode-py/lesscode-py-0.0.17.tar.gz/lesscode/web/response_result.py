# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2021/11/10 3:57 下午
# Copyright (C) 2021 The lesscode Team

from datetime import datetime

from lesscode.web.status_code import StatusCode


class ResponseResult(dict):
    """
    ResponseResult 类用于统一包装数据返回格式
    """
    def __init__(self, status_code=StatusCode.SUCCESS, data=""):
        super(ResponseResult, self).__init__()
        # 业务请求状态编码
        self["status"] = status_code[0]
        # 返回状态码对应的说明信息
        self["message"] = status_code[1]
        # 返回数据对象 主对象 指定类型
        self["data"] = data
        # 时间戳
        self["timestamp"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
