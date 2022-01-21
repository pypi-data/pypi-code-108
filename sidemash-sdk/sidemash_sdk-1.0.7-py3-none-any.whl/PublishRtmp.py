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


from sidemash_sdk.SecureAndNonSecure import SecureAndNonSecure
from typing import Dict
import json


class PublishRtmp:
    def __init__(self,
                 stream_key_prefix: str,
                 ip: SecureAndNonSecure,
                 domain: SecureAndNonSecure):
        self._type = "PublishRtmp" 
        self.stream_key_prefix = stream_key_prefix
        self.ip = ip
        self.domain = domain

    @staticmethod
    def _type(): 
        return "PublishRtmp"

    @staticmethod
    def from_json(js: str):
        value = json.loads(js)
        return PublishRtmp.from_dict(value)

    def __to_remote_dict(self):
        tuples = [
            ('streamKeyPrefix', self.stream_key_prefix),
            ('ip', self.ip.__to_remote_dict()),
            ('domain', self.domain.__to_remote_dict())
        ]
        return dict(t for t in tuples if t[1] is not None)

    def to_dict(self):
        return dict([
            ('stream_key_prefix', self.stream_key_prefix),
            ('ip', self.ip.to_dict()),
            ('domain', self.domain.to_dict())
        ])

    @staticmethod
    def __from_remote_dict(d: Dict[str, any]):
        return PublishRtmp(d["streamKeyPrefix"],
                           SecureAndNonSecure.__from_remote_dict(d["ip"]),
                           SecureAndNonSecure.__from_remote_dict(d["domain"]))

    @staticmethod
    def from_dict(d: Dict[str, any]):
        return PublishRtmp(d["stream_key_prefix"],
                           SecureAndNonSecure.from_dict(d["ip"]),
                           SecureAndNonSecure.from_dict(d["domain"]))

    def to_json(self):
        return json.dumps(self.to_dict())

    def __to_remote_json(self):
        return json.dumps(self.__to_remote_dict())

    def to_string(self):
        return self.__repr__()

    def __repr__(self):
        return ("PublishRtmp(stream_key_prefix=" + self.stream_key_prefix + 
                            ", ip=" + repr(self.ip) + 
                            ", domain=" + repr(self.domain) + ")")