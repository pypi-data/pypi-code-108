#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2015 Jérémy Bobbio <lunar@debian.org>
# Copyright © 2015-2021 Chris Lamb <lamby@debian.org>
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

import re
import pytest
import os.path
import subprocess

from diffoscope.config import Config
from diffoscope.comparators.ar import ArFile
from diffoscope.comparators.elf import ElfFile
from diffoscope.comparators.binary import FilesystemFile
from diffoscope.comparators.directory import FilesystemDirectory
from diffoscope.comparators.missing_file import MissingFile
from diffoscope.comparators.utils.specialize import specialize

from ..utils.data import data, load_fixture, assert_diff
from ..utils.tools import (
    skip_unless_tools_exist,
    skip_if_binutils_does_not_support_x86,
    skip_unless_module_exists,
    skip_if_tool_version_is,
)


obj1 = load_fixture("test1.o")
obj2 = load_fixture("test2.o")
ignore_readelf_errors1 = load_fixture("test1.debug")
ignore_readelf_errors2 = load_fixture("test2.debug")


@pytest.fixture(scope="function", autouse=True)
def init_tests(request, monkeypatch):
    # Ignore radare2 commands so decompiling is skipped
    # See test_elf_decompiler.py for tests related to decompiler
    monkeypatch.setattr(Config(), "exclude_commands", ["^radare2.*"])


def readelf_version():
    try:
        out = subprocess.check_output(["readelf", "--version"])
    except subprocess.CalledProcessError as e:
        out = e.output

    # Only match GNU readelf; we only need to match some versions
    m = re.match(r"^GNU readelf .* (?P<version>[\d.]+)\n", out.decode("utf-8"))

    # Return '0' as the version if we can't parse one; it should be harmless.
    if m is None:
        return "0"

    return m.group("version")


def test_obj_identification(obj1):
    assert isinstance(obj1, ElfFile)


def test_obj_no_differences(obj1):
    difference = obj1.compare(obj1)
    assert difference is None


@pytest.fixture
def obj_differences(obj1, obj2):
    return obj1.compare(obj2).details


@skip_unless_tools_exist("readelf")
@skip_if_tool_version_is("readelf", readelf_version, "2.29")
@skip_if_binutils_does_not_support_x86()
def test_obj_compare_non_existing(monkeypatch, obj1):
    monkeypatch.setattr(Config(), "new_file", True)
    difference = obj1.compare(MissingFile("/nonexisting", obj1))
    assert difference.source2 == "/nonexisting"
    assert len(difference.details) > 0


@skip_unless_tools_exist("readelf")
@skip_if_tool_version_is("readelf", readelf_version, "2.29")
@skip_if_binutils_does_not_support_x86()
def test_diff(obj_differences):
    assert len(obj_differences) == 1
    assert_diff(obj_differences[0], "elf_obj_expected_diff")


TEST_LIB1_PATH = data("test1.a")
TEST_LIB2_PATH = data("test2.a")


@pytest.fixture
def lib1():
    return specialize(FilesystemFile(TEST_LIB1_PATH))


@pytest.fixture
def lib2():
    return specialize(FilesystemFile(TEST_LIB2_PATH))


def test_lib_identification(lib1):
    assert isinstance(lib1, ArFile)


def test_lib_no_differences(lib1):
    difference = lib1.compare(lib1)
    assert difference is None


@pytest.fixture
def lib_differences(lib1, lib2):
    return lib1.compare(lib2).details


@skip_unless_tools_exist("readelf", "objdump")
@skip_if_tool_version_is("readelf", readelf_version, "2.29")
@skip_if_binutils_does_not_support_x86()
def test_lib_differences(lib_differences):
    assert len(lib_differences) == 2
    assert lib_differences[0].source1 == "file list"
    assert_diff(lib_differences[0], "elf_lib_metadata_expected_diff")
    assert "objdump" in lib_differences[1].details[0].source1
    assert_diff(lib_differences[1].details[0], "elf_lib_objdump_expected_diff")


@skip_unless_tools_exist("readelf", "objdump")
@skip_if_tool_version_is("readelf", readelf_version, "2.29")
@skip_if_binutils_does_not_support_x86()
def test_lib_compare_non_existing(monkeypatch, lib1):
    monkeypatch.setattr(Config(), "new_file", True)
    difference = lib1.compare(MissingFile("/nonexisting", lib1))
    assert difference.source2 == "/nonexisting"
    assert len(difference.details) > 0


TEST_LIBMIX1_PATH = data("elfmix1.not_a")
TEST_LIBMIX2_PATH = data("elfmix2.a")


@pytest.fixture
def libmix1():
    return specialize(FilesystemFile(TEST_LIBMIX1_PATH))


@pytest.fixture
def libmix2():
    return specialize(FilesystemFile(TEST_LIBMIX2_PATH))


@pytest.fixture
def libmix_differences(libmix1, libmix2):
    return libmix1.compare(libmix2).details


@skip_unless_tools_exist("xxd")
@skip_unless_tools_exist("llvm-readobj", "llvm-objdump")
@skip_unless_tools_exist("readelf", "objdump")
@skip_if_tool_version_is("readelf", readelf_version, "2.29")
@skip_if_binutils_does_not_support_x86()
def test_libmix_differences(libmix_differences):
    assert len(libmix_differences) == 5
    file_list, mach_o, x86_o, src_c, x_obj = libmix_differences

    # Check order and basic identification
    assert file_list.source1 == "file list"
    x86_o = x86_o.details[0]
    assert x86_o.source1.startswith("objdump ")
    assert src_c.source1.endswith(".c")

    mach_o = mach_o.details[0]
    for diff in mach_o.details:
        assert diff.source1.startswith("llvm-objdump ")

    # Content
    assert "return42_or_3" in file_list.unified_diff
    assert_diff(x86_o, "elfmix_disassembly_expected_diff")
    assert_diff(src_c, "elfmix_src_c_expected_diff")

    mach_o_filenames = ["elfmix_mach_o_expected_diff__text"]
    for idx, diff in enumerate(mach_o.details):
        assert_diff(diff, mach_o_filenames[idx])

    x_obj = x_obj.details[0]
    if x_obj.source1.startswith("readelf "):
        assert_diff(x_obj, "elfmix_x_obj_expected_diff")
    elif x_obj.source1.startswith("objdump "):
        assert_diff(x_obj, "elfmix_x_obj_objdump_expected_diff")
    else:
        pytest.fail(
            f"x_obj is neither readelf or objdump: {repr(x_obj.source1)}"
        )


TEST_DBGSYM_DEB1_PATH = data("dbgsym/add/test-dbgsym_1_amd64.deb")
TEST_DBGSYM_DEB2_PATH = data("dbgsym/mult/test-dbgsym_1_amd64.deb")


@pytest.fixture
def dbgsym_dir1():
    container = FilesystemDirectory(
        os.path.dirname(TEST_DBGSYM_DEB1_PATH)
    ).as_container
    return specialize(
        FilesystemFile(TEST_DBGSYM_DEB1_PATH, container=container)
    )


@pytest.fixture
def dbgsym_dir2():
    container = FilesystemDirectory(
        os.path.dirname(TEST_DBGSYM_DEB2_PATH)
    ).as_container
    return specialize(
        FilesystemFile(TEST_DBGSYM_DEB2_PATH, container=container)
    )


@pytest.fixture
def dbgsym_differences(monkeypatch, dbgsym_dir1, dbgsym_dir2):
    monkeypatch.setattr(Config(), "use_dbgsym", "yes")
    return dbgsym_dir1.compare(dbgsym_dir2)


@skip_unless_tools_exist("readelf", "objdump", "objcopy")
@skip_if_binutils_does_not_support_x86()
@skip_unless_module_exists("debian.deb822")
def test_differences_with_dbgsym(dbgsym_differences):
    assert dbgsym_differences.details[2].source1 == "data.tar.xz"
    bin_details = dbgsym_differences.details[2].details[0].details[0]
    assert bin_details.source1 == "./usr/bin/test"
    assert bin_details.details[1].source1.startswith("objdump")
    assert (
        "test-cases/dbgsym/package/test.c:2"
        in bin_details.details[1].unified_diff
    )


@skip_unless_tools_exist("readelf", "objdump", "objcopy")
@skip_if_binutils_does_not_support_x86()
@skip_unless_module_exists("debian.deb822")
def test_original_gnu_debuglink(dbgsym_differences):
    bin_details = dbgsym_differences.details[2].details[0].details[0]
    assert ".gnu_debuglink" in bin_details.details[2].source1
    assert_diff(bin_details.details[2], "gnu_debuglink_expected_diff")


def test_ignore_readelf_errors1_identify(ignore_readelf_errors1):
    assert isinstance(ignore_readelf_errors1, ElfFile)


def test_ignore_readelf_errors2_identify(ignore_readelf_errors2):
    assert isinstance(ignore_readelf_errors2, ElfFile)


@pytest.fixture
def ignore_readelf_errors_differences(
    ignore_readelf_errors1, ignore_readelf_errors2
):
    return ignore_readelf_errors1.compare(ignore_readelf_errors2).details


@skip_unless_tools_exist("readelf")
@skip_if_tool_version_is("readelf", readelf_version, "2.29")
@skip_if_binutils_does_not_support_x86()
def test_ignore_readelf_errors(ignore_readelf_errors_differences):
    assert_diff(
        ignore_readelf_errors_differences[0],
        "ignore_readelf_errors_expected_diff",
    )
