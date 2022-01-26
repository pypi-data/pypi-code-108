import logging
from logging import Logger, Manager

from ._log import get_default_logger
from ..._private._utilities import *
from ._store import DataStore, SimpleRAMDataStore


class PipelineConfig:
    def __init__(self,
                 name: str = "Pipeline",
                 source_triggerers_thread_count: int = 1,
                 data_store: DataStore = None,
                 logger: Logger = None,
                 logger_changers: List[Callable[[Logger], None]] = None,
                 # ray_config=None
                 ):
        self.name = name
        self.source_triggerers_thread_count = source_triggerers_thread_count
        self.data_store = get_not_none(data_store, lambda: SimpleRAMDataStore())
        self.logger = get_not_none(logger, lambda: get_default_logger(name))
        logger_changers = get_not_none(logger_changers, [])
        for logger_changer in logger_changers:
            logger_changer(self.logger)

