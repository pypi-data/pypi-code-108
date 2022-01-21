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

import plistlib

from diffoscope.tools import tool_required
from diffoscope.difference import Difference

from .utils.file import File
from .utils.command import Command, our_check_output


class OpenSSLPKCS7(Command):
    @tool_required("openssl")
    def cmdline(self):
        return ("openssl", "pkcs7", "-print", "-noout", "-in", self.path)


class Pkcs7File(File):
    DESCRIPTION = "Public Key Cryptography Standards (PKCS) files (version #7)"
    FILE_TYPE_HEADER_PREFIX = b"-----BEGIN PKCS7-----"[:16]

    def compare_details(self, other, source=None):
        return [
            Difference.from_operation(
                OpenSSLPKCS7,
                self.path,
                other.path,
                source="openssl pkcs7 -print",
            )
        ]


class MobileProvisionFile(File):
    DESCRIPTION = "Apple Xcode mobile provisioning files"
    FILE_EXTENSION_SUFFIX = {".mobileprovision"}

    @staticmethod
    @tool_required("openssl")
    def _get_structured_profile_text(path):
        openssl_output = our_check_output(
            [
                "openssl",
                "smime",
                "-inform",
                "der",
                "-verify",
                "-noverify",
                "-in",
                path,
            ]
        )
        return plistlib.dumps(plistlib.loads(openssl_output), sort_keys=True)

    def compare_details(self, other, source=None):
        my_content = MobileProvisionFile._get_structured_profile_text(
            self.path
        )
        other_content = MobileProvisionFile._get_structured_profile_text(
            other.path
        )
        return [
            Difference.from_text(
                my_content,
                other_content,
                self.name,
                other.name,
                source="openssl smime",
            )
        ]
