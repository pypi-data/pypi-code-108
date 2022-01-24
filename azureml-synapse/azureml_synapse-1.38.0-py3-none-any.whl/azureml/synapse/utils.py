# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for Synapse utilities."""

import re
import sys

import requests
from IPython.core import display
from azureml._compute._constants import MLC_WORKSPACE_API_VERSION
from azureml.core import ComputeTarget
from . import consts


def get_synapse_endpoint(workspace: str, sparkpool: str, location: str) -> str:
    """Get Livy service endpoint for a given Synapse Spark pool.

    :param workspace: Synapse workspace name
    :type workspace: str
    :param sparkpool: name of the Synapse Spark pool
    :type sparkpool: str
    :param location: location
    :type location: str
    :return:
    :rtype: str
    """
    assert workspace is not None and sparkpool is not None and location is not None
    if location in consts.US_GOV_CLOUD:
        return consts.LIVY_ENDPOINT_TEMPLATE.format(workspace, consts.LIVY_ENDPOINT_DNS_USGOV, sparkpool)
    elif location in consts.MOONCAKE_CLOUD:
        return consts.LIVY_ENDPOINT_TEMPLATE.format(workspace, consts.LIVY_ENDPOINT_DNS_MOONCAKE, sparkpool)
    elif location in consts.BLACKFOREST_CLOUD:
        return consts.LIVY_ENDPOINT_TEMPLATE.format(workspace, consts.LIVY_ENDPOINT_DNS_BLACKFOREST, sparkpool)
    else:
        return consts.LIVY_ENDPOINT_TEMPLATE.format(workspace, consts.LIVY_ENDPOINT_DNS, sparkpool)


def resolve_synapse_resource_id(resource_id):
    """Parse a resourceId of a Synapse Spark pool."""
    assert resource_id is not None
    match = re.match(
        "^/subscriptions/([^/]+)/resourceGroups/([^/]+)/providers/"
        "Microsoft.Synapse/workspaces/([^/]+)/bigDataPools/(.+)$",
        resource_id)
    if match is not None:
        return match.groups()


def get_compute(workspace: str, name: str):
    """Get compute from an AML workspace by name.

    :param workspace: AML workspace name
    :type workspace: str
    :param name: compute name
    :type name: str
    """
    # TODO: use azureml SDK after linked service is merged
    url = ComputeTarget._get_compute_endpoint(workspace, name)
    headers = workspace._auth.get_authentication_header()
    params = {'api-version': MLC_WORKSPACE_API_VERSION}
    res = _simple_request_get(url, headers, params)
    return res.get('properties')


def is_synapse_compute(compute) -> bool:
    """Check if the compute is Synapse Spark pool."""
    return compute is not None and (compute.get("computeType") == "SynapseSpark")


def _simple_request_get(url, headers, params):
    try:
        r = requests.get(url, params, headers=headers)
    except requests.exceptions.RequestException:
        error = True
        r = None
        status = None
        text = None
    else:
        error = False
        status = r.status_code
        text = r.text
    if error or status != 200:
        raise Exception(u"Invalid status code '{}' from {} with error payload: {}".format(status, url, text))
    return r.json()


def _list_synapse_compute(workspace):
    # TODO: use azureml SDK to get the computes.
    url = ComputeTarget._get_list_computes_endpoint(workspace)
    headers = workspace._auth.get_authentication_header()
    params = {'api-version': MLC_WORKSPACE_API_VERSION}
    res = _simple_request_get(url, headers, params)
    result = []
    for c in res.get("value"):
        if is_synapse_compute(c.get('properties')):
            result.append(c['name'])
    return result


def display_html(to_display):
    """Display html.

    :param to_display: the html to display
    """
    display.display_html(to_display)


def write(msg):
    """Write message and flush."""
    sys.stdout.write(msg)
    sys.stdout.flush()


def writeln(msg=""):
    """Write message with new line."""
    write(u"{}\n".format(msg))


def send_error(error):
    """Write error and flush."""
    sys.stderr.write(u"{}\n".format(error))
    sys.stderr.flush()


def _get_env_desc(env_name, env_ver):
    if env_name is None or env_ver is None:
        return env_name
    else:
        return "{}.{}".format(env_name, env_ver)
