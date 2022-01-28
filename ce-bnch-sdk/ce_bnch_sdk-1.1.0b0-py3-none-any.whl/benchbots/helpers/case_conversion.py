from dataclasses import dataclass
from keyword import iskeyword
import re
from typing import List


def _clean_and_split(string: str) -> List[str]:
    remove_symbols = re.sub(r"[\W_]", " ", string)
    insert_space_before_uppercase = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", remove_symbols)
    return insert_space_before_uppercase.split()


def _make_valid_identifier(string: str) -> str:
    # If it starts with a digit, prefix with _
    identifier = re.sub(r"^(?=\d)", "_", string)

    if iskeyword(identifier) or identifier == "self" or identifier in dir(dataclass):
        return f"{identifier}_"
    else:
        return identifier


def to_pascal_case(string: str) -> str:
    return _make_valid_identifier("".join([word.title() for word in _clean_and_split(string)]))


def to_snake_case(string: str) -> str:
    return _make_valid_identifier("_".join([word.lower() for word in _clean_and_split(string)]))
