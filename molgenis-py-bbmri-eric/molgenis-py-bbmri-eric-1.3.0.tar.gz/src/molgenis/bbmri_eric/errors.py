from collections import defaultdict
from dataclasses import dataclass, field
from typing import DefaultDict, List

import requests

from molgenis.bbmri_eric.model import Node


@dataclass(frozen=True)
class EricWarning:
    """
    Class that contains a warning message. Use this when a problem occurs that
    shouldn't cancel the current action (for example staging or publishing).
    """

    message: str


class EricError(Exception):
    """
    Raise this exception when an error occurs that we can not recover from.
    """

    pass


@dataclass
class ErrorReport:
    """
    Summary object. Stores errors and warnings that occurred for each node.
    """

    nodes: List[Node]
    errors: DefaultDict[Node, EricError] = field(
        default_factory=lambda: defaultdict(list)
    )
    warnings: DefaultDict[Node, List[EricWarning]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def add_error(self, node: Node, error: EricError):
        self.errors[node] = error

    def add_warnings(self, node: Node, warnings: List[EricWarning]):
        if warnings:
            self.warnings[node].extend(warnings)

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        return len(self.warnings) > 0


def requests_error_handler(func):
    """
    Decorator that catches RequestExceptions and wraps them in an EricError.
    """

    def inner_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            raise EricError("Request failed") from e

    return inner_function
