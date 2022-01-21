#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Description:       :构建 elastic search 索引
@Date               :2021/02/05 22:53:42
@Author             :mayq
@version            :1.0
'''
from elasticsearch import Elasticsearch
from elasticsearch import helpers

analyzer = {
    "ik_m": {
        "type" : "custom",
        "tokenizer": "ik_max_word",
        "filter": ["lowercase"],
        "char_filter": ["tsconvert"]
    },
    "ik_s": {
        "type" : "custom",
        "tokenizer": "ik_smart",
        "filter": ["lowercase"],
        "char_filter": ["tsconvert"]
    }
}
char_filter = {
    "tsconvert" : {
        "type" : "stconvert",
        "delimiter" : "#",
        "keep_both" : True,
        "convert_type" : "t2s"
        }
    }
properties = {
    "id": {
        "type": "text"
    },
    "title": {
        "type": "text"
    },
    "Category": {
        "type": "keyword"
    },
    "clean_data": {
        "type": "text",
        "similarity": "BM25",
        "analyzer": "ik_s",
        "search_analyzer":"ik_s"
    }
}

class ES:
    def __init__(
        self,
        ip="localhost",
        user_name = "elastic",
        password = "elastic",
        auth = True,
        port = 9200
        ) -> None:
        if auth:
            self._es = Elasticsearch(ip,http_auth=(user_name, password),port=port)
        else:
            self._es = Elasticsearch(ip,port=port) 
                                                       
    def create_index(
        self,
        new_index_name,
        properties:dict,
        analyzer:dict = analyzer,
        char_filter:dict = char_filter):
        index_config = { 
            "settings": {
                "analysis": 
                {
                    "analyzer": analyzer,
                    "char_filter": char_filter
                },
            },
            "mappings": {
                "properties": properties
            }
        }
        res = self._es.indices.create(
            index = new_index_name,
            body = index_config)
        return res

    def data_input(self,data,index_name):
        """
        @description  :使用生成器批量写入数据
        @param        :
        @Returns      :
        """
        action = ({
            "_index": index_name, #索引名称
            # "_type": _type, # 类型 （可选）
            "_source": row
        } for row in data)
        helpers.bulk(self._es, action)
        print("insert {} success".format(len(data)))

    def _query_es(
        self,
        es_index_name,
        template_id,
        params = {
                "field": "sent",
                "query": "查询词",
                "size": 10
            }
            ):
        """
        @description  :使用模板进行查询
        @param        :
        @Returns      :
        """
        dsl = {
            "id": template_id,
            "params": params
        }

        es_result = self._es.search_template(index=es_index_name, body=dsl)
        es_result = es_result["hits"]["hits"]
        return es_result
    def query_by_template(
        self,
        es_index_name,
        template_id,
        params = {
                "field": "sent",
                "query": "查询词",
                "size": 10
            },
        query_result_parse = lambda query_res :query_res):
        
        query_es = self._query_es(es_index_name,template_id,params)
        return query_result_parse(query_es)

    def query_by_keyword(
        self,
        es_index_name,
        query_keyword,
        query_field_name,
        query_result_parse = lambda query_res :query_res):
        dsl = {
                "query": {
                    "match": {
                    query_field_name: query_keyword
                    }
                }
            }
        es_result = self._es.search(index=es_index_name,body=dsl)
        es_result = es_result["hits"]["hits"]
        return query_result_parse(es_result)