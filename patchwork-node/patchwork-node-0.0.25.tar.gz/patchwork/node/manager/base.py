# -*- coding: utf-8 -*-

from typing import Tuple, Mapping

from patchwork.node.core import Module


class Manager(Module):
    """
    Worker manager to manage the worker remotely
    """

    async def _start(self):
        pass

    async def _stop(self):
        pass

    def get_health(self, include_starting: bool = True) -> Tuple[bool, Mapping[str, bool]]:
        """
        Return health of all worker components.
        :param include_starting: If true starting components are also considered as health
        :return:
        """

        state = {}

        from patchwork.node import PatchworkWorker
        worker: PatchworkWorker = self.worker

        state['worker'] = worker.is_running or (worker.is_starting and include_starting)

        # until worker is running, monitor_task may not be created
        state['monitor'] = not worker.monitor_task.done() if worker.is_running else True

        for mod_name, mod_instance in worker.settings.modules.items():
            state[mod_name] = mod_instance.is_running or (mod_instance.is_starting and include_starting)

        return all(state.values()), state
