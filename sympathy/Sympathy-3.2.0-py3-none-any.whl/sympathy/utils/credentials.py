# This file is part of Sympathy for Data.
# Copyright (c) 2021 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import re
import typing
from typing import Dict
from .. platform.exceptions import (
    SyLoginCredentialError, SySecretCredentialError, SyAzureCredentialError)
from .. platform.parameter_types import Connection, CredentialsMode
# credential_modes = ['login', 'secrets']
# login_mode, secrets_mode = credential_modes
login_mode = CredentialsMode.login
secrets_mode = CredentialsMode.secrets
azure_mode = CredentialsMode.azure


_pattern = re.compile('<([a-z][\\-a-z0-9]*)>', re.IGNORECASE)


def string_credentials_by_prefix(data: Dict[str, str], prefix: str):
    def removeprefix(value, prefix):
        # str.removeprefix is new in Python 3.9.
        if value.startswith(prefix):
            value = value[len(prefix):]
        return value
    return {removeprefix(k, prefix): v
            for k, v in data.items() if k.startswith(prefix)}


def parse_secrets(resource):
    return _pattern.finditer(resource)


def secret_names(resource):
    return [m.group(1) for m in parse_secrets(resource)]


def expand_secrets(resource: str, secrets: dict) -> str:
    """
    Method generally used to expand secrets is generic and
    does not consider the syntax, the values of the secrets must be
    specified in such a way that the expansion will be valid.
    """
    matches = parse_secrets(resource)
    if not matches:
        return resource

    diff = 0
    # String as list to allow setitem.
    resource_list = list(resource)

    for match in matches:
        # Replace according to matched positions.
        value = secrets.get(match.group(1), '') or ''

        start, end = match.span()
        start += diff
        end += diff

        resource_list[start:end] = value
        diff += len(value) + start - end

    return ''.join(resource_list)


def get_resource(connection):
    return connection.resource


def _get_mode(connection):
    return connection.credentials.mode


def _get_name(connection):
    return connection.credentials.name


def expand_credentials(connection: Connection, secrets: dict,
                       expand_login: typing.Callable) -> str:
    resource = get_resource(connection)
    mode = _get_mode(connection)
    res = resource
    if mode == login_mode:
        res = expand_login(resource, secrets)
    elif mode == secrets_mode:
        res = expand_secrets(resource, secrets)
    return res


def _required_secret_names(connection: Connection):
    return secret_names(get_resource(connection))


def _required_login_names(connection: Connection):
    return ['username', 'password']


def _required_names(connection: Connection):
    mode = _get_mode(connection)
    names = []
    if mode == secrets_mode:
        names = _required_secret_names(connection)
    elif mode == login_mode:
        names = _required_login_names(connection)
    return names


def fill_secrets(connection: Connection, secrets: dict):
    """
    Use in an async workflow to ignore missing credentials.
    Attempt login for example with all missing names replaced
    by ''.
    """
    res = {}
    secrets = secrets or {}
    for k in _required_names(connection):
        res[k] = secrets.get(k) or ''
    return res


def _validate_login(connection, secrets):
    if not secrets:
        secrets = {}
    missing_login = any(k not in secrets or secrets[k] is None
                        for k in ['username', 'password'])

    if missing_login:
        raise SyLoginCredentialError.from_connection(connection)


def _validate_secrets(connection, secrets):
    if not secrets:
        secrets = dict.fromkeys(_required_secret_names(connection))
    missing_secrets = sorted(list(
        {k for k, v in secrets.items() if v is None}))

    if missing_secrets:
        raise SySecretCredentialError.from_connection(
            connection, missing_secrets)


def _validate_azure(connection, secrets):
    missing_secrets = any(k not in secrets or secrets[k] is None
                          for k in ['token', 'expires_on'])
    if missing_secrets:
        raise SyAzureCredentialError.from_connection(
            connection)


def _validate_node(node):
    if node is None:
        raise TypeError(
            'Node must not be None when requesting credentials.')


def validate_credentials(connection, secrets):
    if need_credentials(connection):
        mode = _get_mode(connection)
        if mode == secrets_mode:
            _validate_secrets(connection, secrets)
        elif mode == login_mode:
            _validate_login(connection, secrets)
        elif mode == azure_mode:
            _validate_azure(connection, secrets)


def _request_credentials(node, connection):
    _validate_node(node)

    secrets = {}
    if need_credentials(connection):
        secrets = node.request_credentials(
            connection.identifier(), connection.to_dict())
        validate_credentials(connection, secrets)
    return secrets


def get_login_credentials(node, connection):
    return _request_credentials(node, connection)


def get_secret_credentials(node, connection):
    return _request_credentials(node, connection)


def get_credentials(node, connection):
    mode = _get_mode(connection)
    res = {}
    if mode is not None:
        res = _request_credentials(node, connection)
    return res


def get_credentials_async(node, connection, handler):
    """
    Call validate_secrets on the secrets received in the
    handler.
    """
    _validate_node(node)

    if need_credentials(connection):
        node.request_credentials_async(
            connection.identifier(), connection.to_dict(), handler)
    else:
        handler({})


def get_credentials_expanded_resource(node, connection, expand_login):
    secrets = get_credentials(node, connection)
    return expand_credentials(connection, secrets, expand_login)


def need_credentials(connection):
    resource = get_resource(connection)
    mode = _get_mode(connection)
    res = True
    if mode is None:
        res = False
    elif mode == secrets_mode and not has_secrets(resource):
        res = False
    return res


def has_secrets(resource):
    return next(parse_secrets(resource), None) is not None


def validate_mode(mode):
    try:
        mode = CredentialsMode[mode]
    except Exception:
        assert False, f'Unsupported credential mode: {mode}.'


def validate_secret_name(name):
    m = _pattern.match(f'<{name}>')
    if m and m.group(1) == name:
        return True
    return False
