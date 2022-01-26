from typing import List

class APIError(Exception):
    pass

class APIWarning(Warning):
    pass

class ParameterValueError(Exception):
    def __init__(self, param: str, values: List[str]):
        self.param = param
        self.values = values

    def __str__(self):
        return f"Please pass a valid value for {self.param}. Values are {self.values}"
