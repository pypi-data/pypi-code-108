# -*- coding: utf-8 -*-
#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2020 Conrad Ratschan <ratschance@gmail.com>
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
import os
import subprocess

import pytest

from diffoscope.comparators.binary import FilesystemFile
from diffoscope.comparators.fit import FlattenedImageTreeFile
from diffoscope.comparators.utils.specialize import specialize

from ..utils.data import data, assert_diff, load_fixture
from ..utils.tools import skip_unless_tools_exist, skip_unless_tool_is_at_least
from ..utils.nonexisting import assert_non_existing

cpio1 = load_fixture("test1.cpio")
cpio2 = load_fixture("test2.cpio")


def dumpimage_version():
    return (
        subprocess.check_output(("dumpimage", "-V"))
        .decode("utf-8")
        .strip()
        .split(" ")[-1]
    )


def fit_fixture(prefix, entrypoint):
    @pytest.fixture
    def uboot_fit(tmp_path):
        cpio = data("{}.cpio".format(prefix))
        fit_out = tmp_path / "{}.itb".format(prefix)

        # Time must be controlled for reproducible FIT images
        time_env = os.environ.copy()
        time_env["SOURCE_DATE_EPOCH"] = "1609459200"
        time_env["TZ"] = "UTC"
        _ = subprocess.run(
            [
                "mkimage",
                "-f",
                "auto",
                "-A",
                "arm",
                "-O",
                "linux",
                "-T",
                "ramdisk",
                "-C",
                "none",
                "-e",
                entrypoint,
                "-d",
                cpio,
                fit_out,
            ],
            capture_output=True,
            env=time_env,
        )
        return specialize(FilesystemFile(str(fit_out)))

    return uboot_fit


uboot_fit1 = fit_fixture("test1", "0x1000")
uboot_fit2 = fit_fixture("test2", "0x2000")


@skip_unless_tools_exist("dumpimage")
@skip_unless_tools_exist("fdtdump")
def test_identification(uboot_fit1, uboot_fit2):
    assert isinstance(uboot_fit1, FlattenedImageTreeFile)
    assert isinstance(uboot_fit2, FlattenedImageTreeFile)


@skip_unless_tools_exist("dumpimage")
@skip_unless_tools_exist("fdtdump")
def test_no_differences(uboot_fit1):
    difference = uboot_fit1.compare(uboot_fit1)
    assert difference is None


@pytest.fixture
def differences(uboot_fit1, uboot_fit2):
    return uboot_fit1.compare(uboot_fit2).details


@pytest.fixture
def nested_differences(uboot_fit1, uboot_fit2):
    return uboot_fit1.compare(uboot_fit2).details[1].details


@skip_unless_tool_is_at_least("dumpimage", dumpimage_version, "2021.01")
@skip_unless_tools_exist("fdtdump")
def test_file_differences(differences):
    assert_diff(differences[0], "fit_expected_diff")


@skip_unless_tools_exist("cpio")
@skip_unless_tool_is_at_least("dumpimage", dumpimage_version, "2021.01")
@skip_unless_tools_exist("fdtdump")
def test_nested_listing(nested_differences):
    assert_diff(nested_differences[0], "cpio_listing_expected_diff")


@skip_unless_tools_exist("cpio")
@skip_unless_tool_is_at_least("dumpimage", dumpimage_version, "2021.01")
@skip_unless_tools_exist("fdtdump")
def test_nested_symlink(nested_differences):
    assert nested_differences[1].source1 == "dir/link"
    assert nested_differences[1].comment == "symlink"
    assert_diff(nested_differences[1], "symlink_expected_diff")


@skip_unless_tools_exist("cpio")
@skip_unless_tool_is_at_least("dumpimage", dumpimage_version, "2021.01")
@skip_unless_tools_exist("fdtdump")
def test_nested_compressed_files(nested_differences):
    assert nested_differences[2].source1 == "dir/text"
    assert nested_differences[2].source2 == "dir/text"
    assert_diff(nested_differences[2], "text_ascii_expected_diff")


@skip_unless_tools_exist("cpio")
@skip_unless_tool_is_at_least("dumpimage", dumpimage_version, "2021.01")
@skip_unless_tools_exist("fdtdump")
def test_compare_non_existing(monkeypatch, uboot_fit1):
    assert_non_existing(monkeypatch, uboot_fit1)
