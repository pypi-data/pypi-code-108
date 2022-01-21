# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4; encoding:utf8 -*-
#
# Copyright 2002 Ben Escoto <ben@emerose.org>
# Copyright 2007 Kenneth Loafman <kenneth@loafman.com>
#
# This file is part of duplicity.
#
# Duplicity is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# Duplicity is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with duplicity; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

from __future__ import print_function
from __future__ import division
from future import standard_library
standard_library.install_aliases()
from builtins import range
from builtins import object
from past.utils import old_div

import os
import platform
import pytest
import random
import unittest

from duplicity import gpg
from duplicity import path
from testing import _runtest_dir
from . import UnitTestCase


@pytest.mark.usefixtures(u"redirect_stdin")
class GPGTest(UnitTestCase):
    u"""Test GPGFile"""
    def setUp(self):
        super(GPGTest, self).setUp()
        self.unpack_testfiles()
        self.default_profile = gpg.GPGProfile(passphrase=u"foobar")

    def gpg_cycle(self, s, profile=None):
        u"""Test encryption/decryption cycle on string s"""
        epath = path.Path(u"{0}/testfiles/output/encrypted_file".format(_runtest_dir))
        if not profile:
            profile = self.default_profile
        encrypted_file = gpg.GPGFile(1, epath, profile)
        encrypted_file.write(s)
        encrypted_file.close()

        epath2 = path.Path(u"{0}/testfiles/output/encrypted_file".format(_runtest_dir))
        decrypted_file = gpg.GPGFile(0, epath2, profile)
        dec_buf = decrypted_file.read()
        decrypted_file.close()

        assert s == dec_buf, (len(s), len(dec_buf))

    def test_gpg1(self):
        u"""Test gpg short strings"""
        self.gpg_cycle(b"hello, world")
        self.gpg_cycle(b"ansoetuh aoetnuh aoenstuh aoetnuh asoetuh saoteuh ")

    def test_gpg2(self):
        u"""Test gpg long strings easily compressed"""
        self.gpg_cycle(b" " * 50000)
        self.gpg_cycle(b"aoeu" * 1000000)

    def test_gpg3(self):
        u"""Test on random data - must have /dev/urandom device"""
        infp = open(u"/dev/urandom", u"rb")
        rand_buf = infp.read(120000)
        infp.close()
        self.gpg_cycle(rand_buf)

    def test_gpg_asym(self):
        u"""Test GPG asymmetric encryption"""
        profile = gpg.GPGProfile(passphrase=self.sign_passphrase,
                                 recipients=[self.encrypt_key1,
                                             self.encrypt_key2])
        self.gpg_cycle(b"aoensutha aonetuh saoe", profile)

        profile2 = gpg.GPGProfile(passphrase=self.sign_passphrase,
                                  recipients=[self.encrypt_key1])
        self.gpg_cycle(b"aoeu" * 10000, profile2)

    def test_gpg_hidden_asym(self):
        u"""Test GPG asymmetric encryption with hidden key id"""
        profile = gpg.GPGProfile(passphrase=self.sign_passphrase,
                                 hidden_recipients=[self.encrypt_key1,
                                                    self.encrypt_key2])
        self.gpg_cycle(b"aoensutha aonetuh saoe", profile)

        profile2 = gpg.GPGProfile(passphrase=self.sign_passphrase,
                                  hidden_recipients=[self.encrypt_key1])
        self.gpg_cycle(b"aoeu" * 10000, profile2)

    def test_gpg_signing(self):
        u"""Test to make sure GPG reports the proper signature key"""
        plaintext = b"hello" * 50000

        signing_profile = gpg.GPGProfile(passphrase=self.sign_passphrase,
                                         sign_key=self.sign_key,
                                         recipients=[self.encrypt_key1])

        epath = path.Path(u"{0}/testfiles/output/encrypted_file".format(_runtest_dir))
        encrypted_signed_file = gpg.GPGFile(1, epath, signing_profile)
        encrypted_signed_file.write(plaintext)
        encrypted_signed_file.close()

        decrypted_file = gpg.GPGFile(0, epath, signing_profile)
        assert decrypted_file.read() == plaintext
        decrypted_file.close()
        sig = decrypted_file.get_signature()
        assert sig == self.sign_key, sig

    def test_gpg_signing_and_hidden_encryption(self):
        u"""Test to make sure GPG reports the proper signature key even with hidden encryption key id"""
        plaintext = b"hello" * 50000

        signing_profile = gpg.GPGProfile(passphrase=self.sign_passphrase,
                                         sign_key=self.sign_key,
                                         hidden_recipients=[self.encrypt_key1])

        epath = path.Path(u"{0}/testfiles/output/encrypted_file".format(_runtest_dir))
        encrypted_signed_file = gpg.GPGFile(1, epath, signing_profile)
        encrypted_signed_file.write(plaintext)
        encrypted_signed_file.close()

        decrypted_file = gpg.GPGFile(0, epath, signing_profile)
        assert decrypted_file.read() == plaintext
        decrypted_file.close()
        sig = decrypted_file.get_signature()
        assert sig == self.sign_key, sig

    @unittest.skipIf(platform.machine() in [u"ppc64el", u"ppc64le"], u"Skip on ppc64el of ppc64el machines")
    def test_GPGWriteFile(self):
        u"""Test GPGWriteFile"""
        size = 400 * 1000
        gwfh = GPGWriteFile_Helper()
        profile = gpg.GPGProfile(passphrase=u"foobar")
        for i in range(10):
            gpg.GPGWriteFile(gwfh, u"{0}/testfiles/output/gpgwrite.gpg".format(_runtest_dir),
                             profile, size=size)
            # print os.stat("/tmp/testfiles/output/gpgwrite.gpg").st_size-size
            assert size - 64 * 1024 <= os.stat(u"{0}/testfiles/output/gpgwrite.gpg".format(_runtest_dir)).st_size <= size + 64 * 1024
        gwfh.set_at_end()
        gpg.GPGWriteFile(gwfh, u"{0}/testfiles/output/gpgwrite.gpg".format(_runtest_dir),
                         profile, size=size)
        # print os.stat("/tmp/testfiles/output/gpgwrite.gpg").st_size

    def test_GzipWriteFile(self):
        u"""Test GzipWriteFile"""
        size = 400 * 1000
        gwfh = GPGWriteFile_Helper()
        for i in range(10):
            gpg.GzipWriteFile(gwfh, u"{0}/testfiles/output/gzwrite.gz".format(_runtest_dir),
                              size=size)
            # print os.stat("/tmp/testfiles/output/gzwrite.gz").st_size-size
            assert size - 64 * 1024 <= os.stat(u"{0}/testfiles/output/gzwrite.gz".format(_runtest_dir)).st_size <= size + 64 * 1024
        gwfh.set_at_end()
        gpg.GzipWriteFile(gwfh, u"{0}/testfiles/output/gzwrite.gz".format(_runtest_dir), size=size)
        # print os.stat("/tmp/testfiles/output/gzwrite.gz").st_size


class GPGWriteHelper2(object):
    def __init__(self, data):
        self.data = data


class GPGWriteFile_Helper(object):
    u"""Used in test_GPGWriteFile above"""
    def __init__(self):
        self.from_random_fp = open(u"/dev/urandom", u"rb")
        self.at_end = 0

    def set_at_end(self):
        u"""Iterator stops when you call this"""
        self.at_end = 1

    def get_buffer(self, size):
        u"""Return buffer of size size, consisting of half random data"""
        s1 = int(old_div(size, 2))
        s2 = size - s1
        return b"a" * s1 + self.from_random_fp.read(s2)

    def __next__(self):
        if self.at_end:
            raise StopIteration
        block_data = self.get_buffer(self.get_read_size())
        return GPGWriteHelper2(block_data)

    def get_read_size(self):
        size = 64 * 1024
        if random.randrange(2):
            return size
        else:
            return random.randrange(0, size)

    def get_footer(self):
        return b"e" * random.randrange(0, 15000)


class SHATest(UnitTestCase):
    u"""Test making sha signatures"""
    def setUp(self):
        super(SHATest, self).setUp()
        self.unpack_testfiles()

    def test_sha(self):
        testhash = gpg.get_hash(u"SHA1", path.Path(u"{0}/testfiles/various_file_types/regular_file".format(_runtest_dir)))
        assert testhash == u"886d722999862724e1e62d0ac51c468ee336ef8e", testhash


if __name__ == u"__main__":
    unittest.main()
