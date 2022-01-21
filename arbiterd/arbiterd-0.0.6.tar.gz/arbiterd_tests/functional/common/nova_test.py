# -*- coding: utf-8 -*-
# Copyright 2021 - 2021, Sean Mooney and the arbiterd contributors
# SPDX-License-Identifier: Apache-2.0
import configparser
import os

from arbiterd.common import filesystem
from arbiterd.common import nova

from arbiterd_tests import base


class TestNovaData(base.ATTestCase):
    # This is a functional test class that use the etc test fixture
    # to create a fake copy of /etc which it the used in the tests.

    USE_SYS_FIXTURE = False

    def setUp(self):
        super().setUp()
        # clear all cached functions.
        nova.parse_nova_conf.cache_clear()
        self.nova_file = os.path.join(
            filesystem.get_etc_fs_mount(), 'nova/nova.conf')

    def test_parse_nova_conf(self):
        conf = nova.parse_nova_conf(self.nova_file)
        self.assertIsNotNone(conf)
        self.assertIsInstance(conf, configparser.ConfigParser)
        # assert that the sections are not empty
        self.assertTrue(len(conf.sections()) > 0)

    def test_get_dedicated_cpus(self):
        # cpu_dedicated_set = "2-11,13-23,26-35,38-47"
        data = nova.get_dedicated_cpus(self.nova_file)
        # range is a half open range form start to < end with default steps
        # of 1, as a result we add one to the end of the ranges used in the
        # config.
        expected = {
            core for start, end in ((2, 12), (13, 24), (26, 36), (38, 48))
            for core in range(start, end)
        }
        self.assertEqual(data, expected)

    def test_get_shared_cpus(self):
        # cpu_shared_set = 1,13,25,37
        data = nova.get_shared_cpus(self.nova_file)
        expected = {1, 13, 25, 37}
        self.assertEqual(data, expected)
