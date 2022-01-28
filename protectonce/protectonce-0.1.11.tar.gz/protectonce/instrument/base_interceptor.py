import importlib
from abc import ABC, abstractmethod

from .po_exceptions import SecurityException
from .. import common_utils

from wrapt import FunctionWrapper


class BaseInterceptor(ABC):
    def __init__(self, mod, cls, methods, handlers) -> None:
        self._module = mod
        self._class = cls
        self._handlers = handlers
        self._save_methods(methods)

    def pre_callbacks(self, method_name, instance, *args, **kwargs):
        self.__handle_callbacks('before', self._handlers.before,
                                method_name, instance, args, kwargs, None)

    def post_callbacks(self, method_name, result, instance, *args, **kwargs):
        self.__handle_callbacks('after', self._handlers.after,
                                method_name, instance, args, kwargs, result)

    def __handle_callbacks(self, type, handlers, method_name, instance, args, kwargs, result):
        data = {
            'args': args,
            'kwargs': args,
            'instance': instance,
            'result': result
        }
        blocked = False
        for handler in handlers:
            method_data = self._methods.get(method_name, {})

            result = handler.handle_callback(method_data, data)

            if result:
                data['result'] = result

            if blocked == False:
                blocked = common_utils.is_action_blocked(data)

        if blocked:
            raise SecurityException("Malicious input blocked")

    @abstractmethod
    def intercept(self):
        raise NotImplementedError

    def _wrap_method(self, method, wrapper) -> None:
        try:
            mod = self._module
            if isinstance(self._module, str):
                mod = importlib.import_module(self._module)
                mod = getattr(mod, self._class, mod)

            fn = getattr(mod, method)

            fw = FunctionWrapper(fn, wrapper)
            setattr(mod, method, fw)
        except:
            # Skip wrapping libraries which are not in the python path
            # TODO: print log
            pass

    def _save_methods(self, methods):
        self._methods = {}
        for method in methods:
            _method = {}
            _method['args'] = method.get('args', [])
            _method['kwargs'] = method.get('kwargs', [])

            method_name = method.get('method', None)
            _method['method'] = method_name
            if method_name:
                self._methods[method_name] = _method
