# This file is part of Sympathy for Data.
# Copyright (c) 2021, Combine Control Systems AB
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


_odbc_segment_re = re.compile(
    '([^=]*)=([^;]*)(?:;|$)', re.IGNORECASE)


def _odbc_dummy_quote(connection_string):
    """
    Replace all quoted strings with dummy text (X) including the quote
    characters.
    """
    quote = None
    chars = []
    for char in connection_string:
        out = 'X'
        if quote:
            if char == quote:
                quote = None
        elif char in ['"', "'"]:
            quote = char
        else:
            out = char
        chars.append(out)
    return ''.join(chars)


def _odbc_quote_value(value):
    """
    Properly quote a value according to connection string requirements.
    Special characters are: ;"'
    """
    quote = None
    res = value

    if '"' in value:
        quote = "'"
    elif "'" in value:
        quote = '"'
    elif ";" in value:
        quote = '"'

    if quote:
        chars = [quote]
        for char in value:
            if char == quote:
                chars.append(quote * 2)
            else:
                chars.append(char)
        chars.append(quote)
        res = ''.join(chars)
    return res


def expand_login(resource, secrets):
    """
    Expand login in ODBC connection string resource
    UID=<username>;PWD=<password>

    Existing username and password in the resource is replaced.
    """
    unquoted = _odbc_dummy_quote(resource)
    res_list = list(resource)

    for match in reversed(list(_odbc_segment_re.finditer(unquoted))):
        key, value = match.groups()
        start, end = match.span()
        key = key.lower()
        if key.strip().lower() == 'uid':
            res_list[start:end] = ''
        elif key.strip().lower() == 'pwd':
            res_list[start:end] = ''

    res = ''.join(res_list)
    username = _odbc_quote_value(secrets['username'])
    password = _odbc_quote_value(secrets['password'])
    login = f'UID={username};PWD={password}'
    if res.endswith(';'):
        res = f'{res}{login}'
    else:
        res = f'{res};{login}'
    return res
