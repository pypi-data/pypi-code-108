from typing import Dict, Type

from .broker import Message, TMessageHandler


class MessageDispatcher(Dict[Type[Message], TMessageHandler]):
    """
    A message handler that dispatches incoming messages to the appropriate
    handler. Each message type can have a single handler associated.
    """
    def __call__(self, msg: Message):
        message_type = type(msg)
        if message_type in self:
            print('DISPATCH: %s' % msg)
            handler = self[message_type]
            handler(msg)
        else:
            print('IGNORING: %s' % message_type)
