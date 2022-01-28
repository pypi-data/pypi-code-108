#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2016-2022 Chris Lamb <lamby@debian.org>
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
import abc
import magic
import logging
import subprocess

from diffoscope.exc import (
    RequiredToolNotFound,
    OutputParsingError,
    ContainerExtractionError,
)
from diffoscope.tools import tool_required
from diffoscope.utils import format_cmdline, format_class
from diffoscope.config import Config
from diffoscope.profiling import profile
from diffoscope.difference import Difference

try:
    import tlsh
except ImportError:  # noqa
    tlsh = None

SMALL_FILE_THRESHOLD = 65536  # 64 kiB

logger = logging.getLogger(__name__)


def path_apparent_size(path=".", visited=None):
    # should output the same as `du --apparent-size -bs "$path"`
    if not visited:
        stat = os.stat(path, follow_symlinks=False)
        visited = {stat.st_ino: stat.st_size}
    if os.path.isdir(path) and not os.path.islink(path):
        for entry in os.scandir(path):
            inode = entry.inode()
            if inode in visited:
                continue
            visited[inode] = entry.stat(follow_symlinks=False).st_size
            if entry.is_dir(follow_symlinks=False):
                path_apparent_size(entry.path, visited)
    return sum(visited.values())


def _run_tests(fold, tests):
    return fold(t(y, x) for x, t, y in tests)


class File(metaclass=abc.ABCMeta):
    """
    There are two Python modules named 'magic'. One of these ships with the
    file upstream under the python/ directory and PyPI's `python-magic` and
    they have slightly different interfaces despite attempts at a compatibility
    layer.
    """

    # Try and detect the instance of the libmagic shared library (loaded via
    # ctypes) used by the magic.py shipped with file.
    #
    if hasattr(magic, "_libraries"):

        @classmethod
        def guess_file_type(cls, path):
            if not hasattr(cls, "_mimedb"):
                cls._mimedb = magic.open(magic.NONE)
                cls._mimedb.load()
            return cls._mimedb.file(
                path.encode("utf-8", errors="surrogateescape")
            )

        @classmethod
        def guess_encoding(cls, path):
            if not hasattr(cls, "_mimedb_encoding"):
                cls._mimedb_encoding = magic.open(magic.MAGIC_MIME_ENCODING)
                cls._mimedb_encoding.load()
            return cls._mimedb_encoding.file(path)

    else:
        # Assume we are using python-magic

        @classmethod
        def guess_file_type(cls, path):
            if not hasattr(cls, "_mimedb"):
                cls._mimedb = magic.Magic()
            return maybe_decode(cls._mimedb.from_file(path))

        @classmethod
        def guess_encoding(cls, path):
            if not hasattr(cls, "_mimedb_encoding"):
                cls._mimedb_encoding = magic.Magic(mime_encoding=True)
            return maybe_decode(cls._mimedb_encoding.from_file(path))

    def __init__(self, container=None):
        self._comments = []
        self._container = container

    def __repr__(self):
        return f"<{self.__class__} {self.name}>"

    # This should return a path that allows to access the file content
    @property
    @abc.abstractmethod
    def path(self):
        raise NotImplementedError()

    # Remove any temporary data associated with the file. The function
    # should be idempotent and work during the destructor.
    def cleanup(self):
        if hasattr(self, "_as_container"):
            del self._as_container

    def __del__(self):
        self.cleanup()

    FILE_EXTENSION_SUFFIX = None
    FILE_TYPE_RE = None
    FILE_TYPE_HEADER_PREFIX = None  # max 16 bytes

    @classmethod
    def recognizes(cls, file):
        """Check if a file's type matches the one represented by this class.

        The default test returns True if the file matches these tests:

        (cls.FILE_TYPE_RE OR
         cls.FILE_TYPE_HEADER_PREFIX) AND
        (cls.FILE_EXTENSION_SUFFIX)

        If any test is None then the test is ignored and effectively deleted
        from the above definition.

        By default, the tests are all None and the test returns False for all
        files. Subclasses may override them with specific values, or override
        this method to implement a totally different test.
        """
        # The structure below allows us to construct a boolean tree of tests
        # that can be combined with all() and any(). Tests that are not defined
        # for a class are filtered out, so that we don't get into a "vacuous
        # truth" situation like a naive all([]) invocation would give.

        file_type_tests = [
            test
            for test in (
                (
                    cls.FILE_TYPE_RE,
                    lambda m, t: t.search(m),
                    file.magic_file_type,
                ),
                (
                    cls.FILE_TYPE_HEADER_PREFIX,
                    bytes.startswith,
                    file.file_header,
                ),
            )
            if test[0]
        ]  # filter out undefined tests

        all_tests = [
            test
            for test in (
                (cls.FILE_EXTENSION_SUFFIX, cls.any_endswith, file.name),
                (file_type_tests, _run_tests, any),
            )
            if test[0]
        ]  # filter out undefined tests, inc. file_type_tests if it's empty

        return _run_tests(all, all_tests) if all_tests else False

    FALLBACK_FILE_EXTENSION_SUFFIX = None
    FALLBACK_FILE_TYPE_HEADER_PREFIX = None  # max 16 bytes

    @classmethod
    def fallback_recognizes(cls, file):
        """This is checked if the file could not be identified by recognizes().
        This helps to work around bugs in file(1), see Debian bug #876316.

        The default test returns True if the file matches these tests:

        (cls.FALLBACK_FILE_EXTENSION_SUFFIX AND cls.FILE_EXTENSION_SUFFIX) AND
        (cls.FALLBACK_FILE_TYPE_HEADER_PREFIX AND cls.FILE_TYPE_HEADER_PREFIX)

        We also AND-compare with the non-fallback versions to ensure that
        subclasses don't "accidentally match" (e.g. IpkFile vs GzipFile).
        """
        if cls.recognizes.__func__ != File.recognizes.__func__:
            # If the class has overridden the default recognizes() then the
            # logic below about AND-comparing with the non-fallback versions is
            # not valid, they have to re-implement it
            return False

        all_tests = [
            test
            for test in (
                (
                    cls.FALLBACK_FILE_EXTENSION_SUFFIX,
                    cls.any_endswith,
                    file.name,
                ),
                (cls.FILE_EXTENSION_SUFFIX, cls.any_endswith, file.name),
                (
                    cls.FALLBACK_FILE_TYPE_HEADER_PREFIX,
                    bytes.startswith,
                    file.file_header,
                ),
                (
                    cls.FILE_TYPE_HEADER_PREFIX,
                    bytes.startswith,
                    file.file_header,
                ),
            )
            if test[0]
        ]  # filter out undefined tests, inc. file_type_tests if it's empty

        return _run_tests(all, all_tests) if all_tests else False

    @staticmethod
    def any_endswith(val, candidates):
        """
        Return true iff `val` ends with any string present in `candidates`
        iterable.
        """

        for x in candidates:
            if val.endswith(x):
                return True

        return False

    # This might be different from path and is used to do file extension matching
    @property
    def name(self):
        return self._name

    @property
    def container(self):
        return self._container

    CONTAINER_CLASSES = []

    @property
    def as_container(self):
        klasses = self.__class__.CONTAINER_CLASSES

        if not klasses:
            if hasattr(self, "_other_file"):
                return self._other_file.__class__.CONTAINER_CLASSES[0](self)
            return None

        if hasattr(self, "_as_container"):
            return self._as_container

        self._as_container = None

        # Try each container class in turn, returning the first one that
        # instantiates without error.
        for klass in klasses:
            formatted_class = format_class(
                klass, strip="diffoscope.comparators."
            )

            logger.debug(
                "Instantiating a %s for %s",
                formatted_class,
                self.name,
            )
            try:
                self._as_container = klass(self)

                return self._as_container
            except RequiredToolNotFound as exc:
                logger.debug(
                    "Cannot instantiate a %s; missing tool %s",
                    formatted_class,
                    exc.operation,
                )
                try:
                    infix = type(self).DESCRIPTION
                except AttributeError:
                    infix = "this file format"
                msg = (
                    "Format-specific differences are supported for {}.".format(
                        infix
                    )
                )
                self._comments.append(exc.get_comment(msg))

    @property
    def progress_name(self):
        x = self._name

        return x[1:] if x.startswith("./") else x

    @property
    def magic_file_type(self):
        if not hasattr(self, "_magic_file_type"):
            self._magic_file_type = File.guess_file_type(self.path)
        return self._magic_file_type

    @property
    def file_header(self):
        if not hasattr(self, "_file_header"):
            with open(self.path, "rb") as f:
                self._file_header = f.read(16)
        return self._file_header

    @property
    def file_type(self):
        for x, y in (
            (self.is_device, "device"),
            (self.is_symlink, "symlink"),
            (self.is_directory, "directory"),
        ):
            if x():
                return y

        return "file"

    if tlsh:

        @property
        def fuzzy_hash(self):
            def calc():
                # tlsh is not meaningful with files smaller than 512 bytes
                try:
                    if os.stat(self.path).st_size < 512:
                        return None
                except FileNotFoundError:
                    # eg. invalid symlink
                    return None

                h = tlsh.Tlsh()
                with open(self.path, "rb") as f:
                    for buf in iter(lambda: f.read(32768), b""):
                        h.update(buf)
                h.final()

                try:
                    return h.hexdigest()
                except ValueError:
                    # File must contain a certain amount of randomness.
                    return None

            if not hasattr(self, "_fuzzy_hash"):
                self._fuzzy_hash = calc()
            return self._fuzzy_hash

    @abc.abstractmethod
    def is_directory():
        raise NotImplementedError()

    @abc.abstractmethod
    def is_symlink():
        raise NotImplementedError()

    @abc.abstractmethod
    def is_device():
        raise NotImplementedError()

    def compare_bytes(self, other, source=None):
        from .compare import compare_binary_files

        # Don't attempt to compare directories with any other type as binaries
        if os.path.isdir(self.path) or os.path.isdir(other.path):
            return Difference.from_text(
                "type: {}".format(self.file_type),
                "type: {}".format(other.file_type),
                self.name,
                other.name,
                source,
            )

        return compare_binary_files(self, other, source)

    @staticmethod
    def _mangle_file_type(val):
        # Strip off trailing (eg.) "original size modulo 2^32 671" from
        # gzip compressed data as this is just a symptom of the contents itself
        # changing that will be reflected elsewhere.
        if val.startswith("gzip compressed data"):
            val = re.compile(r", original size modulo 2\^\d+ \d+$").sub(
                "", val
            )

        return val

    def _compare_using_details(self, other, source):
        details = []
        difference = Difference(self.name, other.name, source=source)

        if hasattr(self, "compare_details"):
            details.extend(self.compare_details(other, source))
        if self.as_container:
            if self.as_container.auto_diff_metadata:
                details.extend(
                    [
                        Difference.from_text(
                            self._mangle_file_type(self.magic_file_type),
                            self._mangle_file_type(other.magic_file_type),
                            self,
                            other,
                            source="filetype from file(1)",
                        ),
                        Difference.from_text(
                            self.__class__.__name__,
                            other.__class__.__name__,
                            self,
                            other,
                            source="filetype from diffoscope",
                        ),
                    ]
                )
            # Don't recurse forever on archive quines, etc.
            depth = self._as_container.depth
            no_recurse = depth >= Config().max_container_depth
            if no_recurse:
                msg = "Reached max container depth ({})".format(depth)
                logger.debug(msg)
                difference.add_comment(msg)
            elif Config().timeout_exceeded():
                msg = "Timeout exceeded; details may be incomplete."
                logger.debug(msg)
                difference.add_comment(msg)
                no_recurse = True

            details.extend(
                self.as_container.compare(
                    other.as_container, no_recurse=no_recurse
                )
            )

        details = [x for x in details if x]
        if not details:
            return None
        difference.add_details(details)

        return difference

    def has_same_content_as(self, other):
        logger.debug(
            "has_same_content(%s, %s)", self.path or "-", other.path or "-"
        )
        if os.path.isdir(self.path) or os.path.isdir(other.path):
            return False
        # try comparing small files directly first
        try:
            my_size = os.path.getsize(self.path)
            other_size = os.path.getsize(other.path)
        except OSError:
            # files not readable (e.g. broken symlinks) or something else,
            # just assume they are different
            return False
        if my_size != other_size:
            return False

        # Compare from python the first bytes, and only if they are
        # identical then call external command.
        assert my_size == other_size
        try:
            with profile("command", "cmp (internal)"):
                with open(self.path, "rb") as file1, open(
                    other.path, "rb"
                ) as file2:
                    content1 = file1.read(SMALL_FILE_THRESHOLD)
                    content2 = file2.read(SMALL_FILE_THRESHOLD)
        except OSError:
            # one or both files could not be opened for some reason,
            # assume they are different
            return False

        if content1 != content2:
            return False
        if my_size <= SMALL_FILE_THRESHOLD:
            return True

        # Big files, same size, same first bytes
        return self.cmp_external(other)

    @tool_required("cmp")
    def cmp_external(self, other):
        cmdline = ("cmp", "-s", self.path, other.path)
        logger.debug("Executing: %s", " ".join(cmdline))

        with profile("command", "cmp (external)"):
            return subprocess.call(cmdline, close_fds=True) == 0

    # To be specialized directly, or by implementing compare_details
    def compare(self, other, source=None):
        if hasattr(self, "compare_details") or self.as_container:
            try:
                difference = self._compare_using_details(other, source)
                # no differences detected inside? let's at least do a binary diff
                if difference is None:
                    difference = self.compare_bytes(other, source=source)
                    if difference is None:
                        return None
                    try:
                        infix = type(self).DESCRIPTION
                    except AttributeError:
                        infix = "this file format"
                    suffix = ""
                    if self.magic_file_type != "data":
                        suffix = " file(1) reports: {}".format(
                            self.magic_file_type
                        )
                    difference.add_comment(
                        "Format-specific differences are supported for {} but "
                        "no file-specific differences were detected; falling "
                        "back to a binary diff.{}".format(infix, suffix)
                    )
            except subprocess.CalledProcessError as e:
                difference = self.compare_bytes(other, source=source)
                if difference is None:
                    return None

                # Include either stderr (prefered) or stdout in the hexdump
                # difference
                suffix = None
                for prefix, val in (
                    ("Standard output", e.stdout),
                    ("Standard error", e.stderr),
                ):
                    if not val:
                        continue
                    suffix = " {}:\n{}".format(
                        prefix,
                        re.sub(
                            r"^",
                            "    ",
                            val.decode("utf-8").strip(),
                            flags=re.MULTILINE,
                        ),
                    )

                    # Truncate output
                    max_len = 250
                    if len(suffix) > max_len:
                        suffix = "{}  [...]".format(suffix[:max_len])

                difference.add_comment(
                    "Command `{}` failed with exit code {}.{}".format(
                        format_cmdline(e.cmd),
                        e.returncode,
                        suffix or " (No output)",
                    )
                )
            except RequiredToolNotFound as e:
                difference = self.compare_bytes(other, source=source)
                if difference is None:
                    return None
                difference.add_comment(
                    e.get_comment("Falling back to binary comparison.")
                )
            except OutputParsingError as e:
                difference = self.compare_bytes(other, source=source)
                if difference is None:
                    return None
                difference.add_comment(
                    f"Error parsing output of `{e.operation}` for {e.object_class}"
                )
            except ContainerExtractionError as e:
                difference = self.compare_bytes(other, source=source)
                if difference is None:
                    return None
                difference.add_comment(
                    "Error extracting '{}', falling back to "
                    'binary comparison: "{}"'.format(e.pathname, e.wrapped_exc)
                )

            # Append any miscellaneous comments for this file.
            for x in getattr(self, "_comments", []):
                difference.add_comment(x)

            return difference
        return self.compare_bytes(other, source)

    def add_comment(self, msg):
        self._comments.append(msg)


def maybe_decode(s):
    """
    Helper function to convert to bytes if necessary.
    """

    if type(s) is bytes:
        return s.decode("utf-8")
    return s
