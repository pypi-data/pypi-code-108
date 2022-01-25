from abc import abstractmethod
from dataclasses import dataclass
from typing import List, Iterable, Callable, Any, Union, Tuple, Dict

from origin.serialize import Serializable


@dataclass
class Message(Serializable):
    """
    Base-class for messages that can be sent on the bus.
    Inherited classes must remember to use the @dataclass decorator.
    """
    pass


TTopic = str
TTopicList = Union[List[TTopic], Tuple[TTopic, ...]]

TMessageHandler = Callable[[Message], None]


class MessageBroker(object):
    """
    Abstract base-class for publishing and consuming messages
    on the message-bus.
    """

    class PublishError(Exception):
        """
        TODO
        """
        pass

    class DispatchError(Exception):
        """
        TODO
        """
        pass

    @abstractmethod
    def __iter__(self) -> Iterable[Message]:
        """
        Returns an iterable of messages received in any
        of the subscribed topics.
        """
        raise NotImplementedError

    @abstractmethod
    def poll(self, timeout: int = 0) -> Dict[str, List[Message]]:
        """
        Polls the broker for at least one message with a timeout.
        Returns messages mapped by topic.

        :param timeout: Timeout in seconds
        """
        raise NotImplementedError

    @abstractmethod
    def poll_list(self, timeout: int = 0) -> List[Message]:
        """
        Polls the broker for at least one message with a timeout.
        Returns a list of messages from any topics subscribed to.

        :param timeout: Timeout in seconds
        """
        raise NotImplementedError

    @abstractmethod
    def subscribe(self, topics: TTopicList):
        """
        Subscribe to a number of topics.

        :param topics: The topics to subscribe to
        """
        raise NotImplementedError

    def listen(self, topics: TTopicList, handler: TMessageHandler):
        """
        Subscribed to the provided topics and invokes the handler
        with each new message.
        """
        self.subscribe(topics)

        for msg in self:
            handler(msg)

    @abstractmethod
    def publish(self, topic: TTopic, msg: Any, block=False, timeout=10):
        """
        Publish a message to a topic on the bus.

        :param topic: The topic to publish to
        :param msg: The message to publish
        :param block: Whether to block until publishing is complete
        :param timeout: Timeout in seconds (if block=True)
        """
        raise NotImplementedError
