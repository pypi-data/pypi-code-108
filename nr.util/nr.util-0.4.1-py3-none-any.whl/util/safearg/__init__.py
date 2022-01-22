
"""
Utilities to mark values safe or unsafe, for example for the purpose of logging or to expose to users.
Note that anything accepting #Arg instances must explicitly implement support.
"""

import typing as t

from nr.util.generic import T


class Arg(t.Generic[T]):
  """ Base class for arguments. Cannot be directly constructed. """

  def __init__(self, value: T) -> None:
    if type(self) not in (Safe, Unsafe):
      raise RuntimeError(f'cannot create object of type {type(self).__name__}')
    self._value = value

  def __repr__(self) -> str:
    return f'{type(self).__name__}({self._value!r})'

  @property
  def value(self) -> T:
    return self._value

  def is_safe(self) -> t.TypeGuard['Safe']:
    return isinstance(self, Safe)

  def is_unsafe(self) -> t.TypeGuard['Unsafe']:
    return isinstance(self, Unsafe)


class Safe(Arg[T]):
  pass


class Unsafe(Arg[T]):
  pass
