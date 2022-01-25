from jsonclasses.cdef import Cdef


def class_needs_api(cdef: Cdef) -> bool:
    return hasattr(cdef.cls, 'aconf')
