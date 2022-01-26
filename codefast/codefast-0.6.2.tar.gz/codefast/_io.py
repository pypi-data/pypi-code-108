'''IO related methods, classes.
'''
from contextlib import suppress
from typing import Any, List, Tuple

import joblib


class JoblibDiskCaching:
    def __init__(self):
        ...

    @staticmethod
    def load(file_name: str, object_type=dict) -> Any:
        with suppress(FileNotFoundError):
            resp = object_type()
            resp = joblib.load(file_name)
        return resp

    @staticmethod
    def dump(value: Any, file_name: str):
        joblib.dump(value, file_name)
