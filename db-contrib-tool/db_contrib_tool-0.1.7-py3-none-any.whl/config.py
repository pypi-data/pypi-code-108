"""Common config module."""
import os
from enum import Enum

CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config")


class SegmentWriteKey(Enum):
    DEV = "RmMosrk1bf025xLRbZUxF2osVzGLPpL3"
    PROD = "jrHGRmtQBO8HYU1CyCfnB279SnktLgGH"


SEGMENT_WRITE_KEY = SegmentWriteKey.PROD.value
if os.environ.get("ENV") == "DEV":
    SEGMENT_WRITE_KEY = SegmentWriteKey.DEV.value
