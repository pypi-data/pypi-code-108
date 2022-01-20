# Copyright Exafunction, Inc.

import abc
from concurrent.futures import ThreadPoolExecutor
from typing import Dict

from exa.common_pb.common_pb2 import ModuleContextInfo

# Some Python extension libraries (eg. PyTorch) have GIL issues
# when called from C++ threads. These are probably bugs, but
# a simple workaround is forwarding all relevant calls to a
# Python thread pool first.
_executor = ThreadPoolExecutor()


def wrap_call(fn, *args):
    return _executor.submit(fn, *args).result()


class BaseModuleContext(abc.ABC):
    def load(self, data: memoryview, config: Dict[str, bytes]) -> None:
        pass

    def unload(self) -> None:
        pass

    def module_context_info(self) -> ModuleContextInfo:
        return ModuleContextInfo()

    def _load(self, data: memoryview, config: Dict[str, bytes]) -> None:
        return wrap_call(self.load, data, config)

    def _unload(self) -> None:
        return wrap_call(self.unload)

    def _module_context_info(self) -> str:
        return wrap_call(self.module_context_info).SerializeToString()
