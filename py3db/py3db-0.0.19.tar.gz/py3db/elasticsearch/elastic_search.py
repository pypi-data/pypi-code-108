# @Time : 2021/4/11 0:31 
# @Author : GanJianWen
# @File : elastic_search.py 
# @Email: 1727949032@qq.com
# @Software: PyCharm
from elasticsearch5 import Elasticsearch
from py3db.log.Log import Log


class ElasticSearch(object):
    def __init__(self, es_address_list=['127.0.0.1:9200']):
        self.es = Elasticsearch(
            es_address_list,
            # 启动前嗅探es集群服务器
            sniff_on_start=True,
            # es集群服务器结点连接异常时是否刷新es节点信息
            sniff_on_connection_fail=True,
            # 每60秒刷新节点信息
            sniffer_timeout=60
        )
        self.log = Log("elastic_search.log")

    def search(self, index, doc_type, body):
        return self.es.search(
            index=index,
            doc_type=doc_type,
            body=body
        )

    def insert(self, index, doc_type, body, doc_id):
        try:
            self.es.index(index=index, doc_type=doc_type, body=body, id=doc_id)
        except Exception as e:
            self.log.call_error()
            self.log.error(e)


if __name__ == '__main__':
    es = ElasticSearch()
