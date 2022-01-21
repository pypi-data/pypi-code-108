#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2016-2020 Chris Lamb <lamby@debian.org>
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

import contextlib
import curses
import logging
import shutil
import sys


def line_eraser(fd=sys.stderr) -> bytes:
    eraser = b""  # avoid None to avoid 'NoneType + str/bytes' failures
    if fd.isatty():

        curses.setupterm(fd=fd.fileno())
        eraser = curses.tigetstr("el")

    if not eraser and fd.isatty():
        # is a tty, but doesn't support the proper escape code, so let's fake it

        width = shutil.get_terminal_size().columns
        eraser = b"\r" + (b" " * width) + b"\r"

    return eraser


@contextlib.contextmanager
def setup_logging(debug, log_handler):
    logger = logging.getLogger()
    old_level = logger.getEffectiveLevel()
    logger.setLevel(logging.DEBUG if debug else logging.WARNING)

    ch = log_handler or logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    logger.addHandler(ch)

    formatter = logging.Formatter(
        line_eraser().decode("ascii")
        + "%(asctime)s %(levelname).1s: %(name)s: %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )
    ch.setFormatter(formatter)
    try:
        yield logger
    finally:
        # restore old logging settings. this helps pytest not spew out errors
        # like "ValueError: I/O operation on closed file", see
        # https://github.com/pytest-dev/pytest/issues/14#issuecomment-272243656
        logger.removeHandler(ch)
        logger.setLevel(old_level)
