from __future__ import annotations

from typing import Any, Dict, Iterable, Type

from .simplification import Simplification


class Parser(Simplification):
    """
    Represents abstract parsing of config.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def parse(self, value: Any) -> Dict[str, Any]:
        simplified_value = self.simplify(value)
        return self._do_parse(simplified_value)

    @staticmethod
    def parse_with(value: Any, parsers: Iterable[Type[Parser]]) -> Dict[str, Any]:
        """
        `parse_with` allows parsing using other Parser derived classes.

        Usage
        ------
        To use it, pass a list of derived classes to `parse_with` to
        retrieve a dictionary merging result from all subparsers.
        """
        parsed = dict()

        for subparser_class in parsers:
            subparser = subparser_class(value)

            parsed.update(subparser.parse(value))

        return parsed

    def _do_parse(self, value: Any) -> Dict[str, Any]:
        raise NotImplementedError()
