import asyncio
import threading
from typing import Optional, Union

from .trace import Trace
from .utils import Registry, ThreadSafeAsyncioEvent
from .exec_ import exec_with_trace

SCRIPT_FILE_NAME = "<string>"


# __________________________________________________________________||
class StateObsoleteError(Exception):
    """Operation on an obsolete state object."""

    pass


class StateMethodError(Exception):
    """Irrelevant operation on the state."""

    pass


# __________________________________________________________________||
class ObsoleteMixin:
    def assert_not_obsolete(self):
        if self.is_obsolete():
            raise StateObsoleteError(f"The state object is obsolete: {self!r}")

    def is_obsolete(self):
        return getattr(self, "_obsolete", False)

    def obsolete(self):
        self._obsolete = True


class State(ObsoleteMixin):
    """The base state class in the Nextline state machine"""

    def __repr__(self):
        # e.g., "<Initialized 'initialized'>"
        items = [self.__class__.__name__, repr(self.name)]
        if self.is_obsolete():
            items.append("obsolete")
        return f'<{" ".join(items)}>'

    def run(self):
        self.assert_not_obsolete()
        raise StateMethodError(f"Irrelevant operation on the state: {self!r}")

    async def exited(self):
        self.assert_not_obsolete()
        raise StateMethodError(f"Irrelevant operation on the state: {self!r}")

    async def finish(self):
        self.assert_not_obsolete()
        raise StateMethodError(f"Irrelevant operation on the state: {self!r}")

    def reset(self, *_, **__):
        self.assert_not_obsolete()
        raise StateMethodError(f"Irrelevant operation on the state: {self!r}")

    async def close(self):
        self.assert_not_obsolete()
        raise StateMethodError(f"Irrelevant operation on the state: {self!r}")

    def send_pdb_command(self, *_, **__):
        raise StateMethodError(f"Irrelevant operation on the state: {self!r}")

    def exception(self):
        raise StateMethodError(f"Irrelevant operation on the state: {self!r}")

    def result(self):
        raise StateMethodError(f"Irrelevant operation on the state: {self!r}")


class Initialized(State):
    """The state "initialized", ready to run

    Parameters
    ----------
    statement : str or None
        A Python code as a string. None can be given by a state object
        when the state is reset. If None, the statement will be
        obtained from the registry.
    registry : object, optional
        An instance of Registry. This parameter will be given by a state
        object when the state is reset.

    """

    name = "initialized"

    def __init__(
        self, statement: Union[str, None], registry: Optional[Registry] = None
    ):

        if registry:
            self.registry = registry
        else:
            self.registry = Registry()
            self.registry.open_register("statement")
            self.registry.open_register("state_name")
            self.registry.open_register("script_file_name")
            self.registry.open_register_list("thread_task_ids")

        if statement:
            self.registry.register("statement", statement)
            self.registry.register("script_file_name", SCRIPT_FILE_NAME)
        else:
            statement = self.registry.get("statement")

        if isinstance(statement, str):
            self._code = compile(statement, SCRIPT_FILE_NAME, "exec")
        else:
            self._code = statement

        self.registry.register("state_name", self.name)

    def run(self):
        self.assert_not_obsolete()
        running = Running(self.registry, self._code)
        self.obsolete()
        return running

    def reset(self, statement=None):
        self.assert_not_obsolete()
        initialized = Initialized(statement=statement, registry=self.registry)
        self.obsolete()
        return initialized

    async def close(self):
        self.assert_not_obsolete()
        closed = Closed(self.registry)
        await closed._ainit()
        self.obsolete()
        return closed


class Running(State):
    """The state "running", the script is being executed.

    Parameters
    ----------
    registry : object
        An instance of Registry
    code : object
        The code object to be executed.
    """

    name = "running"

    def __init__(self, registry, code):
        self.registry = registry
        self._event = ThreadSafeAsyncioEvent()

        trace = Trace(
            registry=self.registry,
            modules_to_trace={exec_with_trace.__module__},
        )
        self.pdb_ci_registry = trace.pdb_ci_registry

        self.registry.register("state_name", self.name)

        self.loop = asyncio.get_running_loop()

        self._thread = threading.Thread(
            target=exec_with_trace, args=(code, trace, self._done), daemon=True
        )
        self._thread.start()

    def _done(self, result=None, exception=None):
        # callback function, to be called from another thread at the
        # end of exec_with_trace()

        if self.loop.is_closed():
            # The exit is not being waited in the main thread, for
            # example, neither exited() of finish() is called.
            return

        self._exited = Exited(
            self.registry,
            thread=self._thread,
            result=result,
            exception=exception,
        )

        self.obsolete()

        try:
            self._event.set()
        except RuntimeError:
            # The event loop is closed.
            pass

    async def exited(self):
        """return the exited state after the script exits."""
        await self._event.wait()
        return self._exited

    def send_pdb_command(self, thread_asynctask_id, command):
        pdb_ci = self.pdb_ci_registry.get_ci(thread_asynctask_id)
        pdb_ci.send_pdb_command(command)


class Exited(State):
    """The state "exited", the script execution has exited

    Parameters
    ----------
    registry : object
        An instance of Registry
    thread : object
        The object of the thread in which the script was executed.
        This thread is to be joined.
    result : any
        The result of the script execution, always None
    exception : exception or None
        The execution raised in the script execution if any. Otherwise
        None
    """

    name = "exited"

    def __init__(self, registry, thread, result, exception):
        self.registry = registry
        self._thread = thread
        self._result = result
        self._exception = exception

        self.registry.register("state_name", self.name)

    async def finish(self):
        self.assert_not_obsolete()
        await self._join(self._thread)
        finished = Finished(
            self.registry, result=self._result, exception=self._exception
        )
        self.obsolete()
        return finished

    async def _join(self, thread):
        try:
            await asyncio.to_thread(thread.join)
        except AttributeError:
            # for Python 3.8
            # to_thread() is new in Python 3.9
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, thread.join)


class Finished(State):
    """The state "finished", the script execution has finished

    The thread which executed the script has been joined.

    Parameters
    ----------
    registry : object
        An instance of Registry
    result : any
        The result of the script execution, always None
    exception : exception or None
        The exception of the script execution if any. Otherwise None

    """

    name = "finished"

    def __init__(self, registry, result, exception):
        self._result = result
        self._exception = exception

        self.registry = registry
        self.registry.register("state_name", self.name)

    def exception(self):
        """Return the exception of the script execution

        Return None if no execution has been raised.

        """
        return self._exception

    def result(self):
        """Return the result of the script execution

        None in the current implementation as the build-in function
        exec() returns None.

        Re-raise the exception if an exception has been raised in the
        script execution.

        """

        if self._exception:
            raise self._exception

        return self._result

    async def finish(self):
        # This method can be called when Nextline.finish() is
        # asynchronously called multiple times.
        self.assert_not_obsolete()
        return self

    def reset(self, statement=None):
        self.assert_not_obsolete()
        initialized = Initialized(statement=statement, registry=self.registry)
        self.obsolete()
        return initialized

    async def close(self):
        self.assert_not_obsolete()
        closed = Closed(self.registry)
        await closed._ainit()
        self.obsolete()
        return closed


class Closed(State):
    """The state "closed"

    Parameters
    ----------
    registry : object
        An instance of Registry
    """

    name = "closed"

    def __init__(self, registry):
        self.registry = registry
        self.statement = self.registry.get("statement")
        self.registry.register("state_name", self.name)

    async def _ainit(self):
        await self.registry.close()  # close here because "await" is
        # not allowed in __init__()

    def reset(self, statement=None):
        self.assert_not_obsolete()
        if statement is None:
            statement = self.statement
        initialized = Initialized(statement=statement)
        self.obsolete()
        return initialized

    async def close(self):
        # This method can be called when Nextline.close() is
        # asynchronously called multiple times.
        self.assert_not_obsolete()
        return self


# __________________________________________________________________||
