# -*- coding: utf-8 -*-

import datetime
from numbers import Number
from typing import Optional


class DataDogMetricPoint:
    def __init__(self, value: Number, time: Optional[datetime.datetime] = None):
        self.value = value
        self.time = time
