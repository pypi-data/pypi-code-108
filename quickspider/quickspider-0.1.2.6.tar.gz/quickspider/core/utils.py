#!/usr/bin/env python3
from itertools import chain
from collections.abc import Iterator


class MyIterator:
    def __init__(self, iterator):
        if not isinstance(iterator, Iterator):
            iterator = iter(iterator)
        self._container = iterator

    def fetch_one_piece(self):
        try:
            one_piece = next(self._container)
        except StopIteration:
            one_piece = None
        return one_piece

    def not_empty(self):
        one_piece = self.fetch_one_piece()
        if one_piece:
            self._container = chain([one_piece], self._container)
            return True
        return False


class ProcessExceptionEmpty:
    pass
