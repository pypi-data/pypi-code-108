import ctypes,os.path
ctypes.CDLL(os.path.join(os.path.dirname(__file__),"cilkrts20.dll"))
ctypes.CDLL(os.path.join(os.path.dirname(__file__),"mosek9_3.dll"))
