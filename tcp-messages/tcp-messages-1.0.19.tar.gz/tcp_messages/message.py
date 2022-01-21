from .util import check_type
import json
from json_cpp import JsonObject, JsonList
from uuid import uuid1

class Message(JsonObject):

    def __init__(self, header="", body=""):
        JsonObject.__init__(self)
        self.header = header
        self.body = str(body)
        self.id = str(uuid1())
        self._source = None

    def get_body(self, body_type: type = None):
        if body_type:
            if body_type is JsonObject or body_type is JsonList:
                return JsonObject.load(self.body)
            elif issubclass(body_type, JsonObject) or issubclass(body_type, JsonList):
                return body_type.parse(self.body)
            elif body_type is str:
                return self.body
            elif body_type is bool:
                return self.body == "success" or self.body == "true" or self.body == "1"
            else:
                return body_type(json.loads(self.body))
        else:
            return self.body

    def set_body(self, v):
        self.body = str(v)

    def reply(self, message):
        check_type(message, Message, "wrong type for message")
        if self._source:
            self._source.send(message)
            return True
        else:
            return False
