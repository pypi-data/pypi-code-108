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
import os
import contextlib
import msal
from .. import keyring
from sympathy.app import qt_support
from sympathy.platform import os_support
from sympathy.utils import prim
from sympathy.app.version import version
from PySide2.QtCore import QLockFile


# TODO(erik): Move LockFile related functionality
# to another place, os_support is a candidate, but QLockFile is not
# available through Qt.py.

@contextlib.contextmanager
def _escape_hostname():
    key = 'COMPUTERNAME'
    orig = os.environ.get(key, '')
    if not orig:
        yield
    else:
        try:
            replaced = orig.encode('ascii', errors='backslashreplace').decode(
                'ascii')
            os.environ[key] = replaced
            yield
        finally:
            os.environ[key] = orig


class WindowsQLockFile(QLockFile):
    """
    QLockFile for Windows with workaround for unicode characters in
    hostname.
    """
    def __init__(self, filename):
        with _escape_hostname():
            super().__init__(filename)

    def getLockInfo(self, pid: int, hostname: str, appname: str) -> bool:
        with _escape_hostname():
            return super().getLockInfo(pid, hostname, appname)

    def error(self) -> QLockFile.LockError:
        with _escape_hostname():
            return super().error()

    def isLocked(self) -> bool:
        with _escape_hostname():
            return super().isLocked()

    def lock(self) -> bool:
        with _escape_hostname():
            return super().lock()

    def removeStaleLockFile(self) -> bool:
        with _escape_hostname():
            return super().removeStaleLockFile()

    def setStateLockTime(self, staleLockTime: int):
        with _escape_hostname():
            return super().setStateLockTime(staleLockTime)

    def stateLockTime(self) -> int:
        with _escape_hostname():
            return super().staleLockTime()

    def tryLock(self, timeout: int = 0) -> bool:
        with _escape_hostname():
            return super().tryLock(timeout)

    def unlock(self):
        with _escape_hostname():
            super().unlock()


if prim.is_windows():
    _QLockFileCls = WindowsQLockFile
else:
    _QLockFileCls = QLockFile


class LockFile:
    def __init__(self, filename: str, timeout: int = None):
        self._lock = _QLockFileCls(filename)
        if timeout is not None:
            self._res = self._lock.tryLock(timeout * 1000)
        else:
            self._res = self._lock.lock()
        error = self._lock.error()
        if error == QLockFile.LockFailedError:
            raise TimeoutError(f'Coult not lock {filename} before timeout')
        elif error == QLockFile.PermissionError:
            raise PermissionError(f'Could not lock {filename}')
        elif error == QLockFile.UnknownError:
            raise Exception(f'Coult not lock {filename} due to unknown error')

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        if self._res:
            self._lock.unlock()


def _root_location():
    return os.path.join(
        qt_support.cache_location(), 'Azure', 'TokenCache', version)


def _file_location():
    return os.path.join(_root_location(), 'cache')


def _lock_file_location():
    return os.path.join(_root_location(), 'lock')


def _service_name():
    return 'Sympathy for Data Azure'


def _account_name():
    return version


def persistence():
    # Keyring can store very large secrets on some back-ends. I have tested
    # strings of 10 million chars on Mac, Gnome, and it works, although it
    # becomes slow. On Windows the limitation is 512-1024 chars,
    # Therefore, Azure credentials are stored in a file, on Windows.
    if prim.is_windows():
        return WindowsCryptPersistence(_file_location(), _service_name())
    else:
        return KeyringPersistence(_service_name(), _account_name())


def create():
    os.makedirs(_root_location(), exist_ok=True)
    return PersistedTokenCache(persistence(), _lock_file_location())


class Persistence:
    def save(self, data: str):
        raise NotImplementedError

    def load(self) -> str:
        raise NotImplementedError

    def setup(self):
        pass


class WindowsCryptPersistence(Persistence):
    def __init__(self, filename, desc: str):
        super().__init__()
        self._filename = filename
        self._protect = os_support.WindowsCryptProtect(desc=desc)

    def save(self, data):
        with open(self._filename, 'wb') as f:
            f.write(self._protect.encrypt(data.encode('utf8')))

    def load(self):
        with open(self._filename, 'rb') as f:
            return self._protect.decrypt(f.read()).decode('utf8')

    def setup(self):
        if not os.path.exists(self._filename):
            self.save('')


class KeyringPersistence(Persistence):
    def __init__(self, service, username):
        super().__init__()
        self._service = service
        self._username = username

    def save(self, data):
        keyring.set_password(self._service, self._username, data)

    def load(self):
        return keyring.get_password(self._service, self._username)


class PersistedTokenCache(msal.SerializableTokenCache):
    # TODO(erik): implement reloading to support multiple
    # concurrent writers.
    _timeout = 10

    def __init__(self, persistence, lock_filename):
        super().__init__()
        self._lock_filename = lock_filename
        self._persistence = persistence
        with LockFile(self._lock_filename, self._timeout):
            self._persistence.setup()
            self.deserialize(self._persistence.load())

    def modify(self, credential_type, old_entry, new_key_value_pairs=None):
        with LockFile(self._lock_filename, self._timeout):
            super().modify(
                credential_type,
                old_entry,
                new_key_value_pairs=new_key_value_pairs)
            self._persistence.save(self.serialize())

    def find(self, credential_type, **kwargs):
        with LockFile(self._lock_filename, self._timeout):
            return super().find(credential_type, **kwargs)

    def find_accounts(self, **kwargs):
        def valid_account(account):
            authority_type = 'authority_type'
            username = 'username'
            home_account_id = 'home_account_id'
            reqkeys = {authority_type, username, home_account_id}
            allkeys = set(account.keys())
            return allkeys.intersection(reqkeys) == reqkeys and (
                account[authority_type] == self.AuthorityType.MSSTS)

        accounts = self.find(self.CredentialType.ACCOUNT, **kwargs)
        return [account for account in accounts if valid_account(account)]
