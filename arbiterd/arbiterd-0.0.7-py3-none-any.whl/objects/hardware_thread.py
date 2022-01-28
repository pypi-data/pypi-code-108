# -*- coding: utf-8 -*-
# Copyright 2021 - 2021, Sean Mooney and the arbiterd contributors
# SPDX-License-Identifier: Apache-2.0
# import typing as ty
from dataclasses import dataclass

from arbiterd.common import cpu


@dataclass
class HardwareThread:
    """Class to model a hardware thread

    A hardware thread is a single core as reported by sysfs.
    It may be a physical CPU core or a hardware thread on a shared
    CPU core depending on if the system supports SMT.
    """

    # The hardware thread id/number
    ident: int = None
    # sysfs directory path to cpu.
    _path: str = None

    @property
    def path(self) -> str:
        if self._path is None:
            self._path = cpu.gen_cpu_path(self.ident)
        return self._path

    @property
    def online(self) -> bool:
        return cpu.get_online(self.path)

    @online.setter
    def online(self, state: bool) -> None:
        if state:
            cpu.set_online(self.path)
        cpu.set_offline(self.path)

    def __hash__(self):
        return hash(self.ident)
