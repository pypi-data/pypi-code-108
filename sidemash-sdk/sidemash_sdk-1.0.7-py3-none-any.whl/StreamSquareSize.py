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


class StreamSquareSize:
    def __init__(self, value: str):
        self._type = "StreamSquareSize" 
        self.value = value

    @staticmethod
    def S():
        return StreamSquareSize("S")

    @staticmethod
    def M():
        return StreamSquareSize("M")

    @staticmethod
    def L():
        return StreamSquareSize("L")

    @staticmethod
    def XL():
        return StreamSquareSize("XL")

    @staticmethod
    def XXL():
        return StreamSquareSize("XXL")

    @staticmethod
    def all_possibles_values():
        return {"S",
                "M",
                "L",
                "XL",
                "XXL"}

    @staticmethod
    def from_string(value):
        if value == "S": return StreamSquareSize.S()
        elif value == "M": return StreamSquareSize.M()
        elif value == "L": return StreamSquareSize.L()
        elif value == "XL": return StreamSquareSize.XL()
        elif value == "XXL": return StreamSquareSize.XXL()
        else: return None

    @staticmethod
    def is_valid(value):
        return value in StreamSquareSize.all_possibles_values()

    def is_not_s(self):
        return self.value != "S"

    def is_not_m(self):
        return self.value != "M"

    def is_not_l(self):
        return self.value != "L"

    def is_not_xl(self):
        return self.value != "XL"

    def is_not_xxl(self):
        return self.value != "XXL"

    def is_s(self):
        return self.value == "S"

    def is_m(self):
        return self.value == "M"

    def is_l(self):
        return self.value == "L"

    def is_xl(self):
        return self.value == "XL"

    def is_xxl(self):
        return self.value == "XXL"

    def to_json(self):
        return json.dumps(self.value)

    def __to_remote_json(self):
        return json.dumps(self.value)

    def to_string(self):
        return self.__repr__()

    def __repr__(self):
        return "StreamSquareSize(value=" + self.value + ")"

    def __str__(self):
        return self.value