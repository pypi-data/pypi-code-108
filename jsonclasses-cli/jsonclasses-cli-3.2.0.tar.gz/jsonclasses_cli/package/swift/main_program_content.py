from jsonclasses.cgraph import CGraph
from jsonclasses.uconf import uconf
from jsonclasses_cli.package.swift.link_codable import link_codable
from .session_input import session_input
from .import_lines import import_lines
from .string_query import string_query
from .int_query import int_query
from .float_query import float_query
from .bool_query import bool_query
from .date_query import date_query
from .id_query import id_query
from .sort_order import sort_order
from .data_enum import data_enum
from .data_class import data_class
from .session_items import session_items
from .session import session
from .response import response_struct
from .user_default import user_default
from .session_manager import session_manager
from .sign_out import sign_out
from .request_manager import request_manager
from .data_requests_and_clients import data_requests_and_clients, data_client_instances
from ...utils.join_lines import join_lines
from ...utils.package_utils import session_input_cdefs


def main_program_content(cgraph: CGraph) -> str:
    session_classes = session_items(cgraph)
    use_session = len(session_classes) > 0
    request_url = uconf()['package.swift.url']
    return join_lines([
        import_lines(),
        string_query(),
        int_query(),
        float_query(),
        bool_query(),
        date_query(),
        id_query(),
        # list query
        # dict query
        sort_order(),
        link_codable(),
        *map(lambda e: data_enum(e), cgraph._enum_map.values()),
        *map(lambda c: data_class(c), cgraph._map.values()),
        *map(lambda c: session_input(c), session_input_cdefs(cgraph)),
        session(session_classes) if use_session else '',
        response_struct(),
        user_default(),
        session_manager() if use_session else '',
        sign_out() if use_session else '',
        request_manager(request_url, use_session),
        *map(lambda c: data_requests_and_clients(c), cgraph._map.values()),
        join_lines(map(lambda c: data_client_instances(c), cgraph._map.values()), 1),
    ], 2)
