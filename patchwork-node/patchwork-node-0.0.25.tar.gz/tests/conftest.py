# -*- coding: utf-8 -*-
from contextlib import contextmanager

import logging

import pytest


@pytest.fixture
def suppress_logging():

    @contextmanager
    def _suppresor(max_level=logging.WARNING):
        logging.disable(max_level)
        yield
        logging.disable(logging.NOTSET)
    return _suppresor
