import ctypes,os.path
ctypes.CDLL(os.path.join(os.path.dirname(__file__),"libmosek64.so.9.3"))
