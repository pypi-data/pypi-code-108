#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2021—2022 Chris Lamb <lamby@debian.org>
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
import sys

from diffoscope.comparators.python import PycFile

from ..utils.data import assert_diff_startswith, load_fixture
from ..utils.nonexisting import assert_non_existing
from ..utils.tools import (
    skipif,
    skip_unless_file_version_is_at_least,
)

pyc1 = load_fixture("test1.pyc-renamed")
pyc2 = load_fixture("test2.pyc-renamed")


@skip_unless_file_version_is_at_least("5.39")
def test_identification(pyc1, pyc2):
    assert isinstance(pyc1, PycFile)
    assert isinstance(pyc2, PycFile)


@skipif(sys.version_info >= (3, 10), reason="Unstable on 3.10+")
def test_no_differences(pyc1):
    # Disassembling bytecode prior to Python 3.10 is stable when applied to
    # itself, otherwise various memory offsets (or memory addresses?) are
    # non-deterministic.
    assert pyc1.compare(pyc1) is None


@pytest.fixture
def differences(pyc1, pyc2):
    return pyc1.compare(pyc2).details


@skip_unless_file_version_is_at_least("5.39")
@skipif(
    sys.version_info < (3, 8),
    reason="Python 3.7 cannot de-marshal test1.pyc-renamed",
)
def test_diff(differences):
    assert_diff_startswith(
        differences[0],
        "pyc_expected_diff",
    )


def test_compare_non_existing(monkeypatch, pyc1):
    assert_non_existing(
        monkeypatch, pyc1, has_details=False, has_null_source=False
    )
