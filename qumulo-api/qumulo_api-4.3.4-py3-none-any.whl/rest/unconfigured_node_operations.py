# Copyright (c) 2013 Qumulo, Inc.
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

# XXX: Please add types to the functions in this file. Static type checking in
# Python prevents bugs!
# mypy: ignore-errors


import qumulo.lib.request as request

from qumulo.lib.util import tabulate


def fmt_unconfigured_nodes(unconfigured_nodes_response):
    """
    @param unconfigured_nodes_response The result of list_unconfigured_nodes
    @return a string containing a pretty table of the given nodes.
    """
    if not unconfigured_nodes_response.data.get('nodes'):
        return 'No unconfigured nodes found.'

    # Flatten the list of dicts (containing dicts) to a square array, with
    # column headers.
    rows = [
        (
            node['label'],
            node['model_number'],
            node['node_version']['revision_id'],
            node['node_version']['build_id'],
            node['uuid'],
        )
        for node in unconfigured_nodes_response.data['nodes']
    ]
    return tabulate(rows, headers=['LABEL', 'MODEL', 'VERSION', 'BUILD', 'UUID'])


@request.request
def list_unconfigured_nodes(conninfo, credentials):
    method = 'GET'
    uri = '/v1/unconfigured/nodes/'

    return request.rest_request(conninfo, credentials, method, uri)
