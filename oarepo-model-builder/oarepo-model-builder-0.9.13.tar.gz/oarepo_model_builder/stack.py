from functools import cached_property
from typing import Generator, List

from deepdiff import DeepDiff


class ReplaceElement(Exception):
    def __init__(self, data):
        super().__init__()
        self.data = data


class ModelBuilderStackEntry:
    def __init__(self, key=None, data=None):
        self.key = key
        self.data = data

    def __getitem__(self, item):
        return self.data[item]

    def __eq__(self, other):
        return self.key == other.key and not DeepDiff(self.key, other.key)

    def __str__(self):
        return f'{self.key} - {self.data}'


class ModelBuilderStack:
    DICT = 'dict'
    LIST = 'list'
    PRIMITIVE = 'primitive'
    SKIP = 'skip'

    def __init__(self):
        self.stack = []

    def __getitem__(self, item):
        return self.stack[item]

    def push(self, key, el):
        self._clear_path()
        self.stack.append(ModelBuilderStackEntry(key, el))

    def pop(self):
        self._clear_path()
        self.stack.pop()

    @property
    def top(self):
        return self.stack[-1]

    @property
    def level(self):
        return len(self.stack)

    @property
    def top_type(self):
        match self.top.data:
            case dict():
                return self.DICT
            case list():
                return self.LIST
            case _:
                return self.PRIMITIVE

    @cached_property
    def path(self):
        return '/' + '/'.join(x.key for x in self.stack if x.key)

    def _clear_path(self):
        if "path" in self.__dict__:
            del self.__dict__["path"]
