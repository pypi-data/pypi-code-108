""" A simple implementation of ContextVar and Context based on PEP-567 https://www.python.org/dev/peps/pep-0567/
Exports ContextVar included in Python for python versions >= 3.7 and implements fallbacks for 3.5.3+
Note: The backport implementations are simplified for our use case (Propogation of current_bts in agent across tasks)

Simplifications done (Only for the backport -> 3.5.3 - 3.7)
----------------------
- Python dicts used in place of immutables in order to reduce dependency on any external library
- Implementations of Token class and ContextVar.reset skipped as they were not needed
- Context._data is shallow copied

"""

import threading
import asyncio


try:
    # pylint: disable=import-error
    import contextvars
    ContextVar = contextvars.ContextVar
    Context = contextvars.Context

    def get_state():
        loop = None
        try:
            # pylint: disable=no-member
            loop = asyncio.get_running_loop()
        except:
            pass
        if loop is None:
            return threading.current_thread()
        # pylint: disable=no-member
        task = asyncio.current_task(loop=loop)
        return threading.current_thread() if task is None else task
except:
    # Fallback for python 3.5.3 - 3.7 when contextvars are not available
    import collections.abc
    import types

    _DEFAULT_VAL = object()

    class Context(collections.abc.Mapping):
        """ Context class responsible for managing the context across various tasks

        Attributes
        ----------------
        _data : A dict for storing the contextvars inside the context
        _previous_context: The context which was active before the activation of self instance

        Methods
        ----------------
        copy(self)
            Returns a new Context instance with the same data as the instance the function was called on
        run(self, callable, *args, **kwargs)
            Makes the current context the active context and restores the previous context when exiting

        """
        def __init__(self):
            self._data = {}
            self._previous_context = None

        def run(self, callable, *args, **kwargs):
            if self._previous_context is not None:
                raise RuntimeError(
                    'Cannot enter Context: {} is already entered.'.format(self))

            self._previous_context = _get_context()
            try:
                _set_context(self)
                return callable(*args, **kwargs)
            finally:
                _set_context(self._previous_context)
                self._previous_context = None

        def copy(self):
            new = Context()
            new._data = self._data.copy()
            return new

        def __getitem__(self, item):
            return self._data[item]

        def __contains__(self, item):
            return item in self._data

        def __len__(self):
            return len(self._data)

        def __iter__(self):
            return iter(self._data)

    class ContextVar():
        """ ContextVar class responsible for manipulation/management of the actual context variables
        A ContextVar is attached to contexts/tasks via the Context class

        Attributes
        ----------------
        _name : Name of the context var
        _default : Default value of the context var (When it is not set)

        Methods
        -----------------
        get(self, default)
            Return the value of the ContextVar in the current Context
        set(self, value):
            Sets the value of the ContextVar in the current Context

        """
        def __init__(self, name, *, default=_DEFAULT_VAL):
            if not isinstance(name, str):
                raise TypeError('Context Variable name must be a string.')

            self._name = name
            self._default = default

        @property
        def name(self):
            return self._name

        def get(self, default=_DEFAULT_VAL):
            ctx = _get_context()
            try:
                return ctx[self]
            except KeyError:
                pass
            if default is not _DEFAULT_VAL:
                return default
            if self._default is not _DEFAULT_VAL:
                return self._default
            raise LookupError

        def set(self, value):
            ctx = _get_context()
            old_data = ctx._data
            new_data = old_data.copy()
            new_data[self] = value
            ctx._data = new_data

        def __repr__(self):
            ret = '<ContextVar {!r}'.format(self.name)
            return ret + ' at {:0x}>'.format(id(self))

    def get_state():
        # pylint: disable=no-member
        loop = asyncio._get_running_loop()
        if loop is None:
            return threading.current_thread()
        task = asyncio.Task.current_task(loop=loop)
        return threading.current_thread() if task is None else task

    def copy_context():
        return _get_context().copy()

    def _get_context():
        state = get_state()
        ctx = getattr(state, 'context', None)
        if ctx is None:
            ctx = Context()
            state.context = ctx
        return ctx

    def _set_context(ctx):
        state = get_state()
        state.context = ctx

    def create_task(loop, coro):
        task = loop._original_create_task(coro)
        if task._source_traceback:
            del task._source_traceback[-1]
        task.context = copy_context()
        return task

    def _patch_loop(loop):
        if loop and not hasattr(loop, '_original_create_task'):
            loop._original_create_task = loop.create_task
            loop.create_task = types.MethodType(create_task, loop)
        return loop

    def get_event_loop():
        return _patch_loop(_get_event_loop())

    def set_event_loop(loop):
        return _set_event_loop(_patch_loop(loop))

    def new_event_loop():
        return _patch_loop(_new_event_loop())

    _get_event_loop = asyncio.get_event_loop
    _set_event_loop = asyncio.set_event_loop
    _new_event_loop = asyncio.new_event_loop

    # Patching asyncio methods to allow sharing of context between tasks
    asyncio.get_event_loop = asyncio.events.get_event_loop = get_event_loop
    asyncio.set_event_loop = asyncio.events.set_event_loop = set_event_loop
    asyncio.new_event_loop = asyncio.events.new_event_loop = new_event_loop
