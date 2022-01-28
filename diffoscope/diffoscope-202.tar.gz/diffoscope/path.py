#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2017, 2020, 2021 Chris Lamb <lamby@debian.org>
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


def set_path():
    to_add = ["/sbin", "/usr/sbin", "/usr/local/sbin"]
    pathlist = os.environ["PATH"].split(os.pathsep)

    # Check the /usr/lib/<multiarch-triplet directory as well.
    try:
        arch_dir = os.path.join("/usr/lib", sys.implementation._multiarch)
    except AttributeError:
        pass
    else:
        if os.path.exists(arch_dir):
            to_add.append(arch_dir)

    for x in to_add:
        if x not in pathlist:
            pathlist.append(x)

    os.environ["PATH"] = os.pathsep.join(pathlist)
