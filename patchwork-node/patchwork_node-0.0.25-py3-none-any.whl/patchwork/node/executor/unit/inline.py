# -*- coding: utf-8 -*-

from typing import Coroutine, Awaitable

from .base import ProcessingUnit


class InlineUnit(ProcessingUnit):
    """
    Simple processing unit which runs tasks one the same event loop
    as processing unit.
    """

    def _run_job(self, coro: Coroutine) -> Awaitable:
        return coro

