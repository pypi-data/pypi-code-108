from __future__ import annotations

import weakref
from collections import ChainMap

import abc
import asyncio
import sys
import typing as t
from functools import wraps

from ._typing import _T, SimpleCoroutine, _S


def make_async(func: t.Callable[[_T], SimpleCoroutine[_S] | _S]) -> t.Callable[
    [_T], SimpleCoroutine[_S]]:
    """
    Decorator to turn a non async function into a coroutine by running it in the default executor pool.
    """

    if asyncio.iscoroutinefunction(func):
        return t.cast(t.Callable[[_T], SimpleCoroutine[_S]], func)

    @wraps(func)
    async def _callback(*args):
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, func, *args)

        if isinstance(result, t.Awaitable):
            result = await result

        return result

    return _callback


class RegistryMeta(abc.ABCMeta):
    """
    Set __unique_key_attr__ in created classes to some attribute of the class instance that is
    unique to use this attribute as a key in the registry instead of the __default_key__.
    If the __default_key__ attribute is not present in the instance, it will be copied from the class
    on instance creation, and appended with the number of instances created before.
    """
    _wrap_marker = object()

    @staticmethod
    def _post_new(instance: t.Any):
        cls: RegistryMeta = type(instance)

        # we set value in all parents, so they know a new instance is created
        # we know that the mappings are mutable, so it's ok to set the values.
        for mapping in cls.__created__.maps:
            mapping[instance.__registry_key__] = instance  # type: ignore

    @property
    def registry(cls: t.Type[_T]) -> t.Dict[t.Any, _T]:
        return {
            instance.__registry_key__: instance
            for instance in cls.__created__.maps[0].values()
            if instance is not None  # only live references
        }

    @staticmethod
    def _wrap_new(__new__):
        @wraps(__new__)
        def wrapped(cls, *args, **kwargs):
            instance = __new__(cls)
            RegistryMeta._post_new(instance)
            return instance

        wrap_markers = getattr(wrapped, 'markers', set())
        wrap_markers.add(RegistryMeta._wrap_marker)
        wrapped.markers = wrap_markers

        return wrapped

    def __new__(mcs, name, bases, attrs):
        kls: RegistryMeta = super().__new__(mcs, name, bases, attrs)

        wrap_markers = getattr(kls.__new__, 'markers', set())
        if mcs._wrap_marker not in wrap_markers:
            kls.__new__ = mcs._wrap_new(kls.__new__)

        class_namespace = kls.__dict__

        if not hasattr(kls, '__created__'):
            kls.__created__ = ChainMap(weakref.WeakValueDictionary())
        else:
            parent = kls.__created__
            setattr(kls, '__created__', parent.new_child(weakref.WeakValueDictionary()))

        if '__default_key_value__' not in class_namespace:
            kls.__default_key_value__ = f"{attrs['__module__']}.{attrs['__qualname__']}"

        if not hasattr(kls, '__unique_key_attr__'):
            kls.__unique_key_attr__ = '__missing_key__'

        if '__registry_key__' not in class_namespace:
            kls.__registry_key__ = property(
                fget=(
                    lambda instance: getattr(
                        instance,
                        instance.__unique_key_attr__,
                        f"{kls.__default_key_value__}_{id(instance)}"
                    )
                )
            )

        return kls


class Registry(object, metaclass=RegistryMeta):
    pass


def async_exit_on_exc(ctx_manager: t.AsyncContextManager, task: asyncio.Task, loop: asyncio.BaseEventLoop = None):
    loop = loop or asyncio.get_running_loop()
    try:
        task.result()
    except asyncio.CancelledError:
        pass
    except:  # noqa
        exc_info = sys.exc_info()
        loop.call_soon(ctx_manager.__aexit__(*exc_info).__await__().__next__)
