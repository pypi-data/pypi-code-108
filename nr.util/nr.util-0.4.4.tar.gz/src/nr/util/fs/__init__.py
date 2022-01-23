
""" Utilities for filesystem operations. """

from ._atomic import atomic_swap, atomic_write

__all__ = [
  'atomic_swap',
  'atomic_write',
]
