# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4; encoding:utf8 -*-
#
u"""py-unit tests for GnuPG

COPYRIGHT:

Copyright (C) 2001  Frank J. Tobin, ftobin@neverending.org

LICENSE:

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
or see http://www.gnu.org/copyleft/lesser.html
"""

from __future__ import print_function
from future import standard_library
standard_library.install_aliases()

import unittest

import tempfile

from duplicity import gpginterface

__author__ = u"Frank J. Tobin, ftobin@neverending.org"
__version__ = u"0.2.2"
__revision__ = u"$Id: GnuPGInterfacetest.py,v 1.11 2009/06/06 17:35:19 loafman Exp $"


class BasicTest(unittest.TestCase):
    u"""an initializer superclass"""

    def __init__(self, methodName=None):
        self.gnupg = gpginterface.GnuPG()
        unittest.TestCase.__init__(self, methodName)


class GnuPGTests(BasicTest):
    u"""Tests for GnuPG class"""

    def __init__(self, methodName=None):
        BasicTest.__init__(self, methodName)

        self.gnupg.passphrase = u"Three blind mice"
        self.gnupg.options.armor = 1
        self.gnupg.options.meta_interactive = 0
        self.gnupg.options.extra_args.append(u'--no-secmem-warning')

    def do_create_fh_operation(self, args, input, passphrase=None):  # pylint: disable=redefined-builtin
        creations = [u'stdin', u'stdout']

        # Make sure we're getting the passphrase to GnuPG
        # somehow!
        assert passphrase is not None or self.gnupg.passphrase is not None, \
            u"No way to send the passphrase to GnuPG!"

        # We'll handle the passphrase manually
        if passphrase is not None:
            creations.append(u'passphrase')

        proc = self.gnupg.run(args, create_fhs=creations)

        if passphrase is not None:
            proc.handles[u'passphrase'].write(passphrase)
            proc.handles[u'passphrase'].close()

        proc.handles[u'stdin'].write(input)
        proc.handles[u'stdin'].close()

        ciphertext = proc.handles[u'stdout'].read()
        proc.handles[u'stdout'].close()

        # Checking to make sure GnuPG exited successfully
        proc.wait()

        return ciphertext

    def do_attach_fh_operation(self, args, stdin, stdout,
                               passphrase=None):

        # Make sure we're getting the passphrase to GnuPG
        # somehow!
        assert passphrase is not None or self.gnupg.passphrase is not None, \
            u"No way to send the passphrase to GnuPG!"

        creations = []
        attachments = {u'stdin': stdin, u'stdout': stdout}

        proc = self.gnupg.run(args, create_fhs=creations,
                              attach_fhs=attachments)

        # We'll handle the passphrase manually
        if passphrase is not None:
            proc.handles.append(u'passphrase')

        if passphrase is not None:
            proc.handles[u'passphrase'].write(passphrase)
            proc.handles[u'passphrase'].close()

        # Checking to make sure GnuPG exited successfully
        proc.wait()

    def test_create_fhs_solely(self):
        u"""Do GnuPG operations using solely the create_fhs feature"""
        plaintext = b"Three blind mice"

        ciphertext = self.do_create_fh_operation([u'--symmetric'],
                                                 plaintext)

        decryption = self.do_create_fh_operation([u'--decrypt'],
                                                 ciphertext,
                                                 self.gnupg.passphrase)
        assert decryption == plaintext, \
            u"GnuPG decrypted output does not match original input"

    def test_attach_fhs(self):
        u"""Do GnuPG operations using the attach_fhs feature"""
        plaintext_source = __file__

        plainfile = open(plaintext_source, u"rb")
        temp1 = tempfile.TemporaryFile()
        temp2 = tempfile.TemporaryFile()

        self.do_attach_fh_operation([u'--symmetric'],
                                    stdin=plainfile, stdout=temp1)

        temp1.seek(0)

        self.do_attach_fh_operation([u'--decrypt'],
                                    stdin=temp1, stdout=temp2)

        plainfile.seek(0)
        temp2.seek(0)

        assert fh_cmp(plainfile, temp2), \
            u"GnuPG decrypted output does not match original input"


class OptionsTests(BasicTest):
    u"""Tests for Options class"""

    def __init__(self, methodName=None):
        BasicTest.__init__(self, methodName)
        self.reset_options()

    def reset_options(self):
        self.gnupg.options = gpginterface.Options()

    def option_to_arg(self, option):
        return u'--' + option.replace(u'_', u'-')

    def test_boolean_args(self):
        u"""test Options boolean options that they generate
        proper arguments"""

        booleans = [u'armor', u'no_greeting', u'no_verbose',
                    u'batch', u'always_trust', u'rfc1991',
                    u'quiet', u'openpgp', u'force_v3_sigs',
                    u'no_options', u'textmode']

        for option in booleans:
            self.reset_options()
            setattr(self.gnupg.options, option, 1)
            arg = self.option_to_arg(option)

            should_be = [arg]
            result = self.gnupg.options.get_args()

            assert should_be == result, \
                u"failure to set option '%s'; should be %s, but result is %s" \
                % (option, should_be, result)

    def test_string_args(self):
        u"""test Options string-taking options that they generate
        proper arguments"""

        strings = [u'homedir', u'default_key', u'comment', u'compress_algo',
                   u'options']

        string_value = u'test-argument'

        for option in strings:
            self.reset_options()
            setattr(self.gnupg.options, option, string_value)
            arg = self.option_to_arg(option)

            should_be = [arg, string_value]
            result = self.gnupg.options.get_args()

            assert should_be == result, \
                u"failure to set option '%s'; should be %s, but result is %s" \
                % (option, should_be, result)

    def test_list_args(self):
        u"""test Options string-taking options that they generate
        proper arguments"""

        lists = [u'recipients', u'encrypt_to']
        list_value = [u'test1', u'test2']

        for option in lists:
            self.reset_options()
            setattr(self.gnupg.options, option, list_value)

            # special case for recipients, since their
            # respective argument is 'recipient', not 'recipients'
            if option == u'recipients':
                arg = u'--recipient'
            else:
                arg = self.option_to_arg(option)

            should_be = []
            for v in list_value:
                should_be.extend([arg, v])

            result = self.gnupg.options.get_args()

            assert should_be == result, \
                u"failure to set option '%s'; should be %s, but result is %s" \
                % (option, should_be, result)


class PipesTests(unittest.TestCase):
    u"""Tests for Pipes class"""

    def test_constructor(self):
        self.pipe = gpginterface.Pipe(1, 2, 0)
        assert self.pipe.parent == 1
        assert self.pipe.child == 2
        assert not self.pipe.direct

########################################################################


def fh_cmp(f1, f2, bufsize=8192):
    while 1:
        b1 = f1.read(bufsize)
        b2 = f2.read(bufsize)
        if b1 != b2:
            return 0
        if not b1:
            return 1

########################################################################

if __name__ == u"__main__":
    unittest.main()
