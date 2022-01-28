from ..handlers.runtime_handlers import RuntimeHandler
from ..handlers.core_handler import CoreHandler


class Handlers(object):
    def __init__(self, rule, handlers) -> None:
        super().__init__()
        self._before_handlers = self._create_handlers(
            rule, handlers.get('before', []))
        self._after_handlers = self._create_handlers(
            rule, handlers.get('after', []))

    @property
    def before(self):
        return self._before_handlers

    @property
    def after(self):
        return self._after_handlers

    def _create_handlers(self, rule, handlers):
        _handlers = []
        for handler in handlers:
            _handler = self._create_handler(rule, handler)
            if _handler:
                _handlers.append(_handler)

        return _handlers

    def _create_handler(self, rule, data):
        type = data.get('type', '')
        if type == 'core':
            method = data.get('method', '')
            if method:
                return CoreHandler(rule, method)

        if type == 'runtime':
            return RuntimeHandler(rule, data)

        return None
