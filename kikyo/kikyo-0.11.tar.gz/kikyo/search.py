from abc import ABCMeta, abstractmethod


class Index(metaclass=ABCMeta):
    """
    索引
    """

    @abstractmethod
    def exists(self, id: str) -> bool:
        """
        指定ID的数据是否存在

        :param id: 数据ID
        """

    @abstractmethod
    def get(self, id: str) -> dict:
        """
        返回指定数据

        :param id: 数据的ID
        """

    @abstractmethod
    def put(self, id: str, data: dict):
        """
        更新指定数据，指定ID不存在时自动创建数据

        :param id: 数据ID
        :param data: 数据内容
        """

    @abstractmethod
    def delete(self, id: str):
        """
        删除指定数据

        :param id: 数据ID
        """


class Search(metaclass=ABCMeta):
    """
    提供全文检索服务
    """

    @abstractmethod
    def index(self, topic: str) -> Index:
        """
        对指定topic返回索引

        :param topic: topic名称
        """
