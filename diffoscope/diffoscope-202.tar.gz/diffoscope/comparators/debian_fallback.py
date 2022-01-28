#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2015 Jérémy Bobbio <lunar@debian.org>
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

from .text import TextFile


class AbstractDebianFallbackFile(TextFile):
    def compare(self, other, *args, **kwargs):
        difference = super().compare(other, *args, **kwargs)
        if not difference:
            return None
        difference.add_comment(
            'Unable to find the "debian" Python module. Falling back to text comparison.'
        )
        return difference


class DotChangesFile(AbstractDebianFallbackFile):
    DESCRIPTION = "Debian .changes files"
    FILE_EXTENSION_SUFFIX = {".changes"}


class DotDscFile(AbstractDebianFallbackFile):
    DESCRIPTION = "Debian source packages (.dsc)"
    FILE_EXTENSION_SUFFIX = {".dsc"}


class DotBuildinfoFile(AbstractDebianFallbackFile):
    DESCRIPTION = "Debian .buildinfo files"
    FILE_EXTENSION_SUFFIX = {".buildinfo"}
