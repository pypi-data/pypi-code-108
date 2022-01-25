import ctypes
import ctypes.util

libc = ctypes.CDLL(str(ctypes.util.find_library("c")), use_errno=True)
