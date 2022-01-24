# @author: chenfanghang

from elasticsearch5 import Elasticsearch, Transport
from loguru import logger


class ESHandler(Elasticsearch):
    def __init__(self, hosts=None, transport_class=Transport, **kwargs):
        """
        :arg hosts: list of nodes we should connect to. Node should be a
            dictionary ({"host": "localhost", "port": 9200}), the entire dictionary
            will be passed to the :class:`~elasticsearch.Connection` class as
            kwargs, or a string in the format of ``host[:port]`` which will be
            translated to a dictionary automatically.  If no value is given the
            :class:`~elasticsearch.Urllib3HttpConnection` class defaults will be used.

        :arg transport_class: :class:`~elasticsearch.Transport` subclass to use.

        :arg kwargs: any additional arguments will be passed on to the
            :class:`~elasticsearch.Transport` class and, subsequently, to the
            :class:`~elasticsearch.Connection` instances.
        """
        if "index" in kwargs and kwargs["index"] is not None:
            self.index_name = kwargs["index"]
        else:
            self.index_name = "cms_season_test"
        super().__init__(hosts, transport_class, **kwargs)

    def term_search(self, condition):
        """
        精确查询
        """
        body = {
            "query": {
                "term": condition
            }
        }
        result = self.search(index=self.index_name, body=body)
        return result

    def term_searchHits(self, condition):
        """
        精准匹配对于文本类  是keyword
        "term": {
             "name.keyword": "是否"
         }
        """
        body = {
            "query": {
                "term": condition
            }
        }
        result = self.search(index=self.index_name, body=body)
        logger.debug(result)
        if len(result["hits"]["hits"]) > 0:
            return self.search(index=self.index_name, body=body)["hits"]["hits"][0]
        else:
            return None

    def match_search(self, condition):
        """
        匹配查询
        """
        body = {
            "query": {
                "match": condition
            }
        }
        result = self.search(index=self.index_name, body=body)
        logger.debug(result)
        return result

    def match_searchHits(self, condition):
        """
        匹配查询
        """
        body = {
            "query": {
                "match": condition
            }
        }
        result = self.search(index=self.index_name, body=body)
        logger.debug(result)
        if result["hits"]["hits"]:
            return self.search(index=self.index_name, body=body)["hits"]["hits"]
        else:
            return self.search(index=self.index_name, body=body)["hits"]["hits"][0]

    def searchById(self, id):
        """
        查询指定ID数据
        """
        body = {
            "query": {
                "ids": {
                    "type": "_doc",
                    "values": [
                        id
                    ]
                }
            }
        }
        return self.search(index=self.index_name, body=body)

    def searchHitsById(self, id):
        """
        查询指定ID hit数据
        """
        body = {
            "query": {
                "ids": {
                    "type": "_doc",
                    "values": [
                        id
                    ]
                }
            }
        }
        if not self.search(index=self.index_name, body=body)["hits"]["hits"]:
            return self.search(index=self.index_name, body=body)["hits"]["hits"]
        else:
            return self.search(index=self.index_name, body=body)["hits"]["hits"][0]

    def term_delete(self, condition):
        """
        精确删除
        """
        body = {
            "query": {
                "term": condition
            }
        }
        result = self.delete_by_query(index=self.index_name, body=body)
        logger.debug(result)
        return result

    def match_delete(self, condition):
        """
        匹配删除
        """
        body = {
            "query": {
                "match": condition
            }
        }
        result = self.delete_by_query(index=self.index_name, body=body)
        logger.debug(result)
        if result["deleted"] == 0:
            logger.warning("删除失败")
        return result

    def deleteById(self, id):
        """
        删除指定ID数据
        """
        body = {
            "query": {
                "ids": {
                    "type": "_doc",
                    "values": [
                        id
                    ]
                }
            }
        }
        result = self.delete_by_query(index=self.index_name, body=body)
        logger.debug(result)
        return result

    def term_update(self, condition, field, value):
        """
        精确更新
        """
        body = {
            "query": {
                "term": condition
            }
        }
        data = self.term_search(body)
        if data["hits"]["hits"]:
            id = data["hits"]["hits"][0]["_id"]
            source = data["hits"]["hits"][0]["_source"]
            expr = f"""content{field} =value"""
            exec(expr, {'content': source, "value": value})
            result = self.update(index=self.index_name, doc_type='_doc', id=id, body={"doc": source})
            logger.debug(result)
            if result["_shards"]["successful"] == 0:
                logger.warning("更新失败")
            return result
        else:
            logger.warning(f"根据{body}查询的数据为空，更新失败")
            return None

    def updateById(self, id, field, value):
        """
        通过指定id更新
        """
        data = self.searchById(id)
        if data["hits"]["hits"]:
            id = data["hits"]["hits"][0]["_id"]
            source = data["hits"]["hits"][0]["_source"]
            expr = f"""content{field} =value"""
            exec(expr, {'content': source, "value": value})
            result = self.update(index=self.index_name, doc_type='_doc', id=id, body={"doc": source})
            logger.debug(result)
            if result["_shards"]["successful"] == 0:
                logger.warning("更新失败")
            return result
        else:
            logger.warning(f"id为{id}的数据为空，更新失败")
            return None
