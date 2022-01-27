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
import keyring as _keyring_mod
from ... utils import log
core_logger = log.get_logger('core')


_keyring = None


class MemoryKeyring(_keyring_mod.backend.KeyringBackend):
    priority = 1

    def __init__(self, *args, **kwargs):
        self._store = {}
        super().__init__(*args, **kwargs)

    def set_password(self, servicename, username, password):
        self._store[(servicename, username)] = password

    def get_password(self, servicename, username):
        return self._store.get((servicename, username))

    def delete_password(self, servicename, username):
        self._store.pop((servicename, username), None)


def _get_keyring():
    global _keyring
    if not _keyring:
        backend = _keyring_mod.get_keyring()
        if backend.priority < 1:
            core_logger.warning(
                'No recommended keyring backend found, using in-memory '
                'keyring which does not retain changes after closing '
                'Sympathy.')
            _keyring_mod.set_keyring(MemoryKeyring())
        _keyring = _keyring_mod
    return _keyring


def set_password(servicename, username, password):
    _get_keyring().set_password(servicename, username, password)


def get_password(servicename, username):
    return _get_keyring().get_password(servicename, username)


def delete_password(servicename, username):
    _get_keyring().delete_password(servicename, username)
