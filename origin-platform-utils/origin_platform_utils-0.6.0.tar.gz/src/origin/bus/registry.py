from inspect import isclass
from typing import Dict, Union, Type, Optional

from .broker import Message


TDictItem = Union[str, Message, Type[Message]]


class MessageRegistry(Dict[str, Type[Message]]):
    """
    A registry of all messages that the bus knows of.

    Works a a dict where:
        Key = Message type name (str)
        Value = Message class (Serializable)

    TODO Enforce unique names
    """

    @classmethod
    def from_message_types(cls, *types: Type[Message]) -> 'MessageRegistry':
        """
        TODO

        :param types:
        :return:
        """
        return cls({c.__name__: c for c in types})

    def add(self, *message_types: Type[Message]):
        """
        TODO

        :param message_types:
        :return:
        """
        self.update({c.__name__: c for c in message_types})

    def __contains__(self, item: TDictItem) -> bool:
        """
        Check whether an item is known by the registry.

        Item can be either of the following:
            - A string (name of the message type)
            - A class type (the message type itself)
            - An instance of a class (an instance of a message type)
        """
        if isinstance(item, str):
            return item in self.keys()
        elif isclass(item):
            return item in self.values()
        elif isinstance(item, Message):
            return item.__class__ in self.values()
        else:
            return False

    def get(self, item: TDictItem) -> Optional[Message]:
        """
        TODO
        """
        if isinstance(item, str):
            return super(MessageRegistry, self).get(item)
        elif isclass(item):
            return super(MessageRegistry, self).get(item.__name__)
        elif isinstance(item, Message):
            return super(MessageRegistry, self).get(item.__class__.__name__)
        else:
            # TODO:  return something else?
            return None
