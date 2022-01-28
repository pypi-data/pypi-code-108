from abc import ABC, abstractmethod
from typing import Any

from .handlers import Handlers


class BaseRule(ABC):
    def __init__(self, rule, module) -> None:
        self._rule = rule
        self._module = module
        self._create_handlers()

    @abstractmethod
    def add_instrumentation(self) -> None:
        raise NotImplementedError

    @property
    def id(self) -> str:
        return self._rule.get('id', '')

    @property
    def context(self) -> str:
        return self.intercept.get('context', '')

    @property
    def intercept(self):
        return self._rule.get('intercept', {})

    @property
    def mod(self) -> Any:
        if self._module:
            return self._module

        return self.intercept.get('module', '')

    @property
    def cls(self) -> str:
        return self.intercept.get('class', '')

    @property
    def type(self) -> str:
        return self.intercept.get('type', '')

    @property
    def method(self):
        return self.intercept.get('method', '')

    @property
    def methods(self):
        return self.intercept.get('methods', '')

    @property
    def handlers(self):
        return self._handlers

    def _create_handlers(self):
        handlers = self.intercept.get('handlers', [])
        self._handlers = Handlers(self, handlers)
