import argparse
import enum
import functools
import inspect
import json
import mimetypes
import operator
import os
import random
import re
import shutil
import socket
import sys
import time
import typing
import uuid
import warnings

from collections import OrderedDict, defaultdict, namedtuple
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import partial, reduce
from pathlib import Path
from pprint import pprint
from types import SimpleNamespace
from typing import *

import fastcore.all as fastcore
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import PIL
import pyperclip
import rich

from loguru import logger
from PIL import Image, ImageDraw, ImageFile, ImageFont
from PIL import features as PILFeatures
from rich.progress import track
from rich.traceback import install
from tqdm.auto import tqdm
from typing_extensions import Literal

PathLike = Union[str, Path]

logger = logger.opt(colors=True)
