from jsonclasses.cdef import Cdef


def class_needs_session(cdef: Cdef) -> bool:
    return hasattr(cdef.cls, 'auth_conf')
