# -*- coding: utf-8 -*-
"""
:Author: ChenXiaolei
:Date: 2020-04-16 14:38:22
:LastEditTime: 2021-01-18 15:12:16
:LastEditors: ChenXiaolei
:Description: json 帮助类
"""
import json
import datetime
import decimal


class JsonEncoder(json.JSONEncoder):
    """
    继承json.JSONEncoder

    使用方法:json.dumps(json_obj, ensure_ascii=False, cls=JsonEncoder)
    """
    def default(self, obj):  # pylint: disable=E0202
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        elif isinstance(obj, bytes):
            return obj.decode()
        elif isinstance(obj, decimal.Decimal):
            return str(decimal.Decimal(obj).quantize(decimal.Decimal('0.00')))
        else:
            return json.JSONEncoder.default(self, obj)


class JsonHelper(object):
    @classmethod
    def json_dumps(self, json_data,ensure_ascii=False,separators = (',', ':')):
        """
        :description: json转为str
        :param json_data: 需要转换的json/dict数据
        :param ensure_ascii: 是否需要保持或转移为ascii格式(默认不保持)
        :param separators: json是否需要保留格式空格(默认不保留空格)
        :return 转换后的json字符串
        :last_editors: ChenXiaolei
        """
        return json.dumps(json_data,
                          ensure_ascii=ensure_ascii,
                          cls=JsonEncoder,
                          separators=separators)
