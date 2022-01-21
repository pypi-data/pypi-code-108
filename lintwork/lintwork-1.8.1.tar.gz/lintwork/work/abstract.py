# -*- coding: utf-8 -*-

import abc


class WorkAbstract(abc.ABC):
    def __init__(self, config):
        self._config = config

    @abc.abstractmethod
    def _execution(self, project):
        pass

    def run(self, project):
        return self._execution(project)
