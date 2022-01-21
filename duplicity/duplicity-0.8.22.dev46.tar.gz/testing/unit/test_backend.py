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
from future import standard_library
standard_library.install_aliases()

import sys
import mock
import unittest

import duplicity.backend
import duplicity.backends
from duplicity.errors import *  # pylint: disable=unused-wildcard-import
from duplicity import config
from . import UnitTestCase


@unittest.skipIf(sys.version_info[:2] < (3, 6), u"Skip on bad urllib.parse handling")
class ParsedUrlTest(UnitTestCase):
    u"""Test the ParsedUrl class"""
    def test_basic(self):
        u"""Test various url strings"""
        pu = duplicity.backend.ParsedUrl(u"scp://ben@foo.bar:1234/a/b")
        assert pu.scheme == u"scp", pu.scheme
        assert pu.netloc == u"ben@foo.bar:1234", pu.netloc
        assert pu.path == u"/a/b", pu.path
        assert pu.username == u"ben", pu.username
        assert pu.port == 1234, pu.port
        assert pu.hostname == u"foo.bar", pu.hostname

        pu = duplicity.backend.ParsedUrl(u"ftp://foo.bar:1234/")
        assert pu.scheme == u"ftp", pu.scheme
        assert pu.netloc == u"foo.bar:1234", pu.netloc
        assert pu.path == u"/", pu.path
        assert pu.username is None, pu.username
        assert pu.port == 1234, pu.port
        assert pu.hostname == u"foo.bar", pu.hostname

        pu = duplicity.backend.ParsedUrl(u"file:///home")
        assert pu.scheme == u"file", pu.scheme
        assert pu.netloc == u"", pu.netloc
        assert pu.path == u"///home", pu.path
        assert pu.username is None, pu.username
        assert pu.port is None, pu.port

        pu = duplicity.backend.ParsedUrl(u"file://home")
        assert pu.scheme == u"file", pu.scheme
        assert pu.netloc == u"", pu.netloc
        assert pu.path == u"//home", pu.path
        assert pu.username is None, pu.username
        assert pu.port is None, pu.port

        pu = duplicity.backend.ParsedUrl(u"ftp://foo@bar:pass@example.com:123/home")
        assert pu.scheme == u"ftp", pu.scheme
        assert pu.netloc == u"foo@bar:pass@example.com:123", pu.netloc
        assert pu.hostname == u"example.com", pu.hostname
        assert pu.path == u"/home", pu.path
        assert pu.username == u"foo@bar", pu.username
        assert pu.password == u"pass", pu.password
        assert pu.port == 123, pu.port

        pu = duplicity.backend.ParsedUrl(u"ftp://foo%40bar:pass@example.com:123/home")
        assert pu.scheme == u"ftp", pu.scheme
        assert pu.netloc == u"foo%40bar:pass@example.com:123", pu.netloc
        assert pu.hostname == u"example.com", pu.hostname
        assert pu.path == u"/home", pu.path
        assert pu.username == u"foo@bar", pu.username
        assert pu.password == u"pass", pu.password
        assert pu.port == 123, pu.port

        pu = duplicity.backend.ParsedUrl(u"imap://foo@bar:pass@example.com:123/home")
        assert pu.scheme == u"imap", pu.scheme
        assert pu.netloc == u"foo@bar:pass@example.com:123", pu.netloc
        assert pu.hostname == u"example.com", pu.hostname
        assert pu.path == u"/home", pu.path
        assert pu.username == u"foo@bar", pu.username
        assert pu.password == u"pass", pu.password
        assert pu.port == 123, pu.port

        pu = duplicity.backend.ParsedUrl(u"imap://foo@bar@example.com:123/home")
        assert pu.scheme == u"imap", pu.scheme
        assert pu.netloc == u"foo@bar@example.com:123", pu.netloc
        assert pu.hostname == u"example.com", pu.hostname
        assert pu.path == u"/home", pu.path
        assert pu.username == u"foo@bar", pu.username
        assert pu.password is None, pu.password
        assert pu.port == 123, pu.port

        pu = duplicity.backend.ParsedUrl(u"imap://foo@bar@example.com/home")
        assert pu.scheme == u"imap", pu.scheme
        assert pu.netloc == u"foo@bar@example.com", pu.netloc
        assert pu.hostname == u"example.com", pu.hostname
        assert pu.path == u"/home", pu.path
        assert pu.username == u"foo@bar", pu.username
        assert pu.password is None, pu.password
        assert pu.port is None, pu.port

        pu = duplicity.backend.ParsedUrl(u"imap://foo@bar.com@example.com/home")
        assert pu.scheme == u"imap", pu.scheme
        assert pu.netloc == u"foo@bar.com@example.com", pu.netloc
        assert pu.hostname == u"example.com", pu.hostname
        assert pu.path == u"/home", pu.path
        assert pu.username == u"foo@bar.com", pu.username
        assert pu.password is None, pu.password
        assert pu.port is None, pu.port

        pu = duplicity.backend.ParsedUrl(u"imap://foo%40bar.com@example.com/home")
        assert pu.scheme == u"imap", pu.scheme
        assert pu.netloc == u"foo%40bar.com@example.com", pu.netloc
        assert pu.hostname == u"example.com", pu.hostname
        assert pu.path == u"/home", pu.path
        assert pu.username == u"foo@bar.com", pu.username
        assert pu.password is None, pu.password
        assert pu.port is None, pu.port

        pu = duplicity.backend.ParsedUrl(u"scheme://username:passwor@127.0.0.1:22/path/path")
        assert pu.strip_auth() == u"scheme://127.0.0.1:22/path/path"

    def test_errors(self):
        u"""Test various url errors"""
        self.assertRaises(InvalidBackendURL, duplicity.backend.ParsedUrl,
                          u"file:path")  # no relative paths for non-netloc schemes
        self.assertRaises(UnsupportedBackendScheme, duplicity.backend.get_backend,
                          u"ssh://foo@bar:pass@example.com/home")


class BackendWrapperTest(UnitTestCase):

    def setUp(self):
        super(BackendWrapperTest, self).setUp()
        self.mock = mock.MagicMock()
        self.backend = duplicity.backend.BackendWrapper(self.mock)
        self.local = mock.MagicMock()
        self.remote = u'remote'

    @mock.patch(u'sys.exit')
    def test_default_error_exit(self, exit_mock):
        self.set_config(u'num_retries', 1)
        try:
            del self.mock._error_code
        except:
            # Old versions of mock don't let you mark non-present attributes
            # like this.
            return  # can't use self.skip() since that needs py27
        self.mock._put.side_effect = Exception
        self.backend.put(self.local, self.remote)
        exit_mock.assert_called_once_with(50)

    @mock.patch(u'sys.exit')
    def test_translates_code(self, exit_mock):
        self.set_config(u'num_retries', 1)
        self.mock._error_code.return_value = 12345
        self.mock._put.side_effect = Exception
        self.backend.put(self.local, self.remote)
        exit_mock.assert_called_once_with(12345)

    @mock.patch(u'sys.exit')
    def test_uses_exception_code(self, exit_mock):
        self.set_config(u'num_retries', 1)
        self.mock._error_code.return_value = 12345
        self.mock._put.side_effect = BackendException(u'error', code=54321)
        self.backend.put(self.local, self.remote)
        exit_mock.assert_called_once_with(54321)

    @mock.patch(u'sys.exit')
    @mock.patch(u'time.sleep')  # so no waiting
    def test_cleans_up(self, exit_mock, time_mock):  # pylint: disable=unused-argument
        self.set_config(u'num_retries', 2)
        self.mock._retry_cleanup.return_value = None
        self.mock._put.side_effect = Exception
        self.backend.put(self.local, self.remote)
        self.mock._retry_cleanup.assert_called_once_with()

    def test_prefer_lists(self):
        self.mock._delete.return_value = None
        self.mock._delete_list.return_value = None
        self.backend.delete([self.remote])
        self.assertEqual(self.mock._delete.call_count, 0)
        self.assertEqual(self.mock._delete_list.call_count, 1)
        try:
            del self.mock._delete_list
        except:
            return
        self.backend.delete([self.remote])
        self.assertEqual(self.mock._delete.call_count, 1)

        self.mock._query.return_value = None
        self.mock._query_list.return_value = None
        self.backend.query_info([self.remote])
        self.assertEqual(self.mock._query.call_count, 0)
        self.assertEqual(self.mock._query_list.call_count, 1)
        try:
            del self.mock._query_list
        except:
            return
        self.backend.query_info([self.remote])
        self.assertEqual(self.mock._query.call_count, 1)

    @mock.patch(u'sys.exit')
    @mock.patch(u'time.sleep')  # so no waiting
    def test_retries(self, exit_mock, time_mock):  # pylint: disable=unused-argument
        self.set_config(u'num_retries', 2)

        self.mock._get.side_effect = Exception
        self.backend.get(self.remote, self.local)
        self.assertEqual(self.mock._get.call_count, config.num_retries)

        self.mock._put.side_effect = Exception
        self.backend.put(self.local, self.remote)
        self.assertEqual(self.mock._put.call_count, config.num_retries)

        self.mock._list.side_effect = Exception
        self.backend.list()
        self.assertEqual(self.mock._list.call_count, config.num_retries)

        self.mock._delete_list.side_effect = Exception
        self.backend.delete([self.remote])
        self.assertEqual(self.mock._delete_list.call_count, config.num_retries)

        self.mock._query_list.side_effect = Exception
        self.backend.query_info([self.remote])
        self.assertEqual(self.mock._query_list.call_count, config.num_retries)

        try:
            del self.mock._delete_list
        except:
            return
        self.mock._delete.side_effect = Exception
        self.backend.delete([self.remote])
        self.assertEqual(self.mock._delete.call_count, config.num_retries)

        try:
            del self.mock._query_list
        except:
            return
        self.mock._query.side_effect = Exception
        self.backend.query_info([self.remote])
        self.assertEqual(self.mock._query.call_count, config.num_retries)

        self.mock._move.side_effect = Exception
        self.backend.move(self.local, self.remote)
        self.assertEqual(self.mock._move.call_count, config.num_retries)

    def test_move(self):
        self.mock._move.return_value = True
        self.backend.move(self.local, self.remote)
        self.mock._move.assert_called_once_with(self.local, self.remote)
        self.assertEqual(self.mock._put.call_count, 0)

    def test_move_fallback_false(self):
        self.mock._move.return_value = False
        self.backend.move(self.local, self.remote)
        self.mock._move.assert_called_once_with(self.local, self.remote)
        self.mock._put.assert_called_once_with(self.local, self.remote)
        self.local.delete.assert_called_once_with()

    def test_move_fallback_undefined(self):
        try:
            del self.mock._move
        except:
            return
        self.backend.move(self.local, self.remote)
        self.mock._put.assert_called_once_with(self.local, self.remote)
        self.local.delete.assert_called_once_with()

    def test_close(self):
        self.mock._close.return_value = None
        self.backend.close()
        self.mock._close.assert_called_once_with()


if __name__ == u"__main__":
    unittest.main()
