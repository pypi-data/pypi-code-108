from tcell_agent.global_state import django_active, flask_active
from tcell_agent.config.configuration import get_config


def module_name(module):
    if hasattr(module, "__name__"):
        return module.__name__.replace("__", "").replace("builtins", "builtin")

    return ""


def skip_instrumentation(module, original_method_str):
    key = "{}.{}".format(module, original_method_str)
    return key in get_config().disabled_instrumentation


def get_tcell_context():
    if django_active():
        from tcell_agent.instrumentation.djangoinst.middleware.globalrequestmiddleware import GlobalRequestMiddleware  # noqa
        request = GlobalRequestMiddleware.get_current_request()
        if request and request._tcell_context:
            return request._tcell_context

    elif flask_active():
        from flask.globals import _request_ctx_stack
        if _request_ctx_stack.top and _request_ctx_stack.top.request:
            return getattr(_request_ctx_stack.top.request, '_tcell_context', None)

    return None


def header_keys_from_request_env(request_env):
    request_headers_keys = []
    for header in request_env:
        if header.startswith('HTTP_'):
            new_key = header[5:]
            request_headers_keys.append(new_key)
    if 'CONTENT_TYPE' in request_env:
        request_headers_keys.append('CONTENT_TYPE')
    if 'CONTENT_LENGTH' in request_env:
        request_headers_keys.append('CONTENT_LENGTH')
    return request_headers_keys
