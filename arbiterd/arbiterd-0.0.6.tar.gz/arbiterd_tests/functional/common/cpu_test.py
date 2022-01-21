# -*- coding: utf-8 -*-
# Copyright 2021 - 2021, Sean Mooney and the arbiterd contributors
# SPDX-License-Identifier: Apache-2.0
import os

from arbiterd.common import cpu
from arbiterd.common import filesystem
from testtools.content import text_content

from arbiterd_tests import base


class TestCPUData(base.ATTestCase):
    # This is a functional test class that use the sysfs test fixture
    # to create a fake copy of /sys which it the used in the tests.

    USE_ETC_FIXTURE = False

    def test_available_cpus(self):
        # the sysfs test fixture has 48 cores
        cpus = cpu.get_available_cpus()
        self.assertEqual({x for x in range(48)}, cpus)

    def test_online_cpus(self):
        # all cores are online
        cpus = cpu.get_online_cpus()
        self.assertEqual({x for x in range(48)}, cpus)

    def test_offline_cpus(self):
        # so the offline cpus should be empty
        cpus = cpu.get_offline_cpus()
        self.assertEqual(set(), cpus)

    def test_available_equals_online_and_offline(self):
        # the total amount of cpus should be the union of the online
        # and offline cpus.
        self.assertEqual(
            cpu.get_available_cpus(),
            {*cpu.get_online_cpus(), *cpu.get_offline_cpus()}
        )

    def test_nproc(self):
        # the total number of cpus should be 48
        self.assertEqual(cpu.nproc(), 48)

    def test_gen_cpu_paths(self):
        # the per cpu paths should exist within the sys mount
        sys = filesystem.get_sys_fs_mount()
        expected = []
        for core in range(48):
            path = os.path.join(sys, f'devices/system/cpu/cpu{core}')
            self.assertTrue(os.path.exists(path))
            expected.append(str(path))
        self.assertEqual(list(cpu.gen_cpu_paths()), expected)

    def test_get_online(self):
        # and each cpu should report itself as online.
        for path in cpu.gen_cpu_paths():
            self.addDetail(
                f'cpu-online path={path}',
                text_content(
                    filesystem.read_sys(os.path.join(path, 'online')) or
                    'not present')
            )
            self.assertTrue(
                cpu.get_online(path), f'cpu:{path} is offline')
