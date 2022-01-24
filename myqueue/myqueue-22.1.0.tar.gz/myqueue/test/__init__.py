from __future__ import annotations
import os
import sys
import time
from pathlib import Path


def oom(local: bool = True) -> None:
    n = int(os.environ.get('MYQUEUE_TEST_NPROCESSES', '1'))
    if n == 1:
        print('error: exceeded memory limit at some point.', file=sys.stderr)
        raise MemoryError


def timeout_once():
    path = Path('timeout_once.out')
    if not path.is_file():
        path.touch()
        time.sleep(1000)
