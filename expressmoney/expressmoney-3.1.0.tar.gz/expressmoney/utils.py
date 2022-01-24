import json
from typing import Union


def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', None)
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', None)
    return ip


def get_http_referer(request):
    http_referer = request.META.get('HTTP_REFERER')
    http_host = request.META.get('HTTP_HOST')
    return http_referer if http_referer else http_host


def write_cloud_functions_log(message: Union[str, dict], severity: str = 'DEBUG', request_=None,
                              project: str = 'expressmoney'):
    """ Запись структурированных логов в Cloud Functions logger """

    assert severity in ('DEFAULT', 'NOTICE', 'INFO', 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL', 'ALERT', 'EMERGENCY')

    # Build structured log messages as an object.
    global_log_fields = {}

    # Add log correlation to nest all log messages.
    if request_:
        trace_header = request_.headers.get("X-Cloud-Trace-Context")

        if trace_header and project:
            trace = trace_header.split("/")
            global_log_fields[
                "logging.googleapis.com/trace"
            ] = f"projects/{project}/traces/{trace[0]}"

    # Complete a structured log entry.
    entry = dict(
        severity=severity,
        message=message,
        **global_log_fields,
    )

    print(json.dumps(entry))
