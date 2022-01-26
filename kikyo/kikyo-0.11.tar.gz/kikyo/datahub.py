import datetime as dt
from abc import ABCMeta, abstractmethod
from typing import Any


class Producer(metaclass=ABCMeta):
    """
    生产者
    """

    def __enter__(self) -> 'Producer':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @abstractmethod
    def send(self, record: Any, partition_key: str = None):
        """
        发送数据

        :param record: 数据
        :param partition_key: 用于划分数据的key
        """

    @abstractmethod
    def close(self):
        """
        关闭生产者
        """


class Message(metaclass=ABCMeta):
    """
    消息
    """

    @property
    @abstractmethod
    def value(self) -> Any:
        """
        消息内容
        """

    @property
    @abstractmethod
    def publish_time(self) -> dt.datetime:
        """
        消息发布时间
        """


class Consumer(metaclass=ABCMeta):
    """
    消费者
    """

    def __enter__(self) -> 'Consumer':
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @abstractmethod
    def receive(self) -> Message:
        """
        接收数据
        """

    @abstractmethod
    def close(self):
        """
        关闭消费者
        """

    @abstractmethod
    def ack(self, msg: Message):
        """
        确认消息

        :param msg: 消息
        """


class DataHub(metaclass=ABCMeta):
    """
    提供数据总线服务
    """

    @abstractmethod
    def create_producer(self, topic: str) -> Producer:
        """
        创建向指定topic发送数据的生产者

        :param topic: topic名称
        """

    @abstractmethod
    def subscribe(
            self,
            topic: str,
            subscription_name: str = None,
            consumer_name: str = None,
            auto_ack: bool = True,
    ) -> Consumer:
        """
        订阅指定topic

        :param topic: topic名称
        :param subscription_name: 订阅的标识
        :param consumer_name: 消费者名称
        :param auto_ack: 自动确认
        """
