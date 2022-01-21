# -*- coding: utf-8 -*-
# Copyright 2021 - 2021, Sean Mooney and the arbiterd contributors
# SPDX-License-Identifier: Apache-2.0
import os
from unittest import mock

import testtools
from arbiterd.common import filesystem

from arbiterd_tests import fixtures as at_fixtures


class TestFSCommon(testtools.TestCase):

    def setUp(self):
        super().setUp()
        # clear all cached functions in setup to avoid
        # inter test interactions.
        filesystem.get_sys_fs_mount.cache_clear()
        filesystem.get_etc_fs_mount.cache_clear()

    def test_get_etc_fs_mount(self):
        self.assertEqual(filesystem.ETC, filesystem.get_etc_fs_mount())

    def test_get_sys_fs_mount(self):
        mtab_data = 'sysfs /sys'
        open_mock = mock.mock_open(read_data=mtab_data)
        with mock.patch('builtins.open', open_mock) as m_open:
            self.assertEqual(filesystem.SYS, filesystem.get_sys_fs_mount())
            # this function should be cached so calling it again should not
            # result in a second read.
            filesystem.get_sys_fs_mount()
            m_open.assert_called_once()

    def test_get_sys_fs_mount_raises(self):
        with mock.patch('builtins.open', side_effect=OSError()) as m_open:
            self.assertEqual(filesystem.SYS, filesystem.get_sys_fs_mount())
            m_open.assert_called_once()

    def test_get_sys_fs_mount_non_default_location(self):
        mtab_data = 'sysfs /sysfs'
        open_mock = mock.mock_open(read_data=mtab_data)
        with mock.patch('builtins.open', open_mock) as m_open:
            self.assertEqual('/sysfs', filesystem.get_sys_fs_mount())
            m_open.assert_called_once()

    def test_get_sys_fs_mount_shortest_mount_path(self):
        mtab_data = (b'sysfs /sys\n'
                     b'sysfs /sysfs')
        open_mock = mock.mock_open(read_data=mtab_data)
        with mock.patch('builtins.open', open_mock) as m_open:
            self.assertEqual(filesystem.SYS, filesystem.get_sys_fs_mount())
            m_open.assert_called_once()


class TestFSTestData(testtools.TestCase):

    def test_import_test_data(self):
        import arbiterd_tests.test_data as td
        self.assertIsNotNone(td)

    def test_sysfs_test_data_exists(self):
        import arbiterd_tests.test_data as td
        data_path_base = os.path.abspath(td.__path__[0])
        print(data_path_base)
        self.assertTrue(os.path.exists(data_path_base))
        sys_path = os.path.join(data_path_base, filesystem.SYS)
        self.assertTrue(os.path.exists(sys_path))

    def test_sysfs_fixture(self):
        fs_fixture = at_fixtures.SYSFileSystemFixture()
        self.useFixture(fs_fixture)
        self.assertTrue(os.path.exists(fs_fixture.temp_dir))
        self.assertTrue(os.path.exists(fs_fixture.sys_path))
        self.assertIs(filesystem.get_sys_fs_mount, fs_fixture.sys_mock)
        self.assertEqual(fs_fixture.sys_path, filesystem.get_sys_fs_mount())
