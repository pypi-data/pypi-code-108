# -*- coding: utf-8 -*-
# Copyright 2021 - 2021, Sean Mooney and the arbiterd contributors
# SPDX-License-Identifier: Apache-2.0
import typing as ty
from unittest import mock

import testtools
from arbiterd.common import cpu


class TestCPU(testtools.TestCase):

    def setUp(self):
        super().setUp()
        patcher = mock.patch('arbiterd.common.filesystem.read_sys')
        self.read_mock = patcher.start()
        self.addCleanup(patcher.stop)

    def test_parse_cpu_spec_list(self):
        data = cpu.parse_cpu_spec('1,2,3,4')
        self.assertIsInstance(data, ty.Set)
        self.assertEqual(data, {1, 2, 3, 4})

    def test_parse_cpu_spec_range(self):
        data = cpu.parse_cpu_spec('1-4')
        self.assertIsInstance(data, ty.Set)
        self.assertEqual(data, {1, 2, 3, 4})

    def test_parse_cpu_spec_negation(self):
        data = cpu.parse_cpu_spec('1-4,^3')
        self.assertIsInstance(data, ty.Set)
        self.assertEqual(data, {1, 2, 4})

    def test_parse_cpu_spec_negation_range(self):
        data = cpu.parse_cpu_spec('1-4,^2-3')
        self.assertIsInstance(data, ty.Set)
        self.assertEqual(data, {1, 4})

    def test_get_available_cpus(self):
        self.read_mock.return_value = '1-4'
        result = cpu.get_available_cpus()
        self.read_mock.assert_called_once_with(cpu.AVAILABLE_PATH)
        self.assertEqual(result, {1, 2, 3, 4})

    def test_get_online_cpus(self):
        self.read_mock.return_value = '1-4'
        result = cpu.get_online_cpus()
        self.read_mock.assert_called_once_with(cpu.ONLINE_PATH)
        self.assertEqual(result, {1, 2, 3, 4})

    def test_get_offline_cpus(self):
        self.read_mock.return_value = '1-4'
        result = cpu.get_offline_cpus()
        self.read_mock.assert_called_once_with(cpu.OFFLINE_PATH)
        self.assertEqual(result, {1, 2, 3, 4})

    def test_empty_set(self):
        self.read_mock.return_value = ''
        for func in (
                cpu.get_available_cpus,
                cpu.get_online_cpus,
                cpu.get_offline_cpus
        ):
            self.assertEqual(func(), set())

    def test_nproc(self):
        with mock.patch.object(cpu, 'get_available_cpus') as a_cpus:
            a_cpus.return_value = {1, 2}
            self.assertEqual(cpu.nproc(), 2)

    def test_get_cpu_path(self):
        with mock.patch(
                'arbiterd.common.filesystem.get_sys_fs_mount') as sys_mock,\
            mock.patch(
                'arbiterd.common.cpu.exists', return_value=True):
            sys_mock.return_value = '/sys'
            self.assertEqual(
                cpu.gen_cpu_path(1), '/sys/devices/system/cpu/cpu1')

    def test_get_cpu_paths(self):
        with mock.patch(
            'arbiterd.common.filesystem.get_sys_fs_mount') as sys_mock, \
                mock.patch.object(cpu, 'nproc') as nproc_mock:
            sys_mock.return_value = '/sys'
            nproc_mock.return_value = 1
            self.assertEqual(
                list(cpu.gen_cpu_paths()), ['/sys/devices/system/cpu/cpu0'])

    def test_get_online(self):
        self.read_mock.return_value = '1'
        self.assertTrue(cpu.get_online('/fake/path'))
        self.read_mock.assert_called_once_with(
            '/fake/path/online', default='1')
        self.read_mock.return_value = '0'
        self.assertFalse(cpu.get_online('/fake/path'))
