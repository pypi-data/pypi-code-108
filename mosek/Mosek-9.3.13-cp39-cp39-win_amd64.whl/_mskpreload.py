import ctypes,os.path
ctypes.CDLL(os.path.join(os.path.dirname(__file__),"cilkrts20.dll"))
ctypes.CDLL(os.path.join(os.path.dirname(__file__),"mosek64_9_3.dll"))
