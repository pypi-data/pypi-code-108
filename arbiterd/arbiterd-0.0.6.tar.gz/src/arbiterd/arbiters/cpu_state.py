# -*- coding: utf-8 -*-
# Copyright 2021 - 2021, Sean Mooney and the arbiterd contributors
# SPDX-License-Identifier: Apache-2.0
import logging
import typing as ty
from dataclasses import dataclass

from arbiterd.arbiters import base
from arbiterd.objects import context as ctx
from arbiterd.objects import hardware_thread


LOG = logging.getLogger(__name__)


@dataclass
class CPUStateArbiter(base.ArbiterBase):
    TYPE: str = 'cpu-state'

    def arbitrate(self, context: ctx.Context) -> str:
        vm_cores = {
            core for instance in context.instances
            for field in instance.cpu_affinities for core in field}
        offlinable_cores = (
            self.get_online_cores(context.managed_hardware_threads) - vm_cores
        )

        if context.dry_run:
            return f'offlinable_cpus: {offlinable_cores}'

        offlinable_threads = {
            t for t in context.managed_hardware_threads
            if t.ident in offlinable_cores
        }
        for thread in offlinable_threads:
            logging.debug(
                f'offlining core: {thread} as part of cpu_state arbitration')
            thread.online = False

        return f'offlined cpus: {offlinable_cores}'

    def get_online_cores(
            self, managed_cores: ty.List[hardware_thread.HardwareThread]
    ) -> ty.Set[int]:
        return {core.ident for core in managed_cores if core.online}

    def get_offline_cores(
            self, managed_cores: ty.List[hardware_thread.HardwareThread]
    ) -> ty.Set[int]:
        return {core.ident for core in managed_cores if not core.online}

    def revoke(self, context: ctx.Context) -> str:
        onlinable_cores = self.get_offline_cores(
            context.managed_hardware_threads
        )

        if context.dry_run:
            return f'onlinable_cpus: {onlinable_cores}'
        onlinable_threads = {
            t for t in context.managed_hardware_threads
            if t.ident in onlinable_cores
        }
        for thread in onlinable_threads:
            logging.debug(
                f'onlining core: {thread.ident} as part of cpu_state revoke'
            )
            thread.online = True
        return 'onlined cpus: {onlinable_cores}'


def register(current_arbiters: dict) -> None:
    logging.debug(f'registering {CPUStateArbiter.TYPE} arbiter')
    current_arbiters[CPUStateArbiter.TYPE] = CPUStateArbiter
