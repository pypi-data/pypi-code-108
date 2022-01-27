# This file is part of Sympathy for Data.
# Copyright (c) 2018 Combine Control Systems AB
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
import urllib.parse
import requests
import tempfile
import re
from sympathy.api import exceptions
from sympathy.utils import credentials
from sympathy.platform.hooks import request_http

_netloc_username_password_re = re.compile('^([^\\:]+)\\:([^@]+)@(.+)$',
                                          re.IGNORECASE)
_netloc_username_re = re.compile('^([^@]+)@(.+)$',
                                 re.IGNORECASE)


class RequestError(Exception):
    pass


def _file_or_tempkw(filename, tempfile_kwargs):
    if not (filename or tempfile_kwargs):
        raise ValueError('Use either filename or tempfile_kwargs')


def download_datasource(datasource, filename=None, tempfile_kwargs=None):
    _file_or_tempkw(filename, tempfile_kwargs)
    if datasource.decode_type() == datasource.modes.url:
        env = datasource['env']
        result_filename = download_url(
            datasource['path'], env, filename=filename,
            tempfile_kwargs=tempfile_kwargs)
        datasource = type(datasource)()
        datasource.encode_path(result_filename)
    return datasource


def expand_login(resource, secrets):
    """
    Expand login in URL resource
    scheme://<username>:<password>@...

    Existing username and password in the resource is replaced.
    """
    scheme, netloc, *rest = urllib.parse.urlsplit(resource)
    match = _netloc_username_password_re.match(resource)

    if match:
        username, password, host = match.groups()
        # Ignoring username and password.
    else:
        match = _netloc_username_password_re.match(resource)
        if match:
            username, host = match.groups()
            # Ignoring username.
        else:
            host = netloc

    username = secrets['username']
    password = secrets['password']

    return urllib.parse.urlunsplit(
        [scheme, f'{username}:{password}@{host}'] + rest)


def download_url_with_credentials(node, connection, env, **kwargs):
    kwargs = dict(kwargs)
    url = connection.resource
    mode = connection.credentials.mode

    if mode == credentials.login_mode:
        secrets = credentials.get_login_credentials(
            node, connection)
        kwargs['auth'] = (secrets['username'], secrets['password'])

    elif mode == credentials.secrets_mode:
        secrets = credentials.get_secret_credentials(node, connection)
        url = credentials.expand_secrets(url, secrets)

    return download_url(url, env, **kwargs)


def download_url(url, env, filename=None, tempfile_kwargs=None, **kwargs):
    _file_or_tempkw(filename, tempfile_kwargs)
    scheme = urllib.parse.urlparse(url).scheme
    result_filename = None

    if scheme in ['http', 'https']:
        headers = env

        try:
            r = request_http.value.get(url, headers=headers, **kwargs)
        except requests.exceptions.RequestException as e:
            raise RequestError(str(e))

        if r.status_code != requests.codes.ok:
            raise exceptions.SyDataError(
                f'Failed getting data from: {url}')

        if filename:
            file_obj = open(filename, 'w+b')
        elif tempfile_kwargs:
            file_obj = tempfile.NamedTemporaryFile(
                delete=False, **tempfile_kwargs)

        with file_obj as http_temp:
            for chunk in r.iter_content(chunk_size=1024):
                http_temp.write(chunk)

        result_filename = http_temp.name
    else:
        raise exceptions.SyDataError(
            f'URL download only supports HTTP and HTTPS, got "{url}"')
    return result_filename
