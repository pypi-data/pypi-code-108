import importlib
import sys

from typing import Any


class RuntimeHandler(object):
    def __init__(self, rule, data) -> None:
        super(RuntimeHandler, self).__init__()
        self._rule = rule
        self._config = data.get('config', {})

        method = data.get('method', '')
        self.__parse_method(method)

    def handle_callback(self, method_data, data) -> bool:
        mod = self.__get_module()

        if mod == None:
            return True

        data['config'] = self._config
        return getattr(mod, self._method)(data)

    def __get_module(self) -> Any:
        if self._module == None or self._method == None:
            return None

        mod = importlib.import_module(self._module, package='.')
        return getattr(mod, self._class, mod)

    def __parse_method(self, method):
        try:
            method_parts = method.split('.')
            if len(method_parts) == 0 or len(method_parts) > 3:
                raise ValueError(
                    f'method should be of the format: <module>.<class>.<method> or <module>.<method>, specified argument is: {method}')

            self._module = self.__get_module_name(method_parts[0])

            if (len(method_parts) == 2):
                self._class = ''
                self._method = method_parts[1]
            else:
                self._class = method_parts[1]
                self._method = method_parts[2]
        except:
            print(
                f'RuntimeHandler: failed to parse method: {sys.exc_info()[0]}')
            self._module = None
            self._method = None

    def __get_module_name(self, module):
        module_parts = self.__module__.split('.')
        module_parts.pop()
        module_parts.insert(len(module_parts), module)
        return '.'.join(module_parts)
