#!/usr/bin/env python
from abc import ABC,abstractmethod
import os
import random
import re
import sys
from collections import defaultdict
from functools import reduce

import codefast as cf
from dofast.network import Twitter
from dofast.toolkits.telegram import Channel


class Handler(ABC, Twitter, Channel):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def get_text():
        ...



