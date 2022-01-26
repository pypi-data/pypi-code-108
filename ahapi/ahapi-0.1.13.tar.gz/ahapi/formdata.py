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

# HTTP API Form Data Handler for ahapi

import io
import json
import urllib.parse

import aiohttp.web
import multipart

AHAPI_MAX_PAYLOAD = 256 * 1024


async def parse_formdata(body_type, request: aiohttp.web.BaseRequest, max_upload: int = AHAPI_MAX_PAYLOAD) -> dict:
    form_as_dict = {}
    for key, val in urllib.parse.parse_qsl(request.query_string):
        form_as_dict[key] = val
    # PUT/POST form data?
    if request.method not in ["GET", "HEAD"]:
        # Default max is 1MB, if we want larger, we're gonna have to tweak internals.
        if max_upload and max_upload > request._client_max_size:
            request._client_max_size = max_upload
        if request.can_read_body:
            try:
                if request.content_length and request.content_length > max_upload:
                    raise ValueError("Form data payload too large, max %u bytes." % max_upload)
                body = await request.text()
                if body_type == "json":
                    try:
                        js = json.loads(body)
                        assert isinstance(js, dict)  # json data MUST be an dictionary object, {...}
                        form_as_dict.update(js)
                    except ValueError:
                        raise ValueError("Erroneous payload received")
                elif body_type == "form":
                    if request.headers.get("content-type", "").lower() == "application/x-www-form-urlencoded":
                        try:
                            for key, val in urllib.parse.parse_qsl(body):
                                form_as_dict[key] = val
                        except ValueError:
                            raise ValueError("Erroneous payload received")
                    # If multipart, turn our body into a BytesIO object and use multipart on it
                    elif "multipart/form-data" in request.headers.get("content-type", "").lower():
                        fh = request.headers.get("content-type")
                        fb = fh.find("boundary=")
                        if fb > 0:
                            boundary = fh[fb + 9 :]
                            if boundary:
                                try:
                                    for part in multipart.MultipartParser(
                                            io.BytesIO(body.encode("utf-8")),
                                            boundary,
                                            len(body),
                                    ):
                                        form_as_dict[part.name] = part.value
                                except ValueError:
                                    raise ValueError("Erroneous payload received")
            finally:
                pass
    return form_as_dict
