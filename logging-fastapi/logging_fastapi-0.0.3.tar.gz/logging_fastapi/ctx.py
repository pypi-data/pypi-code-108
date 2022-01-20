from contextvars import ContextVar

request_id_ctx = ContextVar("requestId")
error_ctx = ContextVar("error")
