#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2017-2022 Chris Lamb <lamby@debian.org>
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
import subprocess

from diffoscope.tools import tool_required
from diffoscope.difference import Difference

from .utils.file import File
from .utils.command import Command


class Odt2txt(Command):
    @tool_required("odt2txt")
    def cmdline(self):
        # LibreOffice provides a "odt2txt" binary with different command-line
        # options.
        if self.odt2txt_variant() == "unoconv":
            return ("odt2txt", "--stdout", self.path)

        return ("odt2txt", "--width=-1", self.path)

    @staticmethod
    def odt2txt_variant():
        try:
            out = subprocess.check_output(["odt2txt", "--version"])
        except subprocess.CalledProcessError as e:
            out = e.output
        return out.decode("UTF-8").splitlines()[0].split()[0].strip()


class OdtFile(File):
    DESCRIPTION = "OpenOffice .odt files"
    FILE_TYPE_RE = re.compile(r"^OpenDocument Text\b")

    def compare_details(self, other, source=None):
        return [
            Difference.from_operation(
                Odt2txt, self.path, other.path, source="odt2txt"
            )
        ]
