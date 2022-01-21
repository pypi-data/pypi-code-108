# -*- coding: utf-8 -*-
#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2020-2021 Conrad Ratschan <ratschance@gmail.com>
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

import os
import re
import logging
import subprocess

from diffoscope.tools import tool_required, tool_check_installed
from diffoscope.difference import Difference

from .utils import command
from .utils.archive import Archive
from .utils.file import File
from .utils.command import Command

logger = logging.getLogger(__name__)


class FitContainer(Archive):
    # Match the image string in dumpimage list output. Example: " Image 0 (ramdisk@0)"
    IMAGE_RE = re.compile(r"^\sImage ([0-9]+) \((.+)\)", re.MULTILINE)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._members = {}

    def open_archive(self):
        return self

    def close_archive(self):
        pass

    @tool_required("dumpimage")
    def get_member_names(self):
        image_info = command.our_check_output(
            ["dumpimage", "-l", self.source.path],
        )
        members = []
        for match in re.finditer(
            self.IMAGE_RE, image_info.decode(encoding="utf-8")
        ):
            pos, member_name = match.group(1, 2)
            # Save mapping of name -> position as dumpimage takes position as an argument
            self._members[member_name] = pos
            members.append(member_name)

        return members

    @tool_required("dumpimage")
    def extract(self, member_name, dest_dir):
        pos = self._members[member_name]
        dest_path = os.path.join(dest_dir, os.path.basename(member_name))
        logger.debug("fit image extracting %s to %s", member_name, dest_path)

        cmd = (
            "dumpimage",
            "-T",
            "flat_dt",
            "-p",
            pos,
            self.source.path,
            "-o",
            dest_path,
        )

        command.our_check_output(cmd)

        # Cannot rely on dumpimage returning a non-zero exit code on failure.
        if not os.path.exists(dest_path):
            raise subprocess.CalledProcessError(1, cmd)

        return dest_path


class FlattenedImageTreeContents(Command):
    @tool_required("dumpimage")
    def cmdline(self):
        return ["dumpimage", "-l", self.path]


class FlattenedImageTreeFile(File):
    """
    Flattened Image Trees (FIT) are a newer boot image format used by U-Boot. This
    format allows for multiple kernels, root filesystems, device trees, boot
    configurations, and checksums to be packaged into one file. It leverages the
    Flattened Device Tree Blob file format.
    """

    DESCRIPTION = "Flattened Image Tree blob files"
    CONTAINER_CLASSES = [FitContainer]

    @classmethod
    def recognizes(cls, file):
        # Detect file magic manually to workaround incorrect detection of devicetree
        # by libmagic when the devicetree structure section is larger than 1MB
        if file.file_header[:4] != b"\xd0\x0d\xfe\xed":
            return False

        if not tool_check_installed("fdtdump"):
            return False

        # Since the file type is the same as a Device Tree Blob, use fdtget (same
        # package as fdtdump) to differentiate between FIT/DTB
        root_nodes = (
            command.our_check_output(["fdtget", file.path, "-l", "/"])
            .decode(encoding="utf-8")
            .strip()
            .split("\n")
        )
        root_props = (
            command.our_check_output(["fdtget", file.path, "-p", "/"])
            .decode(encoding="utf-8")
            .strip()
            .split("\n")
        )

        # Check for mandatory FIT items used in U-Boot's FIT image verification routine
        return "description" in root_props and "images" in root_nodes

    def compare_details(self, other, source=None):
        return [
            Difference.from_operation(
                FlattenedImageTreeContents, self.path, other.path
            )
        ]
