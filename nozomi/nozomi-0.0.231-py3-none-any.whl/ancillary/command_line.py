"""
Nozomi
Command Line Module
author: hugh@blinkybeach.com
"""
import sys
from typing import Optional, Dict, List, TypeVar, Type
from nozomi.http.parseable_data import ParseableData

T = TypeVar('T', bound='CommandLine')


class CommandLine(ParseableData):

    def __init__(
        self,
        arguments: List[str]
    ) -> None:

        data: Dict[str, Optional[str]] = dict()
        index = 0
        while index < len(arguments):
            value: Optional[str] = None
            argument = arguments[index]
            if argument[0] == '-':
                n = index + 1
                if (n) < len(arguments) and arguments[n][0] != '-':
                    value = arguments[n]
                    index += 1
                else:
                    value = None
            data[argument] = value
            index += 1
            continue

        self._data = data
        super().__init__(raw=data)

        return

    def contains_flag(self, flag: str) -> bool:
        if flag in self._data.keys():
            return True
        return False

    @classmethod
    def load(cls: Type[T]) -> T:
        return cls(sys.argv[1:])
