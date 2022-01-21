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


from sidemash_sdk.Hook import Hook
from sidemash_sdk.StreamSquareSize import StreamSquareSize
from typing import Dict
from typing import Optional
import json


class CreateStreamSquareForm:
    def __init__(self,
                 is_elastic: bool,
                 size: StreamSquareSize,
                 hook: Hook,
                 description: Optional[str] = None,
                 foreign_data: Optional[str] = None,
                 play_domain_name: Optional[str] = None,
                 publish_domain_name: Optional[str] = None):
        self._type = "CreateStreamSquareForm" 
        self.is_elastic = is_elastic
        self.size = size
        self.hook = hook
        self.description = description
        self.foreign_data = foreign_data
        self.play_domain_name = play_domain_name
        self.publish_domain_name = publish_domain_name

    @staticmethod
    def _type(): 
        return "CreateStreamSquareForm"

    @staticmethod
    def from_json(js: str):
        value = json.loads(js)
        return CreateStreamSquareForm.from_dict(value)

    def __to_remote_dict(self):
        tuples = [
            ('isElastic', self.is_elastic),
            ('size', str(self.size)),
            ('hook', self.hook.__to_remote_dict()),
            ('description', self.description),
            ('foreignData', self.foreign_data),
            ('playDomainName', self.play_domain_name),
            ('publishDomainName', self.publish_domain_name)
        ]
        return dict(t for t in tuples if t[1] is not None)

    def to_dict(self):
        return dict([
            ('is_elastic', self.is_elastic),
            ('size', str(self.size)),
            ('hook', self.hook.to_dict()),
            ('description', self.description),
            ('foreign_data', self.foreign_data),
            ('play_domain_name', self.play_domain_name),
            ('publish_domain_name', self.publish_domain_name)
        ])

    @staticmethod
    def __from_remote_dict(d: Dict[str, any]):
        return CreateStreamSquareForm(d["isElastic"],
                                      StreamSquareSize.from_string(d["size"]),
                                      Hook.__from_remote_dict(d["hook"]),
                                      d["description"] if "description" in d else None,
                                      d["foreignData"] if "foreignData" in d else None,
                                      d["playDomainName"] if "playDomainName" in d else None,
                                      d["publishDomainName"] if "publishDomainName" in d else None)

    @staticmethod
    def from_dict(d: Dict[str, any]):
        return CreateStreamSquareForm(d["is_elastic"],
                                      StreamSquareSize.from_string(d["size"]),
                                      Hook.from_dict(d["hook"]),
                                      d["description"] if "description" in d else None,
                                      d["foreign_data"] if "foreign_data" in d else None,
                                      d["play_domain_name"] if "play_domain_name" in d else None,
                                      d["publish_domain_name"] if "publish_domain_name" in d else None)

    def to_json(self):
        return json.dumps(self.to_dict())

    def __to_remote_json(self):
        return json.dumps(self.__to_remote_dict())

    def to_string(self):
        return self.__repr__()

    def __repr__(self):
        return ("CreateStreamSquareForm(is_elastic=" + str(self.is_elastic) + 
                                       ", size=" + repr(self.size) + 
                                       ", hook=" + repr(self.hook) + 
                                       ", description=" + str(self.description) + 
                                       ", foreign_data=" + str(self.foreign_data) + 
                                       ", play_domain_name=" + str(self.play_domain_name) + 
                                       ", publish_domain_name=" + str(self.publish_domain_name) + ")")