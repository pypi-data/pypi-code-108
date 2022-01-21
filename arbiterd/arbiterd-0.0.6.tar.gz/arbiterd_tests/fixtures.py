# -*- coding: utf-8 -*-
# Copyright 2021 - 2021, Sean Mooney and the arbiterd contributors
# SPDX-License-Identifier: Apache-2.0
import os
import shutil
import tempfile
from unittest import mock

import fixtures

import arbiterd_tests.test_data as td

DATA_PATH_BASE = os.path.abspath(td.__path__[0])
SYS = 'sys'
ETC = 'etc'


class TEMPFileSystemFixture(fixtures.Fixture):
    """Creates a fake / filesystem"""

    def _setUp(self):
        if not hasattr(self, 'temp_dir'):
            self.temp_dir = tempfile.mkdtemp(prefix='arbiterd_tests')
            self.addCleanup(shutil.rmtree, self.temp_dir, ignore_errors=True)


class SYSFileSystemFixture(TEMPFileSystemFixture):
    """Creates a fake /sys filesystem"""

    def _setUp(self):
        super()._setUp()
        self.sys_path = os.path.join(self.temp_dir, SYS)
        self.addCleanup(shutil.rmtree, self.sys_path, ignore_errors=True)
        shutil.copytree(
            os.path.join(DATA_PATH_BASE, SYS),
            self.sys_path, symlinks=True,
            ignore_dangling_symlinks=True
        )
        sys_patcher = mock.patch(
            'arbiterd.common.filesystem.get_sys_fs_mount')
        self.sys_mock = sys_patcher.start()
        self.sys_mock.return_value = self.sys_path
        self.addCleanup(sys_patcher.stop)


class ETCFileSystemFixture(TEMPFileSystemFixture):
    """Creates a fake /etc filesystem"""

    def _setUp(self):
        super()._setUp()
        self.etc_path = os.path.join(self.temp_dir, ETC)
        self.addCleanup(shutil.rmtree, self.etc_path, ignore_errors=True)
        shutil.copytree(
            os.path.join(DATA_PATH_BASE, ETC),
            self.etc_path, symlinks=True,
            ignore_dangling_symlinks=True
        )
        etc_patcher = mock.patch(
            'arbiterd.common.filesystem.get_etc_fs_mount')
        self.etc_mock = etc_patcher.start()
        self.etc_mock.return_value = self.etc_path
        self.addCleanup(etc_patcher.stop)
