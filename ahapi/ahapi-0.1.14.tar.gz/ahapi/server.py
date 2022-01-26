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

# Asynchronous HTTP API Server

import importlib.util
import json
import os
import sys
import time
import traceback
import base64

import asyncio
import aiohttp.web
import typing

import ahapi.formdata

__version__ = "0.1.14"


KNOWN_TEXT_EXTENSIONS = {
    "txt": "text/plain",
    "html": "text/html",
    "js": "application/javascript",
    "css": "text/css",
    "svg": "image/svg+xml",
}

KNOWN_BINARY_EXTENSIONS = {
    "png": "image/png",
    "gif": "image/gif",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
}


class Endpoint:
    """API end-point function"""

    exec: typing.Callable

    def __init__(self, executor):
        self.exec = executor


class SimpleServer:
    """Basic HTTP API Server"""

    def load_api_dir(self, dirname):
        dir_relative = dirname.replace(self.api_root, "", 1)
        for endpoint_file in os.listdir(dirname):
            endpoint_path = os.path.join(dirname, endpoint_file)
            if endpoint_file.endswith(".py"):
                endpoint = endpoint_file[:-3]
                modname = ".".join(dir_relative.split("/"))
                spec = importlib.util.spec_from_file_location(f"{modname}.{endpoint}", endpoint_path)
                m = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(m)
                endpoint_url = os.path.join(dir_relative, endpoint).strip("/")
                if hasattr(m, "register"):
                    self.handlers[endpoint_url] = m.__getattribute__("register")(self.state)
                    print(f"Registered endpoint /{endpoint_url}")
                else:
                    print(f"Could not find entry point 'register()' in {endpoint_path}, skipping!")
            elif os.path.isdir(endpoint_path) and not endpoint_file.startswith("__"):
                print(f"Traversing {endpoint_path}")
                self.load_api_dir(endpoint_path)

    def __init__(
        self,
        api_dir: str = "endpoints",
        static_dir: typing.Optional[str] = None,
        bind_ip: str = "127.0.0.1",
        bind_port: int = 8080,
        state: typing.Any = None,
        max_upload: int = ahapi.formdata.AHAPI_MAX_PAYLOAD,
    ):
        print("==== Starting HTTP API server... ====")
        self.state = state
        self.handlers: typing.Dict[str, Endpoint] = {}
        self.server = None
        self.bind_ip = bind_ip
        self.bind_port = bind_port
        self.api_root = api_dir
        self.static_dir = static_dir
        self.max_upload = max_upload
        self.pending_headers: typing.Dict[int, dict] = {}

        # Load each URL endpoint
        self.load_api_dir(api_dir)

    async def handle_request(self, request: aiohttp.web.BaseRequest) -> aiohttp.web.Response:
        """Generic handler for all incoming HTTP requests"""
        resp: aiohttp.web.Response

        # Define response headers first...
        headers = {"Server": "ahapi v/%s" % __version__}

        # Figure out who is going to handle this request, if any, while allowing path info.
        handler = "__404"
        segments = request.path.strip("/").split("/")
        for i in range(0, len(segments)):
            partial_url = "/".join(segments)
            if partial_url in self.handlers:
                handler = partial_url
                break
            segments.pop()

        body_type = "form"
        cct = request.headers.get("content-type", "foobar")
        if cct.lower() == "application/json":
            body_type = "json"

        # Parse form/json data if any
        try:
            indata = await ahapi.formdata.parse_formdata(body_type, request, max_upload=self.max_upload)
        except ValueError as e:
            return aiohttp.web.Response(headers=headers, status=400, text=str(e))

        # Calc request path if for a static file
        static_file_path = None
        if self.static_dir:
            static_file_path = os.path.join(self.static_dir, request.path[1:].replace("..", ""))
            if static_file_path.endswith("/"):
                static_file_path += "index.html"
        # Find a handler, or 404
        if handler in self.handlers:
            try:
                # Wait for endpoint response. This is typically JSON in case of success,
                # but could be an exception (that needs a traceback) OR
                # it could be a custom response, which we just pass along to the client.
                hid = id(request)
                output = await self.handlers[handler].exec(self.state, request, indata)
                if output is not None and not isinstance(output, aiohttp.web.Response):
                    if isinstance(output, str):
                        headers["content-type"] = "text/html"
                        jsout = output
                    elif isinstance(output, dict) or isinstance(output, list) or isinstance(output, tuple):
                        headers["content-type"] = "application/json"
                        jsout = json.dumps(output, indent=2)
                    else:
                        raise ValueError(f"Could not determine output type from API call to {handler}")
                    headers["Content-Length"] = str(len(jsout))
                    if hid in self.pending_headers:
                        headers.update(**self.pending_headers[hid])
                        del self.pending_headers[hid]
                    return aiohttp.web.Response(headers=headers, status=200, text=jsout)
                elif isinstance(output, aiohttp.web.Response):
                    return output
                else:
                    return aiohttp.web.Response(headers=headers, status=404, text="Content not found")
            # If a handler hit an exception, we need to print that exception somewhere,
            # either to the web client or stderr:
            except:  # This is a broad exception on purpose!
                if hid in self.pending_headers:  # clear pending headers if we crashed here...
                    del self.pending_headers[hid]
                exc_type, exc_value, exc_traceback = sys.exc_info()
                err = "\n".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
                return aiohttp.web.Response(headers=headers, status=500, text="API error occurred: \n" + err)

        # Static file handler?
        elif self.static_dir and static_file_path and os.path.isfile(static_file_path):
            # Simple cache support - etag or l-m verification:
            fstat = os.stat(static_file_path)
            last_modified = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(fstat.st_mtime))
            etag = base64.b64encode(b"%f-%u" % (fstat.st_mtime, fstat.st_size)).decode('ascii')
            if request.headers.get("if-none-match", "") == etag:
                return aiohttp.web.Response(headers=headers, status=304)
            if request.headers.get("if-modified-since", "") == last_modified:
                return aiohttp.web.Response(headers=headers, status=304)
            headers["Last-Modified"] = last_modified
            headers["etag"] = etag
            ext = static_file_path.split(".")[-1]
            if ext in KNOWN_TEXT_EXTENSIONS:  # We are sure these are text files
                content_type = KNOWN_TEXT_EXTENSIONS[ext]
                txt_content = open(static_file_path, "r").read()
                return aiohttp.web.Response(headers=headers, status=200, content_type=content_type, body=txt_content)
            else:  # Binary file? Probably
                binary_content = open(static_file_path, "rb").read()
                content_type = KNOWN_BINARY_EXTENSIONS.get(ext, "application/binary")
                return aiohttp.web.Response(headers=headers, status=200, content_type=content_type, body=binary_content)

        # File or handler not found?
        else:
            return aiohttp.web.Response(headers=headers, status=404, text="API Endpoint not found!")

    async def loop(self, forever=True):
        self.server = aiohttp.web.Server(self.handle_request)
        runner = aiohttp.web.ServerRunner(self.server)
        await runner.setup()
        site = aiohttp.web.TCPSite(runner, self.bind_ip, self.bind_port)
        await site.start()
        print("==== HTTP API Server running on %s:%s ====" % (self.bind_ip, self.bind_port))
        if forever:
            while True:
                await asyncio.sleep(100)
