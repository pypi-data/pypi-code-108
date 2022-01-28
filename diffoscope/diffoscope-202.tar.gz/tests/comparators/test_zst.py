#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2019 Jelle van der Waa <jelle@archlinux.org>
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

import subprocess

import pytest

from diffoscope.comparators.zst import ZstFile
from diffoscope.comparators.binary import FilesystemFile
from diffoscope.comparators.utils.specialize import specialize

from ..utils.tools import skip_unless_tools_exist


def zst_fixture(prefix):
    @pytest.fixture
    def zstd(tmpdir):
        input_ = str(tmpdir.join(prefix))
        output = str(tmpdir.join("{}.zst".format(prefix)))

        with open(input_, "w") as f:
            f.write(prefix)

        subprocess.check_call(("zstd", "--quiet", "--no-progress", input_))

        return specialize(FilesystemFile(output))

    return zstd


zst1 = zst_fixture("test1")
zst2 = zst_fixture("test2")


@skip_unless_tools_exist("zstd")
def test_identification(zst1):
    assert isinstance(zst1, ZstFile)


@skip_unless_tools_exist("zstd")
def test_no_differences(zst1):
    difference = zst1.compare(zst1)
    assert difference is None


@pytest.fixture
def differences(zst1, zst2):
    return zst1.compare(zst2).details


@skip_unless_tools_exist("zstd")
def test_content_source(differences):
    assert differences[0].source1 == "test1"
    assert differences[0].source2 == "test2"
