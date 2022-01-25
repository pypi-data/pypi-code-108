# Copyright (c) 2017 Qumulo, Inc.
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


@request.request
def settings_set_v2(
    conninfo,
    credentials,
    bind_uri,
    base_distinguished_names,
    use_ldap=False,
    user=None,
    password=None,
    encrypt_connection=None,
    ldap_schema=None,
    ldap_schema_description=None,
):

    method = 'PUT'
    uri = '/v2/ldap/settings'

    settings = {
        'use_ldap': use_ldap,
        'bind_uri': str(bind_uri),
        'base_distinguished_names': str(base_distinguished_names),
    }
    if user is not None:
        settings['user'] = str(user)
    if password is not None:
        settings['password'] = str(password)
    if encrypt_connection is not None:
        settings['encrypt_connection'] = encrypt_connection
    if ldap_schema is not None:
        settings['ldap_schema'] = str(ldap_schema)
    if ldap_schema_description is not None:
        settings['ldap_schema_description'] = ldap_schema_description

    return request.rest_request(conninfo, credentials, method, uri, body=settings)


@request.request
def settings_get_v2(conninfo, credentials):
    method = 'GET'
    uri = '/v2/ldap/settings'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def settings_update_v2(
    conninfo,
    credentials,
    bind_uri=None,
    base_distinguished_names=None,
    use_ldap=None,
    user=None,
    password=None,
    encrypt_connection=None,
    ldap_schema=None,
    ldap_schema_description=None,
):
    method = 'PATCH'
    uri = '/v2/ldap/settings'

    settings = {}

    if bind_uri != None:
        settings['bind_uri'] = bind_uri
    if base_distinguished_names != None:
        settings['base_distinguished_names'] = base_distinguished_names
    if ldap_schema != None:
        settings['ldap_schema'] = ldap_schema
    if ldap_schema_description != None:
        settings['ldap_schema_description'] = ldap_schema_description
    if user != None:
        settings['user'] = user
    if password != None:
        settings['password'] = password
    if use_ldap != None:
        settings['use_ldap'] = use_ldap
    if encrypt_connection != None:
        settings['encrypt_connection'] = encrypt_connection

    return request.rest_request(conninfo, credentials, method, uri, body=settings)


@request.request
def status_get(conninfo, credentials):
    method = 'GET'
    uri = '/v1/ldap/status'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def uid_number_to_login_name_get(conninfo, credentials, uid_number):
    method = 'GET'
    uri = '/v1/ldap/uid-number/' + str(uid_number) + '/login-name'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def login_name_to_gid_numbers_get(conninfo, credentials, login_name):
    method = 'GET'
    uri = '/v1/ldap/login-name/' + str(login_name) + '/gid-numbers'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def login_name_to_uid_numbers_get(conninfo, credentials, uid):
    method = 'GET'
    uri = '/v1/ldap/login-name/' + str(uid) + '/uid-numbers'

    return request.rest_request(conninfo, credentials, method, uri)
