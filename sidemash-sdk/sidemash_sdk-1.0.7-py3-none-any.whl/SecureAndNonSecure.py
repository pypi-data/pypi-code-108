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


class SecureAndNonSecure:
    def __init__(self, secure: str, non_secure_on80: str, non_secure: str):
        self._type = "SecureAndNonSecure" 
        self.secure = secure
        self.non_secure_on80 = non_secure_on80
        self.non_secure = non_secure

    @staticmethod
    def _type(): 
        return "SecureAndNonSecure"

    @staticmethod
    def from_json(js: str):
        value = json.loads(js)
        return SecureAndNonSecure.from_dict(value)

    def __to_remote_dict(self):
        tuples = [
            ('secure', self.secure),
            ('nonSecureOn80', self.non_secure_on80),
            ('nonSecure', self.non_secure)
        ]
        return dict(t for t in tuples if t[1] is not None)

    def to_dict(self):
        return dict([
            ('secure', self.secure),
            ('non_secure_on80', self.non_secure_on80),
            ('non_secure', self.non_secure)
        ])

    @staticmethod
    def __from_remote_dict(d: Dict[str, any]):
        return SecureAndNonSecure(d["secure"],
                                  d["nonSecureOn80"],
                                  d["nonSecure"])

    @staticmethod
    def from_dict(d: Dict[str, any]):
        return SecureAndNonSecure(d["secure"],
                                  d["non_secure_on80"],
                                  d["non_secure"])

    def to_json(self):
        return json.dumps(self.to_dict())

    def __to_remote_json(self):
        return json.dumps(self.__to_remote_dict())

    def to_string(self):
        return self.__repr__()

    def __repr__(self):
        return ("SecureAndNonSecure(secure=" + self.secure + 
                                   ", non_secure_on80=" + self.non_secure_on80 + 
                                   ", non_secure=" + self.non_secure + ")")