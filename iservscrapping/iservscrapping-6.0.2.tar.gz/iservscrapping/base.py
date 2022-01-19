"""
The MIT License (MIT)
Copyright (c) Alwin Lohrie (Niwla23)
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
import logging

import requests
import requests_cache

from iservscrapping.errors import LoginError


class BaseIserv:
    """
    Args:
        url (str): The URL to connect to without trailing slash
        username (str): The Username to login with
        password (str): The Password to login with
        cache (bool): Whether to use cache or not. Defaults to False
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, url, username, password, cache=False):
        self.username = username
        self.password = password
        self.time_to_next_substitution_request = 0
        self.url = url
        self.session = requests.Session()

        if cache:
            requests_cache.install_cache('cache', expire_after=3600)

    def login(self):
        """
        Raises:
            LoginError: The login failed.
        Sends a login request and stores the tokens in the session
        """
        logging.debug("Starting Login")
        headers = {'User-Agent': 'Mozilla/5.0'}
        payload = {'_username': self.username, '_password': self.password}
        response = self.session.post(self.url + '/iserv/app/login', headers=headers, data=payload)
        if "Anmeldung fehlgeschlagen!" in response.text:
            raise LoginError
