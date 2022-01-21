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
from typing import Optional
import json


class ListForm:
    def __init__(self,
                 where: Optional[str] = None,
                 limit: Optional[int] = None,
                 order_by: Optional[str] = None):
        self._type = "ListForm" 
        self.where = where
        self.limit = limit
        self.order_by = order_by

    @staticmethod
    def _type(): 
        return "ListForm"

    @staticmethod
    def from_json(js: str):
        value = json.loads(js)
        return ListForm.from_dict(value)

    def __to_remote_dict(self):
        tuples = [
            ('where', self.where),
            ('limit', self.limit),
            ('orderBy', self.order_by)
        ]
        return dict(t for t in tuples if t[1] is not None)

    def to_dict(self):
        return dict([
            ('where', self.where),
            ('limit', self.limit),
            ('order_by', self.order_by)
        ])

    @staticmethod
    def __from_remote_dict(d: Dict[str, any]):
        return ListForm(d["where"] if "where" in d else None,
                        d["limit"] if "limit" in d else None,
                        d["orderBy"] if "orderBy" in d else None)

    @staticmethod
    def from_dict(d: Dict[str, any]):
        return ListForm(d["where"] if "where" in d else None,
                        d["limit"] if "limit" in d else None,
                        d["order_by"] if "order_by" in d else None)

    def to_json(self):
        return json.dumps(self.to_dict())

    def __to_remote_json(self):
        return json.dumps(self.__to_remote_dict())

    @staticmethod
    def empty():
        return ListForm(None, None, None)

    def to_query_string(self) -> str:
        if self.where is None and self.limit is None and self.order_by is None :
            return "" 
        else:
            return "?" + "&".join(t[0] + "=" + t[1] for t in [self.__to_remote_dict()] if t[1] is not None)

    def to_string(self):
        return self.__repr__()

    def __repr__(self):
        return ("ListForm(where=" + str(self.where) + 
                         ", limit=" + str(self.limit) + 
                         ", order_by=" + str(self.order_by) + ")")