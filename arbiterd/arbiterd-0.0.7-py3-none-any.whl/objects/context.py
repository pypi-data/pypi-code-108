# -*- coding: utf-8 -*-
# Copyright 2021 - 2021, Sean Mooney and the arbiterd contributors
# SPDX-License-Identifier: Apache-2.0
import dataclasses
import typing as ty
from dataclasses import dataclass


@dataclass
class Context:
    """Dispatcher and Manager of arbiters"""

    instances: ty.List = dataclasses.field(default_factory=list)
    managed_hardware_threads: ty.List = dataclasses.field(default_factory=list)
    dry_run: bool = True
