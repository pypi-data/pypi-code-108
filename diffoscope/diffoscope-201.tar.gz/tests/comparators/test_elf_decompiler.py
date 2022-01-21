#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2020 Chris Lamb <lamby@debian.org>
# Copyright © 2020 Jean-Romain Garnier <salsa@jean-romain.com>
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

from diffoscope.config import Config
from diffoscope.comparators.missing_file import MissingFile

from ..utils.data import load_fixture, assert_diff
from ..utils.tools import (
    skipif,
    tools_missing,
    skip_unless_tools_exist,
    skip_unless_module_exists,
)


def radare2_command_is_undefined(x):
    if tools_missing("radare2"):
        return True

    try:
        # Open any file with radare2 and try to execute the given command
        # If it returns None, then the command doesn't exist
        import r2pipe

        r2 = r2pipe.open("/dev/null", flags=["-2"])
        return r2.cmdj(x) is None
    except ImportError:
        return True


def skip_unless_radare2_command_exists(command):
    return skipif(
        radare2_command_is_undefined(command),
        reason=f"radare2 didn't recognize {command} command",
        tools=(f"{command}_radare2_command",),
    )


def exclude_commands(monkeypatch, patterns):
    excluded = list(Config().exclude_commands)
    excluded += patterns
    monkeypatch.setattr(Config(), "exclude_commands", excluded)


@pytest.fixture(scope="function", autouse=True)
def init_tests(request, monkeypatch):
    # Ignore readelf and objdump as they are already tested by test_elf.py
    exclude_commands(monkeypatch, ["^readelf.*", "^objdump.*"])


obj1 = load_fixture("test1.o")
obj2 = load_fixture("test2.o")


@pytest.fixture
def obj_differences(obj1, obj2):
    return obj1.compare(obj2).details


@skip_unless_tools_exist("radare2")
@skip_unless_module_exists("r2pipe")
@skip_unless_radare2_command_exists("pdgj")
def test_obj_compare_non_existing(monkeypatch, obj1):
    monkeypatch.setattr(Config(), "new_file", True)
    difference = obj1.compare(MissingFile("/nonexisting", obj1))
    assert difference.source2 == "/nonexisting"
    assert len(difference.details) > 0


@skip_unless_tools_exist("radare2")
@skip_unless_module_exists("r2pipe")
@skip_unless_radare2_command_exists("pdgj")
def test_ghidra_diff(monkeypatch, obj1, obj2):
    exclude_commands(monkeypatch, ["^radare2 disass.*"])
    obj_differences = obj1.compare(obj2).details[0].details
    assert len(obj_differences) == 1
    assert_diff(obj_differences[0], "elf_obj_ghidra_expected_diff")


@skip_unless_tools_exist("radare2")
@skip_unless_module_exists("r2pipe")
def test_radare2_diff(monkeypatch, obj1, obj2):
    exclude_commands(monkeypatch, ["^radare2 r2ghidra.*"])
    obj_differences = obj1.compare(obj2).details[0].details
    assert len(obj_differences) == 1
    assert_diff(obj_differences[0], "elf_obj_radare2_expected_diff")
