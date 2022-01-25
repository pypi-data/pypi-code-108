
"""
Provides classes that proxy all operations to a delegate object, allowing to implement behaviours at runtime where
the object contained in a "variable" can be interchanged or different based on the async context or thread.
"""

from ._base import get_name, get, BaseProxy
from ._proxy import bind, is_bound, proxy, set_value, Proxy
from ._stackable import empty, push, pop, StackableProxy
from ._threadlocal import threadlocal, ThreadLocalProxy
from ._contextlocal import contextlocal, ContextLocalProxy


__all__ = [
  'get_name', 'get', 'BaseProxy',
  'bind', 'is_bound', 'proxy', 'set_value', 'Proxy',
  'empty', 'push', 'pop', 'StackableProxy',
  'threadlocal', 'ThreadLocalProxy',
  'contextlocal', 'ContextLocalProxy',
]
