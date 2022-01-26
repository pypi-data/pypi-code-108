from .. import exceptions

def handle_too_many_requests(response, msg=None, **kwargs):
    retry_after = response.headers.get("Retry-After")
    if retry_after is not None:
        retry_after = int(retry_after)
        # retry_after_hours = retry_after / (60.0*60)
    else:
        retry_after_hours = None
    raise exceptions.TooManyRequests(f"Retry after {retry_after} seconds", retry_after)
