# -*- coding: utf-8 -*-
# Copyright 2021 - 2021, Sean Mooney and the arbiterd contributors
# SPDX-License-Identifier: Apache-2.0
import abc
from dataclasses import dataclass

from arbiterd.objects import context as ctx


@dataclass
class ArbiterBase(abc.ABC):

    TYPE: str = 'base'

    @abc.abstractmethod
    def arbitrate(self, context: ctx.Context) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def revoke(self, context: ctx.Context) -> str:
        raise NotImplementedError


def register(current_arbiters: dict) -> None:
    pass
