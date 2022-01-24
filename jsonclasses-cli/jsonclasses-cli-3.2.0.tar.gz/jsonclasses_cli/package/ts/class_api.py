from typing import cast
from jsonclasses.cdef import CDef
from jsonclasses_cli.utils.package_utils import to_client
from jsonclasses_server.aconf import AConf
from jsonclasses.cgraph import CGraph
from ...utils.join_lines import join_lines
from ...utils.package_utils import session_input_cdefs, to_session, to_session_input, to_sign_in_request, to_single_query
from inflection import camelize,pluralize

def class_api(cgraph: CGraph, use_session:bool) -> str:
    return join_lines([
        'class API {',
        *map(lambda c: _client_item(c), cgraph._map.values()),
        _session() if use_session else '',
        _sign_out() if use_session else '',
        '}'
    ], 2)


def _client_item(cdef: CDef) -> str:
    name  = camelize(pluralize(cdef.name))
    return join_lines([
        f"    get {name}(): {to_client(cdef)} {'{'}",
        f"        return new {to_client(cdef)}()",
        "    }"
    ])


def _session() -> str:
    return join_lines([
        '    get session(): SessionManager {',
        '       return SessionManager.share',
        '    }'
    ])


def _sign_out() -> str:
    return join_lines([
        '    signOut(): void {',
        '       SessionManager.share.clearSession()',
        '    }'
    ])
