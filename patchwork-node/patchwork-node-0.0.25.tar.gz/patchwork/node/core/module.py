# -*- coding: utf-8 -*-
import logging
from asyncio import AbstractEventLoop

from patchwork.core.component import Component, OrphanedComponent


class Module(Component):
    """
    Worker level component is named module.
    """

    def __repr__(self):
        return super().__repr__().replace('Component', 'Module')

    @property
    def logger(self) -> logging.Logger:
        return logging.getLogger(f'patchwork.node.{getattr(self, "logger_name", self.__class__.__name__.lower())}')

    @property
    def worker(self):
        """
        Returns worker instance
        :return:
        """
        try:
            return self.parent
        except OrphanedComponent:
            # change exception message
            raise OrphanedComponent("Worker instance gone! This module instance is orphaned and should be destroyed")

    @property
    def app_loop(self) -> AbstractEventLoop:
        """
        Returns worker event loop
        :return:
        """
        return self.worker.event_loop
