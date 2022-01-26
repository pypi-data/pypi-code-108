# Copyright 2013-2019 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type
__all__ = [
    'FakeBackend',
    'FakeBuilder',
    'FakeMethod',
    'UncontainedBackend',
    ]

from collections import defaultdict
import hashlib
import os
import shutil
import stat
import subprocess

from six.moves.configparser import (
    NoOptionError,
    NoSectionError,
    )

from lpbuildd.target.backend import Backend
from lpbuildd.util import (
    set_personality,
    shell_escape,
    )


class FakeMethod:
    """Catch any function or method call, and record the fact.

    Use this for easy stubbing.  The call operator can return a fixed
    value, or raise a fixed exception object.

    This is useful when unit-testing code that does things you don't
    want to integration-test, e.g. because it wants to talk to remote
    systems.
    """

    def __init__(self, result=None, failure=None):
        """Set up a fake function or method.

        :param result: Value to return.
        :param failure: Exception to raise.
        """
        self.result = result
        self.failure = failure

        # A log of arguments for each call to this method.
        self.calls = []

    def __call__(self, *args, **kwargs):
        """Catch an invocation to the method.

        Increment `call_count`, and adds the arguments to `calls`.

        Accepts any and all parameters.  Raises the failure passed to
        the constructor, if any; otherwise, returns the result value
        passed to the constructor.
        """
        self.calls.append((args, kwargs))

        if self.failure is None:
            return self.result
        else:
            # pylint thinks this raises None, which is clearly not
            # possible.  That's why this test disables pylint message
            # E0702.
            raise self.failure

    @property
    def call_count(self):
        return len(self.calls)

    def extract_args(self):
        """Return just the calls' positional-arguments tuples."""
        return [args for args, kwargs in self.calls]

    def extract_kwargs(self):
        """Return just the calls' keyword-arguments dicts."""
        return [kwargs for args, kwargs in self.calls]


class FakeConfig:
    def __init__(self):
        self._overrides = defaultdict(dict)

    def get(self, section, key):
        if key in self._overrides[section]:
            return self._overrides[section][key]
        elif section == "proxy":
            if not self._overrides[section]:
                raise NoSectionError(section)
            else:
                raise NoOptionError(section, key)
        else:
            return key

    def set(self, section, key, value):
        self._overrides[section][key] = value


class FakeBuilder:
    def __init__(self, tempdir):
        self._cachepath = tempdir
        self._config = FakeConfig()
        self.waitingfiles = {}
        for fake_method in (
                "emptyLog", "log",
                "chrootFail", "buildFail", "builderFail", "depFail", "buildOK",
                "buildComplete", "sanitizeBuildlog",
                ):
            setattr(self, fake_method, FakeMethod())

    def cachePath(self, file):
        return os.path.join(self._cachepath, file)

    def addWaitingFile(self, path, name=None):
        if name is None:
            name = os.path.basename(path)
        with open(path, "rb") as f:
            contents = f.read()
        sha1sum = hashlib.sha1(contents).hexdigest()
        shutil.copy(path, self.cachePath(sha1sum))
        self.waitingfiles[name] = sha1sum

    def anyMethod(self, *args, **kwargs):
        pass

    def wasCalled(self, name):
        return getattr(self, name).call_count > 0

    def getArch(self):
        return 'i386'


class FakeBackend(Backend):

    supports_snapd = True

    def __init__(self, *args, **kwargs):
        super(FakeBackend, self).__init__(*args, **kwargs)
        fake_methods = (
            "create", "start",
            "run",
            "kill_processes", "stop", "remove",
            )
        for fake_method in fake_methods:
            setattr(self, fake_method, FakeMethod())
        self.backend_fs = {}
        self.available_packages = set()

    def _add_inode(self, path, contents, full_mode):
        path = os.path.normpath(path)
        parent = os.path.dirname(path)
        if parent != path and parent not in self.backend_fs:
            self.add_dir(parent)
        self.backend_fs[path] = (contents, full_mode)

    def add_dir(self, path, mode=0o755):
        self._add_inode(path, None, stat.S_IFDIR | mode)

    def add_file(self, path, contents, mode=0o644):
        self._add_inode(path, contents, stat.S_IFREG | mode)

    def add_link(self, path, target):
        self._add_inode(path, target, stat.S_IFLNK | 0o777)

    def copy_in(self, source_path, target_path):
        with open(source_path, "rb") as source:
            self.add_file(
                target_path, source.read(), os.fstat(source.fileno()).st_mode)

    def _get_inode(self, path):
        while True:
            contents, mode = self.backend_fs[path]
            if not stat.S_ISLNK(mode):
                return contents, mode
            path = os.path.normpath(
                os.path.join(os.path.dirname(path), contents))

    def copy_out(self, source_path, target_path):
        contents, mode = self._get_inode(source_path)
        with open(target_path, "wb") as target:
            target.write(contents)
            os.fchmod(target.fileno(), stat.S_IMODE(mode))

    def path_exists(self, path):
        try:
            self._get_inode(path)
            return True
        except KeyError:
            return False

    def isdir(self, path):
        _, mode = self.backend_fs.get(path, (b"", 0))
        return stat.S_ISDIR(mode)

    def islink(self, path):
        _, mode = self.backend_fs.get(path, (b"", 0))
        return stat.S_ISLNK(mode)

    def find(self, path, max_depth=None, include_directories=True, name=None):
        def match(backend_path, mode):
            prefix = path + os.sep
            if os.path.commonprefix((backend_path, prefix)) != prefix:
                return False
            rel_path = os.path.relpath(backend_path, path)
            if max_depth is not None:
                if rel_path.count(os.sep) + 1 > max_depth:
                    return False
            if not include_directories:
                if stat.S_ISDIR(mode):
                    return False
            if name is not None:
                if os.path.basename(rel_path) != name:
                    return False
            return True

        return [
            os.path.relpath(backend_path, path)
            for backend_path, (_, mode) in self.backend_fs.items()
            if match(backend_path, mode)]

    def is_package_available(self, package):
        return package in self.available_packages


class UncontainedBackend(Backend):
    """A partial backend implementation with no containment."""

    def run(self, args, cwd=None, env=None, input_text=None, get_output=False,
            echo=False, **kwargs):
        """See `Backend`."""
        if env:
            args = ["env"] + [
                "%s=%s" % (key, shell_escape(value))
                for key, value in env.items()] + args
        if self.arch is not None:
            args = set_personality(args, self.arch, series=self.series)
        if input_text is None and not get_output:
            subprocess.check_call(args, cwd=cwd, **kwargs)
        else:
            if get_output:
                kwargs["stdout"] = subprocess.PIPE
            proc = subprocess.Popen(
                args, stdin=subprocess.PIPE, cwd=cwd, **kwargs)
            output, _ = proc.communicate(input_text)
            if proc.returncode:
                raise subprocess.CalledProcessError(proc.returncode, args)
            if get_output:
                return output

    def _copy(self, source_path, target_path):
        if source_path == target_path:
            raise Exception(
                "TrivialBackend copy operations require source_path and "
                "target_path to differ.")
        subprocess.check_call(
            ["cp", "--preserve=timestamps", source_path, target_path])

    def copy_in(self, source_path, target_path):
        """See `Backend`."""
        self._copy(source_path, target_path)

    def copy_out(self, source_path, target_path):
        """See `Backend`."""
        self._copy(source_path, target_path)

    def remove(self):
        raise NotImplementedError
