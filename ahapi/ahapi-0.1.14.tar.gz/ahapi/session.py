#!/usr/bin/env python3
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

# Session factory for ahapi

import aiohttp.web
import typing
import http.cookies
import time
import uuid
import ahapi.server

MIN_PRUNE_SIZE = 1000  # We won't start pruning sessions until > 1,000 exist in memory at any given time.


class CookieSession:
    def __init__(self, factory: "CookieFactory", cookie: str):
        self.cookie: str = cookie
        self.created: float = time.time()
        self.updated: float = self.created
        self.factory = factory
        self.state: typing.Any = None
        factory.sessions[cookie] = self

    def remove(self):
        """Removes a cookie from the CookieFactory session storage"""
        if self.cookie in self.factory.sessions:
            del self.factory.sessions[self.cookie]


class CookieFactory:
    def __init__(self, server: ahapi.server.SimpleServer, cookie_name: str = "ahapi", expiry: int = 86400 * 7):
        """
        Creates a CookieFactory, responsible for managing cookie-based sessions with arbitrary state objects.
        A session can have any object associated with it (class, dict, list, string etc).
        """
        self.name: str = cookie_name
        self.server = server
        self.expiry: int = expiry
        self.sessions: typing.Dict[str, CookieSession] = {}
        self.last_prune = time.time()

    def prune(self):
        """Prunes the session list, removing stale cookies and their associated states"""
        now = time.time()
        # Prune at most every hour and only if we have a large enough quantity of session objects
        if self.last_prune < (now - 3600) and len(self.sessions) > MIN_PRUNE_SIZE:
            to_del = []
            whence = now - self.expiry
            for key, cookie in self.sessions.items():
                if cookie.updated < whence:  # This cookie is stale :/
                    to_del.append(key)
            for key in to_del:
                del self.sessions[key]
            self.last_prune = now

    def make(self, request: aiohttp.web.Request, state: typing.Any) -> CookieSession:
        """Generates a new session object and returns it.
        If the HTTP response is successful, it will also set the cookie in the client's browser.
        """
        # First, check if we need to prune the session storage
        self.prune()

        # Then, make the cookie
        cid = str(uuid.uuid4())
        cookie: http.cookies.SimpleCookie = http.cookies.SimpleCookie()
        session: CookieSession = CookieSession(self, cid)
        session.state = state
        cookie[self.name] = cid
        self.server.pending_headers[id(request)] = {"Set-Cookie": cookie[self.name].OutputString()}
        return session

    def get(self, request: aiohttp.web.Request) -> typing.Optional[CookieSession]:
        """Fetches a session cookie and its state from the CookieFactory, given a request with a valid cookie header.
        If the cookie could not be found, or if it is too old, None is returned instead and the cookie deleted.
        """
        session_id = None
        for cookie_header in request.headers.getall("cookie"):
            cookies: http.cookies.SimpleCookie = http.cookies.SimpleCookie(cookie_header)
            if self.name in cookies:
                # Must be hex chars only
                if all(c in "abcdefg1234567890-" for c in cookies[self.name].value):
                    session_id = cookies[self.name].value
                break
        if session_id and session_id in self.sessions:
            session: CookieSession = self.sessions[session_id]
            now = time.time()
            # Check for expiry
            if session.updated < (now - self.expiry):
                session.remove()
                return None
            # Not expired, refresh updated timestamp and return
            session.updated = now
            return session
        return None
