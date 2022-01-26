# -*- coding: utf-8 -*-
import datetime
from typing import Any


class DataDogLogMessage:
    def __init__(self, status: str, service: str, host: str, message: str, time: datetime.datetime = None,
                 tags: Any = None, source: str = None, logger_name: str = None, thread_name: str = None,
                 error_message: str = None, error_kind: str = None, error_stack: str = None):

        self.time: datetime.datetime = time
        self.tags: Any = tags
        self.status: str = status
        self.source: str = source
        self.service: str = service
        self.host: str = host
        self.message: str = message
        self.logger_name: str = logger_name
        self.thread_name: str = thread_name
        self.error_message: str = error_message
        self.error_kind: str = error_kind
        self.error_stack: str = error_stack
