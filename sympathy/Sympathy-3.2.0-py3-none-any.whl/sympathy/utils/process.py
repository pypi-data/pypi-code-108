# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
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
import errno
import os
import time
import sys


class TimeoutError(Exception):
    pass


def pid_exists(pid):
    try:
        import psutil
        return psutil.pid_exists(pid)
    except ImportError:
        if sys.platform == 'cygwin':
            try:
                os.kill(pid, 0)
            except OSError:
                return False
            return True


def age(filename):
    try:
        return time.time() - os.path.getmtime(filename)
    except:
        return 0


def expire(filename, lifetime):
    """
    Expire locks that have exceeded their lifetime that have no running
    process.
    """
    if is_expired(filename, lifetime):
        try:
            os.remove(filename)
        except Exception:
            pass
        return True
    return False


def is_expired(filename, lifetime):
    """
    Return True if lock has exceeded its lifetime and has no running process.
    """
    duration = 0
    now = time.time()
    mtime = now
    try:
        mtime = os.path.getmtime(filename)
        duration = now - mtime
    except OSError:
        pass
    else:
        if duration > lifetime:
            try:
                pid = -1
                with open(filename, 'rb') as f:
                    pid = int(f.read())
                if (not pid_exists(pid) and
                        mtime == os.path.getmtime(filename)):
                    # File is older than lifetime, and process creating
                    # it is not running.
                    return True
            except Exception:
                pass
    return False


class Lock(object):
    """
    File based lock for synchronizing processes, implemented using methods from
    os. The file located at 'filename' will be used for synchronization.

    If the lock cannot be acquired directly, the process will wait for 'wait'
    seconds before retrying, repeating the process until the lock is acquired
    or until 'timeout' seconds has elapsed. If 'timeout' is None then the
    process will try acquring the lock until it is acquired.

    Preferably used in a with statement.
    """

    def __init__(self, filename, timeout=10, wait=0.01, lifetime=30):
        self.__file = None
        self.filename = filename
        self.timeout = timeout
        self.wait = wait
        self.lifetime = lifetime

    def acquire(self):
        """Acquire the lock."""
        if self.__file:
            return

        expire(self.filename, self.lifetime)

        start = time.time()
        while time.time() - start < self.timeout or self.timeout is None:
            try:
                self.__file = os.open(
                    self.filename, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                os.write(self.__file, str(os.getpid()).encode('ascii'))
                os.fsync(self.__file)
                os.close(self.__file)
                return
            except OSError as e:
                if e.errno == errno.EEXIST:
                    time.sleep(self.wait)

        raise TimeoutError(
            'Lock on {0} could not be acquired.'.format(self.filename))

    def release(self):
        """Release the lock."""
        if self.__file:
            os.remove(self.filename)
            self.__file = None

    def __enter__(self):
        self.acquire()

    def __exit__(self, *args):
        self.release()

    def __del__(self):
        self.release()
