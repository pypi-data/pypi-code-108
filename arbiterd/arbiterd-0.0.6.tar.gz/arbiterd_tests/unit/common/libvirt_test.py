# -*- coding: utf-8 -*-
# Copyright 2021 - 2021, Sean Mooney and the arbiterd contributors
# SPDX-License-Identifier: Apache-2.0
from unittest import mock

import testtools
from arbiterd.common import libvirt


class TestLibvirt(testtools.TestCase):

    @mock.patch.object(libvirt.Libvirt, 'import_libvirt')
    @mock.patch.object(libvirt.Libvirt, 'get_connection')
    def test_init(self, mock_conn, mock_import):
        mock_conn.return_value = 42
        libvirt_obj = libvirt.Libvirt()
        self.assertEqual(libvirt_obj.uri, libvirt.LIBVIRT_URI)
        mock_conn.assert_called_once()
        self.assertEqual(libvirt_obj.conn, 42)
        mock_import.assert_called_once()

    @mock.patch('importlib.import_module')
    @mock.patch.object(libvirt.Libvirt, 'get_connection')
    def test_import_libvirt(self, mock_conn, mock_import):
        mock_import.return_value = None
        libvirt.Libvirt()
        mock_import.assert_called_once_with('libvirt')

    @mock.patch.object(libvirt, 'libvirt')
    @mock.patch.object(libvirt.Libvirt, '__init__')
    def test_get_connection(self, mock_init, mock_libvirt):
        mock_init.return_value = None
        libvirt_obj = libvirt.Libvirt()
        libvirt_obj.get_connection()
        mock_libvirt.openReadOnly.assert_called_once()

    @mock.patch.object(libvirt.Libvirt, 'import_libvirt')
    @mock.patch.object(libvirt.Libvirt, 'get_connection')
    def test_list_domains(self, mock_conn, mock_import):
        domain_mock = mock.Mock()
        mock_conn.return_value.listAllDomains = domain_mock
        domain_mock.return_value = [1, 2, 3]
        libvirt_obj = libvirt.Libvirt()
        result = libvirt_obj.list_domains()
        self.assertEqual(result, [1, 2, 3])
        domain_mock.assert_called_once_with(0)
