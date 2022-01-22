#!/usr/bin/env python3
class InvalidInputError(BaseException):
    def __init__(self, args):
        self._location = args
