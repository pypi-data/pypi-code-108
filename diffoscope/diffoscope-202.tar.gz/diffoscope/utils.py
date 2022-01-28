#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2019-2020 Chris Lamb <lamby@debian.org>
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
import sys
import tempfile


def format_cmdline(cmd, replace=(), truncate=None):
    """
    NB. Takes a list of strings, not a string.
    """

    prefix = tempfile.gettempdir()

    def fn(x):
        if x in replace:
            return "{}"
        # Don't expose the full path name of the temporary directory
        if x.startswith(prefix):
            x = os.path.join("«TEMP»", x[len(prefix) + 1 :])
        x = repr(x)
        if " " not in x:
            x = x[1:-1]
        return x

    result = " ".join(fn(x) for x in cmd)

    if truncate is not None and len(result) > truncate:
        result = result[: truncate + 4] + " […]"

    return result


def format_bytes(size, decimal_places=2):
    # https://stackoverflow.com/a/43690506

    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if size < 1024.0:
            break
        size /= 1024.0

    return f"{size:.{decimal_places}f} {unit}"


def exit_if_paths_do_not_exist(*paths):
    flag = False
    for path in paths:
        if os.path.lexists(path):
            continue
        flag = True
        print(
            f"{sys.argv[0]}: {path}: No such file or directory",
            file=sys.stderr,
        )

    if flag:
        sys.exit(2)


def format_class(klass, strip=""):
    val = "{}.{}".format(klass.__module__, klass.__name__)

    if val.startswith(strip):
        val = val[len(strip) :]

    return val
