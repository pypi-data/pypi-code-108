#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2019-2021 Chris Lamb <lamby@debian.org>
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

from diffoscope.comparators.ffprobe import FfprobeFile

from ..utils.data import load_fixture, assert_diff
from ..utils.tools import skip_unless_tools_exist, skip_unless_tool_is_at_least
from ..utils.nonexisting import assert_non_existing

mp3_1 = load_fixture("test1.mp3")
mp3_2 = load_fixture("test2.mp3")


def ffprobe_version():
    return (
        subprocess.check_output(["ffprobe", "-version"])
        .decode("utf-8")
        .split()[2]
    )


def test_identification(mp3_1):
    assert isinstance(mp3_1, FfprobeFile)


def test_no_differences(mp3_1):
    difference = mp3_1.compare(mp3_1)
    assert difference is None


@pytest.fixture
def differences(mp3_1, mp3_2):
    return mp3_1.compare(mp3_2).details


@skip_unless_tools_exist("ffprobe")
@skip_unless_tool_is_at_least("ffprobe", ffprobe_version, "4.4")
def test_diff(differences):
    assert_diff(differences[0], "mp3_expected_diff")


@skip_unless_tools_exist("ffprobe")
def test_compare_non_existing(monkeypatch, mp3_1):
    assert_non_existing(monkeypatch, mp3_1, has_null_source=False)
