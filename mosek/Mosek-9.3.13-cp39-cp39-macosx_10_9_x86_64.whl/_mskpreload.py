import ctypes,os.path
ctypes.CDLL(os.path.join(os.path.dirname(__file__),"libcilkrts.5.dylib"))
ctypes.CDLL(os.path.join(os.path.dirname(__file__),"libmosek64.9.3.dylib"))
