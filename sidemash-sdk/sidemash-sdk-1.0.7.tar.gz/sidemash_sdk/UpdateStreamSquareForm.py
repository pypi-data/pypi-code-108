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
from typing import Set
import json


class UpdateStreamSquareForm:
    def __init__(self, id: str, remove: Set[str], set: Dict[str, any]):
        self._type = "UpdateStreamSquareForm" 
        self.id     = id
        self.remove = remove
        self.set    = set

    @staticmethod
    def by_id(id):
        return UpdateStreamSquareForm(id, set(), dict())

    def remove_description(self):
        remove = self.remove.union({'description'})
        return UpdateStreamSquareForm(self.id, remove, self.set)

    def remove_foreign_data(self):
        remove = self.remove.union({'foreignData'})
        return UpdateStreamSquareForm(self.id, remove, self.set)

    def set_is_elastic(self, is_elastic):
        s = dict(self.set, **{'isElastic': is_elastic})
        return UpdateStreamSquareForm(self.id, self.remove, s)

    def set_size(self, size):
        s = dict(self.set, **{'size': str(size)})
        return UpdateStreamSquareForm(self.id, self.remove, s)

    def set_hook(self, hook):
        s = dict(self.set, **{'hook': hook.to_dict()})
        return UpdateStreamSquareForm(self.id, self.remove, s)

    def set_description(self, description):
        if description is None: 
            return self
        s = dict(self.set, **{'description': description})
        return UpdateStreamSquareForm(self.id, self.remove, s)

    def set_foreign_data(self, foreign_data):
        if foreign_data is None: 
            return self
        s = dict(self.set, **{'foreignData': foreign_data})
        return UpdateStreamSquareForm(self.id, self.remove, s)

    def __to_remote_dict(self):
        tuples = [
            self.remove,
            ('set', self.set.__to_remote_dict())
        ]
        return dict(t for t in tuples if t[1] is not None)

    def to_dict(self):
        return dict([
            ('id', self.id),
            self.remove,
            ('set', self.set.to_dict())
        ])

    def to_json(self):
        return json.dumps(self.to_dict())

    def __to_remote_json(self):
        return json.dumps(self.__to_remote_dict())

    def to_string(self):
        return self.__repr__()

    def __repr__(self):
        return ("UpdateStreamSquareForm(id=" + self.id + 
                                       ", remove=" + repr(self.remove) + 
                                       ", set=" + repr(self.set) + ")")