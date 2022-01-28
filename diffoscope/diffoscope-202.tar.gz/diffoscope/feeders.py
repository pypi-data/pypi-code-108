#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2014-2015 Jérémy Bobbio <lunar@debian.org>
# Copyright © 2017, 2019-2020 Chris Lamb <lamby@debian.org>
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

import re
import hashlib
import logging
import subprocess
import functools

from .config import Config
from .profiling import profile

logger = logging.getLogger(__name__)

DIFF_CHUNK = 4096


@functools.lru_cache(maxsize=128)
def compile_string_regex(regex_str):
    return re.compile(regex_str)


@functools.lru_cache(maxsize=128)
def compile_bytes_regex(regex_str):
    return re.compile(regex_str.encode("utf-8"))


def filter_reader(buf, additional_filter=None):
    # Apply the passed filter first, for example Command.filter
    if additional_filter:
        buf = additional_filter(buf)

    # No need to work on empty lines
    if not buf:
        return buf

    # Use either str or bytes objects depending on buffer type
    if isinstance(buf, str):
        compile_func = compile_string_regex
        replace = "[masked]"
    else:
        compile_func = compile_bytes_regex
        replace = b"[masked]"

    for regex in Config().diff_masks:
        buf = compile_func(regex).sub(replace, buf)

    return buf


def from_raw_reader(in_file, filter=None):
    def feeder(out_file):
        max_lines = Config().max_diff_input_lines
        end_nl = False
        line_count = 0

        # If we have a maximum size, hash the content as we go along so we can
        # display a nicer message.
        h = None
        if max_lines < float("inf"):
            h = hashlib.sha256()

        for buf in in_file:
            line_count += 1
            out = filter_reader(buf, filter)

            if h is not None:
                h.update(out)

            if line_count < max_lines:
                out_file.write(out)
                # very long lines can sometimes interact negatively with
                # python buffering; force a flush here to avoid this,
                # see https://bugs.debian.org/870049
                out_file.flush()
            if buf:
                end_nl = buf[-1] == "\n"

        if h is not None and line_count >= max_lines:
            out_file.write(
                "[ Too much input for diff (SHA256: {}) ]\n".format(
                    h.hexdigest()
                ).encode("utf-8")
            )
            end_nl = True

        return end_nl

    return feeder


def from_text_reader(in_file, filter=None):
    if filter is None:

        def encoding_filter(text_buf):
            return text_buf.encode("utf-8")

    else:

        def encoding_filter(text_buf):
            return filter(text_buf).encode("utf-8")

    return from_raw_reader(in_file, encoding_filter)


def from_operation(operation):
    def feeder(out_file):
        with profile("command", operation.name):
            feeder = from_raw_reader(operation.output, operation.filter)
            end_nl = feeder(out_file)

        if operation.should_show_error():
            # On error, default to displaying all lines of the error
            output = operation.error_string or ""
            if not output and operation.output:
                # ... but if we don't have, return the first line of the
                # standard output.
                output = "{}{}".format(
                    operation.output[0].decode("utf-8", "ignore").strip(),
                    "\n[…]" if len(operation.output) > 1 else "",
                )
            raise subprocess.CalledProcessError(
                operation.returncode,
                [operation.full_name()],
                output=output.encode("utf-8"),
            )
        return end_nl

    return feeder


def from_text(content):
    """
    Works for both bytes and str objects.
    """

    def feeder(f):
        for offset in range(0, len(content), DIFF_CHUNK):
            buf = filter_reader(content[offset : offset + DIFF_CHUNK])
            if isinstance(buf, str):
                f.write(buf.encode("utf-8"))
            else:
                f.write(buf)

        return content and content[-1] == "\n"

    return feeder


def empty():
    def feeder(f):
        return False

    return feeder
