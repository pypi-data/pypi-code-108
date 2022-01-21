# -*- coding: utf-8 -*-
# Copyright 2021 - 2021, Sean Mooney and the arbiterd contributors
# SPDX-License-Identifier: Apache-2.0
import typing as ty
from unittest import mock

import testtools
from arbiterd.arbiters import cpu_state
from arbiterd.objects import context
from arbiterd.objects import hardware_thread
from arbiterd.objects import instance


class TestCPUStateArbiter(testtools.TestCase):

    def setUp(self):
        super().setUp()
        self.arbiter = cpu_state.CPUStateArbiter()
        self.uuid = mock.sentinel.instance
        self.vm = mock.create_autospec(
            instance.Instance, spec_set=True, instance=True,
            uuid=self.uuid, name='test-vm',
        )
        self.vm_cpus = {0, 1, 2, 3}
        self.vm.cpu_affinities = instance.CPUAffinity(
            self.vm_cpus,  self.vm_cpus,  self.vm_cpus, set()
        )

    def generate_thread_list(
            self, count: int = 10, online: bool = True
    ) -> ty.List[hardware_thread.HardwareThread]:
        threads = []
        for i in range(count):
            thread = mock.create_autospec(
                hardware_thread.HardwareThread, spec_set=True, instance=True,
                ident=i, online=online
            )
            threads.append(thread)

        return threads

    def test_arbitrate_empty_context(self):
        ctx = context.Context()
        result = self.arbiter.arbitrate(ctx)
        # an empty context has dry_run set to true so match
        # the message printed for the dry_run case.
        self.assertIn('offlinable_cpus:', result)

    def test_arbitrate_empty_context_dry_run_false(self):
        ctx = context.Context(dry_run=False)
        result = self.arbiter.arbitrate(ctx)
        self.assertIn('offlined cpus:', result)

    def test_arbitrate_no_instances(self):
        threads = self.generate_thread_list()
        for t in threads:
            self.assertTrue(t.online)
        ctx = context.Context(dry_run=False, managed_hardware_threads=threads)
        result = self.arbiter.arbitrate(ctx)
        self.assertIn('offlined cpus:', result)
        for t in threads:
            self.assertFalse(t.online)

    def test_arbitrate_with_instance(self):
        threads = self.generate_thread_list()
        for t in threads:
            self.assertTrue(t.online)
        ctx = context.Context(
            dry_run=False, instances=[self.vm],
            managed_hardware_threads=threads
        )
        result = self.arbiter.arbitrate(ctx)
        self.assertIn('offlined cpus:', result)
        for t in threads:
            self.assertEqual(
                t.online, t.ident in self.vm_cpus,
                f'core {t.ident} expected state: {t.ident in self.vm_cpus}'
                f' actual {t.online}'
            )

    def test_get_online_cores(self):
        threads = self.generate_thread_list()
        result = self.arbiter.get_online_cores(threads)
        self.assertEqual({t.ident for t in threads}, result)

    def test_get_offline_cores(self):
        threads = self.generate_thread_list()
        result = self.arbiter.get_offline_cores(threads)
        self.assertEqual(set(), result)

    def test_register(self):
        data = {}
        cpu_state.register(data)
        self.assertEqual(len(data), 1)
        self.assertIn(cpu_state.CPUStateArbiter.TYPE, data)
        self.assertIs(
            data[cpu_state.CPUStateArbiter.TYPE], cpu_state.CPUStateArbiter)

    def test_revoke_empty_context(self):
        ctx = context.Context()
        result = self.arbiter.revoke(ctx)
        # an empty context has dry_run set to true so match
        # the message printed for the dry_run case.
        self.assertIn('onlinable_cpus:', result)

    def test_revoke_empty_context_dry_run_false(self):
        ctx = context.Context(dry_run=False)
        result = self.arbiter.revoke(ctx)
        self.assertIn('onlined cpus:', result)

    def test_revoke_no_instances(self):
        threads = self.generate_thread_list(online=False)
        for t in threads:
            self.assertFalse(t.online)
        ctx = context.Context(dry_run=False, managed_hardware_threads=threads)
        result = self.arbiter.revoke(ctx)
        self.assertIn('onlined cpus:', result)
        for t in threads:
            self.assertTrue(t.online)

    def test_revoke_with_instance(self):
        threads = self.generate_thread_list()
        for t in threads:
            self.assertTrue(t.online)
        ctx = context.Context(
            dry_run=False, instances=[self.vm],
            managed_hardware_threads=threads
        )
        result = self.arbiter.arbitrate(ctx)
        self.assertIn('offlined cpus:', result)
        for t in threads:
            self.assertEqual(
                t.online, t.ident in self.vm_cpus,
                f'core {t.ident} expected state: {t.ident in self.vm_cpus}'
                f' actual {t.online}'
            )
        result = self.arbiter.revoke(ctx)
        self.assertIn('onlined cpus:', result)
        for t in threads:
            self.assertTrue(t.online)
