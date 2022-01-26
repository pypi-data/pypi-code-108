# coding=utf-8

"""
@Author: LiangChao
@Email: kevinleong1011@hotmail.com
@Created: 2022/1/10
@Desc: 
"""
import re


class Dict(dict):
    def __getattr__(self, item):
        return self.get(item)

    def to_query_str(self):
        """
        将字典转换为查询字符串
        :return:
        """
        return '&'.join([k + '=' + str(v) for k, v in self.items()])

    def from_query_str(self, query_str):
        """
        从查询字符串转换并更新键值
        :param query_str:
        :return:
        """
        query_str = query_str + '&'
        p = re.compile(r'[^=&]+=[^=]+(?=&)')
        _list = p.findall(query_str)
        for item in _list:
            _arr = item.split('=', maxsplit=1)
            self[_arr[0]] = _arr[1]
        return self
