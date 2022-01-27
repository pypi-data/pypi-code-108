import base64
import time
import logging
import json

import requests

from Accuinsight.__about__ import __version__
from Accuinsight.modeler.protos import skapi_pb2
from Accuinsight.modeler.utils.proto_json_utils import parse_dict
from Accuinsight.modeler.utils.string_utils import strip_suffix
from Accuinsight.modeler.exceptions import ModelerException, RestException
from Accuinsight.modeler.core.LcConst.LcConst import RUN_RESULT_PATH, RUN_MODEL_SHAP_JSON_PATH

RESOURCE_DOES_NOT_EXIST = 'RESOURCE_DOES_NOT_EXIST'

_logger = logging.getLogger(__name__)

_DEFAULT_HEADERS = {
    'User-Agent': 'modeler-python-client/%s' % __version__
}


def http_request(host_creds, endpoint, retries=3, retry_interval=3,
                 max_rate_limit_interval=60, **kwargs):
    """
    Makes an HTTP request with the specified method to the specified hostname/endpoint. Ratelimit
    error code (429) will be retried with an exponential back off (1, 2, 4, ... seconds) for at most
    `max_rate_limit_interval` seconds.  Internal errors (500s) will be retried up to `retries` times
    , waiting `retry_interval` seconds between successive retries. Parses the API response
    (assumed to be JSON) into a Python object and returns it.

    :param host_creds (object containing)
        hostname and optional authentication.
    :return: Parsed API response
    """
    hostname = host_creds.host
    auth_str = None
    if host_creds.username and host_creds.password:
        basic_auth_str = ("%s:%s" % (host_creds.username, host_creds.password)).encode("utf-8")
        auth_str = "Basic " + base64.standard_b64encode(basic_auth_str).decode("utf-8")
    elif host_creds.token:
        auth_str = "Bearer %s" % host_creds.token

    headers = dict(_DEFAULT_HEADERS)
    if auth_str:
        headers['Authorization'] = auth_str

    verify = not host_creds.ignore_tls_verification

    def request_with_ratelimit_retries(max_rate_limit_interval, **kwargs):
        response = requests.request(**kwargs)
        time_left = max_rate_limit_interval
        sleep = 1
        while response.status_code == 429 and time_left > 0:
            _logger.warning(
                "API request to {path} returned status code 429 (Rate limit exceeded). "
                "Retrying in %d seconds. "
                "Will continue to retry 429s for up to %d seconds.",
                sleep, time_left)
            time.sleep(sleep)
            time_left -= sleep
            response = requests.request(**kwargs)
            sleep = min(time_left, sleep*2)  # sleep for 1, 2, 4, ... seconds;
        return response

    cleaned_hostname = strip_suffix(hostname, '/')
    url = "%s%s" % (cleaned_hostname, endpoint)
    for i in range(retries):
        # response = request_with_ratelimit_retries(max_rate_limit_interval,
        #                                           url=url, headers=headers, verify=verify, **kwargs)
        response = request_with_ratelimit_retries(max_rate_limit_interval,
                                                  url=url, headers=headers, **kwargs)
        if response.status_code >= 200 and response.status_code < 500:
            return response
        else:
            _logger.error(
                "API request to %s failed with code %s != 200, retrying up to %s more times. "
                "API response body: %s",
                url, response.status_code, retries - i - 1, response.text)
            time.sleep(retry_interval)
    raise ModelerException("API request to %s failed to return code 200 after %s tries" %
                          (url, retries))


def _can_parse_as_json(string):
    try:
        json.loads(string)
        return True
    except Exception:  # pylint: disable=broad-except
        return False


def http_request_safe(host_creds, endpoint, **kwargs):
    """
    Wrapper around ``http_request`` that also verifies that the request succeeds with code 200.
    """
    response = http_request(host_creds=host_creds, endpoint=endpoint, **kwargs)
    return verify_rest_response(response, endpoint)


def verify_rest_response(response, endpoint):
    """Verify the return code and raise exception if the request was not successful."""
    if response.status_code != 200:
        if _can_parse_as_json(response.text):
            raise RestException(json.loads(response.text))
        else:
            base_msg = "API request to endpoint %s failed with error code " \
                       "%s != 200" % (endpoint, response.status_code)
            raise ModelerException("%s. Response body: '%s'" % (base_msg, response.text))
    return response


def _get_path(path_prefix, endpoint_path):
    return "{}{}".format(path_prefix, endpoint_path)


def extract_api_info_for_service(service, path_prefix):
    """ Return a dictionary mapping each API method to a tuple (path, HTTP method)"""
    service_methods = service.DESCRIPTOR.methods
    res = {}
    for service_method in service_methods:
        endpoints = service_method.GetOptions().Extensions[skapi_pb2.rpc].endpoints
        endpoint = endpoints[0]
        endpoint_path = _get_path(path_prefix, endpoint.path)
        res[service().GetRequestClass(service_method)] = (endpoint_path, endpoint.method)
    return res


def _make_metrics_data(json_body):
    result = []
    # metrics_object = {'key': '', 'values': [], 'timestamp': [], 'steps': []}

    # get metrics
    metrics_data = json_body['metrics']
    # get visuals
    if 'visuals' in json_body:
        visuals_data = json_body['visuals']
        for item in visuals_data:
            # metrics_object = {'key': '', 'values': [], 'timestamp': [], 'steps': []}
            metrics_object = {'key': item['key'], 'values': [], 'timestamp': item['timestamp'], 'steps': item['steps']}
            # key, listValues, timestamp, steps

            if 'listValues' in item:
                for values in item['listValues'][0]['values']:
                    metrics_object['values'].append(values['values'])
            else:
                metrics_object['values'].extend(item['values'][0]['values'])

            result.append(metrics_object)
            metrics_data.append(metrics_object)

    if 'visuals' in json_body:
        del json_body['visuals']

    return json_body


def _make_parameter_data(json_body):
    result = []
    # metrics_object = {'key': '', 'values': [], 'timestamp': [], 'steps': []}

    # get metrics
    try:
        parameter_data = json_body['parameter']
    except KeyError:
        parameter_data = []
    # "parameter": {
    #     "parameter": {
    #       "learningrate": "0.12",
    #       "subsample": "0.72",
    #       "colsamplebytree": "0.62",
    #       "maxdepth": "52",
    #       "alpha": "0.82"
    #     }
    #   }

    parameter = {'parameter': {}}
    for param in parameter_data:
        key = param['key']
        value = param['value']
        parameter['parameter'].setdefault(key, value)
        # column_dict.setdefault(col_name, []).append(row[col_name])

    if 'parameter' in json_body:
        del json_body['parameter']

    json_body['parameter'] = parameter
    return json_body


def _make_feature_data(json_body, run_info_json):
    json_body['feature'] = {}
    json_body['feature']['importance'] = {}

    run_result_path = run_info_json[RUN_RESULT_PATH]

    #json_path = run_result_path[RUN_MODEL_SHAP_JSON_PATH]

    #json_path = None
    
    if RUN_MODEL_SHAP_JSON_PATH in run_result_path.keys():
        json_path = run_result_path[RUN_MODEL_SHAP_JSON_PATH]
        
        with open(json_path) as json_file:
            shap_json_data = json.load(json_file)
        json_body['feature']['importance'] = shap_json_data   

    return json_body


def call_endpoint(host_creds, endpoint, method, json_body, response_proto, current_run_meta):
    # Cover json String to json dictionary, to pass to requests
    if json_body:
        json_body = json.loads(json_body)
        json_body = _make_metrics_data(json_body)
        json_body = _make_parameter_data(json_body)
        json_body = _make_feature_data(json_body, current_run_meta)
    if method == 'GET':
        response = http_request(
            host_creds=host_creds, endpoint=endpoint, method=method, params=json_body)
    else:
        response = http_request(
            host_creds=host_creds, endpoint=endpoint, method=method, json=json_body)
    response = verify_rest_response(response, endpoint)
    js_dict = json.loads(response.text)
    # print('Backend Response result: ', js_dict)
    parse_dict(js_dict=js_dict, message=response_proto)
    return response_proto


# def key_clock(username, password):
#   headers = {'Content-Type': 'application/x-www-form-urlencoded'}
#   data = {'grant_type': 'password',
#           'client_id': 'accu_modeler_client',
#           'client_secret': '379668c7-70d2-49db-b977-d3c2b6baed14' ,
#           'username': username,
#           'password': password}
#   try:
#     response = requests.post('https://sso.aws-multiverse.skcc.com/auth/realms/DOTS/protocol/openid-connect/token', data, headers=headers)
#
#   except Exception:
#     logging.error("key_clock server connection failed")
#     response = None
#
#   return response

def daapi_list(host, api, token):
  try:
    headers = {'x-auth-token': token}
    response = requests.get(host+api, headers=headers)
    result = response.json()["data"]

  except Exception:
    logging.error("DaApi server connection failed")
    result = None

  return result

def daapi_data_list(host, api, data, token):
  try:
    headers = {'x-auth-token': token}
    response = requests.get(host+api, data, headers=headers)
    result = response.json()["data"]

  except Exception:
    logging.error("DaApi server connection failed")
    result = None

  return result


class ModelerHostCreds(object):
    """
    Provides a hostname and optional authentication for talking to an back-end server.
    :param host: Hostname (e.g., http://localhost:5000) to back-end server. Required.
    :param username: Username to use with Basic authentication when talking to server.
        If this is specified, password must also be specified.
    :param password: Password to use with Basic authentication when talking to server.
        If this is specified, username must also be specified.
    :param token: Token to use with Bearer authentication when talking to server.
        If provided, user/password authentication will be ignored.
    :param ignore_tls_verification: If true, we will not verify the server's hostname or TLS
        certificate. This is useful for certain testing situations, but should never be
        true in production.
    """
    def __init__(self, host, username=None, password=None, token=None,
                 ignore_tls_verification=False):
        if not host:
            raise ModelerException("host is a required parameter for ModelerHostCreds")
        self.host = host
        self.username = username
        self.password = password
        self.token = token
        self.ignore_tls_verification = ignore_tls_verification
