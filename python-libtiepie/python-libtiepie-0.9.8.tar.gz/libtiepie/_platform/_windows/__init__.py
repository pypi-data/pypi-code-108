import sys
import os
import ctypes as ct

this_dir = os.path.dirname(os.path.abspath(__file__))
is_32bit = (sys.maxsize <= 2**32)
arch = 'x86' if is_32bit else 'x64'
arch_dir = os.path.join(this_dir, arch)

try:
    from ...__config__ import LIBTIEPIE as DLL_PATH
except ImportError:
    DLL_PATH = os.path.join(arch_dir, 'libtiepie.dll')
