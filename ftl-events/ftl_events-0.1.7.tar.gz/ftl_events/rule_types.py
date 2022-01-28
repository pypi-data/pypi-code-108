
from typing import NamedTuple, Union, List


class EventSource(NamedTuple):
    name: str
    source_name: str
    source_args: dict
    transform: Union[str, None]


class Action(NamedTuple):
    module: str
    module_args: dict


class Condition(NamedTuple):
    value: str


class Rule(NamedTuple):
    name: str
    condition: Condition
    action: Action


class RuleSet(NamedTuple):
    name: str
    hosts: Union[str, List[str]]
    sources: List[EventSource]
    rules: List[Rule]
