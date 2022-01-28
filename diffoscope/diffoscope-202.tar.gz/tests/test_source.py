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

import os
import glob
import subprocess

from .utils.tools import skip_unless_tool_is_at_least

ALLOWED_TEST_FILES = {
    # Data files we would prefer to generate dynamically
    "android1.img",
    "android2.img",
    "archive1.tar",
    "archive2.tar",
    "base-files_157-r45695_ar71xx.ipk",
    "base-files_157-r45918_ar71xx.ipk",
    "binary1",
    "binary2",
    "bug881937_1.deb",
    "bug881937_2.deb",
    "bug903391_1.deb",
    "bug903391_2.deb",
    "bug903401_1.deb",
    "bug903401_2.deb",
    "bug903565_1.deb",
    "bug903565_2.deb",
    "containers",
    "containers/a.tar.bz2",
    "containers/a.tar.gz",
    "containers/a.tar.xz",
    "containers/b.tar.bz2",
    "containers/b.tar.gz",
    "containers/b.tar.xz",
    "containers/magic_bzip2",
    "containers/magic_gzip",
    "containers/magic_xz",
    "dbgsym/add/test-dbgsym-dbgsym_1_amd64.deb",
    "dbgsym/add/test-dbgsym_1_amd64.deb",
    "dbgsym/mult/test-dbgsym-dbgsym_1_amd64.deb",
    "dbgsym/mult/test-dbgsym_1_amd64.deb",
    "dbgsym/test-dbgsym_1.dsc",
    "dbgsym/test-dbgsym_1.tar.gz",
    "debian-bug-876316-control.tar.gz",
    # Outputs
    "devicetree1.dtb",
    "devicetree2.dtb",
    "elfmix1.not_a",
    "elfmix2.a",
    "encrypted1.zip",
    "encrypted2.zip",
    "fuzzy-tar-in-tar1.tar",
    "fuzzy-tar-in-tar2.tar",
    "fuzzy1.tar",
    "fuzzy2.tar",
    "fuzzy3.tar",
    "hello1.wasm",
    "hello2.wasm",
    "no-perms.tar",
    "quine.gz",
    "quine.zip",
    "quine_a.deb",
    "quine_b.deb",
    "Samyak-Malayalam1.ttf",
    "Samyak-Malayalam2.ttf",
    "test1-le64.cache-4",
    "test1.a",
    "test1.apk",
    "test1.asc",
    "test1.binwalk",
    "test1.buildinfo",
    "test1.bz2",
    "test1.changes",
    "Test1.class",
    "Test2.class",
    "test1.cpio",
    "test1.db",
    "test1.deb",
    "test1.debsrc.tar.gz",
    "test1.debug",
    "test1.dex",
    "test1.docx",
    "test1.dsc",
    "test1.epub",
    "test1.exe",
    "test1.ext4",
    "test1.fat12",
    "test1.fat16",
    "test1.fat32",
    "test1.gif",
    "test1.git-index",
    "test1.gnumeric",
    "test1.gz",
    "test1.hi",
    "test1.icc",
    "test1.ico",
    "test1.inv",
    "test1.iso",
    "test1.jmod",
    "test1.jpg",
    "test1.js",
    "test1.json",
    "test1.kbx",
    "test1.lz4",
    "test1.macho",
    "test1.mo",
    "test1.mozzip",
    "test1.mp3",
    "test1.o",
    "test1.odt",
    "test1.ogg",
    "test1.pcap",
    "test1.pdf",
    "test1.pgp",
    "test1_signed.pgp",
    "test1.png",
    "test1.ppu",
    "test1.ps",
    "test1.pyc-renamed",
    "test1.rdb",
    "test1.rdx",
    "test1.rlib",
    "test1.rpm",
    "test1.sqlite3",
    "test1.squashfs",
    "test1_root.squashfs",
    "test1.tar",
    "test1.xml",
    "test1.xsb",
    "test1.xz",
    "test1.zip",
    "test1_meta.ico",
    "test1_meta.jpg",
    "test2-le64.cache-4",
    "test2.a",
    "test2.apk",
    "test2.asc",
    "test2.binwalk",
    "test2.buildinfo",
    "test2.bz2",
    "test2.changes",
    "test2.cpio",
    "test2.db",
    "test2.deb",
    "test2.debsrc.tar.gz",
    "test2.debug",
    "test2.dex",
    "test2.docx",
    "test2.dsc",
    "test2.epub",
    "test2.exe",
    "test2.ext4",
    "test2.fat12",
    "test2.gif",
    "test2.git-index",
    "test2.gnumeric",
    "test2.gz",
    "test2.hi",
    "test2.icc",
    "test2.ico",
    "test2.inv",
    "test2.iso",
    "test2.jmod",
    "test2.jpg",
    "test2.js",
    "test2.json",
    "test2.kbx",
    "test2.lz4",
    "test2.macho",
    "test2.mo",
    "test2.mozzip",
    "test2.mp3",
    "test2.o",
    "test2.odt",
    "test2.ogg",
    "test2.pcap",
    "test2.pdf",
    "test2.pgp",
    "test2_signed.pgp",
    "test2.png",
    "test2.ppu",
    "test2.ps",
    "test2.pyc-renamed",
    "test2.rdb",
    "test2.rdx",
    "test2.rlib",
    "test2.rpm",
    "test2.sqlite3",
    "test2.squashfs",
    "test2_root.squashfs",
    "test2.tar",
    "test2.xml",
    "test2.xsb",
    "test2.xz",
    "test2.zip",
    "test2_meta.ico",
    "test2_meta.jpg",
    "test3.apk",
    "test3.changes",
    "test3.gif",
    "test3.pdf",
    "test3.zip",
    "test4.changes",
    "test4.gif",
    "test4.pdf",
    "test_comment1.zip",
    "test_comment2.zip",
    "test_invalid.json",
    "test_invalid.xml",
    "test_iso8859-1.mo",
    "test_no_charset.mo",
    "test_openssh_pub_key1.pub",
    "test_openssh_pub_key2.pub",
    "test_weird_non_unicode_chars1.pdf",
    "test_weird_non_unicode_chars2.pdf",
    "text_ascii1",  # used by multiple tests
    "text_ascii2",  # used by multiple tests
    "text_iso8859",
    "text_order1",
    "text_order2",
    "text_unicode1",
    "text_unicode2",
    "text_unicode_binary_fallback",
    # Outputs
    "debian-bug-875281.collapsed-diff.json",
    "order1a.json",
    "order1b.json",
}


def black_version():
    try:
        out = subprocess.check_output(("black", "--version"))
    except subprocess.CalledProcessError as e:
        out = e.output

    # black --version format changed starting in 21.11b0. Returning the first
    # token starting with a decimal digit, since its ordinal position may vary.
    return [
        x for x in out.strip().decode("utf-8").split(" ") if x[0].isdigit()
    ]


@skip_unless_tool_is_at_least("black", black_version, "21.12b0")
def test_code_is_black_clean():
    output = subprocess.check_output(
        ("black", "--diff", "."), stderr=subprocess.PIPE
    ).decode("utf-8")

    # Display diff in "captured stdout call"
    if output:
        print(output)

    assert not output, output


def test_does_not_add_new_test_files():
    """
    For a variety of reasons we are now prefering to generate any test data
    dynamically (via pytest fixtures, etc.) rather than committing and shipping
    such files.

    Exceptions to this may be appropriate (or even required) but this test
    ensures that test files that could be dynamically generated are not added
    "automatically", for example by following previous/older commits.
    """

    test_dir = os.path.join(os.path.dirname(__file__), "data")

    seen = set()

    for x in glob.iglob(os.path.join(test_dir, "**"), recursive=True):
        if os.path.isdir(x):
            continue

        # Strip off common prefix
        x = x[len(test_dir) + 1 :]

        # Skip some known expected diff filename patterns
        if (
            x.endswith("_diff")
            or x.endswith("_diffs")
            or x.endswith(".diff")
            or "_diff_" in x
            or "diff." in x
            or x.startswith("output")
        ):
            continue

        seen.add(x)

    assert seen - ALLOWED_TEST_FILES - {""} == set()
