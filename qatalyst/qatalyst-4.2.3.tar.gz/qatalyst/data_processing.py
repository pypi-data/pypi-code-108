import time
import os
import re
from dataclasses import dataclass, field
from typing import Union, Dict, Tuple, List, AnyStr
from enum import Enum
import pandas as pd
import numpy as np
import scipy.sparse as sp
from scipy.optimize import show_options
import networkx as nx
from itertools import chain
from .encoders import encode_data


@dataclass
class Status:
    status: Union[str, Enum]
    message: str = None
    timestamp: str = None


class StatusCodes(Enum):
    complete = 'COMPLETE'
    processing = 'PROCESSING'
    error = 'ERROR'


class GraphAlgorithms(Enum):
    CLIQUE_COVER = 'clique_cover'
    COMMUNITY_DETECTION = 'community_detection'
    BIPARTITE_COMMUNITY_DETECTION = 'bipartite_community_detection'
    PARTITION = 'partition'


class TicToc(object):

    def __init__(self):
        self.start = time.time()

    @classmethod
    def tic(cls):
        return cls()

    def toc(self):
        return time.time() - self.start


class AwsDeviceClient:

    ONLINE = 'ONLINE'
    OFFLINE = 'OFFLINE'

    def __init__(self, arn, name, status, execution_window):
        self.arn = arn
        self.name = name
        self.status = status
        self.execution_window = execution_window

    @classmethod
    def from_braket_check(cls, response):
        assert response, 'from_braket_check called with empty response'

        status = cls.ONLINE if response['online'] else cls.OFFLINE
        return cls(
            arn=response['arn'],
            name=response['name'],
            status=status,
            execution_window=response['execution_window']
        )
