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


from sidemash_sdk.Auth import Auth
from sidemash_sdk.StreamSquareService import StreamSquareService


class Client:
    def __init__(self, auth: Auth):
        self._type = "Client" 
        self.auth = auth
        self._stream_square = StreamSquareService(auth)

    def stream_square(self):
        return self._stream_square

    def to_string(self):
        return self.__repr__()

    def __repr__(self):
        return "Client(auth=" + repr(self.auth) + ")"