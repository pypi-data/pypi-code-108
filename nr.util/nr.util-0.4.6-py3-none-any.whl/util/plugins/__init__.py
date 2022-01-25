
""" Helpers to implement a plugin infrastructure in Python. """

import logging
import pkg_resources
import sys
import typing as t

from nr.util.generic import T

logger = logging.getLogger(__name__)


def load_plugins(
  group: str,
  base_class: type[T],
  constructor: t.Callable[[type[T]], T] | None = None,
  do_raise: bool = False,
) -> list[T]:
  """ Loads plugins from an entrypoint group. All entrypoints must point to a class of the specified *base_class*.
  If *do_raise* is `True` and an entrypoint does not point to a subclass of the given type, a #RuntimeError is
  raised, otherwise a warning is printed. If the entrypoint cannot be imported and *do_raise* is `False`, a warning
  will be printed as well.

  The *constructor* will be used to create instances of the *base_class*. If it is omitted, the instances will be
  created without arguments. If the construction fails and *do_raise* is `False`, a warning will be printed. """

  if not isinstance(base_class, type):
    raise TypeError(f'base_class must be a type, got {type(base_class).__name__}')

  result = []
  for ep in pkg_resources.iter_entry_points(group):

    try:
      cls = ep.load()
    except ImportError:
      if do_raise:
        raise
      logger.exception(f'Unable to load entrypoint "%s" due to ImportError', ep)
      continue

    if not isinstance(cls, type) or not issubclass(cls, base_class):
      message = f'Entrypoint "%s" does not point to a %s subclass (got value: %r)'
      if do_raise:
        raise RuntimeError(message % (ep, base_class.__name__, cls))
      logger.error(message, ep, base_class.__name__, cls)
      continue

    try:
      result.append(constructor(cls) if constructor else cls())
    except Exception:
      message = f'Instance from entrypoint "%s" could not be created'
      if do_raise:
        raise RuntimeError(message % (ep,))
      logger.exception(message, ep)

  return result
