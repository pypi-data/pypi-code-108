"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.utility.helper import get_qualname_or_name

from .abstract_signal import AbstractSignal

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]


class GidSignal(AbstractSignal):

    def fire_and_forget(self, *args, **kwargs):
        if len(self.targets) <= 0:
            return
        with ThreadPoolExecutor(thread_name_prefix='signal_thread') as pool:
            for target in self.targets:
                pool.submit(target, *args, **kwargs)

    def emit(self, *args, **kwargs):

        for target in self.targets:
            target(*args, **kwargs)

    async def aemit(self, *args, **kwargs):
        if len(self.targets) <= 0:
            return

        for target in self.targets:
            name = get_qualname_or_name(target)
            info = self.targets_info.get(name)
            task_name = f"{str(self.key)}-Signal_{name}"
            if info.get('is_coroutine') is False:
                task = asyncio.to_thread(target, *args, **kwargs)
            else:
                task = target(*args, **kwargs)
            asyncio.create_task(task, name=task_name)


# region[Main_Exec]
if __name__ == '__main__':
    pass
# endregion[Main_Exec]
