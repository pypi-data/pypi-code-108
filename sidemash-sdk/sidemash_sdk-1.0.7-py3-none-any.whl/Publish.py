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


from sidemash_sdk.PublishRtmp import PublishRtmp
from typing import Dict
import json


class Publish:
    def __init__(self, rtmp: PublishRtmp):
        self._type = "Publish" 
        self.rtmp = rtmp

    @staticmethod
    def _type(): 
        return "Publish"

    @staticmethod
    def from_json(js: str):
        value = json.loads(js)
        return Publish.from_dict(value)

    def __to_remote_dict(self):
        tuples = [('rtmp', self.rtmp.__to_remote_dict())]
        return dict(t for t in tuples if t[1] is not None)

    def to_dict(self):
        return dict([('rtmp', self.rtmp.to_dict())])

    @staticmethod
    def __from_remote_dict(d: Dict[str, any]):
        return Publish(PublishRtmp.__from_remote_dict(d["rtmp"]))

    @staticmethod
    def from_dict(d: Dict[str, any]):
        return Publish(PublishRtmp.from_dict(d["rtmp"]))

    def to_json(self):
        return json.dumps(self.to_dict())

    def __to_remote_json(self):
        return json.dumps(self.__to_remote_dict())

    def to_string(self):
        return self.__repr__()

    def __repr__(self):
        return "Publish(rtmp=" + repr(self.rtmp) + ")"