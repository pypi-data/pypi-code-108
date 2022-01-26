from __future__ import annotations

import typing as t

from ._typing import _T, _S, _R


class CoroutineWrapper(t.Coroutine[_T, _S, _R]):
    """
    Complex Coroutines are easy to implement with native ``def async`` coroutine syntax, but often require
    some smaller coroutines to compose. Inheriting from CoroutineWrapper, a complex coroutine can encapsulate
    all it's dependencies and auxiliary methods.
    """

    def __init__(self: CoroutineWrapper[_T, _S, _R], *, coroutine: t.Coroutine[_T, _S, _R], **kwargs):
        self._coroutine = coroutine
        super().__init__(**kwargs)

    def __await__(self):
        return self._coroutine.__await__()

    def send(self, value):
        return self._coroutine.send(value)

    def throw(self, typ, val=None, tb=None):
        if val is None:
            return self._coroutine.throw(typ)
        elif tb is None:
            return self._coroutine.throw(typ, val)
        else:
            return self._coroutine.throw(typ, val, tb)

    def close(self):
        return self._coroutine.close()
