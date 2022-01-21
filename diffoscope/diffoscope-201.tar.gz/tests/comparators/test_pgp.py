#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2017, 2019-2020 Chris Lamb <lamby@debian.org>
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
import subprocess

from diffoscope.comparators.pgp import PgpFile, PgpSignature

from ..utils.data import load_fixture, assert_diff, get_data
from ..utils.tools import skip_unless_tools_exist
from ..utils.versions import Version
from ..utils.nonexisting import assert_non_existing

pgp1 = load_fixture("test1.pgp")
pgp2 = load_fixture("test2.pgp")
signed1 = load_fixture("test1_signed.pgp")
signed2 = load_fixture("test2_signed.pgp")
signature1 = load_fixture("test1.asc")
signature2 = load_fixture("test2.asc")


def test_identification(pgp1):
    assert isinstance(pgp1, PgpFile)


def test_no_differences(pgp1):
    difference = pgp1.compare(pgp1)
    assert difference is None


def pgpdump_version():
    out = subprocess.check_output(
        ("pgpdump", "-v"), stderr=subprocess.STDOUT
    ).decode("utf-8")
    # pgpdump version 0.33, Copyright (C) 1998-2017 Kazu Yamamoto
    m = re.search(r"^pgpdump version (?P<version>\d+\.\d+)", out)
    if m is None:
        raise ValueError(f"Error parsing `pgpdump -v` output: {out}")

    return Version(m.group("version"))


@pytest.fixture
def differences(pgp1, pgp2):
    return pgp1.compare(pgp2).details


@skip_unless_tools_exist("pgpdump")
def test_diff(differences):
    assert_diff(differences[0], "pgp_expected_diff")


@skip_unless_tools_exist("pgpdump")
def test_compare_non_existing(monkeypatch, pgp1):
    assert_non_existing(monkeypatch, pgp1, has_null_source=False)


def test_pgp_signature_identification(signature1, signature2):
    assert isinstance(signature1, PgpSignature)
    assert isinstance(signature2, PgpSignature)


@skip_unless_tools_exist("pgpdump")
def test_pgp_signature(signature1, signature2):
    difference = signature1.compare(signature2)
    assert_diff(difference, "pgp_signature_expected_diff")
    assert difference.details[0].source1 == "pgpdump"
    assert len(difference.details) == 1


@skip_unless_tools_exist("pgpdump")
def test_signed_identification(signed1):
    assert isinstance(signed1, PgpFile)


@pytest.fixture
def signed_differences(signed1, signed2):
    return signed1.compare(signed2).details


@skip_unless_tools_exist("pgpdump")
def test_signed_diff(signed_differences):
    expected_diff = get_data("pgp_signed_expected_diff")
    if pgpdump_version() > Version(0.33):
        expected_diff = expected_diff.replace(
            "Format - binary", "Packet data format - binary"
        )
        expected_diff = expected_diff.replace(
            "File modified time", "Creation time"
        )
    assert signed_differences[0].unified_diff == expected_diff
