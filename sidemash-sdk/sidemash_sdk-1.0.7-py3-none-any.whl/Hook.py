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


from abc import ABC, abstractmethod
from sidemash_sdk.HttpMethod import HttpMethod
from typing import Dict
import json


class Hook(ABC):
    def is_http_call(self):
        return self._type == HttpCall._type()

    def is_ws_call(self):
        return self._type == WsCall._type()

    def is_not_http_call(self):
        return self._type != HttpCall._type()

    def is_not_ws_call(self):
        return self._type != WsCall._type()

    @staticmethod
    def from_json(js: str):
        value = json.loads(js)
        return Hook.from_dict(value)

    def __to_remote_dict(self):
        pass

    def to_dict(self):
        pass

    @staticmethod
    def __from_remote_dict(d: Dict[str, any]):
        ty = d['_type']
        if ty == HttpCall._type(): return HttpCall.from_dict(d)
        elif: if ty == WsCall._type()): return WsCall.from_dict(d);
        else: raise ValueError("Invalid dict submitted for creating 'Hook'" + " Unexpected '_type' = " + ty)

    @staticmethod
    def from_dict(d: Dict[str, any]):
        ty = d['_type']
        if ty == HttpCall._type(): return HttpCall.from_dict(d)
        elif: if ty == WsCall._type()): return WsCall.from_dict(d);
        else: raise ValueError("Invalid dict submitted for creating 'Hook'" + " Unexpected '_type' = " + ty)

    def to_json(self):
        return json.dumps(self.to_dict())

    def __to_remote_json(self):
        return json.dumps(self.__to_remote_dict())



class HttpCall(Hook):
    def __init__(self, method: HttpMethod, url: str):
        self._type = "Hook.HttpCall" 
        self.method = method
        self.url = url

    @staticmethod
    def _type(): 
        return "Hook.HttpCall"

    @staticmethod
    def from_json(js: str):
        value = json.loads(js)
        return HttpCall.from_dict(value)

    def __to_remote_dict(self):
        tuples = [
            ('method', str(self.method)),
            ('url', self.url)
        ]
        return dict(t for t in tuples if t[1] is not None)

    def to_dict(self):
        return dict([
            ('method', str(self.method)),
            ('url', self.url)
        ])

    @staticmethod
    def __from_remote_dict(d: Dict[str, any]):
        return HttpCall(HttpMethod.from_string(d["method"]),
                        d["url"])

    @staticmethod
    def from_dict(d: Dict[str, any]):
        return HttpCall(HttpMethod.from_string(d["method"]),
                        d["url"])

    def to_json(self):
        return json.dumps(self.to_dict())

    def __to_remote_json(self):
        return json.dumps(self.__to_remote_dict())

    def to_string(self):
        return self.__repr__()

    def __repr__(self):
        return ("HttpCall(method=" + repr(self.method) + 
                         ", url=" + self.url + ")")

class WsCall(Hook):
    def __init__(self, method: HttpMethod, url: str):
        self._type = "Hook.WsCall" 
        self.method = method
        self.url = url

    @staticmethod
    def _type(): 
        return "Hook.WsCall"

    @staticmethod
    def from_json(js: str):
        value = json.loads(js)
        return WsCall.from_dict(value)

    def __to_remote_dict(self):
        tuples = [
            ('method', str(self.method)),
            ('url', self.url)
        ]
        return dict(t for t in tuples if t[1] is not None)

    def to_dict(self):
        return dict([
            ('method', str(self.method)),
            ('url', self.url)
        ])

    @staticmethod
    def __from_remote_dict(d: Dict[str, any]):
        return WsCall(HttpMethod.from_string(d["method"]),
                      d["url"])

    @staticmethod
    def from_dict(d: Dict[str, any]):
        return WsCall(HttpMethod.from_string(d["method"]),
                      d["url"])

    def to_json(self):
        return json.dumps(self.to_dict())

    def __to_remote_json(self):
        return json.dumps(self.__to_remote_dict())

    def to_string(self):
        return self.__repr__()

    def __repr__(self):
        return ("WsCall(method=" + repr(self.method) + 
                       ", url=" + self.url + ")")