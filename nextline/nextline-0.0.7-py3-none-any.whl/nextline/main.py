import asyncio
import linecache

from .state import Initialized


# __________________________________________________________________||
class Nextline:
    """Nextline allows line-by-line execution of concurrent Python scripts

    Nextline supports concurrency with threading and asyncio. It uses
    multiple instances of Pdb, one for each thread and async task.

    Note
    ----
    The running asyncio event loop must exists when Nextline is
    instantiated.

    Parameters
    ----------
    statement : str
        A Python code as a string

    """

    def __init__(self, statement):
        self._condition_finish = asyncio.Condition()
        self._condition_close = asyncio.Condition()

        self._state = Initialized(statement)
        self.registry = self._state.registry

    def __repr__(self):
        # e.g., "<Nextline 'running'>"
        return f"<{self.__class__.__name__} {self.global_state!r}>"

    @property
    def global_state(self) -> str:
        """state, e.g., "initialized", "running", "exited", "finished", "closed" """
        return self._state.name

    def run(self):
        """run the script"""
        self._state = self._state.run()
        self._task_exited = asyncio.create_task(self._exited())

    async def _exited(self):
        """receive the exited state, to be scheduled in run()."""
        self._state = await self._state.exited()

    async def finish(self):
        """finish the script execution

        wait for the script execution in another thread to exit and
        join the thread.

        """
        await self._task_exited
        async with self._condition_finish:
            self._state = await self._state.finish()

    def exception(self):
        return self._state.exception()

    def result(self):
        self._state.result()

    def reset(self, statement=None):
        """reset the state"""
        self._state = self._state.reset(statement=statement)

    async def close(self):
        """close the nextline"""
        async with self._condition_close:
            self._state = await self._state.close()

    async def subscribe_global_state(self):
        # wish to be able to write with "yield from" but not possible
        # https://stackoverflow.com/a/59079548/7309855
        agen = self.registry.subscribe("state_name")
        async for y in agen:
            yield y

    async def subscribe_thread_asynctask_ids(self):
        agen = self.registry.subscribe("thread_task_ids")
        async for y in agen:
            yield y

    async def subscribe_thread_asynctask_state(self, thread_asynctask_id):
        agen = self.registry.subscribe(thread_asynctask_id)
        async for y in agen:
            yield y

    def send_pdb_command(self, thread_asynctask_id, command):
        self._state.send_pdb_command(thread_asynctask_id, command)

    def get_source(self, file_name=None):
        if not file_name or file_name == self.registry.get("script_file_name"):
            return self.registry.get("statement").split("\n")
        return [e.rstrip() for e in linecache.getlines(file_name)]

    def get_source_line(self, line_no, file_name=None):
        """
        based on linecache.getline()
        https://github.com/python/cpython/blob/v3.9.5/Lib/linecache.py#L26
        """
        lines = self.get_source(file_name)
        if 1 <= line_no <= len(lines):
            return lines[line_no - 1]
        return ""


# __________________________________________________________________||
