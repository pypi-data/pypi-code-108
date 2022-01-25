# Copyright (c) 2016 Qumulo, Inc.
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


import time

import qumulo.lib.request as request

from qumulo.lib.uri import UriBuilder


@request.request
def login(conninfo, _credentials, username, password):
    method = 'POST'
    uri = '/v1/session/login'

    login_info = {'username': str(username), 'password': str(password)}
    resp = request.rest_request(conninfo, None, method, uri, body=login_info)

    # Authorization uses deltas in time, so we store this systems unix epoch as the issue date.
    # That way time deltas can be computed locally. Server uses its own time deltas so the clocks
    # must tick at the same rate.
    resp.data['issue'] = int(time.time())
    return resp


@request.request
def change_password(conninfo, credentials, old_password, new_password):
    'Unlike SetUserPassword, acts implicitly on logged in user'

    method = 'POST'
    uri = '/v1/session/change-password'
    body = {'old_password': str(old_password), 'new_password': str(new_password)}

    return request.rest_request(conninfo, credentials, method, uri, body=body)


@request.request
def who_am_i(conninfo, credentials):
    'Same as GET on user/<current_id>'

    return request.rest_request(conninfo, credentials, 'GET', '/v1/session/who-am-i')


@request.request
def my_roles(conninfo, credentials):
    return request.rest_request(conninfo, credentials, 'GET', '/v1/session/roles')


@request.request
def auth_id_to_all_related_identities(conninfo, credentials, auth_id):
    method = 'GET'
    uri = f'/v1/auth/auth-ids/{auth_id}/related-identities/'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def posix_uid_to_all_related_identities(conninfo, credentials, posix_uid):
    method = 'GET'
    uri = f'/v1/auth/posix-uids/{posix_uid}/related-identities/'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def posix_gid_to_all_related_identities(conninfo, credentials, posix_gid):
    method = 'GET'
    uri = f'/v1/auth/posix-gids/{posix_gid}/related-identities/'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def sid_to_all_related_identities(conninfo, credentials, sid):
    method = 'GET'
    uri = f'/v1/auth/sids/{sid}/related-identities/'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def local_username_to_all_related_identities(conninfo, credentials, username):
    method = 'GET'
    uri = UriBuilder(path='/v1/auth/local-username')
    uri.add_path_component(str(username))
    uri.add_path_component('related-identities')
    uri.append_slash()
    return request.rest_request(conninfo, credentials, method, str(uri))


@request.request
def get_identity_attributes(conninfo, credentials, auth_id):
    method = 'GET'
    uri = f'/v1/auth/identities/{auth_id}/attributes'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def set_identity_attributes(conninfo, credentials, auth_id, attributes):
    method = 'PUT'
    uri = f'/v1/auth/identities/{auth_id}/attributes'

    return request.rest_request(conninfo, credentials, method, uri, body=attributes)


@request.request
def delete_identity_attributes(conninfo, credentials, auth_id):
    method = 'DELETE'
    uri = f'/v1/auth/identities/{auth_id}/attributes'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def user_defined_mappings_set(conninfo, credentials, mappings):
    method = 'PUT'
    uri = '/v1/auth/user-defined-mappings/'

    return request.rest_request(conninfo, credentials, method, uri, body=mappings)


@request.request
def user_defined_mappings_get(conninfo, credentials):
    method = 'GET'
    uri = '/v1/auth/user-defined-mappings/'

    return request.rest_request(conninfo, credentials, method, uri)


@request.request
def clear_cache(conninfo, credentials):
    request.rest_request(conninfo, credentials, 'POST', '/v1/auth/clear-cache')


@request.request
def find_identity(conninfo, credentials, **attrs):
    """
    Obtain a fully-populated api_identity object. At least one argument other
    than @p domain must be specified. If multiple are specified, they must
    represent the same identity.
    @p domain The domain the identity is in.  LOCAL_DOMAIN, WORLD_DOMAIN,
        POSIX_USER_DOMAIN, POSIX_GROUP_DOMAIN, or AD_DOMAIN.
    @p auth_id The identifier used internally by qsfs.
    @p uid A posix UID
    @p gid A posix GID
    @p sid A SID.
    @p name A name of a cluster-local, AD, or LDAP user.  May be an unqualified
        login name, qualified with netbios name (e.g. DOMAIN\\user), a
        universal principal name (e.g. user@domain.example.com), or an LDAP
        distinguished name (e.g CN=John Doe,OU=users,DC=example,DC=com).
    """
    return request.rest_request(conninfo, credentials, 'POST', '/v1/auth/identity/find', body=attrs)


# User types that can be returned by expand_identity
ID_TYPE_USER = 'USER'
ID_TYPE_GROUP = 'GROUP'
ID_TYPE_UNKNOWN = 'UNKNOWN'


@request.request
def expand_identity(conninfo, credentials, _id, aux_equivalent_ids=None, aux_group_ids=None):
    """
    Find the type, all equivalent identities, and the full (recursive) group
    membership of the given identity.
    @p _id The ID to expand, an instance of qumulo.lib.identity_util.Identity
    @p aux_equivalent_ids An optional list of Identity that should be considered
            equivalent to @p _id for the purpose of this expansion.
    @p aux_group_ids An optional list of Identity that are groups that @p _id
            should be considered a member of for the purpose of this expansion.
    """
    req = {'id': _id.dictionary()}
    if aux_equivalent_ids:
        req['equivalent_ids'] = [i.dictionary() for i in aux_equivalent_ids]
    if aux_group_ids:
        req['group_ids'] = [i.dictionary() for i in aux_group_ids]
    return request.rest_request(conninfo, credentials, 'POST', '/v1/auth/identity/expand', body=req)
