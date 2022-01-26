# Copyright 2017 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type

import argparse
import io
import os
import shutil

from fixtures import MonkeyPatch
from fixtures._fixtures import popen
import six
from systemfixtures import FakeFilesystem as _FakeFilesystem


class SudoUmount:

    name = "sudo"

    def __init__(self, delays=None):
        self.delays = delays or {}

    def __call__(self, proc_args):
        parser = argparse.ArgumentParser()
        parser.add_argument("command", choices=["umount"])
        parser.add_argument("mount_path")
        args = parser.parse_args(proc_args["args"][1:])
        if self.delays.get(args.mount_path, 0) > 0:
            self.delays[args.mount_path] -= 1
            return {'returncode': 1}
        with open("/proc/mounts") as mounts_file:
            mounts = mounts_file.readlines()
        to_remove = None
        for i, mount in reversed(list(enumerate(mounts))):
            if mount.split()[1] == args.mount_path:
                to_remove = i
                break
        if to_remove is None:
            return {'returncode': 1}
        else:
            del mounts[to_remove]
            with open("/proc/mounts", "w") as mounts_file:
                for mount in mounts:
                    mounts_file.write(mount)
            return {}


class Kill:
    """A substitute for `os.kill` that may fail sometimes.

    This must run with a fake `/proc` (e.g. using
    `systemfixtures.FakeFilesystem`).
    """

    def __init__(self, delays=None):
        self.delays = delays or {}
        self.kills = []

    def __call__(self, pid, sig):
        if self.delays.get(pid, 0) > 0:
            self.delays[pid] -= 1
            raise OSError
        self.kills.append((pid, sig))
        shutil.rmtree("/proc/%d" % pid)


class KillFixture(MonkeyPatch):

    def __init__(self, delays=None):
        super(KillFixture, self).__init__("os.kill", Kill(delays=delays))

    @property
    def kills(self):
        return self.new_value.kills


class FakeFilesystem(_FakeFilesystem):
    """A FakeFilesystem that can exclude subpaths.

    Adding /proc to the overlay filesystem behaves badly on Python 3,
    because FakeFilesystem uses /proc/self/fd for its own purposes when
    dealing with file-descriptor-based operations.  Being able to remove
    /proc/self/fd lets us work around this.
    """

    def _setUp(self):
        super(FakeFilesystem, self)._setUp()
        self._excludes = set()

    def remove(self, path):
        """Remove a path from the overlay filesystem.

        Any filesystem operation involving this path or any sub-paths of it
        will not be redirected, even if one of its parent directories is in
        the overlay filesystem.
        """
        if not path.startswith(os.sep):
            raise ValueError("Non-absolute path '{}'".format(path))
        self._excludes.add(path.rstrip(os.sep))

    def _is_fake_path(self, path, *args, **kwargs):
        for prefix in self._excludes:
            if path.startswith(prefix):
                return False
        return super(FakeFilesystem, self)._is_fake_path(path, *args, **kwargs)


class CarefulFakeProcess(popen.FakeProcess):
    """A version of FakeProcess that is more careful about text mode."""

    def __init__(self, *args, **kwargs):
        super(CarefulFakeProcess, self).__init__(*args, **kwargs)
        text_mode = bool(self._args.get("universal_newlines"))
        if not self.stdout:
            self.stdout = io.StringIO() if text_mode else io.BytesIO()
        if not self.stderr:
            self.stderr = io.StringIO() if text_mode else io.BytesIO()

    def communicate(self, *args, **kwargs):
        out, err = super(CarefulFakeProcess, self).communicate(*args, **kwargs)
        if self._args.get("universal_newlines"):
            if isinstance(out, bytes):
                raise TypeError("Process stdout is bytes, expecting text")
            if isinstance(err, bytes):
                raise TypeError("Process stderr is bytes, expecting text")
        else:
            if isinstance(out, six.text_type):
                raise TypeError("Process stdout is text, expecting bytes")
            if isinstance(err, six.text_type):
                raise TypeError("Process stderr is text, expecting bytes")
        return out, err


class CarefulFakeProcessFixture(MonkeyPatch):
    """Patch the Popen fixture to be more careful about text mode."""

    def __init__(self):
        super(CarefulFakeProcessFixture, self).__init__(
            "fixtures._fixtures.popen.FakeProcess", CarefulFakeProcess)
