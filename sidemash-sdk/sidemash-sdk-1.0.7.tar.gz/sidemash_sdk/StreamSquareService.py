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
from sidemash_sdk.CreateStreamSquareForm import CreateStreamSquareForm
from sidemash_sdk.Http import Http
from sidemash_sdk.ListForm import ListForm
from sidemash_sdk.RestCollection import RestCollection
from sidemash_sdk.Sdk import Sdk
from sidemash_sdk.StreamSquare import StreamSquare
from sidemash_sdk.UpdateStreamSquareForm import UpdateStreamSquareForm


class StreamSquareService:
    def __init__(self, auth: Auth):
        self._type = "StreamSquareService" 
        self.auth = auth

    def create(self, form: CreateStreamSquareForm):
        return Http.post("/" + Sdk.version() + "/stream-squares", form.to_json(), "", {}, StreamSquare.from_json, self.auth)

    def get(self, id: str):
        return Http.get("/" + Sdk.version() + "/stream-squares/" + id, "", {}, StreamSquare.from_json, self.auth)

    def list_all(self, form: ListForm = None):
        qs = ListForm.empty().to_query_string() if form is None else form.to_query_string()
        return Http.list_all("/" + Sdk.version() + "/stream-squares", qs, {}, lambda json: RestCollection.from_json(json, StreamSquare.from_json), self.auth)

    def update(self, form: UpdateStreamSquareForm):
        return Http.patch("/" + Sdk.version() + "/stream-squares/" + form.id, form.to_json(), "", {}, StreamSquare.from_json, self.auth)

    def delete(self, id: str):
        Http.delete("/" + Sdk.version() + "/stream-squares/" + id, None, "", {}, None, self.auth)

    def to_string(self):
        return self.__repr__()

    def __repr__(self):
        return "StreamSquareService(auth=" + repr(self.auth) + ")"