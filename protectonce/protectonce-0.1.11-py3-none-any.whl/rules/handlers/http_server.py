from urllib.parse import urlparse, parse_qs
from weakref import WeakValueDictionary
from http import HTTPStatus

from . import cls
from ... import common_utils

__http_request_map = WeakValueDictionary()


def get_http_request_info(data):
    request = data['instance']
    u = urlparse(request.path)

    query_params = parse_qs(u.query)
    for k, v in query_params.items():
        query_params[k] = v[0]
    return {
        'url': request.path,
        'queryParams': query_params,
        'headers': dict(request.headers),
        'method': request.command,
        'path': u.path,
        'sourceIP': request.client_address[0],
        'poSessionId': data['result']
    }


def store_request_object(data):
    po_session_id = data.get('result', '')
    if not po_session_id:
        return

    request = data.get('instance', None)
    if not request:
        return

    __http_request_map[po_session_id] = request


def cancel_request(data):
    if common_utils.is_action_blocked(data) == False:
        return

    po_session_id = cls.get_property(data)
    request = __http_request_map.get(po_session_id, None)

    if not request:
        return

    request.send_error(HTTPStatus.INTERNAL_SERVER_ERROR)
    del __http_request_map[po_session_id]
