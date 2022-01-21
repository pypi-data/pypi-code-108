#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2016-2021 Chris Lamb <lamby@debian.org>
# Copyright © 2018 Mattia Rizzolo <mattia@debian.org>
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
import sys
import shutil
import logging
import tempfile

from .utils import format_bytes

_BASEDIR = None
_FILES = []

logger = logging.getLogger(__name__)


def get_named_temporary_file(*args, **kwargs):
    kwargs["dir"] = kwargs.pop("dir", _get_base_temporary_directory())

    if not kwargs.get("suffix", "_").startswith("_"):
        kwargs["suffix"] = "_{}".format(kwargs["suffix"])

    f = tempfile.NamedTemporaryFile(*args, **kwargs)
    _FILES.append(f.name)

    return f


def get_temporary_directory(*args, **kwargs):
    """
    Create and return a TemporaryDirectory

    Preferably use a "with" statement to control its lifetime:
        with get_temporary_directory() as tmpdir:

    The temporary directory is cleaned up at the end of the "with"
    statement. Otherwise it's cleaned up when the object is garbage collected.

    WARNING, don't do this:

        tmpdir = get_temporary_directory().name

    ... as this may result in the removal of the directory at some unexpected
    time in the future. (Or not at all, depending on whether there are other,
    unexpected, references to this instance.)
    """
    kwargs["dir"] = kwargs.pop("dir", _get_base_temporary_directory())

    if not kwargs.get("suffix", "_").startswith("_"):
        kwargs["suffix"] = "_{}".format(kwargs["suffix"])

    d = tempfile.TemporaryDirectory(*args, **kwargs)

    return d


def clean_all_temp_files():
    logger.debug("Cleaning %d temp files", len(_FILES))

    for x in _FILES:
        try:
            os.unlink(x)
        except FileNotFoundError:
            pass
        except:  # noqa
            logger.exception("Unable to delete %s", x)
    _FILES.clear()

    if _BASEDIR is not None:
        logger.debug(
            "Cleaning top-level temporary directory %s", _BASEDIR.name
        )

        shutil.rmtree(_BASEDIR.name, ignore_errors=True)

    if sys.version_info < (3, 8):
        # Some change in tempfile or weakref handling happened after Python
        # 3.7, resulting in us trying to delete our temporary files multiple
        # times. Unfortunately, the cleanup for TemporaryDirectory does not set
        # "ignore_errors", so we do that here.
        import tempfile

        def _rmtree(*args, **kwargs):
            kwargs.setdefault("ignore_errors", True)
            return shutil.rmtree(*args, **kwargs)

        tempfile._rmtree = _rmtree


def _get_base_temporary_directory():
    global _BASEDIR

    if _BASEDIR is None or not os.path.exists(_BASEDIR.name):
        try:
            # Try and generate a potentially-useful suffix to our temporary directory
            filtered_argv = [x for x in sys.argv if not x.startswith("-")]

            suffix = "_{}".format(
                re.sub(
                    r"[^\w]",
                    "",
                    os.path.basename(os.path.dirname(filtered_argv[-1])),
                )[-10:]
            )
        except IndexError:
            suffix = ""

        # Alias the TemporaryDirectory instance (not the .name instance) as the
        # directory may be reference-counted away.
        _BASEDIR = tempfile.TemporaryDirectory(
            dir=tempfile.gettempdir(),
            prefix="diffoscope_",
            suffix=suffix,
        )
        logger.debug(
            "Created top-level temporary directory: %s (free space: %s)",
            _BASEDIR.name,
            format_bytes(get_tempdir_free_space()),
        )

        with open(os.path.join(_BASEDIR.name, "argv"), "w") as f:
            print("\n".join(sys.argv), file=f)

    return _BASEDIR.name


def get_tempdir_free_space():
    """
    unsigned long f_frsize   Fundamental file system block size.
    fsblkcnt_t    f_blocks   Total number of blocks on file system in units of f_frsize.
    fsblkcnt_t    f_bfree    Total number of free blocks.
    fsblkcnt_t    f_bavail   Number of free blocks available to
                             non-privileged process.
    """
    statvfs = os.statvfs(tempfile.gettempdir())

    return statvfs.f_frsize * statvfs.f_bavail
