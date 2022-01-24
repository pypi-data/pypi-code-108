from contextvars import ContextVar
from enum import Enum
from typing import List


__all__ = 'TRACKING', 'LogOperate'

TRACKING: ContextVar[List[str]] = ContextVar('logger.tracking', default=[])


class LogOperate(str, Enum):
    STRAIGHT = 'straight'
    THREADING = 'threading'
