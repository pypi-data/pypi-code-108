# Copyright 2017 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from __future__ import print_function

__metaclass__ = type

import os.path
import subprocess


class BackendException(Exception):
    pass


class InvalidBuildFilePath(Exception):
    pass


def check_path_escape(buildd_path, path_to_check):
    """Check the build file path doesn't escape the build directory."""
    build_file_path = os.path.realpath(
        os.path.join(buildd_path, path_to_check))
    common_path = os.path.commonprefix((build_file_path, buildd_path))
    if common_path != buildd_path:
        raise InvalidBuildFilePath("Invalid build file path.")


class Backend:
    """A backend implementation for the environment where we run builds."""

    supports_snapd = False

    def __init__(self, build_id, series=None, arch=None):
        self.build_id = build_id
        self.series = series
        self.arch = arch
        self.build_path = os.path.join(os.environ["HOME"], "build-" + build_id)

    def create(self, image_path, image_type):
        """Create the backend based on a base image.

        This puts the backend into a state where it is ready to be started.
        """
        raise NotImplementedError

    def start(self):
        """Start the backend.

        This puts the backend into a state where it can run commands.
        """
        raise NotImplementedError

    def run(self, args, cwd=None, env=None, input_text=None, get_output=False,
            echo=False, **kwargs):
        """Run a command in the target environment.

        :param args: the command and arguments to run.
        :param cwd: run the command in this working directory in the target.
        :param env: additional environment variables to set.
        :param input_text: input text to pass on the command's stdin.
        :param get_output: if True, return the output from the command.
        :param echo: if True, print the command before executing it, and
            print any output from the command if `get_output` is also True.
        :param kwargs: additional keyword arguments for `subprocess.Popen`.
        """
        raise NotImplementedError

    def copy_in(self, source_path, target_path):
        """Copy a file into the target environment.

        The target file will be owned by root/root and have the same
        permission mode as the source file.

        :param source_path: the path to the file that should be copied from
            the host system.
        :param target_path: the path where the file should be installed
            inside the target environment, relative to the target
            environment's root.
        """
        raise NotImplementedError

    def copy_out(self, source_path, target_path):
        """Copy a file out of the target environment.

        The target file will have the same permission mode as the source
        file.

        :param source_path: the path to the file that should be copied,
            relative to the target environment's root.
        :param target_path: the path where the file should be installed in
            the host system.
        """
        raise NotImplementedError

    def path_exists(self, path):
        """Test whether a path exists in the target environment.

        :param path: the path to the file to test, relative to the target
            environment's root.
        """
        try:
            self.run(["test", "-e", path])
            return True
        except subprocess.CalledProcessError:
            return False

    def isdir(self, path):
        """Test whether a path is a directory in the target environment.

        :param path: the path to test, relative to the target environment's
            root.
        """
        try:
            self.run(["test", "-d", path])
            return True
        except subprocess.CalledProcessError:
            return False

    def islink(self, path):
        """Test whether a file is a symbolic link in the target environment.

        :param path: the path to the file to test, relative to the target
            environment's root.
        """
        try:
            self.run(["test", "-h", path])
            return True
        except subprocess.CalledProcessError:
            return False

    def find(self, path, max_depth=None, include_directories=True, name=None):
        """Find entries in `path`.

        :param path: the path to the directory to search.
        :param max_depth: do not descend more than this number of directory
            levels: as with find(1), 1 includes the contents of `path`, 2
            includes the contents of its subdirectories, etc.
        :param include_directories: include entries representing
            directories.
        :param name: only include entries whose name is equal to this.
        """
        cmd = ["find", path, "-mindepth", "1"]
        if max_depth is not None:
            cmd.extend(["-maxdepth", str(max_depth)])
        if not include_directories:
            cmd.extend(["!", "-type", "d"])
        if name is not None:
            cmd.extend(["-name", name])
        cmd.extend(["-printf", "%P\\0"])
        paths = self.run(cmd, get_output=True).split(b"\0")[:-1]
        # XXX cjwatson 2017-08-04: Use `os.fsdecode` instead once we're on
        # Python 3.
        return [p.decode("UTF-8") for p in paths]

    def listdir(self, path):
        """List a directory in the target environment.

        :param path: the path to the directory to list, relative to the
            target environment's root.
        """
        return self.find(path, max_depth=1)

    def is_package_available(self, package):
        """Test whether a package is available in the target environment.

        :param package: a binary package name.
        """
        try:
            with open("/dev/null", "w") as devnull:
                output = self.run(
                    ["apt-cache", "show", package],
                    get_output=True, stderr=devnull, universal_newlines=True)
            return ("Package: %s" % package) in output.splitlines()
        except subprocess.CalledProcessError:
            return False

    def kill_processes(self):
        """Kill any processes left running in the target.

        This is allowed to do nothing if stopping the target will reliably
        kill all processes running in it.
        """
        # XXX cjwatson 2017-08-22: It might make sense to merge this into
        # `stop` later.
        pass

    def stop(self):
        """Stop the backend."""
        raise NotImplementedError

    def remove(self):
        """Remove the backend."""
        subprocess.check_call(["sudo", "rm", "-rf", self.build_path])


def make_backend(name, build_id, series=None, arch=None):
    if name == "chroot":
        from lpbuildd.target.chroot import Chroot
        backend_factory = Chroot
    elif name == "lxd":
        from lpbuildd.target.lxd import LXD
        backend_factory = LXD
    elif name == "fake":
        # Only for use in tests.
        from lpbuildd.tests.fakebuilder import FakeBackend
        backend_factory = FakeBackend
    elif name == "uncontained":
        # Only for use in tests.
        from lpbuildd.tests.fakebuilder import UncontainedBackend
        backend_factory = UncontainedBackend
    else:
        raise KeyError("Unknown backend: %s" % name)
    return backend_factory(build_id, series=series, arch=arch)
