# Copyright (c) 2019-2020 Jonathan Sambrook and Codethink Ltd.
#
#    This file is part of Topplot.
#
#    Topplot is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Topplot is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Topplot.  If not, see <https://www.gnu.org/licenses/>.
#
# ------------------------------------------------------------------------------

import re
import sys
import tempfile

# ------------------------------------------------------------------------------
# Exit with error, displaying msg to stderr


def die(msg):
    print(f"ERR: {msg}", file=sys.stderr)
    sys.exit(1)


# ------------------------------------------------------------------------------
# Display labelled warning message to stderr


def warn(msg):
    print(f"WARN: {msg}", file=sys.stderr)


# ------------------------------------------------------------------------------
# Display labelled informational message to stderr


def info(msg):
    print(f"INFO: {msg}", file=sys.stderr)


# ------------------------------------------------------------------------------
# Convert DD:HH:MM:SS to seconds (re based to flexibly handle optional day/hour/minutes)
# Dies on failure to parse!

RE_DHMS_TO_SEC = re.compile(
    r"^((?P<d>\d+):){0,1}?((?P<h>\d+):){0,1}?((?P<m>\d+):){0,1}?(?P<s>\d\d)$"
)


def dhms_to_sec(text):
    m = RE_DHMS_TO_SEC.match(text)

    if not m:
        die(f"'{text}' doesn't parse as a timestamp with format [[[D:]HH:]MM:]SS")

    groups = m.groupdict()
    d = int(groups["d"]) if groups["d"] else 0
    h = int(groups["h"]) if groups["h"] else 0
    m = int(groups["m"]) if groups["m"] else 0
    s = int(groups["s"])
    # print(f"{text} → d: {d}  h: {h}  m: {m}  s: {s}")
    return d * 24 * 3600 + h * 3600 + m * 60 + s


# ------------------------------------------------------------------------------


def is_dir_writable(path):
    try:
        testfile = tempfile.TemporaryFile(dir=path)
        testfile.close()
    except OSError as e:
        e.filename = path
        raise
    return True


# ------------------------------------------------------------------------------
# vi: sw=4:ts=4:et
