import abc
import json
import os
import re
from json import JSONDecodeError

import yaml


def value_parser(value):
    special_key = "SPECIAL_KEY"
    if re.match("^[-+]?[0-9]*\\.?[0-9]+(e[-+]?[0-9]+)?$", value) is None:
        return str(value)
    else:
        return yaml.safe_load(f"{special_key}: {value}")[special_key]


class Parser(abc.ABC, metaclass=abc.ABCMeta):
    def do(self, parameter_value: str):
        return self._do(parameter_value)

    @abc.abstractmethod
    def _do(self, parameter_value: str) -> dict:
        raise NotImplementedError


class ConfigFileParser(Parser):
    def __init__(self):
        self.file_parsers = {
            ".yaml": yaml.full_load,
            ".yml": yaml.full_load,
            ".json": json.load,
        }

    def _do(self, parameter_value: str) -> dict:
        path = parameter_value
        extension = os.path.splitext(path)[1]
        with open(path, "r") as f:
            return self.file_parsers[extension](f)


class StrParser(Parser):
    @staticmethod
    def key_value_to_dict(key, value):
        if not value:
            return None
        splits = key.split(".", maxsplit=1)
        current_key = splits[0]
        next_key = splits[1] if len(splits) > 1 else None
        if next_key is None:
            dictionary = {current_key: value}
        else:
            dictionary = {
                current_key: StrParser.key_value_to_dict(next_key, value)
            }
        return dictionary

    def _do(self, parameter_value: str) -> dict:
        splits = str(parameter_value).split("=", maxsplit=1)
        key, value = splits[0], value_parser(splits[1])
        return StrParser.key_value_to_dict(key, value)


class InlineJsonParser(Parser):
    def _do(self, parameter_value: str):
        try:
            return json.loads(str(parameter_value))
        except JSONDecodeError as e:
            print(e)
            return None
