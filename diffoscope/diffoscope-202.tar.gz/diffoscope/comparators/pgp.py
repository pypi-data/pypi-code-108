#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2017-2021 Chris Lamb <lamby@debian.org>
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

from diffoscope.tools import tool_required, tool_check_installed
from diffoscope.tempfiles import get_temporary_directory
from diffoscope.difference import Difference

from .text import TextFile
from .utils.archive import Archive
from .utils.file import File
from .utils.command import Command, our_check_output

logger = logging.getLogger(__name__)


class Pgpdump(Command):
    @tool_required("pgpdump")
    def cmdline(self):
        return (
            "pgpdump",
            "-i",  # Dump integer packets
            "-m",  # Dump marker packets
            "-p",  # Dump private packets
            "-u",  # Display UTC time
            self.path,
        )


class PGPContainer(Archive):
    @tool_required("gpg")
    def open_archive(self):
        # Extract to a fresh temporary directory so that we can use the
        # embedded filename.

        self._temp_dir = get_temporary_directory(suffix="pgp")

        try:
            our_check_output(
                (
                    "gpg",
                    "--use-embedded-filename",
                    "--decrypt",
                    "--no-keyring",
                    os.path.abspath(self.source.path),
                ),
                cwd=self._temp_dir.name,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            return False

        return self

    def close_archive(self):
        self._temp_dir.cleanup()

    def get_member_names(self):
        # Will only return one filename, taken from the signature file itself.
        return os.listdir(self._temp_dir.name)

    def extract(self, member_name, dest_dir):
        return os.path.join(self._temp_dir.name, member_name)


class PgpFile(File):
    DESCRIPTION = "PGP signed/encrypted messages"
    FILE_TYPE_RE = re.compile(r"^PGP message\b")
    CONTAINER_CLASSES = [PGPContainer]
    FALLBACK_FILE_EXTENSION_SUFFIX = {".pgp", ".asc", ".pub", ".sec", ".gpg"}

    @classmethod
    def fallback_recognizes(cls, file):
        # Ensure we check FALLBACK_FILE_EXTENSION_SUFFIX, otherwise we run
        # pgpdump against all files that are recognised by file(1) as "data"
        if not super().fallback_recognizes(file):
            return False

        if file.magic_file_type == "data" and tool_check_installed("pgpdump"):
            try:
                output = our_check_output(
                    ("pgpdump", file.path), stderr=subprocess.DEVNULL
                )
            except subprocess.CalledProcessError:
                pass
            else:
                if b"New: unknown" not in output:
                    logger.debug("%s is a PGP file", file.path)
                    return True

            logger.debug("%s is not a PGP file", file.path)

        return False

    def compare_details(self, other, source=None):
        return [
            Difference.from_operation(
                Pgpdump, self.path, other.path, source="pgpdump"
            )
        ]


class PgpSignature(TextFile):
    DESCRIPTION = "PGP signatures"
    FILE_TYPE_RE = re.compile(r"^PGP signature\b")

    def compare(self, other, source=None):
        # Don't display signatures as hexdumps; use TextFile's comparisons...
        difference = super().compare(other, source)

        # ... but attach pgpdump of output
        difference.add_details(
            [
                Difference.from_operation(
                    Pgpdump, self.path, other.path, source="pgpdump"
                )
            ]
        )

        return difference
