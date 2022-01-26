from __future__ import annotations

import typing as t

_T = t.TypeVar('_T')
_S = t.TypeVar('_S')
_R = t.TypeVar('_R')
_T_cov = t.TypeVar('_T_cov', covariant=True)
_T_con = t.TypeVar('_T_con', contravariant=True)
SimpleCoroutine = t.Coroutine[t.Any, t.Any, _T]
