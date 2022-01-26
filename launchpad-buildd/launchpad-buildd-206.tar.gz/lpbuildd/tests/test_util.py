# Copyright 2017 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

__metaclass__ = type

from testtools import TestCase

from lpbuildd.util import (
    get_arch_bits,
    set_personality,
    shell_escape,
    )


class TestShellEscape(TestCase):

    def test_plain(self):
        self.assertEqual("foo", shell_escape("foo"))

    def test_whitespace(self):
        self.assertEqual("'  '", shell_escape("  "))

    def test_single_quotes(self):
        self.assertEqual(
            "'shell'\"'\"'s great'", shell_escape("shell's great"))

    def test_bytes(self):
        self.assertEqual(
            u"'\N{SNOWMAN}'".encode("UTF-8"),
            shell_escape(u"\N{SNOWMAN}".encode("UTF-8")))


class TestGetArchBits(TestCase):

    def test_x32(self):
        self.assertEqual(64, get_arch_bits("x32"))

    def test_32bit(self):
        self.assertEqual(32, get_arch_bits("armhf"))
        self.assertEqual(32, get_arch_bits("i386"))

    def test_64bit(self):
        self.assertEqual(64, get_arch_bits("amd64"))
        self.assertEqual(64, get_arch_bits("arm64"))


class TestSetPersonality(TestCase):

    def test_32bit(self):
        self.assertEqual(
            ["linux32", "sbuild"], set_personality(["sbuild"], "i386"))

    def test_64bit(self):
        self.assertEqual(
            ["linux64", "sbuild"], set_personality(["sbuild"], "amd64"))

    def test_uname_26(self):
        self.assertEqual(
            ["linux64", "--uname-2.6", "sbuild"],
            set_personality(["sbuild"], "amd64", series="precise"))

    def test_no_uname_26(self):
        self.assertEqual(
            ["linux64", "sbuild"],
            set_personality(["sbuild"], "amd64", series="trusty"))
