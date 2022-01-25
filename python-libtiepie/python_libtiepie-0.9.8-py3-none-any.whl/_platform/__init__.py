import sys
import os
import platform

is_windows = platform.system() == 'Windows'
is_linux = platform.system() == 'Linux'
is_32bit = (sys.maxsize <= 2**32)

del sys, os, platform

if is_windows:
    from ._windows import DLL_PATH
elif is_linux:
    from ._linux import DLL_PATH
else:
    raise ImportError("unsupported platform")
