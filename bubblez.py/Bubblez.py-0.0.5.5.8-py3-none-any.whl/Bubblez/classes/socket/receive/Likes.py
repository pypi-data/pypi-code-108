
from ...Color import Color
from ...Log import logTime

from .User import User as ReceivedUser

import json

class Likes:
    def __init__(self, id, type, userdata) -> None:
        self._id = id
        self._type = type
        self._user = ReceivedUser()
        self.raw_data = {"user": userdata, "type": type, "id": id}

    def json(self):
        return self.raw_data