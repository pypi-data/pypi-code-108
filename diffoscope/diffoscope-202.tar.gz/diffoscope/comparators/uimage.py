#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2020 Conrad Ratschan <ratschance@gmail.com>
# Copyright © 2020 Chris Lamb <lamby@debian.org>
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

import logging
import os.path
import re
import subprocess

from .utils.file import File
from .utils.archive import Archive

logger = logging.getLogger(__name__)


class UimageContainer(Archive):
    def open_archive(self):
        return self

    def close_archive(self):
        pass

    def get_member_names(self):
        return [self.get_compressed_content_name(".uboot")]

    def extract(self, member_name, dest_dir):
        dest_path = os.path.join(dest_dir, member_name)
        logger.debug("uImage extracting to %s", dest_path)
        with open(dest_path, "wb") as fp:
            # Use tail to cut off the first 64 bytes without having to do a byte by byte copy in python
            subprocess.check_call(
                ["tail", "-c+65", self.source.path],
                shell=False,
                stdout=fp,
                stderr=None,
            )
        return dest_path


class UimageFile(File):
    """
    U-Boot legacy image files are standard OS boot files (kernel, rootfs) with a 64
    byte header appended to the front of the file by mkimage to provide the load
    address, entrypoint and a CRC for the contained image. By treating this as a
    container and setting our extract method to just cut the first 64 bytes off, the
    rest of diffoscope's tooling can be used to view the differences of the contained
    files.
    """

    DESCRIPTION = "U-Boot legacy image files"
    CONTAINER_CLASSES = [UimageContainer]
    FILE_TYPE_RE = re.compile(r"^u-boot legacy uImage\b")
