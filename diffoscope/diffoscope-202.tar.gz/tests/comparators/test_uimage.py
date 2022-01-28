#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2020 Conrad Ratschan <ratschance@gmail.com>
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

import pytest

from diffoscope.comparators.binary import FilesystemFile
from diffoscope.comparators.uimage import UimageFile
from diffoscope.comparators.utils.specialize import specialize

from ..utils.data import load_fixture, get_data, assert_diff
from ..utils.tools import skip_unless_tools_exist, file_version_is_lt
from ..utils.nonexisting import assert_non_existing

cpio1 = load_fixture("test1.cpio")
cpio2 = load_fixture("test2.cpio")

# Bytes from a U-Boot legacy image header generated via mkimage
uboot_header1 = bytes(
    b"\x27\x05\x19\x56\xf8\x7a\xd2\x00"
    b"\x5f\xc1\x58\x2c\x00\x00\x04\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x34\x71\x61\xa5\x05\x07\x03\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
)


# Bytes from a U-Boot legacy image header generated via mkimage
uboot_header2 = bytes(
    b"\x27\x05\x19\x56\xe8\x66\x86\xf7"
    b"\x5f\xc1\x58\x44\x00\x00\x04\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\xc6\x3c\x4a\x06\x05\x07\x03\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"
)


def uimage_fixture(header, prefix):
    @pytest.fixture
    def uboot_cpio(tmp_path, cpio1, cpio2):
        if prefix == "test1":
            cpio = cpio1
        else:
            cpio = cpio2
        cpio_uboot = tmp_path / "{}.cpio.uboot".format(prefix)
        with open(cpio_uboot, "wb") as t_fp:
            t_fp.write(header)
            with open(cpio.path, "rb") as r_fp:
                t_fp.write(bytes(r_fp.read()))
        return specialize(FilesystemFile(str(cpio_uboot)))

    return uboot_cpio


uboot_cpio1 = uimage_fixture(uboot_header1, "test1")
uboot_cpio2 = uimage_fixture(uboot_header2, "test2")


def test_identification(uboot_cpio1, uboot_cpio2):
    assert isinstance(uboot_cpio1, UimageFile)
    assert isinstance(uboot_cpio2, UimageFile)


def test_no_differences(uboot_cpio1):
    difference = uboot_cpio1.compare(uboot_cpio1)
    assert difference is None


@pytest.fixture
def differences(uboot_cpio1, uboot_cpio2):
    return uboot_cpio1.compare(uboot_cpio2).details


@pytest.fixture
def nested_differences(uboot_cpio1, uboot_cpio2):
    return uboot_cpio1.compare(uboot_cpio2).details[1].details


def test_file_differences(differences):
    filename = "uimage_expected_diff"
    # file-5.41 slightly changed the output format by dropping leading 0x.
    if file_version_is_lt("5.41"):
        filename = "uimage_expected_diff_pre_5_41"

    assert_diff(differences[0], filename)


@skip_unless_tools_exist("cpio")
def test_nested_listing(nested_differences):
    expected_diff = get_data("cpio_listing_expected_diff")
    assert nested_differences[0].unified_diff == expected_diff


@skip_unless_tools_exist("cpio")
def test_nested_symlink(nested_differences):
    assert nested_differences[1].source1 == "dir/link"
    assert nested_differences[1].comment == "symlink"
    expected_diff = get_data("symlink_expected_diff")
    assert nested_differences[1].unified_diff == expected_diff


@skip_unless_tools_exist("cpio")
def test_nested_compressed_files(nested_differences):
    assert nested_differences[2].source1 == "dir/text"
    assert nested_differences[2].source2 == "dir/text"
    expected_diff = get_data("text_ascii_expected_diff")
    assert nested_differences[2].unified_diff == expected_diff


@skip_unless_tools_exist("cpio")
def test_compare_non_existing(monkeypatch, uboot_cpio1):
    assert_non_existing(monkeypatch, uboot_cpio1)
