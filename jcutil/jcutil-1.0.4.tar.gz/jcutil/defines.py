import os
from sys import version_info
import platform
from datetime import timedelta

if version_info.major >= 3 and version_info.minor > 7:
    from typing import Protocol, runtime_checkable

    @runtime_checkable
    class Writable(Protocol):
        def write(self, *args, **kwargs): ...
        def close(self): ...


    @runtime_checkable
    class Readable(Protocol):
        def read(self, *args, **kwargs): ...
        def close(self): ...
else:
    class Writable(object):
        def write(self, *args, **kwargs): ...
        def close(self): ...


    class Readable(object):
        def read(self, *args, **kwargs): ...
        def close(self): ...


CACHE_DEFAULT_DIR = os.getenv('TEMP') if platform.system() == 'Windows' else '/tmp'
DEFAULT_CACHE_TIME = timedelta(seconds=30)  # 30 seconds
