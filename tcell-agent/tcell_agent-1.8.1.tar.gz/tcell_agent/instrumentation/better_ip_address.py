from tcell_agent.config.configuration import get_config


def get_remote_address(request_env):
    return request_env.get("REMOTE_ADDR")


def get_reverse_proxy_header(request_env):
    if get_config().reverse_proxy:
        return request_env.get("HTTP_" + get_config().reverse_proxy_ip_address_header.upper().replace("-", "_"))

    return None


def tcell_get_host(request):
    """Returns the HTTP host using the environment or request headers."""
    from django.conf import settings as d_settings
    if d_settings.USE_X_FORWARDED_HOST and (
            'HTTP_X_FORWARDED_HOST' in request.META):
        host = request.META['HTTP_X_FORWARDED_HOST']
    elif 'HTTP_HOST' in request.META:
        host = request.META['HTTP_HOST']
    else:
        # Reconstruct the host using the algorithm from PEP 333.
        host = request.META['SERVER_NAME']
        server_port = str(request.META['SERVER_PORT'])
        if server_port != ('443' if request.is_secure() else '80'):
            host = host + ':' + server_port
    return host
