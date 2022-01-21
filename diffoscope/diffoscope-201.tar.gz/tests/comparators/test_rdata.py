#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2017 Ximin Luo <infinity0@debian.org>
# Copyright © 2017, 2020-2021 Chris Lamb <lamby@debian.org>
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

import pytest

from diffoscope.comparators.gzip import GzipFile
from diffoscope.comparators.rdata import RdbFile

from ..utils.data import load_fixture, get_data, assert_diff
from ..utils.tools import skip_unless_tools_exist


rdb1 = load_fixture("test1.rdb")
rdb2 = load_fixture("test2.rdb")
rdx1 = load_fixture("test1.rdx")
rdx2 = load_fixture("test2.rdx")


def test_identification(rdb1, rdx1):
    assert isinstance(rdb1, RdbFile)
    assert isinstance(rdx1, GzipFile)


def test_no_differences(rdb1, rdx1):
    assert rdx1.compare(rdx1) is None
    assert rdx1.compare(rdx1) is None


@pytest.fixture
def differences_rdb(rdb1, rdb2):
    return rdb1.compare(rdb2).details


@pytest.fixture
def differences_rdx(rdx1, rdx2):
    return rdx1.compare(rdx2).details


@skip_unless_tools_exist("Rscript")
def test_num_items_rdb(differences_rdb):
    assert len(differences_rdb) == 1


@skip_unless_tools_exist("Rscript")
def test_item_rdb(differences_rdb):
    assert differences_rdb[0].source1.startswith("Rscript")
    assert_diff(differences_rdb[0], "rdb_expected_diff")


@skip_unless_tools_exist("Rscript")
def test_num_items_rdx(differences_rdx):
    assert len(differences_rdx) == 1


@skip_unless_tools_exist("Rscript")
def test_item_rdx(differences_rdx):
    assert differences_rdx[0].source1 == "test1.rdx-content"
    assert differences_rdx[0].source2 == "test2.rdx-content"
    assert_diff(differences_rdx[0].details[0], "rds_expected_diff")
