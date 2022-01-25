from abc import ABC

from whizbang.config.app_config import AppConfig


class IHandler(ABC):
    """The base handler interface"""


class HandlerBase(IHandler):
    """Handler should be responsible for building domain models based on incoming request and passing them to the manager(s)"""

    def __init__(self, app_config: AppConfig):
        self._app_config = app_config
