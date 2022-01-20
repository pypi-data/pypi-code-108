"""
Search Object Wrapper
"""
import typing

from elasticsearch_dsl import Search, connections
from pydantic import BaseModel
from wisdoms_dapr import exceptions

import elasticsearch


class ESSearchResult(typing.TypedDict):
    page: int
    size: int
    total: int
    data: typing.Optional[typing.List[dict[str, typing.Any]]]


class SearchBase(object):
    """Search Base Class"""

    @property
    def search(self) -> Search:
        """生成search"""
        raise NotImplementedError

    @property
    def result(self):
        raise NotImplementedError('Not implement `result` property method.')


class ESSearch(SearchBase):
    """ElasticSearch Search"""

    def __init__(
        self,
        search: Search,
        *args: typing.Any,
        schema: typing.Optional[typing.Type[BaseModel]] = None,
        page: int = 1,
        size: int = 10,
        sort: typing.Union[str, typing.List[str]] = '',
        **schema_options: typing.Any,
    ):
        """

        Args:
            search: ElasticSearch Search object instance
            schema: 用于格式化输出结果（marshmallow schema class)
            page: 页数
            size: 每页结果大小
            raise_exception: 当`many=False`，结果查询为空时是否触发异常
        """

        self._search = search
        self.schema = schema
        self.page = page if page >= 1 else 1
        self.size = size if size >= 1 else 10
        self.sort = sort
        self.schema_options = schema_options

    @property
    def search(self) -> Search:
        """生成search"""
        search = self._search
        # 返回总数
        search.extra(track_total_hits=True)

        # 添加排序
        if self.sort:
            if isinstance(self.sort, list):
                sort = list(filter(lambda x: x, map(lambda x: x.strip(), self.sort)))
                if sort:
                    search = search.sort(*sort)
            else:
                sort = self.sort.strip()
                search = search.sort(sort)

        return search[(self.page - 1) * self.size : self.page * self.size]

    @property
    def result(self) -> ESSearchResult:
        """返回最终搜索结果列表"""

        result = {'page': self.page, 'size': self.size}

        try:
            res = self.search.execute()
        except elasticsearch.exceptions.RequestError as e:
            print('ESSearch Exception:', e)
            raise exceptions.ParameterException(msg=f'参数错误: {e}')

        # Use schema to format
        data = res.to_dict()['hits']['hits']
        if self.schema:
            result['data'] = [
                self.schema(**{'id': item['_id'], **item['_source']}).dict(**self.schema_options) for item in data
            ]
        else:
            result['data'] = data

        # 获取total信息，下面为了兼容6和7版本
        if hasattr(res.hits.total, 'value'):
            total = res.hits.total.value
        else:
            total = res.hits.total

        result['total'] = total
        return result


class DslSearch(SearchBase):
    """通过原始DSL查询进行搜索"""

    def __init__(self, dsl: dict[str, typing.Any], *args: typing.Any, **kwargs: typing.Any):
        """
        Elasticsearch DSL search interface

        Args:
            data:
                {
                    'header': # 查询条件控制（此处为Elasticsearch搜索控制添加）
                        {
                            'index': 'f5-*',    # Such as: index, ...
                            ...
                        }
                    'body':  # DSL 查询语句
                }

        Returns:
            Elasticsearch 原生查询结果（和使用DSL查询结果一致）
        """
        self.dsl = dsl
        self.header = dsl['header']
        self.body = dsl['body']

    @property
    def search(self) -> Search:
        search = Search(**self.header).from_dict(self.body)
        return search

    @property
    def result(self):
        return self.search.execute()


class MultiDslSearch(SearchBase):
    """
    Elasticsearch Multi DSL Search interface
    """

    def __init__(self, raw_dsl: str, index: typing.Optional[str] = None, **kwargs: typing.Any):
        """通过DSL字符串查询并返回结果

        Args:
            raw_dsl: 原始DSL字符串
            index: 索引同`elasticsearch` msearch()方法`index`

        Returns:
            返回原始响应数据
        """
        self.raw_dsl = raw_dsl
        self.index = index
        self._kwargs = kwargs

    @property
    def search(self) -> str:
        return self.raw_dsl

    @property
    def result(self):
        c = connections.get_connection()
        result = c.msearch(body=self.raw_dsl, index=self.index, **self._kwargs)
        return result
