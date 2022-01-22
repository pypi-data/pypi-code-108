
import typing as t

from nr.util.generic import T_co


class Supplier(t.Protocol[T_co]):

  def __call__(self) -> T_co:
    ...


class ContextSupplier(Supplier[t.ContextManager[T_co]]):
  ...
