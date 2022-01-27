# -*- coding: utf-8 -*-
from datetime import timedelta
from time import sleep

from arkindex_worker.utils import Timer


def test_timer_type():
    with Timer() as timer:
        pass
    assert isinstance(timer.delta, timedelta)


def test_timer():
    # Assert the second timer has recorded a longer period
    with Timer() as timer:
        pass
    with Timer() as timer2:
        sleep(1 / 100)
    assert timer.delta < timer2.delta
