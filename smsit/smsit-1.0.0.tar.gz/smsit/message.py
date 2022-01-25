import json
from typing import Union, Generator, Iterator

ContactList = Union[list, tuple, Generator, str]


class Message:
    type = "message"

    def __init__(
        self,
        text: str,
        receiver: ContactList,
        sender: str = None,
        meta: dict = None,
    ):
        self.text = text
        self.receiver = (
            (receiver,) if isinstance(receiver, str) else tuple(receiver)
        )
        self.sender = sender
        self.meta = meta

    def to_dict(self):
        return {
            "text": self.text,
            "receiver": self.receiver,
            "sender": self.sender,
        }

    def __repr__(self):
        return json.dumps(self.to_dict())


class SMS(Message):
    type = "sms"


class MMS(Message):
    # TODO
    type = "mms"


class TemplatedMessage(Message):
    type = "templatedMessage"

    def __init__(self, template: str, params: Iterator[str], **kw):
        self.template = template
        self.params = params
        super().__init__(text=None, **kw)

    def to_dict(self):
        r = super().to_dict()
        r["template"] = self.template
        r["params"] = self.params
        return r


class VoiceMessage(Message):
    # TODO
    type = "voiceMessage"
