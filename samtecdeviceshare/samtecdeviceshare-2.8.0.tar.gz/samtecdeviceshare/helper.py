#!/usr/bin/env python
import os
import socket
import struct
import functools
import fcntl
import asyncio
import logging
from concurrent.futures import Executor
from typing import Optional, Callable

logger = logging.getLogger('sdc.helper')

async def is_online_async(host="8.8.8.8", port=53, timeout=3) -> bool:
    try:
        _, w = await asyncio.open_connection(host=host, port=port)
        w.close()
        return True
    except Exception:
        return False

def is_online(host="8.8.8.8", port=53, timeout=3) -> bool:
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False

def get_hostname():
    return socket.gethostname()

def env_flag(env_var: str, default: bool = False) -> bool:
    """
    Return the specified environment variable coerced to a bool, as follows:
    - When the variable is unset, or set to the empty string, return `default`.
    - When the variable is set to a truthy value, returns `True`.
      These are the truthy values:
          - 1
          - true, yes, on
    - When the variable is set to the anything else, returns False.
       Example falsy values:
          - 0
          - no
    - Ignore case and leading/trailing whitespace.
    """
    environ_string = os.environ.get(env_var, "").strip().lower()
    if not environ_string:
        return default
    return environ_string in ["1", "true", "yes", "on"]

def is_on_balena() -> bool:
    return env_flag('BALENA') or env_flag('RESIN')

def get_ip_address(ifname: str):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15].encode('utf-8'))
        )[20:24])
    except Exception:
        return ''

async def awaitify(loop: Optional[asyncio.AbstractEventLoop] = None, pool: Optional[Executor] = None, func: Optional[Callable] = None, **kwargs):
    if func is None:
        return
    if loop is None:
        loop = asyncio.get_running_loop()
    routine = functools.partial(func, **kwargs)
    rsts = await loop.run_in_executor(pool, routine)
    return rsts

if __name__ == "__main__":
    pass
