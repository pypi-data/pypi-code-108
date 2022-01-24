from typing import cast
from jsonclasses.cgraph import CGraph
from jsonclasses_server.auth_conf import AuthConf
from ...utils.package_utils import class_needs_session


def session_items(cgraph: CGraph) -> dict[str, str]:
    result: dict[str, str] = {}
    for cdef in cgraph._map.values():
        if not class_needs_session(cdef):
            continue
        conf = cast(AuthConf, cdef.cls.auth_conf)
        singular_name = conf.info.srname
        class_name = cdef.cls.__name__
        result[singular_name] = class_name
    return result
