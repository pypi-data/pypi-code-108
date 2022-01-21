# -*- coding: utf-8 -*-
# Copyright 2021 - 2021, Sean Mooney and the arbiterd contributors
# SPDX-License-Identifier: Apache-2.0
from unittest import mock

import testtools
from arbiterd.objects import hardware_thread as ht


class TestHardwareThread(testtools.TestCase):

    def setUp(self):
        super().setUp()

    def test_default_init(self):
        thread = ht.HardwareThread()
        self.assertIsNone(thread.ident)
        self.assertIsNone(thread._path)

    @mock.patch('arbiterd.common.cpu.gen_cpu_path')
    def test_path(self, gen_mock):
        thread = ht.HardwareThread(ident=42)
        gen_mock.return_value = 'test/path'
        result = thread.path
        self.assertEqual(result, 'test/path')
        self.assertEqual(thread._path, 'test/path')
        gen_mock.assert_called_once_with(42)

    @mock.patch('arbiterd.common.cpu.get_online')
    def test_online(self, online_mock):
        thread = ht.HardwareThread(ident=42)
        thread._path = 'fake/path'
        online_mock.return_value = True
        result = thread.online
        self.assertTrue(result)
        online_mock.assert_called_once_with('fake/path')

    @mock.patch('arbiterd.common.cpu.set_online')
    def test_set_online(self, online_mock):
        thread = ht.HardwareThread(ident=42)
        thread._path = 'fake/path'
        online_mock.return_value = True
        thread.online = True
        online_mock.assert_called_once_with('fake/path')

    @mock.patch('arbiterd.common.cpu.set_offline')
    def test_set_offline(self, online_mock):
        thread = ht.HardwareThread(ident=42)
        thread._path = 'fake/path'
        online_mock.return_value = True
        thread.online = False
        online_mock.assert_called_once_with('fake/path')
