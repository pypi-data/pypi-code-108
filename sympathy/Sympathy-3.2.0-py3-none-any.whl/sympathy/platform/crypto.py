# This file is part of Sympathy for Data.
# Copyright (c) 2020, Combine Control Systems AB
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
import os
import json
import base64
import cryptography.fernet

_crypto_key = b''
_cipher = None

_env_key = 'SY_CRYPT_KEY'


def _set_key(crypto_key: bytes):
    global _crypto_key
    global _cipher

    if crypto_key:
        _crypto_key = crypto_key
        _cipher = cryptography.fernet.Fernet(crypto_key)

        os.environ[_env_key] = _crypto_key.decode('ascii')


def init():
    _set_key(cryptography.fernet.Fernet.generate_key())


def init_from_env():
    env_val = os.environ.pop(_env_key, None)
    if env_val:
        _set_key(env_val.encode('ascii'))


def env():
    return {_env_key: _crypto_key.decode('ascii')}


def encrypt(data):
    res = data
    if _cipher and data:
        res = _cipher.encrypt(data)
    return res


def decrypt(data):
    res = data
    if _cipher and data:
        res = _cipher.decrypt(data)
    return res


def decode_json(str_):
    return json.loads(base64.b64decode(decrypt(str_)).decode('ascii'))


def encode_json(dict_):
    return encrypt(base64.b64encode(json.dumps(dict_).encode('ascii')))
