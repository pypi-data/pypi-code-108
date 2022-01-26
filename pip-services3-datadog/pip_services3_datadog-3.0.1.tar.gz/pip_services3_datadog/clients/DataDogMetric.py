# -*- coding: utf-8 -*-
from typing import List, Any

from .DataDogMetricPoint import DataDogMetricPoint


class DataDogMetric:
    def __init__(self, metric: str, type: str, points: List[DataDogMetricPoint],
                 service: str = None, host: str = None, tags: Any = None, interval: int = None):

        self.metric: str = metric
        self.service: str = service
        self.host: str = host
        self.tags: Any = tags
        self.type: str = type
        self.interval: int = interval
        self.points: List[DataDogMetricPoint] = points
