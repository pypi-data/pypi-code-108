#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2021 Chris Lamb <lamby@debian.org>
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

import zlib

from diffoscope.difference import Difference

from .utils.file import File

MAGIC = b"# Sphinx inventory version"


class SphinxInventoryFile(File):
    DESCRIPTION = "Sphinx inventory files"
    FILE_EXTENSION_SUFFIX = {".inv"}

    def compare_details(self, other, source=None):
        return [
            Difference.from_text(
                describe_inventory(self.path),
                describe_inventory(other.path),
                self.path,
                other.path,
                source="Sphinx inventory",
            )
        ]


def describe_inventory(filename):
    head = b""
    tail = b""

    with open(filename, "rb") as f:
        for line in f:
            if line.startswith(b"#"):
                # Save commented lines at top of file
                head += line
            else:
                # ... save the rest for decompression
                tail += line

    result = head + b"\n" if head else b""

    try:
        result += zlib.decompress(tail)
    except zlib.error:
        # Even if the file is labelled "The remainder of this file is
        # compressed using zlib.", it might not actually be. In this case,
        # simply return the original content.
        result += tail

    return result.decode("utf-8", "ignore")
