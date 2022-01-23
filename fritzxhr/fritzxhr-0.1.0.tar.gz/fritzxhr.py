#!/usr/bin/env python3
#
# Copyright 2020 Andreas Oberritter
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Specification:
# https://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/Session-ID_english_13Nov18.pdf
#

from hashlib import md5
from time import sleep

from defusedxml import ElementTree
from requests import session
from requests.exceptions import RequestException
from requests.models import Response


class FritzXHR:
    def __init__(self, base_uri="http://fritz.box", username="", password="", lang="en", verify=None):
        self._base_uri = base_uri
        self._username = username
        self._password = password
        self._lang = lang
        self._verify = verify

        self._session = session()
        self._block_time = 0
        self._rights = {}
        self._sid = "0000000000000000"

    def _script_uri(self, script):
        return f"{self._base_uri}/{script}.lua"

    def _get(self, script, headers={}, params={}) -> Response:
        uri = self._script_uri(script)
        try:
            r = self._session.get(uri, params=params, headers=headers, verify=self._verify)
        except RequestException as e:
            print(e)
        else:
            return r

    def _post(self, script: str, headers: dict, data: dict) -> Response:
        uri = self._script_uri(script)
        try:
            r = self._session.post(uri, data=data, headers=headers, verify=self._verify)
        except RequestException as e:
            print(e)
        else:
            return r

    def _post_xhr(self, script: str, data: dict) -> Response:
        headers = {"Accept": "*/*", "Content-Type": "application/x-www-form-urlencoded"}
        _data = {
            "xhr": 1,
            "sid": self._sid,
            "lang": self._lang,
            "no_sidrenew": "",
        }
        _data.update(data)

        return self._post(script, headers, _data)

    def _parse_rights(self, root: ElementTree) -> None:
        self._rights = {}
        rights = root.find("./Rights")
        if rights:
            name_list = rights.findall("./Name")
            access_list = rights.findall("./Access")
            for name, access in zip(name_list, access_list):
                self._rights[name.text] = int(access.text)

    def _parse_login_response(self, root: ElementTree) -> bool:
        self._sid = root.find("./SID").text
        self._block_time = int(root.find("./BlockTime").text)
        self._parse_rights(root)
        return self._sid != "0000000000000000"

    def login(self) -> bool:
        r = self._get("login_sid")
        if not (r and r.ok):
            return False

        root = ElementTree.fromstring(r.content)
        if self._parse_login_response(root):
            return True

        sleep(self._block_time)

        challenge = root.find("./Challenge").text
        data = challenge + "-" + self._password
        m = md5(data.encode("utf-16-le"))
        response = challenge + "-" + m.hexdigest()

        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        params = {
            "username": self._username,
            "response": response,
        }
        r = self._get("login_sid", headers=headers, params=params)
        if not (r and r.ok):
            return False

        root = ElementTree.fromstring(r.content)
        return self._parse_login_response(root)

    def logout(self) -> bool:
        data = {"logout": 1}
        r = self._post_xhr("login_sid", data)
        return r and r.ok

    def set_data(self, data: dict) -> bool:
        r = self._post_xhr("data", data)
        return r and r.ok

    def has_access(self, name, level=2):
        return (self._rights.get(name) or 0) >= level
