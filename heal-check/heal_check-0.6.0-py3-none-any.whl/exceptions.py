from datetime import datetime


class CheckWarning(Exception):
    pass


class UrlWarning(CheckWarning):
    def __init__(self, url: str, request_timeout: float):
        self.url = url
        self.request_timeout = request_timeout


class ResponseWarning(CheckWarning):
    def __init__(self, response: str):
        self.response = response


class TimestampWarning(CheckWarning):
    def __init__(self, timestamp: datetime, heal_timeout: float, now: datetime):
        self.timestamp = timestamp
        self.heal_timeout = heal_timeout
        self.now = now


class StatusWarning(CheckWarning):
    pass


class CheckError(Exception):
    pass


class DictionaryError(CheckError):
    def __init__(self, dictionary: dict):
        self.dictionary = dictionary


class StatusError(CheckError):
    def __init__(self, status: str):
        self.status = status


class WarningTimeoutError(CheckError):
    def __init__(self, warning: CheckWarning):
        self.warning = warning
