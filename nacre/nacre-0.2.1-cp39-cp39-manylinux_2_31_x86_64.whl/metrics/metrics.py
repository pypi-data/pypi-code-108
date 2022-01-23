from prometheus_client import Counter
from prometheus_client import Gauge
from prometheus_client import Histogram


WEBSOCKET_DISCONNECT_COUNTER = Counter(
    "nacre_ws_disconnect", "websocket disconnect count", ["endpoint"]
)
WEBSOCKET_RECONNECT_BACKOFF = Gauge(
    "nacre_ws_reconnect_backoff", "websocket reconnect backoff seconds", ["endpoint"]
)
WEBSOCKET_RECV_ERROR_COUNTER = Counter(
    "nacre_ws_errors", "error count in handle websocket recv loop", ["endpoint"]
)


REQ_TIME = Histogram(
    "nacre_http_request_duration_seconds", "time spent in http requests", ["method", "endpoint"]
)
HTTP_ERROR_COUNTER = Counter(
    "nacre_http_request_errors", "error count for http requests", ["method", "endpoint"]
)
