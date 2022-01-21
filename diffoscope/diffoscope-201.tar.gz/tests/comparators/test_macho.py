#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2015 Jérémy Bobbio <lunar@debian.org>
# Copyright © 2015 Clemens Lang <cal@macports.org>
# Copyright © 2016-2021 Chris Lamb <lamby@debian.org>
# Copyright © 2021 Jean-Romain Garnier <salsa@jean-romain.com>
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
from diffoscope.comparators.macho import MachoFile
from diffoscope.comparators.missing_file import MissingFile

from ..utils.data import load_fixture, assert_diff
from ..utils.tools import skip_unless_tools_exist
from .test_rlib import llvm_version


obj1 = load_fixture("test1.macho")
obj2 = load_fixture("test2.macho")


@pytest.fixture(scope="function", autouse=True)
def init_tests(request, monkeypatch):
    # Ignore radare2 commands so decompiling is skipped
    # See test_macho_decompiler.py for tests related to decompiler
    monkeypatch.setattr(Config(), "exclude_commands", ["^radare2.*"])


def test_obj_identification(obj1):
    assert isinstance(obj1, MachoFile)


@skip_unless_tools_exist("llvm-readobj", "llvm-objdump")
def test_obj_no_differences(obj1):
    difference = obj1.compare(obj1)
    assert difference is None


@pytest.fixture
def obj_differences(obj1, obj2):
    return obj1.compare(obj2).details


@skip_unless_tools_exist("otool", "lipo")
def test_otool_obj_compare_non_existing(monkeypatch, obj1):
    monkeypatch.setattr(Config(), "new_file", True)
    difference = obj1.compare(MissingFile("/nonexisting", obj1))
    assert difference.source2 == "/nonexisting"
    assert len(difference.details) > 0


@skip_unless_tools_exist("otool", "lipo")
def test_otool_diff(obj_differences):
    assert len(obj_differences) == 2
    assert_diff(obj_differences[0], "macho_otool_expected_diff_strings")

    arch_differences = obj_differences[-1].details
    assert len(arch_differences) == 6

    filenames = [
        "macho_otool_expected_diff_headers",
        "macho_otool_expected_diff_libraries",
        "macho_otool_expected_diff_indirect_symbols",
        "macho_otool_expected_diff__text",
        "macho_otool_expected_diff__cstring",
        "macho_otool_expected_diff__data",
    ]
    for idx, diff in enumerate(arch_differences):
        assert_diff(diff, filenames[idx])


@skip_unless_tools_exist("llvm-readobj", "llvm-objdump")
def test_llvm_obj_compare_non_existing(monkeypatch, obj1):
    monkeypatch.setattr(Config(), "new_file", True)
    difference = obj1.compare(MissingFile("/nonexisting", obj1))
    assert difference.source2 == "/nonexisting"
    assert len(difference.details) > 0


@skip_unless_tools_exist("llvm-readobj", "llvm-objdump")
def test_llvm_diff(obj_differences):
    if llvm_version() < "13":
        diff_symbols = "macho_llvm_expected_diff_symbols_llvm_11"
    else:
        diff_symbols = "macho_llvm_expected_diff_symbols"

    # Headers
    assert len(obj_differences) == 8
    filenames = [
        "macho_llvm_expected_diff_strings",
        "macho_llvm_expected_diff_file_headers",
        "macho_llvm_expected_diff_needed_libs",
        diff_symbols,
        "macho_llvm_expected_diff_dyn_symbols",
        "macho_llvm_expected_diff_relocations",
        "macho_llvm_expected_diff_dyn_relocations",
    ]
    for idx, diff in enumerate(obj_differences[:-1]):
        assert_diff(diff, filenames[idx])

    # Sections
    arch_differences = obj_differences[-1].details
    assert len(arch_differences) == 7
    filenames = [
        "macho_llvm_expected_diff__text",
        "macho_llvm_expected_diff__stubs",
        "macho_llvm_expected_diff__stub_helper",
        "macho_llvm_expected_diff__cstring",
        "macho_llvm_expected_diff__unwind_info",
        "macho_llvm_expected_diff__eh_frame",
        "macho_llvm_expected_diff__la_symbol_ptr",
    ]
    for idx, diff in enumerate(arch_differences):
        assert_diff(diff, filenames[idx])
