#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2018-2021 Chris Lamb <lamby@debian.org>
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

from diffoscope.comparators.ocaml import OcamlInterfaceFile
from diffoscope.comparators.binary import FilesystemFile
from diffoscope.comparators.utils.specialize import specialize

from ..utils.data import assert_diff_startswith
from ..utils.tools import skip_unless_tool_is_at_least
from ..utils.nonexisting import assert_non_existing


def ocaml_fixture(prefix):
    @pytest.fixture
    def cmi(tmpdir):
        input_ = str(tmpdir.join("{}.mli".format(prefix)))
        output = str(tmpdir.join("{}.cmi".format(prefix)))

        with open(input_, "w"):
            pass

        subprocess.check_call(("ocamlc", "-c", input_))

        return specialize(FilesystemFile(output))

    return cmi


cmi1 = ocaml_fixture("test1")
cmi2 = ocaml_fixture("test2")


def ocaml_version():
    try:
        out = subprocess.check_output(["ocaml", "-version"])
    except subprocess.CalledProcessError as e:
        out = e.output
    return out.decode("utf-8").split()[-1]


@skip_unless_tool_is_at_least("ocamlobjinfo", ocaml_version, "4.11")
def test_identification(cmi1):
    assert isinstance(cmi1, OcamlInterfaceFile)


@pytest.fixture
def differences(cmi1, cmi2):
    return cmi1.compare(cmi2).details


@skip_unless_tool_is_at_least("ocamlobjinfo", ocaml_version, "4.11")
def test_no_differences(cmi1):
    difference = cmi1.compare(cmi1)
    assert difference is None


@skip_unless_tool_is_at_least("ocamlobjinfo", ocaml_version, "4.11")
def test_diff(differences):
    assert_diff_startswith(differences[0], "ocaml_expected_diff")


@skip_unless_tool_is_at_least("ocamlobjinfo", ocaml_version, "4.11")
def test_compare_non_existing(monkeypatch, cmi1):
    assert_non_existing(monkeypatch, cmi1, has_null_source=False)
