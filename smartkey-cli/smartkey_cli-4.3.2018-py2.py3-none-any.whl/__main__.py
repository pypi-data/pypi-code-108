#!/usr/bin/python

from __future__ import print_function

import copy
import json
import re
import os.path
import sdkms.v1
import argparse
import textwrap
import requests
import warnings
import traceback
import textwrap
import time

from os.path import expanduser
from getpass import getpass
from six.moves import http_client, input
from six import string_types
from argparse import RawTextHelpFormatter
from sdkms.v1.rest import ApiException
from sdkms.v1 import SecurityObjectsApi
from sdkms.v1 import SignAndVerifyApi
from sdkms.v1 import WrappingAndUnwrappingApi
from sdkms.v1 import EncryptionAndDecryptionApi
from sdkms.v1 import AuthenticationApi
from sdkms.v1 import AppsApi
from sdkms.v1 import GroupsApi
from sdkms.v1 import UsersApi
from sdkms.v1 import PluginsApi
from sdkms.v1 import AccountsApi
from sdkms.v1 import SignRequestEx
from sdkms.v1 import VerifyRequestEx
from sdkms.v1.models import BaseEnumObject
from sdkms.v1 import AppRequest
from sdkms.v1 import AppResetSecretRequest
from sdkms.v1 import GroupRequest
from sdkms.v1 import BatchEncryptRequest
from sdkms.v1 import BatchDecryptRequest
from sdkms.v1 import EncryptRequest
from sdkms.v1 import EncryptRequestEx
from sdkms.v1 import EncryptInitRequestEx
from sdkms.v1 import EncryptUpdateRequestEx
from sdkms.v1 import EncryptFinalRequestEx
from sdkms.v1 import DecryptInitRequestEx
from sdkms.v1 import DecryptUpdateRequestEx
from sdkms.v1 import DecryptFinalRequestEx
from sdkms.v1 import DecryptRequest
from sdkms.v1 import DecryptRequestEx
from sdkms.v1 import WrapKeyRequest
from sdkms.v1 import UnwrapKeyRequest
from sdkms.v1 import WrapKeyRequestEx
from sdkms.v1 import UnwrapKeyRequestEx
from sdkms.v1 import SobjectRequest
from sdkms.v1 import SignRequest
from sdkms.v1 import VerifyRequest
from sdkms.v1 import DigestApi
from sdkms.v1 import DigestRequest
from sdkms.v1 import DeriveKeyMechanism
from sdkms.v1 import DeriveKeyRequest
from sdkms.v1 import PersistTransientKeyRequest
from sdkms.v1 import RevocationReason
from sdkms.v1 import KeyOperations
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

from .pycompatible import *

DEFAULT_API_ENDPOINT = "https://apps.smartkey.io"
verify_ssl = True
ssl_ca_cert = None
api_endpoint = DEFAULT_API_ENDPOINT
proxy = None
# 350k
CHUNK_SIZE = 358400

AES_BLOCK_SIZE = 16
DES_BLOCK_SIZE = 8
AES = 'AES'
DES = 'DES'
DES3 = 'DES3'
RSA = 'RSA'
EC = 'EC'
SYMMETRIC_ALG = (AES, DES, DES3)
ASYMMETRIC_ALG = (RSA, EC)
SECURITY_ALGO = SYMMETRIC_ALG + ASYMMETRIC_ALG
# create .token file in user home directory
USER_HOME= expanduser("~")
TOKEN_FILE = "{}/.token".format(USER_HOME)
USER_TOKEN = 'user-token'
APP_TOKEN = 'app-token'
CERT_PATH = "cert-path"
KEY_PATH = "key-path"
ENDPOINT = "end-point"
PROXY = "proxy"

default_symmetric_ops = [
    'ENCRYPT',
    'DECRYPT',
    'WRAPKEY',
    'UNWRAPKEY',
    'DERIVEKEY',
    'APPMANAGEABLE',
]

default_rsa_ops = [
    'SIGN',
    'VERIFY',
    'ENCRYPT',
    'DECRYPT',
    'WRAPKEY',
    'UNWRAPKEY',
    'APPMANAGEABLE',
]

default_hmac_ops = [
    'MACGENERATE',
    'MACVERIFY',
    'APPMANAGEABLE',
]

default_ec_ops = [
    'SIGN',
    'VERIFY',
    'APPMANAGEABLE',
]


class Globals(object):
    pass


class RequiredAuth:
    USER = "user"
    APP = "app"
    EITHER = "either"
    NONE = "none"


class ClientException(Exception):
    def __init__(self, message, verbose=False):
        self.message = message
        self.verbose = verbose


_globals = Globals()
_globals.app_token = ""
_globals.user_token = ""
_globals.cert_path = ""
_globals.key_path = ""
_globals.preferred_auth = ""


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, BaseEnumObject):
            return obj.value

        return json.JSONEncoder.default(self, obj)


def serialize(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, BaseEnumObject):
        return obj.value
    if isinstance(obj, bytearray):
        return to_string(obj)

    return obj.to_dict()


def _get_args(f, parser):
    lno_arg_dict = {}
    for lno, line in enumerate(f):
        lno_arg_dict[lno] = vars(parser.parse_args(line.split()))

    return lno_arg_dict


def _print_err(errors):
    for err in errors:
        sys.stderr.write("[E] {}\n".format(err))

def fetch_version():
    version_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'VERSION')
    if not os.path.isfile(version_file_path):
        print("version info is missing. please check the installation")
        sys.exit(1)

    version_file = open(version_file_path)
    version = version_file.read().strip()
    if version == "":
        print("version info is missing. please check the installation")
        sys.exit(1)

    global VERSION
    VERSION = version

def _fill_digest(batch_arg_dict):
    """
    Parse dictionary and fill out digest of in file
    :param args_dict:
    :return:
    """

    for key in batch_arg_dict:
        arguments = batch_arg_dict[key]
        with open(arguments['in']) as f:
            buff = to_byte_array(f.read())
            drequest = DigestRequest(alg=arguments['hash_alg'], data=buff)
            try:
                arguments['hash'] = make_request(RequiredAuth.APP, DigestApi, DigestApi.compute_digest, drequest).digest
            except ApiException as e:
                if e.status != 403:
                    sys.stderr.write("[E] Error at linue number {}\n".format(key+1))
                raise e


def _validate_cipher_param(alg, in_f=None, iv=None, mode=None, tag_len=None, tag=None, is_encrypt=True, **kwargs):
    errors = []

    if alg.upper() in SYMMETRIC_ALG:

        if mode is None:
            errors.append("--mode is required argument for alg({})".format(alg))

        if iv is None and mode.upper() not in ('ECB', 'KW', 'KWP') :
            errors.append("--iv is required argument for alg({}) and Optional if mode is ECB, KW or KWP".format(alg))

        if mode == 'ECB':
            # check file size
            b_size = AES_BLOCK_SIZE
            if alg.upper() != AES:
                b_size = DES_BLOCK_SIZE
            size = os.path.getsize(in_f)
            if size % b_size != 0:
                errors.append("For ECB mode input file size should be multiple of {}".format(b_size))

        if is_encrypt and mode is not None and mode.upper() in ('GCM', 'CCM'):
            if tag_len is None:
                errors.append("--tag-len is required argument for mode({})".format(mode))

        if not is_encrypt and mode is not None and mode.upper() in ('GCM', 'CCM'):
            if tag is None:
                errors.append("--tag is required for mode({})".format(mode))

    if alg.upper() in ASYMMETRIC_ALG:

        if mode is not None and alg.upper() == "EC" :
           errors.append("--mode is not required argument for alg({})".format(alg))

        if iv is not None:
            errors.append("--iv is not required argument for alg({})".format(alg))

        if tag_len is not None:
            errors.append("--tag-len is not required argument for alg({})".format(alg))

    if errors:
        raise ClientException(errors)


def _write_binary(buff, out_f=None, mode='wb'):
    """
    Common function to write data to file or stdout for cipher operation
    :param buff: data to write
    :param out_f: optional file path
    :param out_f: optional mode to open file in
    :return:
    """
    byte_buff = to_bytes(buff)
    if out_f is None:
        os.write(sys.stdout.fileno(), byte_buff)
    else:
        with open(out_f, mode) as f_out:
            f_out.write(byte_buff)


def _read_binary(in_f=None, mode='rb'):
    """
    Common function to read data from file or stdout for cipher operation
    :param buff: data to write
    :param out_f: optional file path
    :param out_f: optional mode to open file in
    :return:
    """
    # Use pycompatible function. There is difference in reading from std-in in PY2 and PY3
    return read_binary(in_f, mode)


def select_token(required_auth=RequiredAuth.NONE):
    if required_auth == RequiredAuth.APP:
        if not value_exists(_globals.app_token):
            raise ClientException("Preferred auth is {}. Please use sdkms-cli app-login to continue".format(_globals.preferred_auth),verbose=True)
        token = _globals.app_token
    elif required_auth == RequiredAuth.USER:
        if not value_exists(_globals.user_token):
            raise ClientException("Preferred auth is {}. Please use sdkms-cli user-login to continue".format(_globals.preferred_auth),verbose=True)
        token = _globals.user_token
    elif required_auth == RequiredAuth.EITHER:
        if not value_exists(_globals.app_token) and not value_exists(_globals.user_token):
            raise ClientException(
                "Error: Not logged in. Please use sdkms-cli app-login or user-login.")
        if value_exists(_globals.app_token):
            required_auth = RequiredAuth.APP
            token = _globals.app_token
        else:
            required_auth = RequiredAuth.USER
            token = _globals.user_token
    elif required_auth == RequiredAuth.NONE:
        token = ""
    else:
        raise ClientException("Invalid auth type: {}".format(required_auth), verbose=True)
    return token, required_auth

def get_api_config():
    config = sdkms.v1.configuration.Configuration()
    config.verify_ssl = verify_ssl
    config.host = api_endpoint
    config.proxy = proxy
    config.ssl_ca_cert = ssl_ca_cert
    return config


def get_api_client(config):
    return sdkms.v1.ApiClient(configuration=config)

def make_request(required_auth, instance_of, method, *argv):
    access_token, auth = select_token(required_auth)
    config = get_api_config()
    config.api_key['Authorization'] = access_token
    config.api_key_prefix['Authorization'] = 'Bearer'
    # Add certificate related details if cert path is present in token file
    if auth == RequiredAuth.APP and _globals.cert_path != 'None' and _globals.key_path != 'None' :
        config.cert_file = _globals.cert_path
        config.key_file = _globals.key_path
    api_client = get_api_client(config)
    obj = instance_of(api_client=api_client)
    return method(obj, *argv)

def _dump_response(required_auth, instance_of, method, id):
    """
    Make request to SDKMS and return the JSON blob
    :param required_auth:
    :param instance_of:
    :param method:
    :param id:
    :return: string json blob
    """
    response = make_request(required_auth, instance_of, method, id)
    return json.dumps(response, default=serialize)

def value_exists(config_value):
    return False if config_value is None or config_value == "" or config_value == "None" else True

def get_proxy_for_requests():
    if not value_exists(proxy):
        return None
    return {"https": proxy}

def validate_url(url):
    u = urlparse(url)
    scheme = u.scheme
    if scheme == "":
        return u.geturl().replace(scheme, "https://", 1)
    else:
        return u.geturl().replace(scheme, "https", 1)

def json_request(url, header=None, body=None, method='GET', exp_status=200, required_auth=RequiredAuth.NONE):
    if (required_auth != RequiredAuth.APP and
            required_auth != RequiredAuth.USER and
            required_auth != RequiredAuth.EITHER and
            required_auth != RequiredAuth.NONE):
        raise ClientException("Invalid auth type: {}".format(required_auth), verbose=True)

    if required_auth == RequiredAuth.EITHER:
        if not value_exists(_globals.app_token) and not value_exists(_globals.user_token):
            raise ClientException(
                "Error: Not logged in. Please use sdkms-client.py app-login or sdkms-client.py user-login.")

        if value_exists(_globals.app_token) and value_exists(_globals.user_token):
            if _globals.preferred_auth == RequiredAuth.APP:
                required_auth = RequiredAuth.APP
            else:
                required_auth = RequiredAuth.USER
        else:
            if value_exists(_globals.app_token):
                required_auth = RequiredAuth.APP
            else:
                required_auth = RequiredAuth.USER

    default_header = {'Content-Type': 'application/json'}

    if 'auth' not in url:
        if required_auth == RequiredAuth.APP and not _globals.app_token:
            raise ClientException("Error: Application not logged in. Please use sdkms-client.py app-login");
        if required_auth == RequiredAuth.USER and not _globals.user_token:
            raise ClientException("Error: User not logged in. Please use sdkms-client.py user-login");

        if required_auth == RequiredAuth.APP:
            default_header['Authorization'] = 'Bearer ' + _globals.app_token
        else:
            default_header['Authorization'] = 'Bearer ' + _globals.user_token

    if header:
        default_header.update(header)

    # verify param in requests.request can take 3 kind of values:
    # False, True, or path to CA bundle file.
    request_verify = verify_ssl
    if ssl_ca_cert is not None:
        request_verify = ssl_ca_cert

    try:
        res = requests.request(method=method, url=validate_url(api_endpoint) + url, headers=default_header, data=body,
                               verify=request_verify, proxies = get_proxy_for_requests())
    except requests.exceptions.RequestException as e:
        raise ClientException("Error: Request to SDKMS failed : " + str(e), verbose=False)

    if res.status_code == exp_status:
        if len(res.text) == 0:
            return {}
        else:
            return res.json()
    else:
        raise ClientException("Error: {} {}".format(str(res.status_code),res.text))


def write_access_tokens():
    with open(TOKEN_FILE, 'w') as f:
        f.write("{}={}\n".format(USER_TOKEN, _globals.user_token))
        f.write("{}={}\n".format(APP_TOKEN, _globals.app_token))
        f.write("{}={}\n".format(CERT_PATH, _globals.cert_path))
        f.write("{}={}\n".format(KEY_PATH, _globals.key_path))
        f.write("{}={}\n".format(ENDPOINT, api_endpoint))
        f.write("{}={}\n".format(PROXY, proxy))


def _login(username, password):
    config = get_api_config()
    config.username = username
    config.password = password
    api_client = get_api_client(config)
    auth = sdkms.v1.AuthenticationApi(api_client=api_client).authorize()
    return auth.access_token


def app_login(**kwargs):
    try:
        app_logout()
    except Exception:
        pass

    sys.stderr.write("Logging in " + api_endpoint + " \n")

    if "api_key" in kwargs and kwargs["api_key"]:
        api_key = kwargs["api_key"]
    else:
        api_key = input("Please enter your API Key: ")
    del kwargs['api_key']

    if "timeout" in kwargs and kwargs["timeout"]:
        kwargs['_request_timeout'] = int(kwargs["timeout"])
    del kwargs['timeout']
    config = get_api_config()
    config.app_api_key = api_key
    api_client = get_api_client(config)

    auth = sdkms.v1.AuthenticationApi(api_client=api_client).authorize(**kwargs)
    _globals.app_token = auth.access_token
    write_access_tokens()


def certificate_login(**kwargs):
    try:
        app_logout()
    except Exception:
        pass
    sys.stderr.write("Logging in " + api_endpoint + " \n")

    if "app_id" in kwargs and kwargs["app_id"]:
        app_id = kwargs["app_id"]
    else:
        app_id = input("Please enter App Id : ")

    if "certificate_path" in kwargs and kwargs["certificate_path"]:
        certificate_path = kwargs["certificate_path"]
    else:
        certificate_path = input("Please enter certificate path : ")

    if "key_path" in kwargs and kwargs["key_path"]:
        key_path = kwargs["key_path"]
    else:
        key_path = input("Please enter key path : ")


    config = get_api_config()
    config.key_file = key_path
    config.cert_file = certificate_path
    config.username = app_id
    api_client = get_api_client(config)
    res = sdkms.v1.AuthenticationApi(api_client=api_client).authorize()
    _globals.app_token = res.access_token
    _globals.cert_path = certificate_path
    _globals.key_path = key_path
    write_access_tokens()

def ldap_auth(**kwargs):
    try:
        user_logout()
    except Exception:
        pass

    sys.stderr.write("Logging in " + api_endpoint + " \n")

    if not kwargs['user_email']:
        kwargs['user_email']= input("Please enter your useremail: ")

    if kwargs['password']:
        print("WARNING: Passing your password via --password is not very secure.")
        print("It is better to enter your password interactively")
    else:
        kwargs['password'] = getpass("SDKMS Password: ")
    res=json_request('/sys/v1/session/auth/discover',header=None,body=json.dumps(kwargs),method='POST',exp_status=200, required_auth=RequiredAuth.NONE)

    if not kwargs['email']:
        kwargs['email'] = kwargs['user_email']

    for i in range(0, res.__len__()):
        if res[i]['method']=='ldap-password':
            if not kwargs['method']:
                kwargs['method']='ldap-basic-auth'
            kwargs['idp_id']=res[i]['idp_id']

    response=json_request('/sys/v1/session/auth', header=None,body=json.dumps(kwargs),method='POST',exp_status=200, required_auth=RequiredAuth.NONE)
    _globals.user_token = response['access_token']
    write_access_tokens()

    try:
        select_account(**kwargs)
    except Exception as e:
        # If we didn't successfully select an account, drop the access token to force the user to log in again. The
        # token won't be usable for any actions that require an account to be selected.
        user_logout()
        raise

def user_login(**kwargs):
    try:
        user_logout()
    except Exception:
        pass

    sys.stderr.write("Logging in " + api_endpoint + " \n")

    if kwargs['username']:
        username = kwargs["username"]
    else:
        username = input("Please enter your SDKMS username: ")
    if kwargs['password']:
        print("WARNING: Passing your password via --password is not very secure.")
        print("It is better to enter your password interactively")
        password = kwargs['password']
    else:
        password = getpass("SDKMS Password: ")

    _globals.user_token = _login(username, password)
    write_access_tokens()

    try:
        select_account(**kwargs)
    except Exception as e:
        # If we didn't successfully select an account, drop the access token to force the user to log in again. The
        # token won't be usable for any actions that require an account to be selected.
        user_logout()
        raise


def _logout(required_auth):
    make_request(required_auth,AuthenticationApi, AuthenticationApi.terminate)


def user_logout():
    if _globals.user_token:
        try:
            _logout(RequiredAuth.USER)
        finally:
            _globals.user_token = ""
            write_access_tokens()


def app_logout():
    if _globals.app_token:
        try:
            _logout(RequiredAuth.APP)
        finally:
            _globals.app_token = ""
            _globals.key_path = ""
            _globals.cert_path = ""
            write_access_tokens()


def user_logout_cmd(**kwargs):
    if _globals.user_token:
        user_logout()
    else:
        raise ClientException("User not logged in")


def app_logout_cmd(**kwargs):
    if _globals.app_token:
        app_logout()
    else:
        raise ClientException("App not logged in")


def logout_cmd(**kwargs):
    try:
        user_logout_cmd()
    finally:
        app_logout_cmd()


def logout():
    try:
        app_logout()
    except Exception:
        pass
    try:
        user_logout()
    except Exception:
        pass

def audit_log(**kwargs):
    groups={}
    apps={}
    users={}
    plugins={}
    current_time = int(time.time())

    res=make_request(RequiredAuth.USER,GroupsApi,GroupsApi.get_groups)
    for group in res:
        groups[group.group_id] = group.name
    res=make_request(RequiredAuth.USER,AppsApi,AppsApi.get_apps)
    for app in res:
        apps[app.app_id] = app.name
    res=make_request(RequiredAuth.USER,UsersApi,UsersApi.get_users)
    for user in res:
        users[user.user_id] = user.user_email
    res=make_request(RequiredAuth.USER,PluginsApi,PluginsApi.get_plugins)
    for plugin in res:
        plugins[plugin.plugin_id] = plugin.name

    filename = "log_dump_" + str(current_time) + ".csv"
    f = open(filename, 'w')
    f.write('Severity,Type,Groups,IP-Address,Message,Actor,Time\n')

    print('Fetching logs and saving in file: ' + filename)
    limit = int(kwargs['limit'])
    logs = limit
    query_upper_limit = 1000
    if kwargs['start_time']:
        start_time = int(time.mktime(time.strptime(kwargs['start_time'], "%Y-%m-%d")))
        if (start_time > current_time):
            raise ClientException("--start-time can't be greater than current-time")
    if kwargs['end_time']:
        end_time = int(time.mktime(time.strptime(kwargs['end_time'], "%Y-%m-%d")))

    for start in range(0, limit, query_upper_limit):
        url = '/sys/v1/logs?size=' + str(min(logs, query_upper_limit)) + '&from=' + str(start)
        if kwargs['start_time']:
            url = url + '&range_from=' + str(start_time)
        if kwargs['end_time']:
            url = url + '&range_to=' + str(end_time)

        response = json_request(url, exp_status=200, header=None, body=None, method='GET', required_auth=RequiredAuth.USER)

        if 'hits' not in response or response['hits'] is None or len(response['hits']) == 0:
            break

        for log in response['hits']:
            log_data = log['_source']['severity'] + ',' + \
                       log['_source']['action_type'] + ','

            group_list = []
            for group_id in log['_source']['group_ids']:
                if group_id in groups:
                    group_list.append(groups[group_id])

            ip_data = 'null' if log['_source']['client_ip'] is None else log['_source']['client_ip']
            log_data = log_data + ';'.join(group_list) + ',' + \
                       ip_data + ',' + \
                       '\'' + log['_source']['message'] + '\','

            actor = 'null'
            if log['_source']['actor_type'] == 'App':
                if log['_source']['actor_id'] in apps:
                    actor = 'App: ' + apps[log['_source']['actor_id']]
            elif log['_source']['actor_type'] == 'User':
                if log['_source']['actor_id'] in users:
                    actor = 'User: ' + users[log['_source']['actor_id']]
            elif log['_source']['actor_type'] == 'Plugin':
                if log['_source']['actor_id'] in plugins:
                    actor = 'Plugin: ' + plugins[log['_source']['actor_id']]
            log_data = log_data + actor + ',' + log['_source']['time'] + "\n"
            f.write(log_data)

        logs = logs - query_upper_limit

    print("Fetching logs completed. The log file is " + filename)
    f.close()

def process_custom_metadata(kwargs):
    if kwargs['custom_metadata'] is not None:
        metadata = json.loads(kwargs['custom_metadata'])
        if not isinstance(metadata, dict):
            raise ClientException('--custom_metadata should be a JSON object ' +
                                  'e.g. --custom_metadata \'{ "key" = "value" }\'')
        for key in metadata.keys():
            if not isinstance(metadata[key], string_types):
                raise ClientException('Value for custom metadata key "{}" must be of type string'.format(key))
        kwargs['custom_metadata'] = metadata


def default_ops_for_object(obj_type):
    """
    To support new object type one if statement is required here.
    :param obj_type:
    :return: Supported operation
    """
    if obj_type == 'RSA':
        return copy.copy(default_rsa_ops)
    elif obj_type == 'EC':
        return copy.copy(default_ec_ops)
    elif obj_type == 'DES' or obj_type == 'DES3' or obj_type == 'AES':
        return copy.copy(default_symmetric_ops)
    elif obj_type == 'HMAC':
        return copy.copy(default_hmac_ops)

    return []


def show_app(app_id):
    sys.stdout.write(_dump_response(RequiredAuth.USER, AppsApi, AppsApi.get_app, app_id))


def show_group(group_id):
    sys.stdout.write(_dump_response(RequiredAuth.USER, GroupsApi, GroupsApi.get_group, group_id))


def show_user(user_id):
    sys.stdout.write(_dump_response(RequiredAuth.USER, UsersApi, UsersApi.get_user, user_id))


def show_account(account_id):
    sys.stdout.write(_dump_response(RequiredAuth.USER, AccountsApi, AccountsApi.get_account, account_id))


def create_key(**kwargs):
    # validate input for EC name and key-size
    kwargs['obj_type'] = str.upper(kwargs['obj_type'])
    if kwargs['obj_type'] == EC:
        if kwargs['key_size'] is not None:
            raise ClientException('Error: For object type {}, --key-size is not required'.format(kwargs['obj_type']))
        if kwargs['pub_exponent'] is not None:
            raise ClientException('Error: For object type {}, --pub-exponent is not required'.format(kwargs['obj_type']))

    if kwargs['obj_type'] != EC and kwargs['ec_name'] is not None:
        raise ClientException('Error: For object type {}, --ec-name is not required'.format(kwargs['obj_type']))

    process_custom_metadata(kwargs)
    operations = []
    if kwargs['exportable']:
        operations.append('EXPORT')
        # warn user if exportable is given for AES,DES,DES3 or RSA and EC keys
        # f is for force
        if kwargs['obj_type'].upper() in SECURITY_ALGO and not kwargs['force']:
            print('Do you want to make security object exportable')
            flag = input("This can be security hazard (Y/N):")
            if flag.upper() != 'Y':
                print('Aborting the key creation')
                return
    if kwargs['key_ops']:
        list =kwargs['key_ops'].split(",")
        for ops in list:
            operations.append(ops)
    else:
        operations += default_ops_for_object(kwargs['obj_type'])

    del kwargs['exportable']
    del kwargs['force']
    kwargs['key_ops'] = operations
    kwargs['elliptic_curve'] = kwargs["ec_name"]
    # we don't require this argument now
    del kwargs["ec_name"]
    # Expand kwargs to assign value to respective function argument
    request = sdkms.v1.SobjectRequest(**kwargs)
    # Generic method to make request
    res = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.generate_security_object, request)
    if res.transient_key is not None:
        print("{}".format(res.transient_key))
    else:
        print("{}".format(res.kid))

def persist_key(**kwargs):
    operations = []
    if kwargs['key_ops']:
        operations = kwargs['key_ops'].split(",")
        kwargs['key_ops'] += operations
    request = PersistTransientKeyRequest(**kwargs)
    response = make_request(RequiredAuth.APP, SecurityObjectsApi, SecurityObjectsApi.persist_security_object, request)
    if response.kid is not None:
        print("{}".format(response.kid))

def rotate_key(**kwargs):
    request = SobjectRequest(**kwargs)
    # Generic method to make request
    res = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.rotate_security_object, request)
    if res.kid is not None:
        print("{}".format(res.kid))

def import_key(key_file, **kwargs):
    process_custom_metadata(kwargs)

    in_key = _read_binary(key_file)

    if kwargs['der']:
        kwargs['value'] = to_byte_array(in_key)
    else:
        if kwargs['obj_type'].upper() in ('RSA', 'EC'):
            # It is EC or RSA in PEM format
            # remove PEM related tags if any
            # for python3: decode in_key as string, because file is opened as rb
            in_key = in_key.decode()
            in_key = [x for x in in_key.split(os.linesep) if not x.startswith('-----')]
            in_key = "".join(in_key)
            kwargs['value'] = to_byte_array(b64_decode(in_key))
        else:
            kwargs['value'] = to_byte_array(hex_decode(in_key))

    operations = default_ops_for_object(kwargs['obj_type'])
    if kwargs['exportable']:
        operations.append('EXPORT')
        # warn user if exportable is given for AES,DES,DES3 or RSA and EC keys
        # f is for force
        if kwargs['obj_type'].upper() in SECURITY_ALGO and not kwargs['force']:
            print('Do you want to make security object exportable')
            flag = input("This can be security hazard (Y/N):")
            if flag.upper() != 'Y':
                print('Aborting the key creation')
                return
    if kwargs['key_ops']:
        list =kwargs['key_ops'].split(",")
        for ops in list:
            operations.append(ops)

    del kwargs['exportable']
    del kwargs['force']
    kwargs['key_ops'] = operations
    kwargs['elliptic_curve'] = kwargs["ec_curve"]

    # remove un-wanted argument
    del kwargs["ec_curve"]
    del kwargs['der']
    request = SobjectRequest(**kwargs)
    response = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.import_security_object,
                            request)

    print("{}".format(response.kid))


def import_cert(cert_file, **kwargs):
    process_custom_metadata(kwargs)
    kwargs['value'] = _read_binary(cert_file)
    if not kwargs['der']:
        # simple check to make sure that non der (pem) certificate has required BEGIN TAG
        # There is no check if der format is selected
        if b'-----BEGIN' not in kwargs['value']:
            raise ClientException("Not a valid certificate. The certificate need to have BEGIN and END tag.")

    kwargs['value'] = to_byte_array(kwargs['value'])
    kwargs['obj_type'] = 'OPAQUE'
    del kwargs['der']

    request = SobjectRequest(**kwargs)
    response = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.import_security_object,
                            request)
    print("{}".format(response.kid))


def import_secret(secret_file, **kwargs):
    process_custom_metadata(kwargs)
    # using regular expression to remove auto added '\n' char by f.read() method
    secret = _read_binary(secret_file).decode()
    kwargs['value'] = to_byte_array(to_bytes(re.sub(os.linesep + r'\Z', '', secret)))
    # imported secret is exportable
    kwargs['key_ops'] = ['EXPORT', 'APPMANAGEABLE']

    request = SobjectRequest(**kwargs)
    response = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.import_security_object,
                            request)
    print("{}".format(response.kid))

def update_object(**kwargs):
    kid = None
    object_data = None

    if kwargs['kid'] is not None:
        kid = kwargs['kid']
    elif kwargs['name'] is not None:
        response = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.get_security_objects, kwargs['name'])
        object_data = response[0]
        kid = object_data.kid
        del kwargs['name']
    else:
        raise ClientException("Please enter kid or name.")

    del kwargs['kid']

    if kwargs["description"] is None:
        del kwargs["description"]

    operations = []

    if kwargs['key_ops'] and 'disable_export' in kwargs and kwargs['disable_export']:
        raise ClientException("Please either set --key-ops or --disable-export, but not both")

    if kwargs['key_ops']:
        list =kwargs['key_ops'].split(",")
        for ops in list:
            operations.append(ops)
        kwargs["key_ops"] = operations
    else:
        del kwargs["key_ops"]

    if 'disable_export' in kwargs:
        if kwargs['disable_export']:
            if object_data is None:
                object_data = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.get_security_object, kid)
            operations = object_data.key_ops
            operations.remove(KeyOperations.EXPORT)
            kwargs["key_ops"] = operations
        del kwargs["disable_export"]

    process_custom_metadata(kwargs)

    quorum = 'quorum' in kwargs and kwargs['quorum']
    del kwargs['quorum']

    if quorum:
        _send_approval_request('PATCH', '/crypto/v1/keys/' + kid, kwargs)
    else:
        response = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.update_security_object, kid, kwargs)
        print("{}".format(response.kid))

def obj_size_or_curve(sobject):
    if sobject.key_size:
        return sobject.key_size
    elif sobject.elliptic_curve:
        return sobject.elliptic_curve
    else:
        return ''


def list_objects(offset, limit, filter_out=None, **kwargs):
    if filter_out is None:
        filter_out = []
    name = None
    if 'name' in kwargs:
        name = kwargs['name']

    response = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.get_security_objects, name,
                            None, None, None, None, None, limit, offset)

    for sobject in response:
        if sobject.obj_type in filter_out:
            continue
        print('{} "{}" "{}" {} {}'.format(
            sobject.kid, sobject.name, sobject.description, sobject.obj_type,
            obj_size_or_curve(sobject)))


def list_keys(offset, limit, **kwargs):
    list_objects(offset, limit, filter_out=['OPAQUE'], **kwargs)


def print_operations(ops):
    ops_string = ''
    for op in ops:
        if ops_string == '':
            ops_string = op.value
        else:
            ops_string += ', {}'.format(op.value)

    print('operations: {}'.format(ops_string))


def print_custom_metadata(metadata):
    print('custom metadata:\n{')
    for key in sorted(metadata.keys()):
        print('\t{}: {}'.format(json.dumps(key), json.dumps(metadata[key])))
    print('} // end custom metadata')


def print_property(name, description, key_object):
    if name in key_object:
        print('{}: {}'.format(description, key_object[name]))


def show_sobject(**kwargs):
    if kwargs['kid'] is not None:
        kid = kwargs['kid']
    elif kwargs['name'] is not None:
        response = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.get_security_objects, kwargs['name'])
        kid = response[0].kid
    else:
        raise ClientException("Please enter kid or name.")

    response = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.get_security_object, kid)
    print(json.dumps(response, default=serialize))

def der2pem(response):
    if response.obj_type.value in ('AES', 'DES', 'DES3'):
        return to_bytes(hex_encode(response.value))
    elif response.obj_type.value in ('EC', 'RSA'):
         begin_key = '-----BEGIN ' + response.obj_type.value + ' PRIVATE KEY-----\n'
         end_key = '\n-----END ' + response.obj_type.value + ' PRIVATE KEY-----'
         key = begin_key + '\n'.join(textwrap.wrap(b64_encode(response.value), 64)) + end_key
         return to_bytes(key)
    else:
        return to_bytes(response.value)

def export_object(**kwargs):
    if kwargs['kid'] is not None:
        kid = kwargs['kid']
    elif kwargs['name'] is not None:
        res = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.get_security_objects,
                kwargs['name']);
        if len(res) != 1:
            raise ClientException("Can't find object for the given name")
        else:
            kid = res[0].kid
    else:
        raise ClientException("Please enter kid or name.")

    quorum = 'quorum' in kwargs and kwargs['quorum']
    del kwargs['quorum']

    if quorum:
        _send_approval_request('POST', '/crypto/v1/keys/export', {"kid": kid})
    else:
        response = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.get_security_object_value, kid)
        # Python2 and 3 compatible way to output bytes to stdout
        # imported secret can be a plain text or random bytes
        if kwargs['der']:
            os.write(sys.stdout.fileno(), response.value)
        else:
            os.write(sys.stdout.fileno(), der2pem(response))


def activate_object(**kwargs):
    if kwargs['kid'] is not None:
        kid = kwargs['kid']
    elif kwargs['name'] is not None:
        res = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.get_security_objects,
                kwargs['name']);
        if len(res) != 1:
            raise ClientException("Can't find object for the given name")
        else:
            kid = res[0].kid
    else:
        raise ClientException("Please enter kid or name.")

    response = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.activate_security_object, kid)


def revoke_object(**kwargs):
    if kwargs['kid'] is not None:
        kid = kwargs['kid']
    elif kwargs['name'] is not None:
        res = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.get_security_objects,
                kwargs['name']);
        if len(res) != 1:
            raise ClientException("Can't find object for the given name")
        else:
            kid = res[0].kid
    else:
        raise ClientException("Please enter kid or name.")

    del kwargs['name']
    del kwargs['kid']
    request = RevocationReason(**kwargs)
    response = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.revoke_security_object, kid, request)


def delete(kid, **kwargs):
    make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.delete_security_object, kid)

def _fill_in(batch_argv, key, file='in'):
    """
    Open file provided in --in flag and add a new element in batch_argv as per key field
    :param batch_argv:
    :param key: name of the new dict key. in case of encrypt it is plain and for decrypt it is cipher
    :return:
    """
    for lno in batch_argv:
        argument = batch_argv[lno]
        if argument[file] is not None:
            argument[key] = to_byte_array(read_binary(argument[file]))


def batch_decrypt(in_f):
    """
    Perform encryption for multiple input file.
    Output format:
    <line_number> <output_file_path> <status>
    line_number indicates for which line from input file, this output corresponds to
    :param in_f: input file having encrypt command options per line
    :return: No return
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--kid', required=True)
    parser.add_argument('--in', required=True)
    parser.add_argument('--alg', required=True)
    parser.add_argument('--mode')
    parser.add_argument('--iv')
    parser.add_argument('--ad')
    parser.add_argument('--tag')
    parser.add_argument('--out')
    batch_argv = None
    with open(in_f, "r") as f:
        batch_argv = _get_args(f, parser)

    _fill_in(batch_argv, 'cipher')
    _fill_in(batch_argv, 'tag', file='tag')
    # prepare batch request
    requests = BatchDecryptRequest()
    for key in batch_argv:
        argument = batch_argv[key]
        request_dict = {
            'kid': argument['kid'],
            'request': {
                'alg': argument['alg'],
                'mode': argument['mode'],
                'iv': to_byte_array(hex_decode(argument['iv'])),
                'ad': to_byte_array(hex_decode(argument['ad'])),
                'tag': to_byte_array(argument['tag']),
                'cipher': argument['cipher']
            }
        }

        _validate_cipher_param(in_f=argument['in'], is_encrypt=False, **argument)
        requests.append(request_dict)
    # lets go for batch encryption
    response = make_request(RequiredAuth.EITHER, EncryptionAndDecryptionApi, EncryptionAndDecryptionApi.batch_decrypt, requests)
    # It is blocked because of pysdk bug
    errors = []
    for key in batch_argv:
        enc_res = response[key]
        argument = batch_argv[key]
        status = 0 if enc_res.status == 200 else 1
        if argument['out'] is None:
            argument['out'] = "{}.dec".format(argument['in'])
        if status == 0:
            buff = to_bytes(enc_res.body.plain)
            _write_binary(buff, argument['out'])
            # # write down any GCM tag
            # if enc_res.body.tag is not None:
            #     tag = to_bytes(enc_res.body.tag)
            #     _write_binary(tag, '{}.tag'.format(argument['out']))
        else:
            errors.append("Line Number: {}, Reason: {}".format(key+1, enc_res.error))

        print ("{} {} {}".format(key+1, argument['out'], status))

    if errors:
        raise ClientException(errors)


def batch_encrypt(in_f):
    """
    Perform encryption for multiple input file.
    Output format:
    <line_number> <output_file_path> <status>
    line_number indicates for which line from input file, this output corresponds to
    :param in_f: input file having encrypt command options per line
    :return: No return
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--kid', required=True)
    parser.add_argument('--in', required=True)
    parser.add_argument('--alg', required=True)
    parser.add_argument('--mode')
    parser.add_argument('--iv')
    parser.add_argument('--ad')
    parser.add_argument('--tag-len')
    parser.add_argument('--out')
    batch_argv = None
    with open(in_f, "r") as f:
        batch_argv = _get_args(f, parser)

    _fill_in(batch_argv, 'plain')

    # prepare batch request
    requests = BatchEncryptRequest()
    for key in batch_argv:
        argument = batch_argv[key]
        if argument['tag_len'] is not None:
            argument['tag_len'] = int(argument['tag_len'])

        _validate_cipher_param(in_f=argument['in'], **argument)

        request_dict = {
            'kid': argument['kid'],
            'request': {
                'alg': argument['alg'],
                'mode': argument['mode'],
                'iv': to_byte_array(hex_decode(argument['iv'])),
                'ad': to_byte_array(hex_decode(argument['ad'])),
                'tag_len': argument['tag_len'],
                'plain': argument['plain']
            }
        }

        requests.append(request_dict)
    # lets go for batch encryption
    response = make_request(RequiredAuth.EITHER, EncryptionAndDecryptionApi, EncryptionAndDecryptionApi.batch_encrypt, requests)
    # It is blocked because of pysdk bug
    errors = []
    for key in batch_argv:
        enc_res = response[key]
        argument = batch_argv[key]
        status = 0 if enc_res.status == 200 else 1
        if argument['out'] is None:
            argument['out'] = "{}.enc".format(argument['in'])
        if status == 0:
            buff = to_bytes(enc_res.body.cipher)
            _write_binary(buff, argument['out'])
            # write down any GCM tag
            if enc_res.body.tag is not None:
                tag = to_bytes(enc_res.body.tag)
                _write_binary(tag, '{}.tag'.format(argument['out']))
        else:
            errors.append("Line Number: {}, Reason: {}".format(key+1, enc_res.error))

        print ("{} {} {}".format(key+1, argument['out'], status))

    if errors:
        raise ClientException(errors)

def encrypt(in_f, out, kid, **kwargs):

    _validate_cipher_param(in_f=in_f, **kwargs)

    if kwargs['iv'] is not None:
        kwargs['iv'] = to_byte_array(hex_decode(kwargs['iv']))
    if kwargs['ad'] is not None:
        kwargs['ad'] = to_byte_array(hex_decode(kwargs['ad']))
    # Make a single encrypt request
    out_f = open(out, 'wb')
    if kwargs['transient_key'] is not None:
       kwargs['key'] = sdkms.v1.SobjectDescriptor(transient_key=kwargs['transient_key'])
    elif kwargs['name'] is not None:
        kwargs['key'] = sdkms.v1.SobjectDescriptor(name=kwargs['name'])
    else:
        kwargs['key'] = sdkms.v1.SobjectDescriptor(kid=kid)
    del kwargs['name']
    del kwargs['transient_key']
    if os.path.getsize(in_f) < CHUNK_SIZE:
        kwargs['plain'] = to_byte_array(_read_binary(in_f))
        request = EncryptRequestEx(**kwargs)
        response = make_request(RequiredAuth.EITHER, EncryptionAndDecryptionApi, EncryptionAndDecryptionApi.encrypt_ex,
                                request)
        # store tag information if any
        if response.tag is not None:
            _write_binary(hex_encode(response.tag), "{}.tag".format(out))
    else:
        # Go for multi part encryption
        if kwargs['alg'].upper() == 'RSA':
            raise ClientException("Input data is too big to encrypt with RSA algorithm")
        if kwargs['mode'].upper() in ('GCM', 'CCM'):
            # SDKMS documentation not have field to provide tag-len for GCM mode in-case of multi-part
            raise ClientException("Multipart encryption is not supported for mode({})".format(kwargs['mode']))
        # remove un-wanted argument
        del kwargs['ad']
        del kwargs['tag_len']

        state = _cipher_init(**kwargs).state
        with open(in_f, "rb") as f:
            while True:
                data = to_byte_array(f.read(CHUNK_SIZE))
                if not data:
                    break

                response = _cipher_update(key=kwargs['key'], plain=data, state=state)
                out_f.write(response.cipher)
                state = response.state

        response = _cipher_final(key=kwargs['key'], state=state)

    out_f.write(response.cipher)
    out_f.close()


def _call_cipher(request_of, method, **kwargs):
    request = request_of(**kwargs)
    return make_request(RequiredAuth.EITHER, EncryptionAndDecryptionApi, method, request)


def _cipher_init(request_of=EncryptInitRequestEx, method=EncryptionAndDecryptionApi.encrypt_init_ex,  **kwargs):
    """
    internal method to invoke cipher init
    :param kwargs:
    :return: response
    """
    return _call_cipher(request_of, method, **kwargs)


def _cipher_update(request_of=EncryptUpdateRequestEx, method=EncryptionAndDecryptionApi.encrypt_update_ex, **kwargs):
    """
    internal method to invoke cipher update
    :param kwargs:
    :return: response
    """
    buff = None
    if 'plain' in kwargs:
        buff = kwargs['plain']
    else:
        buff = kwargs['cipher']

    if len(buff) > CHUNK_SIZE:
        raise ClientException('Input chunk size sould not be more than 350K')

    return _call_cipher(request_of, method, **kwargs)


def _cipher_final(request_of=EncryptFinalRequestEx, method=EncryptionAndDecryptionApi.encrypt_final_ex, **kwargs):
    return _call_cipher(request_of, method, **kwargs)


def encrypt_init(state_f, **kwargs):
    _validate_cipher_param(**kwargs)

    if kwargs['iv'] is not None:
        kwargs['iv'] = to_byte_array(hex_decode(kwargs['iv']))
    if kwargs['kid'] is not None:
        kwargs['key'] = {'kid': kwargs['kid']}
    elif kwargs['transient_key'] is not None:
        kwargs['key'] = {'transient_key': kwargs['transient_key']}
    elif kwargs['name'] is not None:
        kwargs['key'] = {'name': kwargs['name']}

    # remove un-wanted field
    del kwargs['kid']
    del kwargs['transient_key']
    del kwargs['name']

    response = _cipher_init(**kwargs)
    _write_binary(response.state, state_f)


def encrypt_update(state_f, out_f, **kwargs):
    if kwargs['plain'] is None:
        kwargs['plain'] = _read_binary()

    kwargs['plain'] = to_byte_array(kwargs['plain'])

    kwargs['state'] = to_byte_array(_read_binary(state_f))
    if kwargs['kid'] is not None:
        kwargs['key'] = {'kid': kwargs['kid']}
    elif kwargs['transient_key'] is not None:
        kwargs['key'] = {'transient_key': kwargs['transient_key']}
    elif kwargs['name'] is not None:
        kwargs['key'] = {'name': kwargs['name']}

    # remove un-wanted field
    del kwargs['kid']
    del kwargs['transient_key']
    del kwargs['name']

    response = _cipher_update(**kwargs)

    _write_binary(response.state, state_f)
    _write_binary(response.cipher, out_f, mode='ab+')


def encrypt_final(state_f, out_f, **kwargs):

    kwargs['state'] = to_byte_array(_read_binary(state_f))
    if kwargs['kid'] is not None:
        kwargs['key'] = {'kid': kwargs['kid']}
    elif kwargs['transient_key'] is not None:
        kwargs['key'] = {'transient_key': kwargs['transient_key']}
    elif kwargs['name'] is not None:
        kwargs['key'] = {'name': kwargs['name']}

    # remove un-wanted field
    del kwargs['kid']
    del kwargs['transient_key']
    del kwargs['name']

    response = _cipher_final(**kwargs)

    _write_binary(response.cipher, out_f, mode='ab+')

def decrypt_init(state_f, **kwargs):

    if kwargs['iv'] is not None:
        kwargs['iv'] = to_byte_array(hex_decode(kwargs['iv']))
    if kwargs['kid'] is not None:
        kwargs['key'] = {'kid': kwargs['kid']}
    elif kwargs['transient_key'] is not None:
        kwargs['key'] = {'transient_key': kwargs['transient_key']}
    elif kwargs['name'] is not None:
        kwargs['key'] = {'name': kwargs['name']}

    # remove un-wanted field
    del kwargs['kid']
    del kwargs['transient_key']
    del kwargs['name']
    response = _cipher_init(request_of=DecryptInitRequestEx, method=EncryptionAndDecryptionApi.decrypt_init_ex, **kwargs)
    _write_binary(response.state, state_f)


def decrypt_update(state_f, out_f, **kwargs):
    if kwargs['cipher'] is None:
        kwargs['cipher'] = _read_binary()

    kwargs['cipher'] = to_byte_array(kwargs['cipher'])
    kwargs['state'] = to_byte_array(_read_binary(state_f))

    if kwargs['kid'] is not None:
        kwargs['key'] = {'kid': kwargs['kid']}
    elif kwargs['transient_key'] is not None:
        kwargs['key'] = {'transient_key': kwargs['transient_key']}
    elif kwargs['name'] is not None:
        kwargs['key'] = {'name': kwargs['name']}

    # remove un-wanted field
    del kwargs['kid']
    del kwargs['transient_key']
    del kwargs['name']
    response = _cipher_update(request_of=DecryptUpdateRequestEx, method=EncryptionAndDecryptionApi.decrypt_update_ex, **kwargs)

    _write_binary(response.state, state_f)
    _write_binary(response.plain, out_f, mode='ab+')


def decrypt_final(state_f, out_f, **kwargs):
    kwargs['state'] = to_byte_array(_read_binary(state_f))

    if kwargs['kid'] is not None:
        kwargs['key'] = {'kid': kwargs['kid']}
    elif kwargs['transient_key'] is not None:
        kwargs['key'] = {'transient_key': kwargs['transient_key']}
    elif kwargs['name'] is not None:
        kwargs['key'] = {'name': kwargs['name']}

    # remove un-wanted field
    del kwargs['kid']
    del kwargs['transient_key']
    del kwargs['name']
    response = _cipher_final(request_of=DecryptFinalRequestEx, method=EncryptionAndDecryptionApi.decrypt_final_ex, **kwargs)

    _write_binary(response.plain, out_f, mode='ab+')

def _send_approval_request(method, operation, body):
    request = json.dumps({ 'method': method, 'operation': operation, 'body': body })
    response = json_request('/sys/v1/approval_requests', exp_status=201, header=None, body=request, method='POST',
                        required_auth=RequiredAuth.EITHER)
    status = response['status']
    req_id = response['request_id']
    print("Approval task for operation " + method + " " + operation + " has been created.\nrequest_id: " + req_id + " Status: " + status)

def sign(in_f, kid, **kwargs):
    data = _read_binary(in_f)
    if kwargs['transient_key'] is not None:
       kwargs['key'] = sdkms.v1.SobjectDescriptor(transient_key=kwargs['transient_key'])
    else:
        kwargs['key'] = sdkms.v1.SobjectDescriptor(kid=kid)
    del kwargs['transient_key']
    # calculate digest
    drequest = DigestRequest(alg=kwargs['hash_alg'], data=to_byte_array(data))
    kwargs['hash'] = make_request(RequiredAuth.EITHER, DigestApi, DigestApi.compute_digest, drequest).digest

    quorum = 'quorum' in kwargs and kwargs['quorum']
    del kwargs['quorum']

    if quorum:
        kwargs['hash'] = b64_encode(kwargs['hash'])
        kwargs['key'] = { 'kid': kid}
        _send_approval_request('POST', '/crypto/v1/sign', kwargs)
    else:
        out = kwargs['out'] if 'out' in kwargs else None
        del kwargs['out']
        request = SignRequestEx(**kwargs)
        signature = make_request(RequiredAuth.EITHER, SignAndVerifyApi, SignAndVerifyApi.sign_ex, request).signature
        _write_binary(signature, out)

def batch_sign(in_f):
    """
    Generate signature for multiple sign request.
    Output format:
    <line_number> <output_file_path> <status>
    line_number indicates for which line from input file, this output corresponds to
    :return: No return
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--kid', required=True)
    parser.add_argument('--hash-alg', required=True)
    parser.add_argument('--in', required=True)
    parser.add_argument('--out')
    batch_argv = None
    with open(in_f, "r") as f:
        batch_argv = _get_args(f, parser)
    # file digest of input file
    _fill_digest(batch_argv)
    # prepare batch request
    requests = []
    for key in batch_argv:
        argument = batch_argv[key]
        rdict = {'key': {'kid': argument['kid']},
                 'hash': argument['hash'], 'hash_alg': argument['hash_alg']}
        requests.append(SignRequestEx(**rdict))

    response = make_request(RequiredAuth.EITHER, SignAndVerifyApi, SignAndVerifyApi.batch_sign, requests)
    errors = []
    for key in batch_argv:
        sig_res = response[key]
        argument = batch_argv[key]
        status = 0 if sig_res.status == 200 else 1
        if argument['out'] is None:
            argument['out'] = "{}.sig".format(argument['in'])
        if status == 0:
            buff = to_bytes(sig_res.body.signature)
            _write_binary(buff, argument['out'])
        else:
            errors.append("Line Number: {}, Reason: {}".format(key+1, sig_res.error))

        print ("{} {} {}".format(key+1, argument['out'], status))

    if errors:
        raise ClientException(errors)


def batch_verify(in_f):
    """
    Perform signature verification for batch.
    Output format:
    <line_number> <output_file_path> <status>
    line_number indicates for which line from input file, this output corresponds to
    :return: No return
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--kid', required=True)
    parser.add_argument('--hash-alg', required=True)
    parser.add_argument('--in', required=True)
    parser.add_argument('--sig-in', required=True)
    batch_argv = None
    with open(in_f, "r") as f:
        batch_argv = _get_args(f, parser)
    # file digest of input file
    _fill_digest(batch_argv)
    # Add signature
    for key in batch_argv:
        with open(batch_argv[key]['sig_in'], 'rb') as f:
            batch_argv[key]['signature'] = to_byte_array(f.read())

    # prepare batch request
    requests = []
    for key in batch_argv:
        argument = batch_argv[key]
        rdict = {
                 'key': {'kid': argument['kid']},
                 'hash': argument['hash'],
                 'hash_alg': argument['hash_alg'],
                 'signature': argument['signature']
                 }
        requests.append(VerifyRequestEx(**rdict))

    response = make_request(RequiredAuth.EITHER, SignAndVerifyApi, SignAndVerifyApi.batch_verify, requests)
    errors = []
    for key in batch_argv:
        sig_res = response[key]

        if sig_res.status == 200:
            # 0 means successful verification
            status = 0 if sig_res.body.result else 1
        else:
            errors.append("Line Number: {}, "
                          "Reason: {}, "
                          "HTTP Status:{}".format(key+1, sig_res.error, sig_res.status))
            # Verification not fail, However some different error at server side because of wrong input provided
            status = 2

        print ("{} {}".format(key+1, status))

    if errors:
        raise ClientException(errors)


def verify(in_f, sig_f, kid, **kwargs):
    data = _read_binary(in_f)
    if kwargs['transient_key'] is not None:
       kwargs['key'] = sdkms.v1.SobjectDescriptor(transient_key=kwargs['transient_key'])
    else:
        kwargs['key'] = sdkms.v1.SobjectDescriptor(kid=kid)
    del kwargs['transient_key']
    # Generate digest from input file
    drequest = DigestRequest(alg=kwargs['hash_alg'], data=to_byte_array(data))
    kwargs['hash'] = make_request(RequiredAuth.EITHER, DigestApi, DigestApi.compute_digest, drequest).digest

    kwargs['signature'] = to_byte_array(_read_binary(sig_f))

    vrequest = VerifyRequestEx(**kwargs)
    res = make_request(RequiredAuth.EITHER, SignAndVerifyApi, SignAndVerifyApi.verify_ex, vrequest)
    if res.result is not True:
        raise ClientException("Signature verification fail")


def wrap_key(wrapping_kid, kid, **kwargs):
    if kwargs['iv'] is not None:
        kwargs['iv'] = to_byte_array(hex_decode(kwargs["iv"]))
    if kwargs['ad'] is not None:
        kwargs['ad'] = to_byte_array(hex_decode(kwargs["ad"]))
    
    quorum = 'quorum' in kwargs and kwargs['quorum']
    del kwargs['quorum']

    if quorum:
        if kwargs['wrapped_key_name'] is not None:
            kwargs['subject'] = { 'name': kwargs['wrapped_key_name']}
        else:
            kwargs['subject'] = {'kid': kid }
        if kwargs['transient_key'] is not None:
            kwargs['key'] = { 'transient_key': kwargs['transient_key'] }
        elif kwargs['wrapping_key_name'] is not None:
            kwargs['key'] = { 'name': kwargs['wrapping_key_name']}
        else:
            kwargs['key'] = { 'kid': wrapping_kid }

        del kwargs['wrapped_key_name']
        del kwargs['transient_key']
        del kwargs['wrapping_key_name']
        _send_approval_request('POST', '/crypto/v1/wrapkey', kwargs)
    else:
        if kwargs['wrapped_key_name'] is not None:
            kwargs['subject'] = sdkms.v1.SobjectDescriptor(name=kwargs['wrapped_key_name'])
        else:
            kwargs['subject'] = sdkms.v1.SobjectDescriptor(kid=kid)
        del kwargs['wrapped_key_name']
        if kwargs['transient_key'] is not None:
           kwargs['key'] = sdkms.v1.SobjectDescriptor(transient_key=kwargs['transient_key'])
        elif kwargs['wrapping_key_name'] is not None:
            kwargs['key'] = sdkms.v1.SobjectDescriptor(name=kwargs['wrapping_key_name'])
        else:
            kwargs['key'] = sdkms.v1.SobjectDescriptor(kid=wrapping_kid)
        del kwargs['transient_key']
        del kwargs['wrapping_key_name']
        
        if 'out' not in kwargs or kwargs['out'] is None:
            raise ClientException("argument --out is required")
        out = kwargs['out']
        del kwargs['out']

        wrequest = WrapKeyRequestEx(**kwargs)
        response = make_request(RequiredAuth.EITHER, WrappingAndUnwrappingApi, WrappingAndUnwrappingApi.wrap_key_ex,
                             wrequest)
        _write_binary(response.wrapped_key, out)
        if kwargs['iv'] is None and response.iv is not None:
            print("iv: {}".format(hex_encode(response.iv)))
            _write_binary(hex_encode(response.iv), "{}.iv".format(out))
        if response.tag is not None:
            print("tag: {}".format(hex_encode(response.tag)))
            _write_binary(hex_encode(response.tag), "{}.tag".format(out))


def derive_key(kid, **kwargs):

    kwargs['plain'] = to_byte_array(kwargs['plain'])
    kwargs['iv'] = to_byte_array(hex_decode(kwargs["iv"]))
    #check size of plain data and iv
    if (kwargs['key_type'] == "AES")  and \
            (len(kwargs['plain']) % 16 != 0 or len(kwargs['iv']) % 16 != 0):
        raise ClientException("iv size and plain size must be multiple of 16")
    if (kwargs['key_type'] == "DES" or kwargs['alg'] == "DES3") and \
            (len(kwargs['plain']) % 8 != 0 or len(kwargs['iv']) % 8 != 0):
        raise ClientException("iv size and plain size must be multiple of 8")

    if kwargs['ad'] is not None:
        kwargs['ad'] = to_byte_array(hex_decode(kwargs["ad"]))

    process_custom_metadata(kwargs)
    kwargs['key_ops'] = default_ops_for_object(kwargs['key_type'])
    # check if exportable is enabled on derived key
    if kwargs['exportable']:
        kwargs['key_ops'].append('EXPORT')

    del kwargs['exportable']

    mechanism = {'alg': kwargs['alg'], 'plain': kwargs['plain'],
                 'mode': kwargs['mode'], 'iv': kwargs['iv'],
                 'ad': kwargs['ad'], 'tag_len': kwargs['tag_len']}
    # remove unwanted keys from kwargs
    for key in ['alg', 'plain', 'mode', 'iv', 'ad', 'tag_len']:
        del kwargs[key]

    encrypt_obj = EncryptRequest(**mechanism)
    mechanism_obj = DeriveKeyMechanism(encrypt_data=encrypt_obj)
    kwargs['mechanism'] = mechanism_obj
    request = DeriveKeyRequest(**kwargs)
    response = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.derive_key, kid, request)

    print("{}".format(response.kid))


def unwrap_key(in_f, wrapping_kid, **kwargs):
    kwargs['wrapped_key'] = to_byte_array(_read_binary(in_f))
    
    if kwargs['iv'] is not None:
        kwargs['iv'] = to_byte_array(hex_decode(kwargs['iv']))
    if kwargs['ad'] is not None:
        kwargs['ad'] = to_byte_array(hex_decode(kwargs['ad']))
    if kwargs['tag'] is not None:
        kwargs['tag'] = to_byte_array(hex_decode(kwargs['tag']))

    process_custom_metadata(kwargs)
    operations = default_ops_for_object(kwargs['obj_type'])
    if kwargs['exportable']:
        operations.append('EXPORT')
    del kwargs['exportable']
    kwargs['key_ops'] = operations

    quorum = 'quorum' in kwargs and kwargs['quorum']
    del kwargs['quorum']

    if quorum:
        if kwargs['transient_key'] is not None:
            kwargs['key'] = {'transient_key' : kwargs['transient_key']}
        else:
            kwargs['key'] = {'kid': wrapping_kid}
        del kwargs['transient_key']
       
        kwargs['wrapped_key'] = b64_encode(kwargs['wrapped_key'])
        
        if kwargs['iv'] is not None:
            kwargs['iv'] = b64_encode(kwargs['iv'])
        if kwargs['ad'] is not None:
            kwargs['ad'] = b64_encode(kwargs['ad'])
        if kwargs['tag'] is not None:
            kwargs['tag'] = b64_encode(kwargs['tag'])

        _send_approval_request('POST', '/crypto/v1/unwrapkey', kwargs)
    else:
        if kwargs['transient_key'] is not None:
            kwargs['key'] = sdkms.v1.SobjectDescriptor(transient_key=kwargs['transient_key'])
        else:
            kwargs['key'] = sdkms.v1.SobjectDescriptor(kid=wrapping_kid)
        del kwargs['transient_key']
       
        wrequest = UnwrapKeyRequestEx(**kwargs)
        res = make_request(RequiredAuth.EITHER, WrappingAndUnwrappingApi, WrappingAndUnwrappingApi.unwrap_key_ex,
                       wrequest)
        print("{}".format(res.kid))

def decrypt(in_f, out_f, kid, **kwargs):
    _validate_cipher_param(in_f=in_f, is_encrypt=False, **kwargs)

    if kwargs['iv'] is not None:
        kwargs['iv'] = to_byte_array(hex_decode(kwargs['iv']))
    if kwargs['ad'] is not None:
        kwargs['ad'] = to_byte_array(hex_decode(kwargs['ad']))
    if kwargs['tag'] is not None:
        kwargs['tag'] = to_byte_array(hex_decode(read_binary(kwargs['tag'])))
    if kwargs['transient_key'] is not None:
        kwargs['key'] = sdkms.v1.SobjectDescriptor(transient_key=kwargs['transient_key'])
    elif kwargs['name'] is not None:
        kwargs['key'] = sdkms.v1.SobjectDescriptor(name=kwargs['name'])
    else:
        kwargs['key'] = sdkms.v1.SobjectDescriptor(kid=kid)
    del kwargs['name']
    del kwargs['transient_key']
    output = open(out_f, 'wb')

    if os.path.getsize(in_f) < CHUNK_SIZE:
        with open(in_f, "rb") as f:
            kwargs['cipher'] = to_byte_array(f.read())

        request = DecryptRequestEx(**kwargs)
        response = make_request(RequiredAuth.EITHER, EncryptionAndDecryptionApi, EncryptionAndDecryptionApi.decrypt_ex,
                                request)
    else:
        # Go for multi part decryption
        if kwargs['alg'].upper() == 'RSA':
            raise ClientException("Input data is too big to decrypt with RSA algorithm")
        if kwargs['mode'].upper() in ('GCM', 'CCM'):
            # SDKMS documentation not have field to provide tag for GCM mode in-case of multi-part
            raise ClientException("Multipart decryption is not supported for mode({})".format(kwargs['mode']))
        # remove un-wanted argument
        del kwargs['ad']
        del kwargs['tag']

        state = _cipher_init(request_of=DecryptInitRequestEx, method=EncryptionAndDecryptionApi.decrypt_init_ex,
                             **kwargs).state

        with open(in_f, "rb") as f:
            while True:
                data = to_byte_array(f.read(CHUNK_SIZE))
                if not data:
                    break
                response = _cipher_update(request_of=DecryptUpdateRequestEx, method=EncryptionAndDecryptionApi.decrypt_update_ex,
                                          key=kwargs['key'], cipher=data, state=state)
                output.write(response.plain)
                state = response.state

        response = _cipher_final(request_of=DecryptFinalRequestEx, method=EncryptionAndDecryptionApi.decrypt_final_ex,
                                 key=kwargs['key'], state=state)
    output.write(response.plain)
    output.close()

def message_digest(in_f, **kwargs):
    kwargs['data'] = to_byte_array(_read_binary(in_f))
    request = sdkms.v1.DigestRequest(**kwargs)
    response = make_request(RequiredAuth.EITHER, DigestApi, DigestApi.compute_digest, request)
    print("{}".format(hex_encode(response.digest)))

def hmac_digest(in_f, kid, **kwargs):
    kwargs['data'] = to_byte_array(_read_binary(in_f))
    request = sdkms.v1.MacGenerateRequest(**kwargs)
    response = make_request(RequiredAuth.EITHER, DigestApi, DigestApi.compute_mac, kid, request)
    print("{}".format(hex_encode(response.digest)))

def hmac_digest_verify(in_f, kid, **kwargs):
    kwargs['data'] = to_byte_array(_read_binary(in_f))
    kwargs['digest'] = to_byte_array(hex_decode(kwargs['digest']))

    request = sdkms.v1.MacVerifyRequest(**kwargs)
    response = make_request(RequiredAuth.EITHER, DigestApi, DigestApi.verify_mac, kid, request)
    if response.result is not True:
        raise ClientException("Digest verification fail")

def agree_key(private_key,public_key,**kwargs):
    kwargs['mechanism'] = "diffie_hellman"
    kwargs['private_key'] = sdkms.v1.SobjectDescriptor(kid=private_key)
    kwargs['public_key'] = sdkms.v1.SobjectDescriptor(kid=public_key)
    request = sdkms.v1.AgreeKeyRequest(**kwargs)
    response = make_request(RequiredAuth.EITHER, SecurityObjectsApi, SecurityObjectsApi.agree_key, request)
    print("{}".format(response.kid))

def invoke_plugin(name, id, in_f, **kwargs):
    if name is None and id is None:
        raise ClientException('Name or UUID is required to invoke plugin')
    data = None
    if in_f is not None:
        data = _read_binary(in_f, mode='r')

    if name is not None:
        response = json_request('/sys/v1/plugins', exp_status=200, header=None, body=None, method='GET',
                            required_auth=RequiredAuth.EITHER)
        plugin_id = None
        for plugin in response:
            if plugin['name'] == name:
                plugin_id = plugin['plugin_id']
        if plugin_id is None:
            raise ClientException('Plugin not found with name {}'.format(name))

    if id is not None:
        plugin_id = id

    response = json_request('/sys/v1/plugins/'+plugin_id, exp_status=200, header=None, body=data, method='POST', required_auth=RequiredAuth.EITHER)
    _write_binary(json.dumps(response), kwargs['out'])


def delete_plugin(name, id, **kwargs):
    if name is None and id is None:
        raise ClientException('Name or UUID is required to delete plugin')

    if name is not None:
        response = json_request('/sys/v1/plugins', exp_status=200, header=None, body=None, method='GET',
                            required_auth=RequiredAuth.EITHER)
        plugin_id = None
        for plugin in response:
            if plugin['name'] == name:
                plugin_id = plugin['plugin_id']
        if plugin_id is None:
            raise ClientException('Plugin not found with name {}'.format(name))

    if id is not None:
        plugin_id = id

    response = json_request('/sys/v1/plugins/'+plugin_id, exp_status=204, header=None, body=None, method='DELETE', required_auth=RequiredAuth.EITHER)


def update_plugin(uuid, in_f, group_id, **kwargs):
    code = _read_binary(in_f).decode("utf-8")
    all_groups = get_groups()
    all_group_id = [o.group_id for o in all_groups]
    if kwargs['name'] is None :
        response = json_request('/sys/v1/plugins/'+uuid, exp_status=200, header=None, body= None, method='GET', required_auth=RequiredAuth.EITHER)
        kwargs['name'] = response['name']
    # TODO : Move to using python sdk, depends on fix of RC-92
    #source = sdkms.v1.PluginSource(language = "Lua",code = data)
    #request = sdkms.v1.PluginRequest(name = "Test",source = source,add_groups = [],default_group = all_groups[0].group_id)
    #response = make_request(RequiredAuth.USER, PluginsApi, PluginsApi.create_plugin, uuid, request)
    source = {}
    source['language'] = "lua"
    source['code'] = code
    kwargs['source'] = source
    kwargs['add_groups'] = []
    if group_id is None :
        kwargs['default_group'] = all_groups[0].group_id
    else :
        kwargs['default_group'] = group_id
    kwargs['plugin-id'] = uuid
    response = json_request('/sys/v1/plugins/'+uuid, exp_status=200, header=None, body=json.dumps(kwargs), method='PATCH', required_auth=RequiredAuth.EITHER)
    print("{}".format(response['plugin_id']))


def create_plugin(name, in_f, group_id, **kwargs):
    code = _read_binary(in_f).decode("utf-8")
    all_groups = get_groups()
    all_group_id = [o.group_id for o in all_groups]
    # TODO : Move to using python sdk, depends on fix of RC-95
    #source = sdkms.v1.PluginSource(language = "lua",code = data)
    #request = sdkms.v1.PluginRequest(name = name,source = source,add_groups = all_group_id,default_group = all_groups[0].group_id,plugin_type = "standard")
    #response = make_request(RequiredAuth.USER, PluginsApi, PluginsApi.create_plugin,request)
    source = {}
    source['language'] = "lua"
    source['code'] = code
    kwargs['name'] = name
    kwargs['source'] = source
    kwargs['add_groups'] = all_group_id
    if group_id is None :
        kwargs['default_group'] = all_groups[0].group_id
    else :
        kwargs['default_group'] = group_id
    kwargs['plugin_type'] = "standard"
    response = json_request('/sys/v1/plugins', exp_status=201, header=None, body=json.dumps(kwargs), method='POST', required_auth=RequiredAuth.EITHER)
    print("{}".format(response['plugin_id']))


def get_accounts():
    return make_request(RequiredAuth.USER, UsersApi, UsersApi.get_user_account)

def get_account_details(account_id):
    return make_request(RequiredAuth.USER, AccountsApi, AccountsApi.get_account, account_id)


def get_acccounts_list(detail=False):
    acc_ls = []
    accounts = get_accounts()
    for acct in sorted(accounts.keys()):
        detail_obj = get_account_details(acct)
        if detail:
            acc_ls.append(json.dumps(detail_obj, default=serialize))
        else:
            acc_ls.append('{} {} {} {}'.format(acct, detail_obj.name, detail_obj.auth_type, detail_obj.state.name))
    return acc_ls

def show_version(**kwargs):
    res = make_request(RequiredAuth.NONE, AuthenticationApi, AuthenticationApi.get_server_version , kwargs)
    print("API Version : {} \nServer Mode : {} \nVersion     : {} \nFIPS Level: {}".format(res.api_version,res.server_mode,res.version,res.fips_level))


def show_health(**kwargs):
    res = make_request(RequiredAuth.NONE, AuthenticationApi, AuthenticationApi.check_health_with_http_info , kwargs)
    if res[1] != 204:
        print("Server is Down")
    print("Server is Healthy")

def list_users():
    users = make_request(RequiredAuth.USER,UsersApi,UsersApi.get_users)
    for user in users:
        sys.stdout.write("{} ".format(user.user_id))
        sys.stdout.write("{} ".format(user.user_email))
        # Add new line
        print("")

def list_accounts(detail=False):
    accounts = get_acccounts_list(detail)
    for account in accounts:
        print('{}'.format(account))

def select_account_with_id(**kwargs):
    if not kwargs['account_id']:
        raise ClientException("--account-id is required argument for select-account command")

    request = sdkms.v1.SelectAccountRequest(kwargs['account_id'])
    make_request(RequiredAuth.USER, AuthenticationApi, AuthenticationApi.select_account, request)

def select_account(**kwargs):
    accounts = get_accounts()
    if len(accounts.keys()) == 1:
        account_id = list(accounts.keys())[0]
    else:
        if not kwargs['account_name']:
            err = []
            err.append("You have more than one account available. Please select the account name or id")
            err.append("with the --account-name option")
            err.extend(get_acccounts_list())
            raise ClientException(err)

        account_id = None
        for acct in accounts.keys():
            details = get_account_details(acct)
            if details.name == kwargs['account_name'] or details.acct_id == kwargs['account_name']:
                account_id = acct
                break
        if account_id is None:
            errs = []
            errs.append("Your selected account '{}' is not associated with this user account".format(kwargs['account_name']))
            errs.append("Available accounts:")
            errs.extend(get_acccounts_list())
            raise ClientException(errs)

    request = sdkms.v1.SelectAccountRequest(account_id)
    make_request(RequiredAuth.USER, AuthenticationApi, AuthenticationApi.select_account, request)


def get_apps():
    return make_request(RequiredAuth.USER, AppsApi, AppsApi.get_apps)


def get_apps_with_offset(offset, limit):
    return make_request(RequiredAuth.USER, AppsApi, AppsApi.get_apps, None, None, None, limit, offset)


def list_apps(offset, limit, **kwargs):
    apps = get_apps_with_offset(offset, limit)
    detail = kwargs['detail']
    for app in apps:
        if detail:
            print(json.dumps(app, default=serialize))
        else:
            sys.stdout.write("{} ".format(app.app_id))
            sys.stdout.write("\"{}\"".format(app.name))
            # Add new line at the end
            print ("")


def create_app(**kwargs):
    if kwargs['groups']:
        groups_arg = kwargs['groups'].split(',')
    del kwargs['groups']
    all_groups = get_groups()
    kwargs['add_groups'] = []
    # setup default group
    found_group = False
    for group in all_groups:
        if group.name == kwargs['default_group'] or group.group_id == kwargs['default_group']:
            kwargs['default_group'] = group.group_id
            found_group = True
            break
    if not found_group:
        raise ClientException("Default group {} not found".format(kwargs['default_group']))

    for requested_group in groups_arg:
        found_group = False
        for group in all_groups:
            if group.name == requested_group or group.group_id == requested_group:
                kwargs['add_groups'].append(group.group_id)
                found_group = True
                break
        if not found_group:
            raise ClientException('Unable to fine group with name or id {}'.format(requested_group))

    kwargs['app_type'] = kwargs['type']
    del kwargs['type']
    request = AppRequest(**kwargs)
    response = make_request(RequiredAuth.USER, AppsApi, AppsApi.create_app, request)
    print(response.app_id)


def get_app_id_for_request(**kwargs):
    if (kwargs['name'] and kwargs['app_id']) or (not kwargs['name'] and not kwargs['app_id']):
        raise ClientException("Please select the Application with --name or --app-id (but not both)")

    app_id = None
    if kwargs['name']:
        apps = get_apps()
        for app in apps:
            if app.name == kwargs['name']:
                app_id = app.app_id
                break
        if app_id is None:
            raise ClientException("No application found with name '{}'".format(kwargs['name']))
    else:
        app_id = kwargs['app_id']
    return app_id


def get_app_api_key(**kwargs):
    app_id = get_app_id_for_request(**kwargs)
    res = make_request(RequiredAuth.USER, AppsApi, AppsApi.get_credential, app_id)
    if res.app_id != app_id:
        raise ClientException("Error: returned credential had incorrect app_id", verbose=True)
    if res.credential.secret is None:
        if res.credential.certificate:
            raise ClientException("Application {} uses certificate-based credentials".format(app_id))
        else:
            raise ClientException("Application {} had no valid credentials".format(app_id), verbose=True)
    api_key = '{}:{}'.format(app_id, res.credential.secret)
    api_key_b64 = b64_encode(api_key)

    print('{}'.format(api_key_b64))


def regenerate_app_api_key(**kwargs):
    app_id = get_app_id_for_request(**kwargs)
    if "secret_size" in kwargs and kwargs["secret_size"]:
        secret_size = kwargs["secret_size"]
    else:
        secret_size = 64
    request = AppResetSecretRequest(secret_size=secret_size)
    make_request(RequiredAuth.USER, AppsApi, AppsApi.regenerate_api_key, app_id, request)
    get_app_api_key(**kwargs)


def delete_app(**kwargs):
    if not kwargs['name'] and not kwargs['app_id']:
        raise ClientException("Either --name or --app_id is a required argument for delete-app")
    app_id = None
    if kwargs['name'] is not None:
        apps = get_apps()
        for app in apps:
            if app.name == kwargs['name']:
                app_id = app.app_id
                break
        if app_id is None:
            raise ClientException("No app with name '{}'".format(kwargs['name']))

    if kwargs['app_id'] is not None:
        if kwargs['name'] is not None:
            if app_id != kwargs['app_id']:
                raise ClientException(
                    "Application with name '{}' has group id {}".format(kwargs['name'], kwargs['group_id']) +
                    "When both --name and --group-id are provided, the deleted Application must match " +
                    "both name and app id. Perhaps you meant to provide just --name or just --app-id?")
        else:
            app_id = kwargs['app_id']

    make_request(RequiredAuth.USER, AppsApi, AppsApi.delete_app, app_id)


def get_groups():
    return make_request(RequiredAuth.USER, GroupsApi, GroupsApi.get_groups)

def list_groups(**kwargs):
    groups = get_groups()
    for group in groups:
        sys.stdout.write("{} ".format(group.group_id))
        sys.stdout.write("\"{}\" ".format(group.name))
        sys.stdout.write("{} ".format(group.acct_id))
        # Add new line
        print ("")


def create_group(**kwargs):
    if kwargs['add_quorum_policy']:
        del kwargs['add_quorum_policy']
        approval_policy = {}
        quorum = {}
        if not kwargs['n']:
            raise ClientException("n is required to add quorum policy")
        else:
            quorum['n'] = kwargs['n']
        quorum['require_2fa']=kwargs['require_2fa']
        quorum['require_password']=kwargs['require_password']
        members = []
        if kwargs['users']:
            users_arg = kwargs['users'].split(',')
        else:
            raise ClientException("user-id is required to add quorum policy")
        del kwargs['users']
        all_users = make_request(RequiredAuth.USER, UsersApi, UsersApi.get_users)

        for requested_user in users_arg:
            found_user = False
            for user in all_users:
                if user.user_id == requested_user:
                    users = {"user": user.user_id}
                    members.append(users)
                    found_user = True
                    break
            if not found_user:
                raise ClientException('Unable to find user with id {}'.format(requested_user))

        quorum['members'] = members
        approval_policy['quorum'] = quorum
        kwargs['approval_policy'] = approval_policy

    response = make_request(RequiredAuth.USER, GroupsApi, GroupsApi.create_group, kwargs)
    print(response.group_id)

def update_group(**kwargs):
    if not kwargs['name'] and not kwargs['group_id']:
        raise ClientException("Either --name or --group-id is a required argument for update-group")
    group_id=None
    if kwargs['name'] is not None:
        groups = get_groups()
        for group in groups:
            if group.name == kwargs['name']:
                group_id = group.group_id
                break
        if group_id is None:
            raise ClientException("No group with name '{}'".format(kwargs['name']))

    if kwargs['group_id'] is not None:
        if kwargs['name'] is not None:
            if group_id != kwargs['group_id']:
                raise ClientException(
                    "Group with name '{}' has group id {}.".format(kwargs['name'], kwargs['group_id']) +
                    "When both --name and --group-id are provided, the updated group must match " +
                    "both name and group id. Perhaps you meant to provide just --name or just --group-id?")
        else:
            group_id = kwargs['group_id']
            del kwargs['group_id']

    if kwargs['description'] is None:
        del kwargs['description']

    if kwargs['add_quorum_policy']:
        del kwargs['add_quorum_policy']
        approval_policy = {}
        quorum = {}
        if not kwargs['n']:
            raise ClientException("n is required to add quorum policy")
        else:
            quorum['n'] = kwargs['n']
        quorum['require_2fa']=kwargs['require_2fa']
        quorum['require_password']=kwargs['require_password']
        members = []
        if kwargs['users']:
            users_arg = kwargs['users'].split(',')
        else:
            raise ClientException("user-id is required to add quorum policy")
        del kwargs['users']
        all_users = make_request(RequiredAuth.USER, UsersApi, UsersApi.get_users)

        for requested_user in users_arg:
            found_user = False
            for user in all_users:
                if user.user_id == requested_user:
                    users = {"user": user.user_id}
                    members.append(users)
                    found_user = True
                    break
            if not found_user:
                raise ClientException('Unable to find user with id {}'.format(requested_user))

        quorum['members'] = members
        approval_policy['quorum'] = quorum
        kwargs['approval_policy'] = approval_policy

    response = make_request(RequiredAuth.USER, GroupsApi, GroupsApi.update_group, group_id, kwargs)
    print(response.group_id)

def delete_group(**kwargs):
    if not kwargs['name'] and not kwargs['group_id']:
        raise ClientException("Either --name or --group-id is a required argument for delete-group")
    gid = None
    if kwargs['name'] is not None:
        groups = get_groups()
        for group in groups:
            if group.name == kwargs['name']:
                gid = group.group_id
                break
        if gid is None:
            raise ClientException("No group with name '{}'".format(kwargs['name']))

    if kwargs['group_id'] is not None:
        if kwargs['name'] is not None:
            if gid != kwargs['group_id']:
                raise ClientException(
                    "Group with name '{}' has group id {}.".format(kwargs['name'], kwargs['group_id']) +
                    "When both --name and --group-id are provided, the deleted group must match " +
                    "both name and group id. Perhaps you meant to provide just --name or just --group-id?")
        else:
            gid = kwargs['group_id']

    make_request(RequiredAuth.USER, GroupsApi, GroupsApi.delete_group, gid)

def task_result(request_id, **kwargs) :
    status_response = json_request('/sys/v1/approval_requests/' + request_id, exp_status=200, header=None, body=None, method='GET', required_auth=RequiredAuth.EITHER)
    if status_response['status'] == "APPROVED":
        response = json_request('/sys/v1/approval_requests/' + request_id + '/result', exp_status=200, header=None, body=None, method='POST', required_auth=RequiredAuth.EITHER)
        print(json.dumps(response))
        if 'body' in response and response['body'] is not None and 'out' in kwargs and kwargs['out'] is not None:
            body = response['body']
            if 'wrapped_key' in body and body['wrapped_key'] is not None: 
                _write_binary(to_byte_array(b64_decode(body['wrapped_key'])), kwargs['out'])
            if 'signature' in body and body['signature'] is not None:
                _write_binary(to_byte_array(b64_decode(body['signature'])), kwargs['out'])
            if 'value' in body and body['value'] is not None: 
                _write_binary(to_byte_array(b64_decode(body['value'])), kwargs['out'])
            if 'iv' in body and body.iv is not None:
                print("iv: {}".format(hex_encode(b64_decode(body['iv']))))
                _write_binary(hex_encode(b64_decode(body['iv'])), "{}.iv".format(out))
            if 'tag' in body and body['tag'] is not None:
                print("tag: {}".format(hex_encode(b64_decode(body['tag']))))
                _write_binary(hex_encode(b64_decode(body['tag'])), "{}.tag".format(out))
    else:
        print(json.dumps(status_response))

#Read the file passed as parameter as a properties file.
def load_properties(filepath, sep='=', comment_char='#'):
    props = {}
    try:
        with open(filepath, "rt") as f:
            for line in f:
                l = line.strip()
                if l and not l.startswith(comment_char):
                    key_value = l.split(sep)
                    key = key_value[0].strip()
                    value = sep.join(key_value[1:]).strip().strip('"')
                    props[key] = value
    except Exception:
        pass
    return props

def _add_version(parser):
    """
    Add version to sub-command
    :param parser:
    :return: NIL
    """
    parser.add_argument('--version', action='version', version='{}'.format(VERSION), help=argparse.SUPPRESS)

def main():
    fetch_version()

    help = '''
sdkms-client.py {}

Perform operations on a Fortanix SDKMS server.

The following environment variables may be set to control application behavior:

FORTANIX_API_ENDPOINT: The Fortanix SDKMS server instance to talk to. Default
                       value is https://sdkms.fortanix.com

FORTANIX_API_KEY*: The API key of the application to use for application-
                   authenticated operations.

Variables marked with * contain security-sensitive information and are intended
for use in testing and development. They should not normally be used in
secure deployments.
'''.format(VERSION)

    parser = argparse.ArgumentParser(
        description=help, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--version', action='version', version='{}'.format(VERSION))
    parser.add_argument("--api-endpoint", action="store",
                                  default=os.getenv("FORTANIX_API_ENDPOINT", os.getenv("SDKMS_API_ENDPOINT", DEFAULT_API_ENDPOINT)),
                                  help="SDKMS API endpoint to connect to")
    parser.add_argument("--no-verify-ssl", action="store_true", default=False, help="Don't verify server certificate")
    parser.add_argument("--ssl-ca-cert", action="store", help="Path to CA certificate for SSL verification")
    parser.add_argument("--debug-http", action="store_true", help="Turn on verbose HTTP request debugging")
    parser.add_argument("--debug-errors", action="store_true", help="Turn on more verbose error output")
    parser.add_argument("--prefer-user-auth", action="store_const", const=RequiredAuth.USER, dest='preferred_auth',
                        help="Prefer using user authentication for APIs that accept both")
    parser.add_argument("--prefer-app-auth", action="store_const", const=RequiredAuth.APP, dest='preferred_auth',
                        help="Prefer using app authentication for APIs that accept both")
    parser.add_argument("--proxy", action="store", help="URL of the proxy to be used")

    subparsers = parser.add_subparsers(help="sub-command help", dest="command")
    subparsers.required = True

    # app-login parser
    parser_login_app = subparsers.add_parser("app-login", help="Log in to SDKMS with an application API key " +
                                                               "for performing crypto operations and key management",
                                             formatter_class=argparse.RawDescriptionHelpFormatter,
                                             epilog=textwrap.dedent('''\
                                                     Output:
                                                         No output.

                                                     Exit Status:
                                                       0 on success and 1 on error. Error message is printed on stderr
                                                     ''')
                                             )
    _add_version(parser_login_app)
    parser_login_app.add_argument("--api-key", action="store",
                                  default=os.getenv("FORTANIX_API_KEY", os.getenv("SDKMS_API_KEY", None)),
                                  help="API key to use to log in")
    parser_login_app.add_argument("--api-endpoint", action="store",
                        default=os.getenv("FORTANIX_API_ENDPOINT",os.getenv("SDKMS_API_ENDPOINT", DEFAULT_API_ENDPOINT)),
                        help="SDKMS API endpoint to connect to")
    parser_login_app.add_argument("--timeout", action="store", help="timeout for app login in seconds")

    parser_login_app.set_defaults(func=app_login)

    parser_login_user = subparsers.add_parser("user-login", help="Log in to SDKMS with a username and password " +
                                                                 "for performing crypto operations and key management")
    _add_version(parser_login_user)
    parser_login_user.add_argument("--api-endpoint", action="store",
                                             default=os.getenv("FORTANIX_API_ENDPOINT", os.getenv("SDKMS_API_ENDPOINT", DEFAULT_API_ENDPOINT)),
                                             help="SDKMS API endpoint to connect to")
    parser_login_user.add_argument("--username", help="SDKMS username to log in with")
    parser_login_user.add_argument("--account-name",
                                   help="Account name or account UUID to use for user actions (only necessary if the user has more than one account)")
    parser_login_user.add_argument("--password", help=argparse.SUPPRESS)

    parser_login_user.set_defaults(func=user_login)

    parser_logout_app = subparsers.add_parser("app-logout", help="Log out of application credentials",
                                              formatter_class=argparse.RawDescriptionHelpFormatter,
                                              epilog=textwrap.dedent('''\
                                                      Output:
                                                          No output.

                                                      Exit Status:
                                                        0 on success and 1 on error. Error message is printed on stderr
                                                      ''')
                                              )
    parser_logout_app.set_defaults(func=app_logout_cmd)

    parser_logout_user = subparsers.add_parser("user-logout", help="Log out of user credentials",
                                               formatter_class=argparse.RawDescriptionHelpFormatter,
                                               epilog=textwrap.dedent('''\
                                                       Output:
                                                           No output.

                                                       Exit Status:
                                                         0 on success and 1 on error. Error message is printed on stderr
                                                       ''')
                                               )
    parser_ldap_auth = subparsers.add_parser("ldap-auth", help="Log in to SDKMS with a useremail and password ")
    _add_version(parser_ldap_auth)
    parser_ldap_auth.add_argument("--user-email", help="User email to login")
    parser_ldap_auth.add_argument("--email",help="User email to login")
    parser_ldap_auth.add_argument("--password", help= argparse.SUPPRESS)
    parser_ldap_auth.add_argument("--account-name",
                                   help="Account name or account UUID to use for user actions (only necessary if the user has more than one account)")
    parser_ldap_auth.add_argument("--method",help="Method of authentication:ldap-basic-auth")
    parser_ldap_auth.add_argument("--idp-id",required=False)
    parser_ldap_auth.set_defaults(func=ldap_auth)

    parser_select_account = subparsers.add_parser("select-account", help="switch to another account")
    _add_version(parser_select_account)
    parser_select_account.add_argument("--account-id", help="account id of an account", required=True)
    parser_select_account.set_defaults(func=select_account_with_id)

    _add_version(parser_logout_user)
    parser_logout_user.set_defaults(func=user_logout_cmd)

    parser_logout = subparsers.add_parser("logout", help="Log out of both application and user credentials")
    _add_version(parser_logout)
    parser_logout.set_defaults(func=logout_cmd)

    parser_audit_log = subparsers.add_parser("audit-log", help="download audit log",
                                             formatter_class=argparse.RawDescriptionHelpFormatter,
                                             epilog=textwrap.dedent('''\
                                                       Output:
                                                            Write audit-log data in output file
                                                       Exit Status:
                                                            Zero on success and 1 on error. Error message is printed on stderr
                                                   '''))
    _add_version(parser_audit_log)
    parser_audit_log.add_argument("--start-time", help="start time in yyyy-mm-dd format")
    parser_audit_log.add_argument("--end-time", help="end time in yyyy-mm-dd format")
    parser_audit_log.add_argument("--limit", default=25, help="Maximum number of audit logs to return. If not provided, the limit is 25")
    parser_audit_log.set_defaults(func=audit_log)

    parser_rotate = subparsers.add_parser("rotate-key", help="rotate a key",
                                          formatter_class=argparse.RawDescriptionHelpFormatter,
                                          epilog=textwrap.dedent('''\
                                            Output:
                                                Key UUID on console.

                                                Exit Status:
                                                    Zero on success and 1 on error. Error message is printed on stderr.
                                            '''))
    _add_version(parser_rotate)
    parser_rotate.add_argument("--name", help="Name of key", required=True)
    parser_rotate.set_defaults(func=rotate_key)

    parser_create = subparsers.add_parser("create-key", help="create a key",
                                          formatter_class=argparse.RawDescriptionHelpFormatter,
                                          epilog=textwrap.dedent('''\
                                                  Output:
                                                    Key UUID on console.

                                                  Exit Status:
                                                    Zero on success and 1 on error. Error message is printed on stderr.
                                                   '''))
    _add_version(parser_create)
    parser_create.add_argument("--obj-type", help="Type of key: AES, DES, DES3, EC or RSA", required=True)
    parser_create.add_argument("--name", help="Name of key", required=True)
    parser_create.add_argument("--key-size", help="Length of key in bits", type=int)
    parser_create.add_argument("--pub-exponent", help="Override RSA public exponent", type=int)
    parser_create.add_argument("--ec-name", help="Elliptic curve name. Required for EC object type"
                                " Supported curve are SecP192K1, SecP224K1, SecP256K1, NistP192, NistP224, NistP256, NistP384, NistP521")
    parser_create.add_argument("--description", help="Description of key", default="Created by sdkms-cli {}".format(VERSION))
    parser_create.add_argument("--group-id", help="Security Group for this key."
                                                  "Group id is mandatory if you logged in as user")
    parser_create.add_argument("--exportable", help="Allow key to be exported from SDKMS by wrapping",
                               action="store_true")
    parser_create.add_argument("-f", "--force", help="Force key to be exportable",
                               action="store_true")

    parser_create.add_argument("--transient", help="Allow key to be exported from SDKMS by wrapping",
                               action="store_true")
    parser_create.add_argument("--key-ops", help="Allowed key operations. Comma separated list of operations")

    parser_create.add_argument("--custom-metadata", help="""
A JSON object encoding custom metadata for the unwrapped Security Object
as "key" : "value" pairs. Values must be strings (and not integers,
booleans or objects).
""")
    parser_create.set_defaults(func=create_key)

    parser_persist = subparsers.add_parser("persist-key", help="persist a transient key",
                                          formatter_class=argparse.RawDescriptionHelpFormatter,
                                          epilog=textwrap.dedent('''\
                                                  Output:
                                                    Key UUID on console.
                                                  Exit Status:
                                                    Zero on success and 1 on error. Error message is printed on stderr.
                                                   '''))
    _add_version(parser_persist)
    parser_persist.add_argument("--name", help="Name of newly created persistent key", required=True)
    parser_persist.add_argument("--description", help="Description of key", default="Created by sdkms-cli {}".format(VERSION))
    parser_persist.add_argument("--group-id", help="Security Group for this key."
                                                  "Group id is mandatory if you logged in as user")
    parser_persist.add_argument("--transient-key", help="Transient key material", required=True)
    parser_persist.add_argument("--key-ops", help="Allowed key operations. Comma seperated list of operations")
    parser_persist.add_argument("--custom-metadata", help="""
                                A JSON object encoding custom metadata for the unwrapped Security Object
                                as "key" : "value" pairs. Values must be strings (and not integers,
                                booleans or objects).
                                """)
    parser_persist.set_defaults(func=persist_key)

    parser_import_key = subparsers.add_parser("import-key", help="Import a key into SDKMS",
                                              formatter_class=argparse.RawDescriptionHelpFormatter,
                                              epilog=textwrap.dedent('''\
                                                  Output:
                                                    Key UUID of imported key on console.

                                                  Exit Status:
                                                    Zero on success and 1 on error. Error message is printed on stderr.
                                                       ''')
                                              )
    _add_version(parser_import_key)
    parser_import_key.add_argument("--in", help="Input key file path", required=True, dest="key_file")
    parser_import_key.add_argument("--obj-type", help="Type of key: AES, DES, DES3, EC or RSA."
                                                      "Default format for AES, DES and DES3 are HEX."
                                                      "Default format for EC and RSA are PEM."
                                                      "If key is in DER format then specify using flag --der", required=True)
    parser_import_key.add_argument("--group-id", help="Security Group for this key")
    parser_import_key.add_argument("--name", help="Name of key", required=True)
    parser_import_key.add_argument("--description", help="Description of key", default="Created by sdkms-client")
    parser_import_key.add_argument("--ec-curve", help="Elliptic curve name. Required for --obj-type EC"
                                " Supported curve are SecP192K1, SecP224K1, SecP256K1, NistP192, NistP224, NistP256, NistP384, NistP521")
    parser_import_key.add_argument("--der", "--binary", help="Input key file in binary format",
                                   action='store_true')
    parser_import_key.add_argument("--exportable", help="Allow key to be exported from SDKMS by wrapping",
                                   action='store_true')
    parser_import_key.add_argument("-f", "--force", help="Force key to be exportable",
                               action="store_true")
    parser_import_key.add_argument("--key-ops", help="Allowed key operations. Comma separated list of operations")
    parser_import_key.add_argument("--custom-metadata", help="""
A JSON object encoding custom metadata for the unwrapped Security Object
as "key" : "value" pairs. Values must be strings (and not integers,
booleans or objects).
""")
    parser_import_key.set_defaults(func=import_key)

    parser_import_cert = subparsers.add_parser("import-cert", help="import a certificate",
                                               formatter_class=argparse.RawDescriptionHelpFormatter,
                                               epilog=textwrap.dedent('''\
                                                  Output:
                                                    Key UUID of imported certificate on console.

                                                  Exit Status:
                                                    Zero on success and 1 on error. Error message is printed on stderr.
                                                        ''')
                                               )

    _add_version(parser_import_cert)
    parser_import_cert.add_argument("--in", help="Input certificate file path", required=True, dest="cert_file")
    parser_import_cert.add_argument("--name", help="Name of certificate", required=True)
    parser_import_cert.add_argument("--description", help="Description of certificate",
                                    default="Created by sdkms-client")
    parser_import_cert.add_argument("--der", help="Input cert in binary format",
                                   action='store_true')
    parser_import_cert.set_defaults(func=import_cert)
    parser_import_cert.add_argument("--custom_metadata", help="""
                                        A JSON object encoding custom metadata for the unwrapped Security Object
                                        as "key" : "value" pairs. Values must be strings (and not integers,
                                        booleans or objects).
                                    """)
    # Parser to support secret import
    parser_import_secret = subparsers.add_parser("import-secret", help="Import a secret into SDKMS",
                                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                                 epilog=textwrap.dedent('''\
                                                  Output:
                                                    Key UUID of imported secret on console.

                                                  Exit Status:
                                                    Zero on success and 1 on error. Error message is printed on stderr.
                                                          ''')
                                                 )

    _add_version(parser_import_secret)
    parser_import_secret.add_argument("--in", help="Input secret file path", required=True, dest="secret_file")
    parser_import_secret.add_argument("--name", help="Name of secret key", required=True)
    parser_import_secret.add_argument("--group-id", help="Name of secret")
    parser_import_secret.add_argument("--obj-type", help="Type of key: Secret, OPAQUE")
    parser_import_secret.add_argument("--description", help="Description of certificate", default="Created by sdkms-client")
    parser_import_secret.add_argument("--custom_metadata", help="""
    A JSON object encoding custom metadata for the imported secret
    as "key" : "value" pairs. Values must be strings (and not integers,
    booleans or objects).
    """)
    parser_import_secret.set_defaults(func=import_secret)

    # Update metadata for security object
    parser_update = subparsers.add_parser("update-object", help="Update metadata of a security object",
                                          formatter_class=argparse.RawDescriptionHelpFormatter,
                                          epilog=textwrap.dedent('''\
                                                  Output:
                                                    Key UUID on console.

                                                  Exit Status:
                                                    Zero on success and 1 on error. Error message is printed on stderr.
                                                   '''))
    _add_version(parser_update)
    parser_update.add_argument("--name", help="Name of security object to be updated")
    parser_update.add_argument("--kid", help="UUID of security object to be updated")
    parser_update.add_argument("--description", help="The updated description of security object to be set")
    parser_update.add_argument("--key-ops", help="Updated list of allowed key operations. Comma seperated list of operations")
    parser_update.add_argument("--disable-export", help="Revoke EXPORT key operation for security object", action='store_true')
    parser_update.add_argument("--quorum", action="store_true", default=False, help="Send an quorum approval request for the update request", required=False)
    parser_update.add_argument("--custom-metadata", help="""
The updated JSON object encoding custom metadata for the unwrapped Security Object
as "key" : "value" pairs. Values must be strings (and not integers,
booleans or objects).
""")
    parser_update.set_defaults(func=update_object)

    # Parser for delete-key operation
    parser_delete = subparsers.add_parser("delete-key", help="Delete a key",
                                          formatter_class=argparse.RawDescriptionHelpFormatter,
                                          epilog=textwrap.dedent('''\
                                                  Output:
                                                    No output

                                                  Exit Status:
                                                    Zero on success and 1 on error. Error message is printed on stderr
                                                   ''')
                                          )
    _add_version(parser_delete)
    parser_delete.add_argument("--kid", help="UUID of key", required=True)
    parser_delete.set_defaults(func=delete)

    parser_list_keys = subparsers.add_parser("list-keys", help="List keys")
    parser_list_keys.add_argument("--name", help="Name of the object to list")
    parser_list_keys.add_argument("--offset", default=0, help="Number of security objects to skip")
    parser_list_keys.add_argument("--limit", default=100, help="Maximum number of security objects to return. If not provided, the limit is 100")
    parser_list_keys.set_defaults(func=list_keys)

    parser_list_objects = subparsers.add_parser("list-objects",
                                                help="List objects (keys, certificates, and other opaque objects)",
                                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                                epilog=textwrap.dedent('''\
                                                        Output:
                                                          Five column output:
                                                          <kid> <name> <description> <object-type> <object-size>

                                                        Exit Status:
                                                          Zero on success and 1 on error. Error message is printed on stderr
                                                         ''')
                                                )
    _add_version(parser_list_objects)
    parser_list_objects.add_argument("--name", help="Name of the object to list")
    parser_list_objects.add_argument("--offset", default=0, help="Number of security objects to skip. Default is zero")
    parser_list_objects.add_argument("--limit", default=100, help="Maximum number of security objects to return. If not provided, the limit is 100")
    parser_list_objects.set_defaults(func=list_objects)

    parser_show_object = subparsers.add_parser("show-sobject", help="Show details about a Security Object",
                                               formatter_class=argparse.RawDescriptionHelpFormatter,
                                               epilog=textwrap.dedent('''\
                                                       Output:
                                                         Seven property, one property per line.
                                                           kid: <value>
                                                           name: <value>
                                                           description: <value>
                                                           obj_type: <value>
                                                           key_size: <value>
                                                           elliptic_curve: <value>
                                                           origin: <value>
                                                       Exit Status:
                                                         Zero on success and 1 on error. Error message is printed on stderr
                                                        ''')
                                               )
    _add_version(parser_show_object)
    parser_show_object.add_argument("--kid", help="UUID of the Security Object to show")
    parser_show_object.add_argument("--name", help="Name of the Security Object to show")
    parser_show_object.set_defaults(func=show_sobject)

    parser_export_object = subparsers.add_parser("export-object",
                                                 help="Show value of a Security Object. This works only if the object "
                                                      "is marked exportable.",
                                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                                 epilog=textwrap.dedent('''\
                                                         Output:
                                                           key/secret material on console
                                                         Exit Status:
                                                           Zero on success and 1 on error. Error message is printed on stderr
                                                          ''')
                                                 )
    _add_version(parser_export_object)
    parser_export_object.add_argument("--kid", help="UUID of the Security Object")
    parser_export_object.add_argument("--name", help="Name of the Security Object")
    parser_export_object.add_argument("--der", "--binary", help="export key in binary format", action='store_true')
    parser_export_object.add_argument("--quorum", action='store_true', default=False, help="Send a quorum approval request, instead of direct key material export", required=False)
    parser_export_object.set_defaults(func=export_object)

    parser_activate_object = subparsers.add_parser("activate-object",
                                                   help="Activate a Security Object. This works only if the object "
                                                        "is in Preactive state.",
                                                   formatter_class=argparse.RawDescriptionHelpFormatter,
                                                   epilog=textwrap.dedent('''\
                                                           Output:
                                                             No output
                                                           Exit Status:
                                                             Zero on success and 1 on error. Error message is printed on stderr
                                                            ''')
                                                   )
    _add_version(parser_activate_object)
    parser_activate_object.add_argument("--kid", help="UUID of the Security Object")
    parser_activate_object.add_argument("--name", help="Name of the Security Object")
    parser_activate_object.set_defaults(func=activate_object)

    parser_revoke_object = subparsers.add_parser("revoke-object",
                                                 help="Revoke a Security Object.",
                                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                                 epilog=textwrap.dedent('''\
                                                         Output:
                                                           No output
                                                         Exit Status:
                                                           Zero on success and 1 on error. Error message is printed on stderr
                                                          ''')
                                                 )
    _add_version(parser_revoke_object)
    parser_revoke_object.add_argument("--kid", help="UUID of the Security Object")
    parser_revoke_object.add_argument("--name", help="Name of the Security Object")
    parser_revoke_object.add_argument("--code", help="Revocation Reason. Supported codes are: "
                                      "Unspecified, KeyCompromise, CACompromise, AffiliationChanged, Superseded, "
                                      "CessationOfOperation, PrivilegeWithdrawn", required=True)
    parser_revoke_object.add_argument("--message", help="Optional message")
    parser_revoke_object.set_defaults(func=revoke_object)

    parser_encrypt = subparsers.add_parser("encrypt", help="Encrypt with key",
                                           formatter_class=argparse.RawDescriptionHelpFormatter,
                                           epilog=textwrap.dedent('''\
                                                   Output:
                                                     Write encrypted data in output file
                                                   Exit Status:
                                                     Zero on success and 1 on error. Error message is printed on stderr
                                                    ''')
                                           )
    _add_version(parser_encrypt)
    parser_encrypt.add_argument("--kid", help="UUID of key")
    parser_encrypt.add_argument("--name", help="Name of security object")
    parser_encrypt.add_argument("--alg", help="Encryption algorithm: AES, DES, or RSA", required=True)
    parser_encrypt.add_argument("--in", help="Input plain data file path", required=True, dest="in_f")
    parser_encrypt.add_argument("--out", help="Output cipher file path", required=True)
    parser_encrypt.add_argument("--mode", help="Encryption mode required for symmetric algorithms")
    parser_encrypt.add_argument("--iv", help="Initialization vector for symmetric algorithm, should be a hex string."
                                             " It is optional for ECB mode")
    parser_encrypt.add_argument("--ad", help="Authentication data for AES GCM mode, should be a hex string")
    parser_encrypt.add_argument("--tag-len", help="Length of tag for AES GCM mode", type=int)
    parser_encrypt.add_argument("--transient-key", help="transient key material")
    parser_encrypt.set_defaults(func=encrypt)

    # Multipart encryption and decryption
    parser_enc_init = subparsers.add_parser("encrypt-init", help="Multipart encryption initialization",
                                            formatter_class=argparse.RawDescriptionHelpFormatter,
                                            epilog=textwrap.dedent('''\
                                                    Output:
                                                      Write initial state in state file

                                                    Exit Status:
                                                      Zero on success and 1 on error. Error message is printed on stderr
                                                     ''')
                                            )
    _add_version(parser_enc_init)
    parser_enc_init.add_argument("--kid", help="UUID of key")
    parser_enc_init.add_argument("--alg", help="Encryption algorithm: AES, DES, DES3", required=True)
    parser_enc_init.add_argument("--mode", help="Encryption mode required for symmetric algorithms", required=True)
    parser_enc_init.add_argument("--iv", help="Initialization vector for symmetric algorithm, should be a hex string. "
                                              "It is optional for ECB mode", required=True)
    parser_enc_init.add_argument("--state", help="File path to store multipart state", dest="state_f", required=True)
    parser_enc_init.add_argument("--transient-key", help="transient key material")
    parser_enc_init.add_argument("--name", help="Name of key")
    parser_enc_init.set_defaults(func=encrypt_init)

    parser_enc_update = subparsers.add_parser("encrypt-update", help="Multipart encryption update",
                                              formatter_class=argparse.RawDescriptionHelpFormatter,
                                              epilog=textwrap.dedent('''\
                                                      Output:
                                                        Write multipart state in state file and encrypted content in out file

                                                      Exit Status:
                                                        Zero on success and 1 on error. Error message is printed on stderr
                                                       ''')
                                              )
    _add_version(parser_enc_update)
    parser_enc_update.add_argument("--kid", help="UUID of key")
    parser_enc_update.add_argument("--out", help="File path to write encrypted chunk. Each update append the encrypted "
                                                 "chunk to this file.", dest="out_f", required=True)
    parser_enc_update.add_argument("--state", help="File path to read last multipart state and write new state",
                                   dest="state_f", required=True)
    parser_enc_update.add_argument("--plain", help="Plain text to encrypt. It is optional parameter. "
                                                   "Default behaviour is to read plain text from stdin (or pipe)")
    parser_enc_update.add_argument("--transient-key", help="transient key material")
    parser_enc_update.add_argument("--name", help="Name of key")
    parser_enc_update.set_defaults(func=encrypt_update)

    parser_enc_final = subparsers.add_parser("encrypt-final", help="Multipart encryption final",
                                             formatter_class=argparse.RawDescriptionHelpFormatter,
                                             epilog=textwrap.dedent('''\
                                                     Output:
                                                       Append final encrypted content in out file.

                                                     Exit Status:
                                                       Zero on success and 1 on error. Error message is printed on stderr
                                                      ''')
                                             )
    _add_version(parser_enc_final)
    parser_enc_final.add_argument("--kid", help="UUID of key")
    parser_enc_final.add_argument("--state", help="File path to read last multipart state and write new state",
                                  dest="state_f", required=True)
    parser_enc_final.add_argument("--out", help="File path to write final encrypted chunk. This file path should be "
                                                "same as --out of encrypt-update", dest="out_f", required=True)
    parser_enc_final.add_argument("--transient-key", help="transient key material")
    parser_enc_final.add_argument("--name", help="Name of key")
    parser_enc_final.set_defaults(func=encrypt_final)

    parser_dec_init = subparsers.add_parser("decrypt-init", help="Multipart decryption initialization",
                                            formatter_class=argparse.RawDescriptionHelpFormatter,
                                            epilog=textwrap.dedent('''\
                                                    Output:
                                                      Write multipart init state in state file.

                                                    Exit Status:
                                                      Zero on success and 1 on error. Error message is printed on stderr
                                                     ''')
                                            )
    _add_version(parser_dec_init)
    parser_dec_init.add_argument("--kid", help="UUID of key")
    parser_dec_init.add_argument("--alg", help="Decryption algorithm: AES, DES, DES3", required=True)
    parser_dec_init.add_argument("--mode", help="Decryption mode required for symmetric algorithms", required=True)
    parser_dec_init.add_argument("--iv", help="Initialization vector for symmetric algorithm, should be a hex string. "
                                              "It is optional for ECB mode", required=True)
    parser_dec_init.add_argument("--state", help="File path to store multipart state", dest="state_f", required=True)
    parser_dec_init.add_argument("--transient-key", help="transient key material")
    parser_dec_init.add_argument("--name", help="Name of key")
    parser_dec_init.set_defaults(func=decrypt_init)

    parser_dec_update = subparsers.add_parser("decrypt-update", help="Multipart decryption update",
                                              formatter_class=argparse.RawDescriptionHelpFormatter,
                                              epilog=textwrap.dedent('''\
                                                      Output:
                                                        Write multipart update state in state file and append decrypted content in out file.

                                                      Exit Status:
                                                        Zero on success and 1 on error. Error message is printed on stderr
                                                       ''')
                                              )
    _add_version(parser_dec_update)
    parser_dec_update.add_argument("--kid", help="UUID of key")
    parser_dec_update.add_argument("--out", help="File path to write decrypted chunk. Each update append the decrypted "
                                                 "chunk to this file.", dest="out_f", required=True)
    parser_dec_update.add_argument("--state", help="File path to read last multipart state and write new state",
                                   dest="state_f", required=True)
    parser_dec_update.add_argument("--cipher", help="Cipher text to decrypt. It is optional parameter and not "
                                                    "recommended way to pass cipher. Default behaviour is to read "
                                                    " cipher from stdin (or pipe).")
    parser_dec_update.add_argument("--transient-key", help="transient key material")
    parser_dec_update.add_argument("--name", help="Name of key")
    parser_dec_update.set_defaults(func=decrypt_update)

    parser_dec_final = subparsers.add_parser("decrypt-final", help="Multipart encryption final",
                                             formatter_class=argparse.RawDescriptionHelpFormatter,
                                             epilog=textwrap.dedent('''\
                                                     Output:
                                                       Append final decrypted content in out file.

                                                     Exit Status:
                                                       Zero on success and 1 on error. Error message is printed on stderr
                                                      ''')
                                             )
    _add_version(parser_dec_final)
    parser_dec_final.add_argument("--kid", help="UUID of key")
    parser_dec_final.add_argument("--state", help="File path to read last multipart state and write new state",
                                  dest="state_f", required=True)
    parser_dec_final.add_argument("--out", help="File path to write final encrypted chunk. This file path should be "
                                                "same as --out of encrypt-update", dest="out_f", required=True)
    parser_dec_final.add_argument("--transient-key", help="transient key material")
    parser_dec_final.add_argument("--name", help="Name of key")
    parser_dec_final.set_defaults(func=decrypt_final)

    # decrypt parser
    parser_decrypt = subparsers.add_parser("decrypt", help="Decrypt with key",
                                           formatter_class=argparse.RawDescriptionHelpFormatter,
                                           epilog=textwrap.dedent('''\
                                                   Output:
                                                     Write decrypted text in out file.

                                                   Exit Status:
                                                     Zero on success and 1 on error. Error message is printed on stderr
                                                    ''')
                                           )
    _add_version(parser_decrypt)
    parser_decrypt.add_argument("--kid", help="UUID of key")
    parser_decrypt.add_argument("--name", help="Name of key")
    parser_decrypt.add_argument("--alg", help="Decryption algorithm: AES, DES, or RSA", required=True)
    parser_decrypt.add_argument("--in", help="Input file", dest="in_f", required=True )
    parser_decrypt.add_argument("--out", help="Output file", dest="out_f", required=True)
    parser_decrypt.add_argument("--mode", help="Decryption mode required for symmetric algorithms")
    parser_decrypt.add_argument("--iv", help="Initialization vector for symmetric algorithm, should be a hex string."
                                             "It is optional for ECB mode")
    parser_decrypt.add_argument("--ad", help="Authentication data for AES GCM mode, should be a hex string")
    parser_decrypt.add_argument("--tag", help="File path of <out>.tag file for AES GCM mode")
    parser_decrypt.add_argument("--transient-key", help="transient key material")
    parser_decrypt.set_defaults(func=decrypt)

    parser_wrap = subparsers.add_parser("wrap-key", help="Wrap a key with another key",
                                        formatter_class=argparse.RawDescriptionHelpFormatter,
                                        epilog=textwrap.dedent('''\
                                                Output:
                                                  Write wrapped key into out file.
                                                  For cipher mode GCM, write tag into <out>.tag.

                                                Exit Status:
                                                  Zero on success and 1 on error. Error message is printed on stderr
                                                 ''')
                                        )
    _add_version(parser_wrap)
    parser_wrap.add_argument("--kid", help="UUID of the key to be wrapped")
    parser_wrap.add_argument("--wrapped-key-name", help="Name of the key to be wrapped")
    parser_wrap.add_argument("--alg", help="Encryption algorithm: AES, DES or RSA", required=True)
    parser_wrap.add_argument("--mode", help="Encryption mode required for symmetric algorithms")
    parser_wrap.add_argument("--iv", help="Initialization vector for symmetric algorithms, should be a hex string")
    parser_wrap.add_argument("--ad", help="Authentication data for AES GCM or CCM mode, should be a hex string")
    parser_wrap.add_argument("--tag-len", help="Length of tag for AES GCM or CCM mode", type=int)
    parser_wrap.add_argument("--wrapping-kid", help="UUID of the key being used to wrap", dest="wrapping_kid",)
    parser_wrap.add_argument("--wrapping-key-name", help="Name of the key being used to wrap")
    parser_wrap.add_argument("--out", help="Output file. Not required if this is a quorum approval request.", dest="out")
    parser_wrap.add_argument("--transient-key", help="Value of the transient key being used to wrap.")
    parser_wrap.add_argument("--key-format", help="Desired key formatting. Default is PKCS1. Other supported format is Pkcs8.")
    parser_wrap.add_argument("--quorum", action='store_true', default=False, help="Send a quorum approval request, instead of direct key wrapping", required=False)

    parser_wrap.set_defaults(func=wrap_key)

    parser_unwrap = subparsers.add_parser("unwrap-key", help="Unwrap a key that has been wrapped with another key",
                                          formatter_class=argparse.RawDescriptionHelpFormatter,
                                          epilog=textwrap.dedent('''\
                                                  Output:
                                                      Un-wrap key UUID.

                                                  Exit Status:
                                                    0 on success and 1 on error. Error message is printed on stderr
                                                  ''')
                                          )
    _add_version(parser_unwrap)
    parser_unwrap.add_argument("--in", help="Input wrapped key file", required=True, dest="in_f")
    parser_unwrap.add_argument("--wrapping-kid", help="UUID of the key being used to unwrap", dest="wrapping_kid"
                              )
    parser_unwrap.add_argument("--alg", help="Encryption algorithm of the wrapping key: AES, DES or RSA", required=True)
    parser_unwrap.add_argument("--mode", help="Encryption mode required for symmetric algorithms")
    parser_unwrap.add_argument("--obj-type",
                               help="Security object type of the wrapped object: AES, DES, DES3, RSA, EC, or OPAQUE",
                               required=True)
    parser_unwrap.add_argument("--name", help="Name of key being unwrapped")
    parser_unwrap.add_argument("--description", help="Description of key being unwrapped",
                               default="Created by sdkms-client")
    parser_unwrap.add_argument("--iv", help="Initialization vector for symmetric algorithms, should be a hex string")
    parser_unwrap.add_argument("--ad", help="Authentication data for AES GCM or CCM mode, should be a hex string")
    parser_unwrap.add_argument("--tag", help="Tag for AES GCM or CCM mode, should be a hex string")
    parser_unwrap.add_argument("--exportable", help="Allow key to be exported from SDKMS by wrapping",
                               action='store_true')
    parser_unwrap.add_argument("--transient-key", help="Value of the transient key being used to wrap.")
    parser_unwrap.add_argument("--custom-metadata", help="""
A JSON object encoding custom metadata for the unwrapped Security Object
as "key" : "value" pairs. Values must be strings (and not integers,
booleans or objects).
""")
    parser_unwrap.add_argument("--quorum", action='store_true', default=False, help="Send a quorum approval request, instead of direct key unwrapping", required=False)
    parser_unwrap.set_defaults(func=unwrap_key)

    # Parser for derive-key
    parser_dkey = subparsers.add_parser("derive-key", help="Derive a new key from existing (base) key.",
                                        formatter_class=argparse.RawDescriptionHelpFormatter,
                                        epilog=textwrap.dedent('''\
                                                Output:
                                                    Derive key UUID.

                                                Exit Status:
                                                  0 on success and 1 on error. Error message is printed on stderr
                                                ''')
                                        )
    _add_version(parser_dkey)
    parser_dkey.add_argument("--kid", help="UUID of the the base key", dest="kid",  required=True)
    parser_dkey.add_argument("--name", help="Name of the derived key. Key names must be unique within an account.", required=True)
    parser_dkey.add_argument("--key-size", help="Key size of the derived key in bits.", type=int, required=True)
    parser_dkey.add_argument("--key-type", help="Type of the derived key. "
                                               "Supported types are AES, DES, DES3, RSA, EC, OPAQUE, HMAC, SECRET.", required=True)
    parser_dkey.add_argument("--group-id", help="Group ID (not name) of the security group that this security object should belong to."
                                               " The user or application creating this security object must be a member of this group. "
                                               "If no group is specified, the default group for the user or application will be used."
                                               "Group id is mandatory if you logged in as user")
    parser_dkey.add_argument("--plain", help="The plaintext to encrypt.", required=True)
    parser_dkey.add_argument("--alg", help="Encryption algorithm: AES, DES or RSA.", required=True)
    parser_dkey.add_argument("--mode", help="Encryption mode required for symmetric algorithms. It is used in key derivation mechanism")
    parser_dkey.add_argument("--iv", help="Initialization vector for symmetric algorithms. "
                                          "It is required for symmetric algorithm, should be a hex string")
    parser_dkey.add_argument("--ad", help="Authentication data for AES GCM or CCM mode, should be a hex string")
    parser_dkey.add_argument("--tag-len", help="Length of tag for AES GCM or CCM mode", type=int)
    parser_dkey.add_argument("--description", help="Description of new key")
    parser_dkey.add_argument("--exportable", help="Allow key to be exported from SDKMS by wrapping",
                               action='store_true')
    parser_dkey.add_argument("--custom-metadata", help="""
    A JSON object encoding custom metadata for the derive Security Object
    as "key" : "value" pairs. Values must be strings (and not integers,
    booleans or objects).
    """)
    parser_dkey.set_defaults(func=derive_key)

    parser_list_users = subparsers.add_parser('list-users', help="List users in SDKMS")
    _add_version(parser_list_users)
    parser_list_users.set_defaults(func=list_users)

    parser_list_accounts = subparsers.add_parser('list-accounts', help='List associated accounts',
                                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                                 epilog=textwrap.dedent('''\
                                                         Output:
                                                           Default four column output:
                                                           <acc-id> <name> <auth-type> <state>

                                                           If --detail is given then account object json per line.

                                                         Exit Status:
                                                           0 on success and 1 on error. Error message is printed on stderr
                                                          ''')
                                                 )
    _add_version(parser_list_accounts)
    parser_list_accounts.add_argument("--detail", help='Output complete account json',
                               action="store_true", dest='detail')

    parser_list_accounts.set_defaults(func=list_accounts)

    parser_list_apps = subparsers.add_parser('list-apps', help="List Applications in SDKMS",
                                             formatter_class=argparse.RawDescriptionHelpFormatter,
                                             epilog=textwrap.dedent('''\
                                                     Output:
                                                       Output on console.
                                                       Default two column:
                                                            <app-id> <app-name>

                                                       If --detail is given then app object json per line.

                                                     Exit Status:
                                                       0 on success and 1 on error. Error message is printed on stderr.
                                                      ''')
                                             )
    _add_version(parser_list_apps)
    parser_list_apps.add_argument("--detail", help="Output complete app json",
                               action="store_true")
    parser_list_apps.add_argument("--offset", default=0, help="Number of security objects to skip")
    parser_list_apps.add_argument("--limit", default=100, help="Maximum number of security objects to return. If not provided, the limit is 100")

    parser_list_apps.set_defaults(func=list_apps)

    parser_create_app = subparsers.add_parser('create-app', help="Create a new Application in SDKMS",
                                              formatter_class=argparse.RawDescriptionHelpFormatter,
                                              epilog=textwrap.dedent('''\
                                                      Output:
                                                        App UUID on console.

                                                      Exit Status:
                                                        0 on success and 1 on error. Error message is printed on stderr.
                                                       ''')
                                              )
    _add_version(parser_create_app)
    parser_create_app.add_argument('--name', help="Name of Application to create", required=True)
    parser_create_app.add_argument('--groups', help="Comma-separated list of groups id this application should belong to",
                                   required=True)
    parser_create_app.add_argument('--description', help="Description for Application")
    parser_create_app.add_argument('--type', help="Application type description (e.g. Apache, Nginx, etc.)")
    parser_create_app.add_argument('--default-group', required=True, help="Application type description "
                                                                              "(e.g. Apache, Nginx, etc.)")
    parser_create_app.set_defaults(func=create_app)

    parser_get_app_api_key = subparsers.add_parser('get-app-api-key', help="Get the API key for an Application. "
                                                                           "Specify the application with --name or "
                                                                           "--app-id (but not both)",
                                                   formatter_class=argparse.RawDescriptionHelpFormatter,
                                                   epilog=textwrap.dedent('''\
                                                           Output:
                                                             API key on console.

                                                           Exit Status:
                                                             0 on success and 1 on error. Error message is printed on stderr.
                                                            ''')
                                                   )
    _add_version(parser_get_app_api_key)
    parser_get_app_api_key.add_argument('--name', help="Name of the Application")
    parser_get_app_api_key.add_argument('--app-id', help="UUID of the Application")
    parser_get_app_api_key.set_defaults(func=get_app_api_key)

    parser_regen_app_api_key = subparsers.add_parser('regenerate-app-api-key',
                                                     help="Reset the API key for an Application. "
                                                          "This will invalidate any previous API keys. "
                                                          "Specify the application "
                                                          "with --name or --app-id (but not both)",
                                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                                     epilog=textwrap.dedent('''\
                                                             Output:
                                                               API key on console.

                                                             Exit Status:
                                                               0 on success and 1 on error. Error message is printed on stderr.
                                                              ''')
                                                     )
    _add_version(parser_regen_app_api_key)
    parser_regen_app_api_key.add_argument('--name', help="Name of the Application")
    parser_regen_app_api_key.add_argument('--app-id', help="UUID of the Application")
    parser_regen_app_api_key.add_argument('--secret-size', help="Size of app secret in bytes", type=int)
    parser_regen_app_api_key.set_defaults(func=regenerate_app_api_key)

    parser_delete_app = subparsers.add_parser('delete-app', help="Delete an Application. The Application to be deleted"
                                                                 "may be specified by name or by app id. If both name and app id are "
                                                                 "provided, the Application will only be deleted if both name and app id match",
                                              formatter_class=argparse.RawDescriptionHelpFormatter,
                                              epilog=textwrap.dedent('''\
                                                      Output:
                                                        No output.

                                                      Exit Status:
                                                        0 on success and 1 on error. Error message is printed on stderr.
                                                       ''')
                                              )
    _add_version(parser_delete_app)
    parser_delete_app.add_argument('--name', help="Name of Application to delete")
    parser_delete_app.add_argument('--app-id', help="Application ID of group to delete")
    parser_delete_app.set_defaults(func=delete_app)

    parser_list_groups = subparsers.add_parser('list-groups', help="List groups in SDKMS")
    _add_version(parser_list_groups)
    parser_list_groups.set_defaults(func=list_groups)

    parser_create_group = subparsers.add_parser('create-group', help="Create a new security group")
    _add_version(parser_create_group)
    parser_create_group.add_argument("--name", help="Name of group to create", required=True)
    parser_create_group.add_argument("--description", help="Description of the new group")
    parser_create_group.add_argument("--add-quorum-policy", action="store_true", default=False)
    parser_create_group.add_argument("--n", type=int, help="Number of users")
    parser_create_group.add_argument("--users", help="Comma-separated list of users id from whom this group require approval to perform sensitive operations")
    parser_create_group.add_argument("--require-2fa", action="store_true", default=False)
    parser_create_group.add_argument("--require-password", action="store_true", default=False)
    parser_create_group.set_defaults(func=create_group)

    parser_update_group = subparsers.add_parser('update-group', help="Update a security group")
    _add_version(parser_update_group)
    parser_update_group.add_argument("--group-id", help="Group id of the group to update")
    parser_update_group.add_argument("--name", help="Name of group to update")
    parser_update_group.add_argument("--description", help="Description of the group")
    parser_update_group.add_argument("--add-quorum-policy", action="store_true", default=False)
    parser_update_group.add_argument("--n", type=int, help="Number of users")
    parser_update_group.add_argument("--users", help="Comma-separated list of users id from whom this group require approval to perform sensitive operations")
    parser_update_group.add_argument("--require-2fa", action="store_true", default=False)
    parser_update_group.add_argument("--require-password", action="store_true", default=False)
    parser_update_group.set_defaults(func=update_group)

    parser_delete_group = subparsers.add_parser('delete-group', help="Delete a security group.",
                                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                                epilog=textwrap.dedent('''\
                                                        Output:
                                                          No output.

                                                        Exit Status:
                                                          0 on success and 1 on error. Error message is printed on stderr.
                                                         ''')
                                                )
    _add_version(parser_delete_group)
    parser_delete_group.add_argument("--name", help="Name of group to delete")
    parser_delete_group.add_argument("--group-id", help="Group ID of group to delete.")
    parser_delete_group.set_defaults(func=delete_group)

    # parser for sign operation
    parser_sign = subparsers.add_parser("sign", help="Signature generation with RSA and EC keys",
                                        formatter_class=argparse.RawDescriptionHelpFormatter,
                                        epilog=textwrap.dedent('''\
                                                Output:
                                                  Signature output to out file.

                                                Exit Status:
                                                  0 on successful signature generation and 1 on error. Error message is printed on stderr.
                                                 ''')
                                        )
    _add_version(parser_sign)
    parser_sign.add_argument("--kid", help="UUID of key", dest="kid")
    parser_sign.add_argument("--hash-alg", help="Message digest algorithm : SHA1,SHA256,SHA384,SHA512", required=True)
    parser_sign.add_argument("--in", help="Input data file path", dest="in_f", required=True)
    parser_sign.add_argument("--out", help="Output signature file path", required=False)
    parser_sign.add_argument("--quorum", action="store_true", default=False, help="Send an quorum approval request, instead of direct signing", required=False)
    parser_sign.add_argument("--transient-key", help="transient key material")
    parser_sign.set_defaults(func=sign)

    # parser for batch sign operation
    parser_bs = subparsers.add_parser("batch-sign", help="Signature generation with RSA and EC keys in batch",
                                      formatter_class=argparse.RawDescriptionHelpFormatter,
                                      epilog=textwrap.dedent('''\
                                              Output:
                                                Three column output:
                                                    <line-number> <output file path> <status>

                                                line number from input file, signature output file path for that line and status.
                                                Possible values for <status> are 0 and 1.
                                                0 -- output file path has the generated signature.
                                                1 -- Server rejected the request and there is not output.

                                              Exit Status:
                                                0 on successful signature generation of complete batch and 1 on error. Error message is printed on stderr.
                                               ''')
                                      )
    _add_version(parser_bs)
    parser_bs.add_argument("--in", help="Input file having sign command line options per line", dest="in_f", required=True)
    parser_bs.set_defaults(func=batch_sign)

    # parser for batch encrypt/decrypt operation
    parser_benc = subparsers.add_parser("batch-encrypt", help="Encryption in batch",
                                        formatter_class=argparse.RawDescriptionHelpFormatter,
                                        epilog=textwrap.dedent('''\
                                                Output:
                                                  Three column output:
                                                      <line-number> <out_file_path> <status>

                                                  line number from input file, corresponding encrypted output file path and operation status.
                                                  Possible values for <status> are 0, 1.
                                                  0 -- Encryption operation successful
                                                  1 -- Encryption operation fail

                                                  out_file_path is only available for operation status 0.

                                                Exit Status:
                                                  0 on successful encryption of complete batch and 1 on error. Error message is printed on stderr
                                                 ''')
                                        )
    parser_benc.add_argument("--in", help="Input file having encrypt command line options per line", dest="in_f",
                                   required=True)
    parser_benc.set_defaults(func=batch_encrypt)

    parser_bdec = subparsers.add_parser("batch-decrypt", help="Decryption in batch",
                                        formatter_class=argparse.RawDescriptionHelpFormatter,
                                        epilog=textwrap.dedent('''\
                                                Output:
                                                  Three column output:
                                                      <line-number> <out_file_path> <status>

                                                  line number from input file, corresponding plain output file path and operation status.
                                                  Possible values for <status> are 0, 1.
                                                  0 -- Decryption operation successful
                                                  1 -- Decryption operation fail

                                                  out_file_path is only available for operation status 0.

                                                Exit Status:
                                                  0 on successful decryption of complete batch and 1 on error. Error message is printed on stderr
                                                 ''')
                                        )
    parser_bdec.add_argument("--in", help="Input file having decrypt command line options per line", dest="in_f",
                             required=True)
    parser_bdec.set_defaults(func=batch_decrypt)

    # parser for batch verify operation
    parser_bv = subparsers.add_parser("batch-verify", help="Signature verification with RSA and EC keys in batch",
                                      formatter_class=argparse.RawDescriptionHelpFormatter,
                                      epilog=textwrap.dedent('''\
                                              Output:
                                                Two column output:
                                                    <line-number> <status>

                                                line number from input file and verification status of that line.
                                                Possible values for <status> are 0, 1 and 2.
                                                0 -- Verification Successful
                                                1 -- Verification Failure
                                                2 -- Input arguments not valid and hence server rejected the request

                                              Exit Status:
                                                0 on successful verification of complete batch and 1 on error. Error message is printed on stderr
                                               ''')
                                      )
    _add_version(parser_bv)
    parser_bv.add_argument("--in", help="Input file having verify command line options per line", dest="in_f",
                                   required=True)
    parser_bv.set_defaults(func=batch_verify)

    # parser for verify operation
    parser_verify = subparsers.add_parser("verify", help="Signature verification with RSA and EC keys",
                                          formatter_class=argparse.RawDescriptionHelpFormatter,
                                          epilog=textwrap.dedent('''\
                                                  Output:
                                                    No output.

                                                  Exit Status:
                                                    0 on successful verification and 1 on error. Error message is printed on stderr
                                                   ''')
                                          )
    _add_version(parser_verify)
    parser_verify.add_argument("--kid", help="UUID of key", dest="kid")
    parser_verify.add_argument("--hash-alg", help="Message digest algorithm : SHA1,SHA256,SHA384,SHA512", required=True)
    parser_verify.add_argument("--in", help="Input plain data file path", required=True, dest="in_f")
    parser_verify.add_argument("--sig-in", help="Input signature file path", dest="sig_f", required=True)
    parser_verify.add_argument("--transient-key", help="transient key material")
    parser_verify.set_defaults(func=verify)

    # parser for message digest operation
    parser_message_digest = subparsers.add_parser("message-digest", help="Message Digest",
                                                  formatter_class=argparse.RawDescriptionHelpFormatter,
                                                  epilog=textwrap.dedent('''\
                                                          Output:
                                                            MAC digest (in hex) on console.

                                                          Exit Status:
                                                            0 on success and 1 on error. Error message is printed on stderr.
                                                           ''')
                                                  )
    _add_version(parser_message_digest)
    parser_message_digest.add_argument("--alg", help="Message digest algorithm : SHA1,SHA256,SHA384,SHA512",required=True)
    parser_message_digest.add_argument("--in", help="Input data file path", required=True, dest="in_f")
    parser_message_digest.set_defaults(func=message_digest)

    # parser for hmac compute digest operation
    parser_hmac_digest = subparsers.add_parser("hmac-digest", help="Compute HMAC digest. Computed digest is hex encoded",
                                               formatter_class=argparse.RawDescriptionHelpFormatter,
                                               epilog=textwrap.dedent('''\
                                                       Output:
                                                         HMAC digest (in hex) on console.

                                                       Exit Status:
                                                         0 on success and 1 on error. Error message is printed on stderr
                                                        ''')
                                               )
    _add_version(parser_hmac_digest)
    parser_hmac_digest.add_argument("--kid", help="UUID of key", dest="kid", required=True)
    parser_hmac_digest.add_argument("--alg", help="Message digest algorithm : SHA1,SHA256,SHA384,SHA512", required=True)
    parser_hmac_digest.add_argument("--in", help="Input data file path", required=True, dest="in_f")
    parser_hmac_digest.set_defaults(func=hmac_digest)

    # parser for hmac compute digest operation
    parser_hmac_digest_verify = subparsers.add_parser("hmac-verify", help="Verify HMAC digest",
                                                      formatter_class=argparse.RawDescriptionHelpFormatter,
                                                      epilog=textwrap.dedent('''\
                                                              Output:
                                                                The verification status of the HMAC digest for the input data.

                                                              Exit Status:
                                                                Zero on success and 1 on error. Error message is printed on stderr
                                                               ''')
                                                      )
    _add_version(parser_hmac_digest_verify)
    parser_hmac_digest_verify.add_argument("--kid", help="UUID of key", dest="kid", required=True)
    parser_hmac_digest_verify.add_argument("--alg", help="Message digest algorithm : SHA1,SHA256,SHA384,SHA512", required=True)
    parser_hmac_digest_verify.add_argument("--in", help="Input data file path", required=True, dest="in_f")
    parser_hmac_digest_verify.add_argument("--digest", help="Hex encoded message digest", required=True)
    parser_hmac_digest_verify.set_defaults(func=hmac_digest_verify)

    # parser for agree key
    parser_agree_key = subparsers.add_parser("agree-key", help="Agree key")
    _add_version(parser_agree_key)
    parser_agree_key.add_argument("--private-key", help="Private key UUID. Only EC key supported", dest="private_key", required=True)
    parser_agree_key.add_argument("--public-key", help="Public key UUID. Only EC key supported",dest="public_key", required=True)
    parser_agree_key.add_argument("--name", help="Name of the key agreed upon key", required=True)
    parser_agree_key.add_argument("--key-size", help="Key size of the derived key in bits", required=True, type=int)
    parser_agree_key.add_argument("--key-type", help="Type of newly created security object. Default security object type is SECRET."
                                               "Supported types are AES, DES, DES3, RSA, EC, OPAQUE, HMAC, SECRET.", default="SECRET")
    parser_agree_key.set_defaults(func=agree_key)

    # parser for plugin invocation
    parser_invoke_plugin = subparsers.add_parser("invoke-plugin", help="Invoke sdkms plugin",
                                           formatter_class=argparse.RawDescriptionHelpFormatter,
                                           epilog=textwrap.dedent('''\
                                                   Output:
                                                     Return value of plugin execution.

                                                   Exit Status:
                                                     0 on successful and 1 on error. Error message is printed on stderr
                                                    ''')
                                           )
    _add_version(parser_invoke_plugin)
    parser_invoke_plugin.add_argument("--name", help="Name of plugin to invoke", dest="name")
    parser_invoke_plugin.add_argument("--id", help="UUID of plugin to invoke", dest="id")
    parser_invoke_plugin.add_argument("--in", help="Plugin input Json file path", dest="in_f")
    parser_invoke_plugin.add_argument("--out", help="Plugin output Json file path")
    parser_invoke_plugin.set_defaults(func=invoke_plugin)

    # parser for update plugin
    parser_update_plugin = subparsers.add_parser("update-plugin", help="Invoke sdkms update plugin")
    _add_version(parser_update_plugin)
    parser_update_plugin.add_argument("--id", help="UUID of plugin", dest="uuid")
    parser_update_plugin.add_argument("--in", help="Lua plugin file path", required=True, dest="in_f")
    parser_update_plugin.add_argument("--name", help="Plugin Name")
    parser_update_plugin.add_argument("--group-id", help="Plugin group id", dest="group_id")
    parser_update_plugin.set_defaults(func=update_plugin)

    # parser for delete plugin
    parser_delete_plugin = subparsers.add_parser("delete-plugin", help="Invoke sdkms delete plugin")
    _add_version(parser_delete_plugin)
    parser_delete_plugin.add_argument("--id", help="UUID of plugin")
    parser_delete_plugin.add_argument("--name", help="Name of plugin")
    parser_delete_plugin.set_defaults(func=delete_plugin)

    # parser for create plugin
    parser_create_plugin = subparsers.add_parser("create-plugin", help="Invoke sdkms update plugin")
    _add_version(parser_create_plugin)
    parser_create_plugin.add_argument("--in", help="Lua plugin file path", required=True, dest="in_f")
    parser_create_plugin.add_argument("--name", help="Name of plugin", required=True, dest="name")
    parser_create_plugin.add_argument("--group-id", help="Plugin Group id", dest="group_id")
    parser_create_plugin.set_defaults(func=create_plugin)

    # parser for show version
    parser_show_version = subparsers.add_parser("server-version", help="check sdkms server version")
    parser_show_version.set_defaults(func=show_version)

    # parser for show health
    parser_show_health = subparsers.add_parser("server-health", help="check sdkms server health")
    parser_show_health.set_defaults(func=show_health)

    parser_login_certificate = subparsers.add_parser("app-certificate-login", help="Log in to SDKMS with a certificate " +
                                                                 "for performing account tasks")
    _add_version(parser_login_certificate)
    parser_login_certificate.add_argument("--app-id", help="SDKMS app id to log in")
    parser_login_certificate.add_argument("--certificate-path",
                                   help="Path of certificate")
    parser_login_certificate.add_argument("--key-path", help="Path to certificate key")
    parser_login_certificate.set_defaults(func=certificate_login)

    # parsers for show object
    parser_show_app = subparsers.add_parser("show-app", help="Display app properties",
                                            formatter_class=argparse.RawDescriptionHelpFormatter,
                                            epilog=textwrap.dedent('''\
                                                    Output:
                                                      Dump the app json on standard output.

                                                    Exit Status:
                                                      0 on successful and 1 on error. Error message is printed on stderr
                                                     ''')
                                            )
    _add_version(parser_show_app)
    parser_show_app.add_argument("--app-id", help="Application id", required=True, dest="app_id")
    parser_show_app.set_defaults(func=show_app)

    parser_show_group = subparsers.add_parser("show-group", help="Display group properties",
                                            formatter_class=argparse.RawDescriptionHelpFormatter,
                                            epilog=textwrap.dedent('''\
                                                    Output:
                                                      Dump the group json on standard output.

                                                    Exit Status:
                                                      0 on successful and 1 on error. Error message is printed on stderr
                                                     ''')
                                            )
    _add_version(parser_show_group)
    parser_show_group.add_argument("--group-id", help="Group id", required=True, dest="group_id")
    parser_show_group.set_defaults(func=show_group)

    parser_show_user = subparsers.add_parser("show-user", help="Display user properties",
                                            formatter_class=argparse.RawDescriptionHelpFormatter,
                                            epilog=textwrap.dedent('''\
                                                    Output:
                                                      Dump the user json on standard output.

                                                    Exit Status:
                                                      0 on successful and 1 on error. Error message is printed on stderr
                                                     ''')
                                            )
    _add_version(parser_show_user)
    parser_show_user.add_argument("--user-id", help="User id", required=True, dest="user_id")
    parser_show_user.set_defaults(func=show_user)

    parser_show_user = subparsers.add_parser("show-account", help="Display account properties",
                                            formatter_class=argparse.RawDescriptionHelpFormatter,
                                            epilog=textwrap.dedent('''\
                                                    Output:
                                                      Dump the account json on standard output.

                                                    Exit Status:
                                                      0 on successful and 1 on error. Error message is printed on stderr
                                                     ''')
                                            )
    _add_version(parser_show_user)
    parser_show_user.add_argument("--account-id", help="Account id", required=True, dest="account_id")
    parser_show_user.set_defaults(func=show_account)

    parser_task_result = subparsers.add_parser("task-result", help="Display resault of an approval task",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''\
                Output:
                  If task successful, dumps the full result, otherwise dumps just the status as json on standard output

                Exit Status:
                  0 on successful and 1 on error. Error message is printed on stderr
                 '''
        )
    )
    _add_version(parser_task_result)
    parser_task_result.add_argument("--request-id", help="Task Request id", required=True, dest="request_id")
    parser_task_result.add_argument("--out", dest="out", help="For approved tasks, this saves the byte output of the task in a file. Operations supported: export, wrap-key, sign")
    parser_task_result.set_defaults(func=task_result)

    args = parser.parse_args()
    global api_endpoint
    global proxy
    global ssl_ca_cert
    api_endpoint = args.api_endpoint
    proxy = args.proxy

    if args.debug_http:
        http_client.HTTPConnection.debuglevel = 1

    if args.preferred_auth:
        _globals.preferred_auth = args.preferred_auth

    #Load token file and populate globals
    properties = load_properties(TOKEN_FILE)
    _globals.user_token = properties.get(USER_TOKEN)
    _globals.app_token = properties.get(APP_TOKEN)
    _globals.cert_path = properties.get(CERT_PATH)
    _globals.key_path = properties.get(KEY_PATH)

    if api_endpoint is None and properties.get(ENDPOINT) != 'None':
        api_endpoint = properties.get(ENDPOINT)

    if proxy is None and properties.get(PROXY) != 'None':
        proxy = properties.get(PROXY)

    if args.no_verify_ssl:
        verify_ssl = False
    else:
        verify_ssl = True
    ssl_ca_cert = args.ssl_ca_cert

    debug_errors = args.debug_errors

    # Here we delete the global options from the args dict. Many subcommands directly construct JSON objects from
    # args, and we shouldn't add unintended properties to these objects.
    global_opts = ['api_endpoint', 'proxy', 'no_verify_ssl', 'ssl_ca_cert', 'debug_http', 'preferred_auth', 'func',
                   'debug_errors', 'command']
    func = args.func
    args_dict = vars(args)
    for opt in global_opts:
        if opt in args_dict:
            del args_dict[opt]

    exception = None
    exit_status = 0

    try:
        func(**args_dict)
    except ClientException as e:
        exception = e
        if type(e.message) is str:
            _print_err([e.message])
        else:
            _print_err(e.message)
    except ApiException as e:
        exception = e
        errors = [
            'Request Fail',
            'status:   {}'.format(e.status),
            'reason:   {}'.format(e.reason),
            'response: {}'.format(e.body),
            'headers:  {}'.format(e.headers)
        ]
        _print_err(errors)

    if exception is not None:
        if debug_errors:
            traceback.print_exc(file=sys.stderr)
        exit_status = 1

    exit(exit_status)


if __name__ == '__main__':
    main()
