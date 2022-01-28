#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2017, 2020 Chris Lamb <lamby@debian.org>
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

from diffoscope.comparators.fontconfig import FontconfigCacheFile

from ..utils.data import load_fixture, assert_diff

cache1 = load_fixture("test1-le64.cache-4")
cache2 = load_fixture("test2-le64.cache-4")


def test_identification(cache1):
    assert isinstance(cache1, FontconfigCacheFile)


def test_no_differences(cache1):
    difference = cache1.compare(cache1)
    assert difference is None


@pytest.fixture
def differences(cache1, cache2):
    return cache1.compare(cache2).details


def test_diff(differences):
    assert_diff(differences[0], "fontconfig_expected_diff")
