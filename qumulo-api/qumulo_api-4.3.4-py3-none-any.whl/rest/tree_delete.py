# Copyright (c) 2021 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import time

from typing import Optional

import qumulo.lib.request as request

from qumulo.lib.auth import Credentials
from qumulo.lib.uri import UriBuilder


@request.request
def list_jobs(
    conninfo: request.Connection, credentials: Optional[Credentials]
) -> request.RestResponse:
    uri = UriBuilder(path='/v1/tree-delete/jobs').append_slash()
    method = 'GET'
    return request.rest_request(conninfo, credentials, method, str(uri))


@request.request
def create_job(
    conninfo: request.Connection, credentials: Optional[Credentials], dir_id: str
) -> request.RestResponse:
    uri = UriBuilder(path='/v1/tree-delete/jobs').append_slash()
    method = 'POST'
    body = {'id': dir_id}
    return request.rest_request(conninfo, credentials, method, str(uri), body=body)


@request.request
def get_job(
    conninfo: request.Connection, credentials: Optional[Credentials], dir_id: str
) -> request.RestResponse:
    method = 'GET'
    uri = UriBuilder(path=f'/v1/tree-delete/jobs/{dir_id}')
    return request.rest_request(conninfo, credentials, method, str(uri))


@request.request
def cancel_job(
    conninfo: request.Connection, credentials: Optional[Credentials], dir_id: str
) -> request.RestResponse:
    method = 'DELETE'
    uri = UriBuilder(path=f'/v1/tree-delete/jobs/{dir_id}')
    return request.rest_request(conninfo, credentials, method, str(uri))


@request.void_request
def wait_for_job(
    conninfo: request.Connection, credentials: Optional[Credentials], dir_id: str
) -> None:
    while True:
        try:
            get_job(conninfo, credentials, dir_id)
        except request.RequestError as e:
            if e.error_class == 'http_not_found_error':
                return
            raise
        time.sleep(1.0)
