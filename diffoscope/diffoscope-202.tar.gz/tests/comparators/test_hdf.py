#
# diffoscope: in-depth comparison of files, archives, and directories
#
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

import re
import pytest

from diffoscope.comparators.hdf import Hdf5File
from diffoscope.comparators.binary import FilesystemFile
from diffoscope.comparators.utils.specialize import specialize

from ..utils.data import load_fixture, get_data
from ..utils.tools import skip_unless_tools_exist, skip_unless_module_exists
from ..utils.nonexisting import assert_non_existing

hdf5_1 = load_fixture("test1.hdf5")
hdf5_2 = load_fixture("test2.hdf5")

re_normalise = re.compile(r'(HDF5 ")[^\"]+/([^\"]+")')


def hdf5_fixture(prefix):
    @pytest.fixture
    def hdf5d(tmpdir):
        filename = str(tmpdir.join("{}.db".format(prefix)))

        # Listed in debian/tests/control.in
        import h5py

        with h5py.File(filename, "w"):
            pass

        return specialize(FilesystemFile(filename))

    return hdf5d


hdf5_1 = hdf5_fixture("test1")
hdf5_2 = hdf5_fixture("test2")


@skip_unless_module_exists("h5py")
def test_identification(hdf5_1):
    assert isinstance(hdf5_1, Hdf5File)


@skip_unless_module_exists("h5py")
def test_no_differences(hdf5_1):
    difference = hdf5_1.compare(hdf5_1)
    assert difference is None


@pytest.fixture
def differences(hdf5_1, hdf5_2):
    return hdf5_1.compare(hdf5_2).details


@skip_unless_tools_exist("h5dump")
@skip_unless_module_exists("h5py")
def test_diff(differences):
    expected_diff = get_data("hdf5_expected_diff")
    # Remove absolute build path
    normalised = re_normalise.sub(
        lambda m: m.group(1) + m.group(2), differences[0].unified_diff
    )
    assert normalised == expected_diff


@skip_unless_tools_exist("h5dump")
@skip_unless_module_exists("h5py")
def test_compare_non_existing(monkeypatch, hdf5_1):
    assert_non_existing(monkeypatch, hdf5_1, has_null_source=False)
