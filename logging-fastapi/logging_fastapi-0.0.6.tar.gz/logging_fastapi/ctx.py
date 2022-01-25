from contextvars import ContextVar

request_id_ctx = ContextVar("requestId")
span_ctx = ContextVar("span")
error_ctx = ContextVar("error")
