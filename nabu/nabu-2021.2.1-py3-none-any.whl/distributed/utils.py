from os import getpid
from datetime import datetime
from socket import gethostname


# Default formatter
FORMATTER = "[{hostname}/{pid}/{worker}] {day}/{month}/{year} {hour}:{min}:{sec} {message}"


def format_message(message, worker_name=None, replacements=None):
    """
    Format a message with additional information.
    The formating is defined by `nabu.distributed.utils.FORMATTER`.

    Parameters
    -----------
    message: str
        Message to log.
    worker_name: str, optional
        Name of the current worker.
    replacements: dict, optional
        Dictionary of additional patterns that should be replaced in the current
        formatter.
    """
    now = datetime.now()
    # poor man's templating engine
    formatters = {
        "hostname": gethostname(),
        "pid": getpid(),
        "worker": "",
        "day": now.strftime("%d"),
        "month": now.strftime("%m"),
        "year": now.strftime("%Y"),
        "hour": now.strftime("%H"),
        "min": now.strftime("%M"),
        "sec": now.strftime("%S"),
        "message": message
    }
    if worker_name is not None:
        formatters["worker"] = worker_name
    FMT = FORMATTER.replace("{", "").replace("}", "")
    for fmt_key, fmt_val in formatters.items():
        FMT = FMT.replace(fmt_key, str(fmt_val))
    if replacements is not None:
        for what, replacement in replacements.items():
            FMT = FMT.replace(what, replacement)
    return FMT


def log(message):
    """
    Log a message using the current formater.
    """
    print(format_message(message))



