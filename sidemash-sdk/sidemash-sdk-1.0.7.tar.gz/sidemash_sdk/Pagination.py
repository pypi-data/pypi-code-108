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


from sidemash_sdk.UTCDateTime import UTCDateTime
from typing import Dict
from typing import Optional
import json


class Pagination:
    def __init__(self,
                 self_url: str,
                 prev_url: Optional[str],
                 next_url: Optional[str],
                 started_time: UTCDateTime,
                 nb_items_on_this_page: int,
                 page: int,
                 nb_items_per_page: int):
        self._type = "Pagination" 
        self.self_url = self_url
        self.prev_url = prev_url
        self.next_url = next_url
        self.started_time = started_time
        self.nb_items_on_this_page = nb_items_on_this_page
        self.page = page
        self.nb_items_per_page = nb_items_per_page

    @staticmethod
    def _type(): 
        return "Pagination"

    @staticmethod
    def from_json(js: str):
        value = json.loads(js)
        return Pagination.from_dict(value)

    def __to_remote_dict(self):
        tuples = [
            ('selfUrl', self.self_url),
            ('prevUrl', self.prev_url),
            ('nextUrl', self.next_url),
            ('startedTime', self.started_time.__to_remote_dict()),
            ('nbItemsOnThisPage', self.nb_items_on_this_page),
            ('page', self.page),
            ('nbItemsPerPage', self.nb_items_per_page)
        ]
        return dict(t for t in tuples if t[1] is not None)

    def to_dict(self):
        return dict([
            ('self_url', self.self_url),
            ('prev_url', self.prev_url),
            ('next_url', self.next_url),
            ('started_time', self.started_time.to_dict()),
            ('nb_items_on_this_page', self.nb_items_on_this_page),
            ('page', self.page),
            ('nb_items_per_page', self.nb_items_per_page)
        ])

    @staticmethod
    def __from_remote_dict(d: Dict[str, any]):
        return Pagination(d["selfUrl"],
                          d["prevUrl"] if "prevUrl" in d else None,
                          d["nextUrl"] if "nextUrl" in d else None,
                          UTCDateTime.__from_remote_dict(d["startedTime"]),
                          d["nbItemsOnThisPage"],
                          d["page"],
                          d["nbItemsPerPage"])

    @staticmethod
    def from_dict(d: Dict[str, any]):
        return Pagination(d["self_url"],
                          d["prev_url"] if "prev_url" in d else None,
                          d["next_url"] if "next_url" in d else None,
                          UTCDateTime.from_dict(d["started_time"]),
                          d["nb_items_on_this_page"],
                          d["page"],
                          d["nb_items_per_page"])

    def to_json(self):
        return json.dumps(self.to_dict())

    def __to_remote_json(self):
        return json.dumps(self.__to_remote_dict())

    def to_string(self):
        return self.__repr__()

    def __repr__(self):
        return ("Pagination(self_url=" + self.self_url + 
                           ", prev_url=" + str(self.prev_url) + 
                           ", next_url=" + str(self.next_url) + 
                           ", started_time=" + repr(self.started_time) + 
                           ", nb_items_on_this_page=" + str(self.nb_items_on_this_page) + 
                           ", page=" + str(self.page) + 
                           ", nb_items_per_page=" + str(self.nb_items_per_page) + ")")