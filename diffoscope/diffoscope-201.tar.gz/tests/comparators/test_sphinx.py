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

import pytest

from diffoscope.comparators.sphinx import SphinxInventoryFile

from ..utils.data import assert_diff, load_fixture


inv1 = load_fixture("test1.inv")
inv2 = load_fixture("test2.inv")


def test_identification(inv1, inv2):
    assert isinstance(inv1, SphinxInventoryFile)
    assert isinstance(inv2, SphinxInventoryFile)


def test_no_differences(inv1):
    assert inv1.compare(inv1) is None


@pytest.fixture
def differences(inv1, inv2):
    return inv1.compare(inv2).details


def test_diff(differences):
    assert_diff(differences[0], "inv_expected_diff")
