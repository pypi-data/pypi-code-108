import ctypes
from daltons_tensorflow.python.core.binding import lib

def version():
    lib.daltons_version.restype = ctypes.c_char_p
    return lib.daltons_version().decode("utf-8")
