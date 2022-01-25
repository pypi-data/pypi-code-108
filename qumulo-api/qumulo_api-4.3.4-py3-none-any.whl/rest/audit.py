# Copyright (c) 2019 Qumulo, Inc.
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


from typing import MutableMapping, Optional

import qumulo.lib.request as request

from qumulo.lib.auth import Credentials

#                _
#  ___ _   _ ___| | ___   __ _
# / __| | | / __| |/ _ \ / _` |
# \__ \ |_| \__ \ | (_) | (_| |
# |___/\__, |___/_|\___/ \__, |
#      |___/             |___/
#  FIGLET: syslog
#


@request.request
def get_syslog_config(
    conninfo: request.Connection, credentials: Credentials
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/audit/syslog/config'
    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def set_syslog_config(
    conninfo: request.Connection,
    credentials: Credentials,
    enabled: Optional[bool] = None,
    server_address: Optional[str] = None,
    server_port: Optional[int] = None,
    etag: Optional[str] = None,
) -> request.RestResponse:
    method = 'PATCH'
    uri = '/v1/audit/syslog/config'
    body: MutableMapping[str, object] = {}
    if enabled is not None:
        body['enabled'] = enabled
    if server_address is not None:
        body['server_address'] = server_address
    if server_port is not None:
        body['server_port'] = server_port
    return request.rest_request(conninfo, credentials, method, uri, body=body, if_match=etag)


@request.request
def get_syslog_status(
    conninfo: request.Connection, credentials: Credentials
) -> request.RestResponse:
    method = 'GET'
    uri = '/v1/audit/syslog/status'
    return request.rest_request(conninfo, credentials, method, uri)


#       _                 _               _       _
#   ___| | ___  _   _  __| |_      ____ _| |_ ___| |__
#  / __| |/ _ \| | | |/ _` \ \ /\ / / _` | __/ __| '_ \
# | (__| | (_) | |_| | (_| |\ V  V / (_| | || (__| | | |
#  \___|_|\___/ \__,_|\__,_| \_/\_/ \__,_|\__\___|_| |_|
#  FIGLET: cloudwatch
#


@request.request
def get_cloudwatch_config(
    conninfo: request.Connection, credentials: Optional[Credentials]
) -> request.RestResponse:
    """
    Get the cluster's CloudWatch configuration. It includes the region, the log group
    name, and the enabled flag. Here's what the initial configuration looks like:

        {
            "region": "",
            "enabled": false,
            "log_group_name": ""
        }

    When CloudWatch is enabled the returned document will look something like this:

        {
            "region": "us-west-2",
            "enabled": true,
            "log_group_name": "my-cluster-log-group"
        }
    """
    method = 'GET'
    uri = '/v1/audit/cloudwatch/config'
    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def set_cloudwatch_config(
    conninfo: request.Connection,
    credentials: Optional[Credentials],
    enabled: Optional[bool] = None,
    log_group_name: Optional[str] = None,
    region: Optional[str] = None,
) -> request.RestResponse:
    """
    Set the cluster's CloudWatch configuration. You can specify the region, log group
    name, and enabled flag. A valid region and log group name are required when enabling
    the CloudWatch feature.
    """
    method = 'PATCH'
    uri = '/v1/audit/cloudwatch/config'
    body: MutableMapping[str, object] = {}
    if enabled is not None:
        body['enabled'] = enabled
    if log_group_name is not None:
        body['log_group_name'] = log_group_name
    if region is not None:
        body['region'] = region
    return request.rest_request(conninfo, credentials, method, uri, body=body)


@request.request
def get_cloudwatch_status(
    conninfo: request.Connection, credentials: Optional[Credentials]
) -> request.RestResponse:
    """
    Get the cluster's CloudWatch status. Return a dictionary where each keyed by node
    ID. Each value is a dictionary with a "last_seen_error" key containing the last
    error the node got from the CloudWatch service, if there was no error on the nodes
    all the last seen errors will be null:

        {
            "node_statuses": {
                "1": {
                    "last_seen_error": null
                },
                "3": {
                    "last_seen_error": null
                },
                "2": {
                    "last_seen_error": null
                },
                "4": {
                    "last_seen_error": null
                }
            }
        }

    This is useful to troubleshoot CloudWatch issues. For example if you didn't assign
    the proper IAM role to node 1 and 4, you will see something like this:

        {
            "node_statuses": {
                "1": {
                    "last_seen_error": "Access denied sending logs to CloudWatch"
                },
                "3": {
                    "last_seen_error": null
                },
                "2": {
                    "last_seen_error": null
                },
                "4": {
                    "last_seen_error": "Access denied sending logs to CloudWatch"
                }
            }
        }
    """
    method = 'GET'
    uri = '/v1/audit/cloudwatch/status'
    return request.rest_request(conninfo, credentials, method, uri)
