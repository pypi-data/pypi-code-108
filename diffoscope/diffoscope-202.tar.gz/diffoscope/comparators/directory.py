#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2015 Jérémy Bobbio <lunar@debian.org>
# Copyright © 2015-2021 Chris Lamb <lamby@debian.org>
#
# diffoscope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# diffoscope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with diffoscope.  If not, see <https://www.gnu.org/licenses/>.

import os
import re
import logging
import subprocess

from diffoscope.exc import RequiredToolNotFound
from diffoscope.tools import python_module_missing, tool_required
from diffoscope.config import Config
from diffoscope.difference import Difference

from .binary import FilesystemFile
from .missing_file import AbstractMissingType
from .utils.command import Command, our_check_output
from .utils.container import Container

logger = logging.getLogger(__name__)


if os.uname()[0] == "FreeBSD":

    class Stat(Command):
        @tool_required("stat")
        def cmdline(self):
            return [
                "stat",
                "-t",
                "%Y-%m-%d %H:%M:%S",
                "-f",
                "%Sp %l %Su %Sg %z %Sm %k %b %#Xf",
                self.path,
            ]

else:

    class Stat(Command):
        @tool_required("stat")
        def cmdline(self):
            return ["stat", self.path]

        FILE_RE = re.compile(r"^\s*File:.*$")
        DEVICE_RE = re.compile(r"Device: [0-9a-f]+h/[0-9]+d\s+")
        INODE_RE = re.compile(r"Inode: [0-9]+\s+")
        ACCESS_TIME_RE = re.compile(r"^Access: [0-9]{4}-[0-9]{2}-[0-9]{2}.*$")
        CHANGE_TIME_RE = re.compile(r"^Change: [0-9]{4}-[0-9]{2}-[0-9]{2}.*$")
        BIRTH_TIME_RE = re.compile(r"^\s*Birth:.*$")

        def filter(self, line):
            line = line.decode("utf-8")
            line = Stat.FILE_RE.sub("", line)
            line = Stat.DEVICE_RE.sub("", line)
            line = Stat.INODE_RE.sub("", line)
            line = Stat.ACCESS_TIME_RE.sub("", line)
            line = Stat.CHANGE_TIME_RE.sub("", line)
            line = Stat.BIRTH_TIME_RE.sub("", line)
            return line.encode("utf-8")


# compare only what matters
def stat_results_same(stat1, stat2):
    return all(
        getattr(stat1, i) == getattr(stat2, i)
        for i in [
            "st_mode",
            "st_uid",
            "st_gid",
            "st_size",
            "st_mtime",
        ]
    )


@tool_required("lsattr")
def lsattr(path):
    """
    NB. Difficult to replace with in-Python version. See
    <https://stackoverflow.com/questions/35501249/python-get-linux-file-immutable-attribute/38092961#38092961>
    """

    try:
        output = our_check_output(
            ["lsattr", "-d", path], stderr=subprocess.STDOUT
        ).decode("utf-8")
        return output.split()[0]
    except subprocess.CalledProcessError as e:
        if e.returncode == 1:
            # filesystem doesn't support xattrs
            return ""


class Getfacl(Command):
    @tool_required("getfacl")
    def cmdline(self):
        osname = os.uname()[0]
        if osname == "FreeBSD":
            return ["getfacl", "-q", "-h", self.path]
        return ["getfacl", "-p", "-c", self.path]


def xattr(path1, path2):
    try:
        import xattr as xattr_
    except ImportError:
        python_module_missing("xattr")
        return None

    # Support the case where the python3-xattr package is installed but
    # python3-pyxattr is not; python3-xattr has an xattr class that can be used
    # like a dict.
    try:
        get_all = xattr_.get_all
    except AttributeError:

        def get_all(x):
            return xattr_.xattr(x).items()

    def fn(x):
        return "\n".join(
            "{}: {}".format(
                k.decode("utf-8", "ignore"), v.decode("utf-8", "ignore")
            )
            for k, v in get_all(x)
        )

    return Difference.from_text(
        fn(path1), fn(path2), path1, path2, source="extended file attributes"
    )


def compare_meta(path1, path2):
    if Config().exclude_directory_metadata in ("yes", "recursive"):
        logger.debug(
            "Excluding directory metadata for paths (%s, %s)", path1, path2
        )
        return []

    logger.debug("compare_meta(%r, %r)", path1, path2)

    # Don't run any commands if any of the paths do not exist
    # or have other issues.
    try:
        stat1 = os.lstat(path1)
        stat2 = os.lstat(path2)
    except Exception:
        return []

    differences = []
    if stat_results_same(stat1, stat2):
        logger.debug("Stat structs are identical, moving on!")
    else:
        try:
            differences.append(
                Difference.from_operation(Stat, path1, path2, short=True)
            )
        except RequiredToolNotFound:
            logger.error("Unable to find 'stat'! Is PATH wrong?")

    if os.path.islink(path1) or os.path.islink(path2):
        return [d for d in differences if d is not None]

    if Config().extended_filesystem_attributes:
        try:
            differences.append(
                Difference.from_operation(Getfacl, path1, path2, short=True)
            )
        except RequiredToolNotFound:
            logger.info(
                "Unable to find 'getfacl', some directory metadata differences might not be noticed."
            )

        try:
            lsattr1 = lsattr(path1)
            lsattr2 = lsattr(path2)
            differences.append(
                Difference.from_text(
                    lsattr1, lsattr2, path1, path2, source="lsattr"
                )
            )
        except RequiredToolNotFound:
            logger.info(
                "Unable to find 'lsattr', some directory metadata differences might not be noticed."
            )
        differences.append(xattr(path1, path2))

    return [d for d in differences if d is not None]


def compare_directories(path1, path2, source=None):
    return FilesystemDirectory(path1).compare(FilesystemDirectory(path2))


class Directory:
    DESCRIPTION = "directories"

    @classmethod
    def recognizes(cls, file):
        return file.is_directory()

    @classmethod
    def fallback_recognizes(cls, file):
        return False


class FilesystemDirectory(Directory):
    def __init__(self, path):
        self._path = path

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._path

    @property
    def progress_name(self):
        x = self.name
        return x[1:] if x.startswith("./") else x

    @property
    def as_container(self):
        if not hasattr(self, "_as_container"):
            self._as_container = DirectoryContainer(self)
        return self._as_container

    def is_directory(self):
        return True

    def has_same_content_as(self, other):
        # no shortcut
        return False

    def compare(self, other, source=None):
        differences = []

        if not isinstance(other, FilesystemDirectory):
            return differences

        # We don't need to recurse into subdirectories; DirectoryContainer will
        # find them and do that for us.
        def list_files(path):
            return sorted(os.listdir(os.path.realpath(path)))

        listing_diff = Difference.from_text(
            "\n".join(list_files(self.path)),
            "\n".join(list_files(other.path)),
            self.path,
            other.path,
            source="file list",
        )
        if listing_diff:
            differences.append(listing_diff)

        if not isinstance(other, AbstractMissingType):
            differences.extend(compare_meta(self.name, other.name))

        my_container = DirectoryContainer(self)
        other_container = DirectoryContainer(other)
        differences.extend(my_container.compare(other_container))

        if not differences:
            return None

        difference = Difference(self.path, other.path, source)
        difference.add_details(differences)
        return difference


class DirectoryContainer(Container):
    def get_member_names(self):
        return sorted(os.listdir(self.source.path or "."))

    def get_member(self, member_name):
        member_path = os.path.join(self.source.path, member_name)

        if not os.path.islink(member_path) and os.path.isdir(member_path):
            return FilesystemDirectory(member_path)

        return FilesystemFile(
            os.path.join(self.source.path, member_name), container=self
        )
