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
from sidemash_sdk.InstanceStatus import InstanceStatus
from sidemash_sdk.Publish import Publish
from sidemash_sdk.StreamSquareSize import StreamSquareSize
from typing import Dict
from typing import Optional
import json


class StreamSquare:
    def __init__(self,
                 id: str,
                 url: str,
                 status: InstanceStatus,
                 is_elastic: bool,
                 size: StreamSquareSize,
                 play_domain_name: Optional[str],
                 publish_domain_name: Optional[str],
                 publish: Publish,
                 hook: Hook,
                 description: Optional[str],
                 foreign_data: Optional[str]):
        self._type = "StreamSquare" 
        self.id = id
        self.url = url
        self.status = status
        self.is_elastic = is_elastic
        self.size = size
        self.play_domain_name = play_domain_name
        self.publish_domain_name = publish_domain_name
        self.publish = publish
        self.hook = hook
        self.description = description
        self.foreign_data = foreign_data

    @staticmethod
    def _type(): 
        return "StreamSquare"

    @staticmethod
    def from_json(js: str):
        value = json.loads(js)
        return StreamSquare.from_dict(value)

    def __to_remote_dict(self):
        tuples = [
            ('id', self.id),
            ('url', self.url),
            ('status', str(self.status)),
            ('isElastic', self.is_elastic),
            ('size', str(self.size)),
            ('playDomainName', self.play_domain_name),
            ('publishDomainName', self.publish_domain_name),
            ('publish', self.publish.__to_remote_dict()),
            ('hook', self.hook.__to_remote_dict()),
            ('description', self.description),
            ('foreignData', self.foreign_data)
        ]
        return dict(t for t in tuples if t[1] is not None)

    def to_dict(self):
        return dict([
            ('id', self.id),
            ('url', self.url),
            ('status', str(self.status)),
            ('is_elastic', self.is_elastic),
            ('size', str(self.size)),
            ('play_domain_name', self.play_domain_name),
            ('publish_domain_name', self.publish_domain_name),
            ('publish', self.publish.to_dict()),
            ('hook', self.hook.to_dict()),
            ('description', self.description),
            ('foreign_data', self.foreign_data)
        ])

    @staticmethod
    def __from_remote_dict(d: Dict[str, any]):
        return StreamSquare(d["id"],
                            d["url"],
                            InstanceStatus.from_string(d["status"]),
                            d["isElastic"],
                            StreamSquareSize.from_string(d["size"]),
                            d["playDomainName"] if "playDomainName" in d else None,
                            d["publishDomainName"] if "publishDomainName" in d else None,
                            Publish.__from_remote_dict(d["publish"]),
                            Hook.__from_remote_dict(d["hook"]),
                            d["description"] if "description" in d else None,
                            d["foreignData"] if "foreignData" in d else None)

    @staticmethod
    def from_dict(d: Dict[str, any]):
        return StreamSquare(d["id"],
                            d["url"],
                            InstanceStatus.from_string(d["status"]),
                            d["is_elastic"],
                            StreamSquareSize.from_string(d["size"]),
                            d["play_domain_name"] if "play_domain_name" in d else None,
                            d["publish_domain_name"] if "publish_domain_name" in d else None,
                            Publish.from_dict(d["publish"]),
                            Hook.from_dict(d["hook"]),
                            d["description"] if "description" in d else None,
                            d["foreign_data"] if "foreign_data" in d else None)

    def to_json(self):
        return json.dumps(self.to_dict())

    def __to_remote_json(self):
        return json.dumps(self.__to_remote_dict())

    def to_string(self):
        return self.__repr__()

    def __repr__(self):
        return ("StreamSquare(id=" + self.id + 
                             ", url=" + self.url + 
                             ", status=" + repr(self.status) + 
                             ", is_elastic=" + str(self.is_elastic) + 
                             ", size=" + repr(self.size) + 
                             ", play_domain_name=" + str(self.play_domain_name) + 
                             ", publish_domain_name=" + str(self.publish_domain_name) + 
                             ", publish=" + repr(self.publish) + 
                             ", hook=" + repr(self.hook) + 
                             ", description=" + str(self.description) + 
                             ", foreign_data=" + str(self.foreign_data) + ")")