from json_cpp import JsonList
from .message import Message
from .message_event import MessageEvent


class MessageList(JsonList):
    def __init__(self, iterable=None):
        JsonList.__init__(self, iterable, list_type=Message)
        self.pending_responses = dict()

    def queue(self, message: Message):
        if message.id in self.pending_responses:
            self.pending_responses.pop(message.id).trigger(message)
        else:
            self.append(message)

    def add_message_event(self, request_id: str, event: MessageEvent):
        if request_id in self.pending_responses:
            return False
        self.pending_responses[request_id] = event
        return True

    def dequeue(self) -> Message:
        if len(self):
            message = self[0]
            del self[0]
            return message
        return None

    def contains(self, header: str) -> bool:
        for message in self:
            if message.header == header:
                return True
        return False

    def get_message(self, header: str) -> Message:
        for i in range(len(self)):
            if self[i].header == header:
                message = self[i]
                del self[i]
                return message
        return None

    def get_last_message(self, header: str) -> Message:
        message = None
        for i in range(len(self)):
            if self[i].header == header:
                message = self[i]
                del self[i]
        return message

