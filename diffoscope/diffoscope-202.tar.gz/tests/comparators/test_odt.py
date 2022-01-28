#
# diffoscope: in-depth comparison of files, archives, and directories
#
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
import subprocess

from diffoscope.comparators.odt import OdtFile

from ..utils.data import load_fixture, assert_diff
from ..utils.tools import skip_unless_tool_is_at_least

from ..utils.nonexisting import assert_non_existing

odt1 = load_fixture("test1.odt")
odt2 = load_fixture("test2.odt")


def odt2txt_version():
    try:
        out = subprocess.check_output(["odt2txt", "--version"])
    except subprocess.CalledProcessError as e:
        out = e.output
    return out.decode("UTF-8").splitlines()[0].split()[1].strip()


def test_identification(odt1):
    assert isinstance(odt1, OdtFile)


def test_no_differences(odt1):
    difference = odt1.compare(odt1)
    assert difference is None


@pytest.fixture
def differences(odt1, odt2):
    return odt1.compare(odt2).details


@skip_unless_tool_is_at_least("odt2txt", odt2txt_version, "0.7")
def test_diff(differences):
    assert_diff(differences[0], "odt_expected_diff")


@skip_unless_tool_is_at_least("odt2txt", odt2txt_version, "0.7")
def test_compare_non_existing(monkeypatch, odt1):
    assert_non_existing(monkeypatch, odt1, has_null_source=False)
