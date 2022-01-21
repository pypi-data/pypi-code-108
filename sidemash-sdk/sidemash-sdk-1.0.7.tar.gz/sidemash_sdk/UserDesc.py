#   Copyright © 2020 Sidemash Cloud Services
#
#   Licensed under the Apache  License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless  required  by  applicable  law  or  agreed to in writing,
#   software  distributed  under  the  License  is distributed on an
#   "AS IS"  BASIS, WITHOUT  WARRANTIES  OR CONDITIONS OF  ANY KIND,
#   either  express  or  implied.  See the License for the  specific
#   language governing permissions and limitations under the License.


from typing import Dict
import json


class UserDesc:
    def __init__(self, todo: int):
        self._type = "UserDesc" 
        self.todo = todo

    @staticmethod
    def _type(): 
        return "UserDesc"

    @staticmethod
    def from_json(js: str):
        value = json.loads(js)
        return UserDesc.from_dict(value)

    def __to_remote_dict(self):
        tuples = [('todo', self.todo)]
        return dict(t for t in tuples if t[1] is not None)

    def to_dict(self):
        return dict([('todo', self.todo)])

    @staticmethod
    def __from_remote_dict(d: Dict[str, any]):
        return UserDesc(d["todo"])

    @staticmethod
    def from_dict(d: Dict[str, any]):
        return UserDesc(d["todo"])

    def to_json(self):
        return json.dumps(self.to_dict())

    def __to_remote_json(self):
        return json.dumps(self.__to_remote_dict())

    def to_string(self):
        return self.__repr__()

    def __repr__(self):
        return "UserDesc(todo=" + str(self.todo) + ")"