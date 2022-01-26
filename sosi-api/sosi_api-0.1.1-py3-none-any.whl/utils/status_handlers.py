from .. import exceptions

def handle_too_many_requests(response, msg=None, **kwargs):
    retry_after = response.headers.get("Retry-After")
    if retry_after is not None:
        retry_after = int(retry_after)
    else:
        retry_after_hours = None
    raise exceptions.TooManyRequests(f"Retry after {retry_after} seconds", retry_after)

DEFAULT_STATUS_HANDLERS = {
    429: handle_too_many_requests,
}
