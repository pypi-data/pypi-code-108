#!/usr/bin/env python3
# coding: utf-8


from volkanic.introspect import ErrorBase


class KnownError(ErrorBase):
    pass


class BusinessError(KnownError):
    extra = {'code': 1}


C1Error = BusinessError


class TechnicalError(KnownError):
    extra = {'code': 2}

    def __str__(self):
        s = super().__str__()
        return f'{s} <{self.error_key}>'


C2Error = TechnicalError

__all__ = [
    'KnownError',
    'BusinessError',
    'TechnicalError',
    'C1Error',
    'C2Error',
]
