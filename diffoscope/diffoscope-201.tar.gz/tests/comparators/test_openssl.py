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

import subprocess

import pytest

from diffoscope.comparators.binary import FilesystemFile
from diffoscope.comparators.openssl import Pkcs7File
from diffoscope.comparators.utils.specialize import specialize

from ..utils.tools import skip_unless_tools_exist


def pkcs7_fixture(prefix):
    @pytest.fixture
    def inner(tmpdir):
        crt = str(tmpdir.join("{}.crt".format(prefix)))
        pem = str(tmpdir.join("{}.pem".format(prefix)))
        p7c = str(tmpdir.join("{}.p7c".format(prefix)))

        subprocess.check_call(
            (
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "rsa:4096",
                "-keyout",
                pem,
                "-out",
                crt,
                "-days",
                "365",
                "-nodes",
                "-subj",
                "/CN=localhost",
            )
        )
        subprocess.check_call(
            (
                "openssl",
                "crl2pkcs7",
                "-nocrl",
                "-certfile",
                crt,
                "-out",
                p7c,
                "-certfile",
                pem,
            )
        )

        return specialize(FilesystemFile(p7c))

    return inner


pkcs71 = pkcs7_fixture("test1")
pkcs72 = pkcs7_fixture("test2")


@skip_unless_tools_exist("openssl")
def test_identification(pkcs71):
    assert isinstance(pkcs71, Pkcs7File)


@skip_unless_tools_exist("openssl")
def test_no_differences(pkcs71):
    difference = pkcs71.compare(pkcs71)
    assert difference is None


@pytest.fixture
def differences(pkcs71, pkcs72):
    return pkcs71.compare(pkcs72).details


@skip_unless_tools_exist("openssl")
def test_differences(differences):
    # Don't test exact unified diff; the signatures generated in
    # `pkcs7_fixture` are non-deterministic.

    assert "notAfter:" in differences[0].unified_diff
    assert "serialNumber:" in differences[0].unified_diff
