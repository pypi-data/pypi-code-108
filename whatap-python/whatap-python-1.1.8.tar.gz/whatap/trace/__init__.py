import ctypes

from whatap.trace.trace_context_manager import TraceContextManager

_get_dict = ctypes.pythonapi._PyObject_GetDictPtr
_get_dict.restype = ctypes.POINTER(ctypes.py_object)
_get_dict.argtypes = [ctypes.py_object]


def get_dict(obj):
    return _get_dict(obj).contents.value

