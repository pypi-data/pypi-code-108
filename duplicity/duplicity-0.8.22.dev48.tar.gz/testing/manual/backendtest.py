#!/usr/bin/env python3
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

import os
import sys
import traceback
import unittest

_top_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), u'..', u'..')
sys.path.insert(0, _top_dir)

from duplicity import config

try:
    from testing.manual import test_config
except ImportError as e:
    # It's OK to not have copied config.py.tmpl over yet, if user is just
    # calling us directly to test a specific backend.  If they aren't, we'll
    # fail later when config.blah is used.
    traceback.print_exc()
    pass
from testing.unit.test_backend_instance import BackendInstanceBase
import duplicity.backend

# undo the overrides support that our testing framework adds
sys.path = [x for x in sys.path if u'/overrides' not in x]
os.environ[u'PATH'] = u':'.join([x for x in os.environ[u'PATH'].split(u':')
                               if u'/overrides' not in x])
os.environ[u'PYTHONPATH'] = u':'.join([x for x in os.environ[u'PYTHONPATH'].split(u':')
                                     if u'/overrides' not in x])


class ManualBackendBase(BackendInstanceBase):

    url_string = None
    password = None

    def setUp(self):
        super(ManualBackendBase, self).setUp()
        self.set_config(u'num_retries', 1)
        self.set_config(u'ssl_no_check_certificate', True)
        self.setBackendInfo()
        if self.password is not None:
            self.set_environ(u"FTP_PASSWORD", self.password)
        if self.url_string is not None:
            self.backend = duplicity.backend.get_backend_object(self.url_string)

        # Clear out backend first
        if self.backend is not None:
            if hasattr(self.backend, u'_delete_list'):
                self.backend._delete_list(self.backend._list())
            else:
                for x in self.backend._list():
                    self.backend._delete(x)

    def setBackendInfo(self):
        pass


class sshParamikoTest(ManualBackendBase):
    def setBackendInfo(self):
        from duplicity.backends import ssh_paramiko_backend
        duplicity.backend._backends[u'ssh'] = ssh_paramiko_backend.SSHParamikoBackend
        self.url_string = test_config.ssh_url
        self.password = test_config.ssh_password


class sshParamikoScpTest(ManualBackendBase):
    def setBackendInfo(self):
        from duplicity.backends import ssh_paramiko_backend
        duplicity.backend._backends[u'scp'] = ssh_paramiko_backend.SSHParamikoBackend
        self.url_string = test_config.ssh_url
        self.password = test_config.ssh_password


class sshPexpectTest(ManualBackendBase):
    def setBackendInfo(self):
        from duplicity.backends import ssh_pexpect_backend
        duplicity.backend._backends[u'ssh'] = ssh_pexpect_backend.SSHPExpectBackend
        self.url_string = test_config.ssh_url
        self.password = test_config.ssh_password


class sshPexpectScpTest(ManualBackendBase):
    def setBackendInfo(self):
        from duplicity.backends import ssh_pexpect_backend
        duplicity.backend._backends[u'scp'] = ssh_pexpect_backend.SSHPExpectBackend
        self.url_string = test_config.ssh_url
        self.password = test_config.ssh_password


class ftpTest(ManualBackendBase):
    def setBackendInfo(self):
        self.url_string = test_config.ftp_url
        self.password = test_config.ftp_password


class ftpsTest(ManualBackendBase):
    def setBackendInfo(self):
        self.url_string = test_config.ftp_url.replace(u'ftp://', u'ftps://') if test_config.ftp_url else None
        self.password = test_config.ftp_password


class gsTest(ManualBackendBase):
    def setBackendInfo(self):
        self.url_string = test_config.gs_url
        self.set_environ(u"GS_ACCESS_KEY_ID", test_config.gs_access_key)
        self.set_environ(u"GS_SECRET_ACCESS_KEY", test_config.gs_secret_key)


class s3SingleTest(ManualBackendBase):
    def setBackendInfo(self):
        from duplicity.backends import _boto_single
        duplicity.backend._backends[u's3+http'] = _boto_single.BotoBackend
        self.set_config(u's3_use_new_style', True)
        self.set_environ(u"AWS_ACCESS_KEY_ID", test_config.s3_access_key)
        self.set_environ(u"AWS_SECRET_ACCESS_KEY", test_config.s3_secret_key)
        self.url_string = test_config.s3_url


class s3MultiTest(ManualBackendBase):
    def setBackendInfo(self):
        from duplicity.backends import _boto_multi
        duplicity.backend._backends[u's3+http'] = _boto_multi.BotoBackend
        self.set_config(u's3_use_new_style', True)
        self.set_environ(u"AWS_ACCESS_KEY_ID", test_config.s3_access_key)
        self.set_environ(u"AWS_SECRET_ACCESS_KEY", test_config.s3_secret_key)
        self.url_string = test_config.s3_url


class cfCloudfilesTest(ManualBackendBase):
    def setBackendInfo(self):
        from duplicity.backends import _cf_cloudfiles
        duplicity.backend._backends[u'cf+http'] = _cf_cloudfiles.CloudFilesBackend
        self.set_environ(u"CLOUDFILES_USERNAME", test_config.cf_username)
        self.set_environ(u"CLOUDFILES_APIKEY", test_config.cf_api_key)
        self.url_string = test_config.cf_url


class cfPyraxTest(ManualBackendBase):
    def setBackendInfo(self):
        from duplicity.backends import _cf_pyrax
        duplicity.backend._backends[u'cf+http'] = _cf_pyrax.PyraxBackend
        self.set_environ(u"CLOUDFILES_USERNAME", test_config.cf_username)
        self.set_environ(u"CLOUDFILES_APIKEY", test_config.cf_api_key)
        self.url_string = test_config.cf_url


class swiftTest(ManualBackendBase):
    def setBackendInfo(self):
        self.url_string = test_config.swift_url
        self.set_environ(u"SWIFT_USERNAME", test_config.swift_username)
        self.set_environ(u"SWIFT_PASSWORD", test_config.swift_password)
        self.set_environ(u"SWIFT_TENANTNAME", test_config.swift_tenant)
        # Assumes you're just using the same storage as your cloudfiles config above
        self.set_environ(u"SWIFT_AUTHURL", u'https://identity.api.rackspacecloud.com/v2.0/')
        self.set_environ(u"SWIFT_AUTHVERSION", u'2')


class megaTest(ManualBackendBase):
    def setBackendInfo(self):
        self.url_string = test_config.mega_url
        self.password = test_config.mega_password


class webdavTest(ManualBackendBase):
    def setBackendInfo(self):
        self.url_string = test_config.webdav_url
        self.password = test_config.webdav_password


class webdavsTest(ManualBackendBase):
    def setBackendInfo(self):
        self.url_string = test_config.webdavs_url
        self.password = test_config.webdavs_password
        self.set_config(u'ssl_no_check_certificate', True)


class gdocsTest(ManualBackendBase):
    def setBackendInfo(self):
        self.url_string = test_config.gdocs_url
        self.password = test_config.gdocs_password


class dpbxTest(ManualBackendBase):
    def setBackendInfo(self):
        self.url_string = test_config.dpbx_url


class imapTest(ManualBackendBase):
    def setBackendInfo(self):
        self.url_string = test_config.imap_url
        self.set_environ(u"IMAP_PASSWORD", test_config.imap_password)
        self.set_config(u'imap_mailbox', u'deja-dup-testing')


class gioSSHTest(ManualBackendBase):
    def setBackendInfo(self):
        self.url_string = u'gio+' + test_config.ssh_url if test_config.ssh_url else None
        self.password = test_config.ssh_password


class gioFTPTest(ManualBackendBase):
    def setBackendInfo(self):
        self.url_string = u'gio+' + test_config.ftp_url if test_config.ftp_url else None
        self.password = test_config.ftp_password


if __name__ == u"__main__":
    defaultTest = None
    if len(sys. argv) > 1:
        class manualTest(ManualBackendBase):
            def setBackendInfo(self):
                self.url_string = sys.argv[1]
        defaultTest = u'manualTest'
    unittest.main(argv=[sys.argv[0]], defaultTest=defaultTest)
