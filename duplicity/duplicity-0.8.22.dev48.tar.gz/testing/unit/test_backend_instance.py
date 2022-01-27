# -*- Mode:Python; indent-tabs-mode:nil; tab-width:4; encoding:utf8 -*-
#
# Copyright 2014 Canonical Ltd
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

import os
import io
import unittest

from . import UnitTestCase
from duplicity import log
from duplicity import path
from duplicity import util
from duplicity.errors import BackendException
import duplicity.backend

from testing import _runtest_dir
from testing import _testing_dir

class BackendInstanceBase(UnitTestCase):

    def setUp(self):
        UnitTestCase.setUp(self)
        assert not os.system(u"rm -rf {0}/testfiles".format(_runtest_dir))
        os.makedirs(u'{0}/testfiles'.format(_runtest_dir))
        self.backend = None
        self.local = path.Path(u'{0}/testfiles/local'.format(_runtest_dir))
        self.local.writefileobj(io.BytesIO(b"hello"))

    def tearDown(self):
        assert not os.system(u"rm -rf {0}/testfiles".format(_runtest_dir))
        if self.backend is None:
            return
        if hasattr(self.backend, u'_close'):
            self.backend._close()

    def test_get(self):
        if self.backend is None:
            return
        self.backend._put(self.local, b'file-a')
        getfile = path.Path(u'{0}/testfiles/getfile'.format(_runtest_dir))
        self.backend._get(b'file-a', getfile)
        self.assertTrue(self.local.compare_data(getfile))

    def test_list(self):
        if self.backend is None:
            return
        self.backend._put(self.local, b'file-a')
        self.backend._put(self.local, b'file-b')
        # It's OK for backends to create files as a side effect of put (e.g.
        # the par2 backend does), so only check that at least a and b exist.
        self.assertTrue(b'file-a' in self.backend._list())
        self.assertTrue(b'file-b' in self.backend._list())

    def test_delete(self):
        if self.backend is None:
            return
        if not hasattr(self.backend, u'_delete'):
            self.assertTrue(hasattr(self.backend, u'_delete_list'))
            return
        self.backend._put(self.local, b'file-a')
        self.backend._put(self.local, b'file-b')
        self.backend._delete(b'file-a')
        self.assertFalse(b'file-a' in self.backend._list())
        self.assertTrue(b'file-b' in self.backend._list())

    def test_delete_clean(self):
        if self.backend is None:
            return
        if not hasattr(self.backend, u'_delete'):
            self.assertTrue(hasattr(self.backend, u'_delete_list'))
            return
        self.backend._put(self.local, b'file-a')
        self.backend._delete(b'file-a')
        self.assertFalse(b'file-a' in self.backend._list())

    def test_delete_missing(self):
        if self.backend is None:
            return
        if not hasattr(self.backend, u'_delete'):
            self.assertTrue(hasattr(self.backend, u'_delete_list'))
            return
        # Backends can either silently ignore this, or throw an error
        # that gives log.ErrorCode.backend_not_found.
        try:
            self.backend._delete(b'file-a')
        except BackendException as e:
            pass  # Something went wrong, but it was an 'expected' something
        except Exception as e:
            code = duplicity.backend._get_code_from_exception(self.backend, u'delete', e)
            self.assertEqual(code, log.ErrorCode.backend_not_found)

    def test_delete_list(self):
        if self.backend is None:
            return
        if not hasattr(self.backend, u'_delete_list'):
            self.assertTrue(hasattr(self.backend, u'_delete'))
            return
        self.backend._put(self.local, b'file-a')
        self.backend._put(self.local, b'file-b')
        self.backend._put(self.local, b'file-c')
        self.backend._delete_list([b'file-a', b'd', b'file-c'])
        files = self.backend._list()
        self.assertFalse(b'file-a' in files, files)
        self.assertTrue(b'file-b' in files, files)
        self.assertFalse(b'file-c' in files, files)

    def test_move(self):
        if self.backend is None:
            return
        if not hasattr(self.backend, u'_move'):
            return

        copy = path.Path(u'{0}/testfiles/copy'.format(_runtest_dir))
        self.local.copy(copy)

        self.backend._move(self.local, b'file-a')
        self.assertTrue(b'file-a' in self.backend._list())
        self.assertFalse(self.local.exists())

        getfile = path.Path(u'{0}/testfiles/getfile'.format(_runtest_dir))
        self.backend._get(b'file-a', getfile)
        self.assertTrue(copy.compare_data(getfile))

    def test_query_exists(self):
        if self.backend is None:
            return
        if not hasattr(self.backend, u'_query'):
            return
        self.backend._put(self.local, b'file-a')
        info = self.backend._query(b'file-a')
        self.assertEqual(info[u'size'], self.local.getsize())

    def test_query_missing(self):
        if self.backend is None:
            return
        if not hasattr(self.backend, u'_query'):
            return
        # Backends can either return -1 themselves, or throw an error
        # that gives log.ErrorCode.backend_not_found.
        try:
            info = self.backend._query(b'file-a')
        except BackendException as e:
            pass  # Something went wrong, but it was an 'expected' something
        except Exception as e:
            code = duplicity.backend._get_code_from_exception(self.backend, u'query', e)
            self.assertEqual(code, log.ErrorCode.backend_not_found)
        else:
            self.assertEqual(info[u'size'], -1)

    def test_query_list(self):
        if self.backend is None:
            return
        if not hasattr(self.backend, u'_query_list'):
            return
        self.backend._put(self.local, b'file-a')
        self.backend._put(self.local, b'file-c')
        info = self.backend._query_list([b'file-a', b'file-b'])
        self.assertEqual(info[b'file-a'][u'size'], self.local.getsize())
        self.assertEqual(info[b'file-b'][u'size'], -1)
        self.assertFalse(b'file-c' in info)


class LocalBackendTest(BackendInstanceBase):
    def setUp(self):
        super(LocalBackendTest, self).setUp()
        url = u'file://{0}/testfiles/output'.format(_runtest_dir)
        self.backend = duplicity.backend.get_backend_object(url)
        self.assertEqual(self.backend.__class__.__name__, u'LocalBackend')


# TODO: Add par2-specific tests here, to confirm that we can recover
@unittest.skipIf(not util.which(u'par2'), u"par2 not installed")
class Par2BackendTest(BackendInstanceBase):
    def setUp(self):
        super(Par2BackendTest, self).setUp()
        url = u'par2+file://{0}/testfiles/output'.format(_runtest_dir)
        self.backend = duplicity.backend.get_backend_object(url)
        self.assertEqual(self.backend.__class__.__name__, u'Par2Backend')


# TODO: Fix so localhost is not required.  Fails on LP and GitLab
# class RsyncBackendTest(BackendInstanceBase):
#     def setUp(self):
#         super(RsyncBackendTest, self).setUp()
#         os.makedirs(u'{0}/testfiles/output')  # rsync needs it to exist first
#         url = u'rsync://localhost:2222//%s/{0}/testfiles/output' % os.getcwd()
#         self.backend = duplicity.backend.get_backend_object(url)
#         self.assertEqual(self.backend.__class__.__name__, u'RsyncBackend')


class TahoeBackendTest(BackendInstanceBase):
    def setUp(self):
        super(TahoeBackendTest, self).setUp()
        os.makedirs(u'{0}/testfiles/output'.format(_runtest_dir))
        url = u'tahoe://{0}/testfiles/output'.format(_runtest_dir)
        self.backend = duplicity.backend.get_backend_object(url)
        self.assertEqual(self.backend.__class__.__name__, u'TAHOEBackend')


# TODO: Modernize hsi backend stub
#  class HSIBackendTest(BackendInstanceBase):
#      def setUp(self):
#          super(HSIBackendTest, self).setUp()
#          os.makedirs(u'{0}/testfiles/output')
#          # hostname is ignored...  Seemingly on purpose
#          url = u'hsi://hostname%s/{0}/testfiles/output' % os.getcwd()
#          self.backend = duplicity.backend.get_backend_object(url)
#          self.assertEqual(self.backend.__class__.__name__, u'HSIBackend')


@unittest.skipIf(not util.which(u'lftp'), u"lftp not installed")
class FTPBackendTest(BackendInstanceBase):
    def setUp(self):
        super(FTPBackendTest, self).setUp()
        os.makedirs(u'{0}/testfiles/output'.format(_runtest_dir))
        url = u'ftp://user:pass@hostname/{0}/testfiles/output'.format(_runtest_dir)
        self.backend = duplicity.backend.get_backend_object(url)
        self.assertEqual(self.backend.__class__.__name__, u'LFTPBackend')


@unittest.skipIf(not util.which(u'lftp'), u"lftp not installed")
class FTPSBackendTest(BackendInstanceBase):
    def setUp(self):
        super(FTPSBackendTest, self).setUp()
        os.makedirs(u'{0}/testfiles/output'.format(_runtest_dir))
        url = u'ftps://user:pass@hostname/{0}/testfiles/output'.format(_runtest_dir)
        self.backend = duplicity.backend.get_backend_object(url)
        self.assertEqual(self.backend.__class__.__name__, u'LFTPBackend')


@unittest.skipIf(not util.which(u'rclone'), u"rclone not installed")
class RCloneBackendTest(BackendInstanceBase):
    def setUp(self):
        super(RCloneBackendTest, self).setUp()
        os.makedirs(u'{0}/testfiles/output'.format(_runtest_dir))
        url = u'rclone://duptest:/%s/{0}/testfiles/output'.format(_runtest_dir)
        self.backend = duplicity.backend.get_backend_object(url)
        self.assertEqual(self.backend.__class__.__name__, u'RcloneBackend')
