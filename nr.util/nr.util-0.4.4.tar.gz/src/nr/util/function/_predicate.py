
import typing as t

from nr.util.generic import T_contra


class Predicate(t.Protocol[T_contra]):

  def __call__(self, obj: T_contra) -> bool:
    ...
