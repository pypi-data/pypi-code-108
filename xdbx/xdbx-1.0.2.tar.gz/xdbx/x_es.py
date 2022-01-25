# #!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time : 2022/1/24 17:14
# @Author : BruceLong
# @FileName: x_es.py
# @Email   : 18656170559@163.com
# @Software: PyCharm
# @Blog ：http://www.cnblogs.com/yunlongaimeng/
import hashlib
import itertools
import json
import math

import pandas as pd
from elasticsearch import Elasticsearch

from .config import ES_HOST_PORT_LIST
from .x_single import SingletonType


class XES(metaclass=SingletonType):
    def __init__(self, host_port_list=ES_HOST_PORT_LIST):
        self.host_port_list = host_port_list.split(';') if ES_HOST_PORT_LIST else []
        self.index = None
        self.batch_size = 50000
        self.max_request_timeout = 60
        self.batch_id = ''
        self.aggs_result_sign = 0
        self.aggs_result = []
        self.total_count = 0
        self.total_count_sign = 0
        self.agg_name = ''
        pass

    def connect(self):
        es = Elasticsearch(self.host_port_list)
        return es

    # def query(self, index: str, query_json: str, to_excel: bool = False):
    def query(self, query_json: str, to_excel: bool = False):
        es = self.connect()
        self.batch_id = hashlib.md5((str(query_json)).encode('utf8')).hexdigest()
        query_body = json.loads(query_json)
        size = query_body.get('size')
        hits_result = itertools.chain()
        if size >= self.batch_size:
            times = math.ceil(size / self.batch_size)
            for t in range(1, times + 1):
                query_body['size'] = self.batch_size * t
                result_temp = self.__get_data(es, query_body=query_body)
                hits_result = itertools.chain(hits_result, result_temp)
        else:
            hits_result = self.__get_data(es, query_body=query_body)
        return_hits_result, temp_hits_result = itertools.tee(hits_result, 2)

        if to_excel:
            self.__init_excel()
            df = pd.DataFrame(list(temp_hits_result))
            df.fillna('', inplace=True)
            df.to_excel(self.writer, encoding='utf_8_sig', sheet_name='hits_result')
            if self.aggs_result_sign:
                df = pd.DataFrame(list(self.aggs_result))
                df.fillna('', inplace=True)
                df.to_excel(self.writer, encoding='utf_8_sig', sheet_name=self.agg_name + 'aggs_result')
            self.writer.save()

        return return_hits_result
        pass

    def __get_data(self, es, query_body):
        contents = es.search(index=self.index, body=query_body, request_timeout=self.max_request_timeout)
        hits_result = (i['_source'] for i in contents.get('hits').get('hits') if i)
        if not self.total_count_sign:
            self.total_count = contents.get('hits').get('total')
        aggs_data = contents.get('aggregations')
        if aggs_data and not self.aggs_result_sign:
            self.agg_name = '_'.join(list(aggs_data.keys()))
            self.aggs_result = (data for i in aggs_data.keys() for data in aggs_data[i]['buckets'])
            self.aggs_result_sign = 1
        return hits_result

    def __init_excel(self):
        self.file_name = f'es_result_{self.batch_id}.xlsx'
        self.writer = pd.ExcelWriter(self.file_name, engine='xlsxwriter')


x_es = XES()
