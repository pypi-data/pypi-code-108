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

from typing import Optional

from typing_extensions import TypedDict

import qumulo.lib.request as request

from qumulo.lib.auth import Credentials
from qumulo.lib.uri import UriBuilder


@request.request
def blocked(conninfo: request.Connection, credentials: Credentials) -> request.RestResponse:
    method = 'GET'
    uri = '/v2/upgrade/blocked'
    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def verify_image(
    conninfo: request.Connection,
    credentials: Credentials,
    image_path: str,
    override_compatibility_check: bool = False,  # TODO NDU US42882: hide this somehow
) -> request.RestResponse:
    method = 'POST'
    uri_builder = UriBuilder(path='/v2/upgrade/verify-image')
    if override_compatibility_check:
        uri_builder.add_query_param('override_compatibility_check', True)
    body = {'image_path': image_path}
    return request.rest_request(conninfo, credentials, method, str(uri_builder), body=body)


@request.request
def prepare(
    conninfo: request.Connection,
    credentials: Credentials,
    image_path: str,
    auto_commit: bool,
    override_compatibility_check: bool = False,  # TODO NDU US42882: hide this somehow
) -> request.RestResponse:
    method = 'POST'
    uri_builder = UriBuilder(path='/v2/upgrade/prepare')
    if override_compatibility_check:
        uri_builder.add_query_param('override_compatibility_check', True)
    body = {'image_path': image_path, 'auto_commit': auto_commit}
    return request.rest_request(conninfo, credentials, method, str(uri_builder), body=body)


@request.request
def commit(conninfo: request.Connection, credentials: Credentials) -> request.RestResponse:
    method = 'POST'
    uri = '/v2/upgrade/commit'
    return request.rest_request(conninfo, credentials, method, uri)


class ApiV2UpgradeSettings(TypedDict):
    auto_commit: bool
    install_path: str
    target_version: str
    upgrade_type: str


class ApiV2UpgradeStatus(TypedDict):
    error_info: Optional[str]
    progress: Optional[int]
    settings: Optional[ApiV2UpgradeSettings]
    state: str


@request.request
def status(conninfo: request.Connection, credentials: Credentials) -> request.RestResponse:
    method = 'GET'
    uri = '/v2/upgrade/status'
    return request.rest_request(conninfo, credentials, method, uri)
