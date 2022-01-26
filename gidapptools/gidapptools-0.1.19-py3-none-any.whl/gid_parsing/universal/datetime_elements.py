"""
WiP.

Soon.
"""

# region [Imports]

import os
import re
import sys
import json
import queue
import math
import base64
import pickle
import random
import shelve
import dataclasses
import shutil
import asyncio
import logging
import sqlite3
import platform
import importlib
import subprocess
import inspect

from time import sleep, process_time, process_time_ns, perf_counter, perf_counter_ns
from io import BytesIO, StringIO
from abc import ABC, ABCMeta, abstractmethod
from copy import copy, deepcopy
from enum import Enum, Flag, auto, unique
from time import time, sleep
from pprint import pprint, pformat
from pathlib import Path
from string import Formatter, digits, printable, whitespace, punctuation, ascii_letters, ascii_lowercase, ascii_uppercase
from timeit import Timer
from typing import TYPE_CHECKING, Union, Callable, Iterable, Optional, Mapping, Any, IO, TextIO, BinaryIO, Hashable, Generator, Literal, TypeVar, TypedDict, AnyStr
from zipfile import ZipFile, ZIP_LZMA
from datetime import datetime, timezone, timedelta
from tempfile import TemporaryDirectory
from textwrap import TextWrapper, fill, wrap, dedent, indent, shorten
from functools import wraps, partial, lru_cache, singledispatch, total_ordering, cached_property, reduce
from operator import add
from importlib import import_module, invalidate_caches
from contextlib import contextmanager, asynccontextmanager, nullcontext, closing, ExitStack, suppress
from statistics import mean, mode, stdev, median, variance, pvariance, harmonic_mean, median_grouped
from collections import Counter, ChainMap, deque, namedtuple, defaultdict
from urllib.parse import urlparse
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from importlib.machinery import SourceFileLoader
import pp

from dateutil.tz import gettz
import pyparsing as ppa
import pyparsing.common as ppc
from tzlocal import get_localzone
from gidapptools.gid_parsing.tokens.base_tokens import BaseTokenWithPos
# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


def microsecond_parse_action(tokens):
    miliseconds_string = tokens[0]
    while len(miliseconds_string) < 6:
        miliseconds_string += "0"
    return int(miliseconds_string)


datetime_format_mapping: dict[str, ppa.ParserElement] = {"%Y": ppa.Regex(r"\d{4}").set_parse_action(ppc.convert_to_integer)("year"),
                                                         "%m": ppa.Regex(r"[01]?\d").set_parse_action(ppc.convert_to_integer)("month"),
                                                         "%d": ppa.Regex(r"[0123]?\d").set_parse_action(ppc.convert_to_integer)("day"),
                                                         "%H": ppa.Regex(r"[012]?\d").set_parse_action(ppc.convert_to_integer)("hour"),
                                                         "%M": ppa.Regex(r"[0-5]?\d").set_parse_action(ppc.convert_to_integer)("minute"),
                                                         "%S": ppa.Regex(r"[0-5]?\d").set_parse_action(ppc.convert_to_integer)("second"),
                                                         "%f": ppa.Regex(r"\d+").set_parse_action(microsecond_parse_action)("microsecond"),
                                                         "%Z": ppa.Combine(ppa.Word(ppa.alphas) + ppa.Optional(ppa.one_of(["+", "-"]) + ppa.Word(ppa.nums) + ppa.Literal(":") + ppa.Word(ppa.nums)))("tzinfo")}


class DateTimeToken(BaseTokenWithPos):

    def __init__(self,
                 start: int,
                 end: int,
                 year: int,
                 month: int,
                 day: int,
                 hour: int,
                 minute: int,
                 second: int,
                 microsecond: int = 0,
                 tzinfo: str = None) -> None:
        super().__init__(start=start, end=end)
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.microsecond = microsecond
        self.raw_tzinfo = tzinfo

    @classmethod
    def from_parse_action(cls, s, l, t) -> "BaseTokenWithPos":
        data_dict = t[0].as_dict()
        data_dict["start"] = data_dict.pop("locn_start")
        data_dict["end"] = data_dict.pop("locn_end")
        data_dict.pop("value")
        return cls(**data_dict)

    @cached_property
    def tzinfo(self) -> timezone:
        if self.raw_tzinfo is None:
            return None
        if self.raw_tzinfo == "UTC":
            return timezone.utc

        if self.raw_tzinfo.startswith("UTC"):
            offset_part = self.raw_tzinfo.removeprefix("UTC").split(":")[0]
            amount = int(offset_part[1:].strip())
            if offset_part[0] == "-":
                amount = amount * (-1)
            return timezone(timedelta(hours=amount))

        return gettz(self.raw_tzinfo)

    def as_datetime(self) -> datetime:
        return datetime(year=self.year, month=self.month, day=self.day, hour=self.hour, minute=self.minute, second=self.second, microsecond=self.microsecond, tzinfo=self.tzinfo)


def get_grammar_from_dt_format(dt_format: str) -> ppa.ParserElement:
    parts = []
    previous_char = ""
    for char in dt_format:
        if previous_char == "%":
            parts.append(datetime_format_mapping[previous_char + char])
        elif char not in {"%", " "}:
            parts.append(ppa.Literal(char).suppress())
        previous_char = char
    return ppa.locatedExpr(reduce(add, parts)).set_parse_action(DateTimeToken.from_parse_action)


# region[Main_Exec]
if __name__ == '__main__':
    from gidapptools.general_helper.output_helper.rich_helper import inspect_object_with_html
    print(f'{get_grammar_from_dt_format("%Y-%m-%d %H:%M:%S %Z")=}')
# endregion[Main_Exec]
