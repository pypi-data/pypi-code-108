# -*- coding: utf-8 -*-
# Copyright 2021 - 2021, Sean Mooney and the arbiterd contributors
# SPDX-License-Identifier: Apache-2.0
import os
from unittest import mock

import testtools
from arbiterd.objects import instance

import arbiterd_tests.test_data as td

DATA_PATH_BASE = os.path.abspath(td.__path__[0])


class TestInstance(testtools.TestCase):

    def setUp(self):
        super().setUp()
        self.dom = mock.MagicMock()
        self.uuid = mock.sentinel.instance
        self.dom.UUID.return_value = self.uuid
        self.dom.UUIDString.return_value = str(self.uuid)
        self.dom.name.return_value = 'test-domain'
        test_xml = os.path.join(DATA_PATH_BASE, 'libvirt-domain.xml')
        with open(test_xml) as f:
            self.dom.XMLDesc.return_value = f.read()

    def test_default_init(self):
        inst = instance.Instance()
        self.assertIsNone(inst.name)
        self.assertIsNone(inst.uuid)
        with testtools.ExpectedException(
                ValueError,
                'domain lookup failed, name or uuid must be set.*'):
            inst.domain
        with testtools.ExpectedException(ValueError):
            inst.xml
        with testtools.ExpectedException(ValueError):
            inst.xml_str

    def test_from_domain(self):
        inst = instance.Instance.from_domain(self.dom)
        self.assertEqual(inst.uuid, str(self.uuid))
        self.assertEqual(inst.name, 'test-domain')
        self.assertEqual(inst.xml_str, self.dom.XMLDesc.return_value)
        self.assertTrue(inst.is_nova_instance)

    def test_cpu_affinity(self):
        inst = instance.Instance.from_domain(self.dom)
        affinity = inst.cpu_affinities
        expected = instance.CPUAffinity(
            set(), {1, 4, 37, 5, 6, 13, 25}, set(), set()
        )
        self.assertEqual(affinity, expected)
