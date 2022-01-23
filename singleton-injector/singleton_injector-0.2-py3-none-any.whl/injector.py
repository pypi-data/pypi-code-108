import inspect

from typing import Dict, Callable
from singleton_injector.singleton import Singleton


class Injector:
    def __init__(self, singleton: Singleton):
        self.singleton = singleton
        self._classes: Dict[str, Callable] = {}

    def __call__(self, _class: Callable) -> Callable:
        class_wrapper = self.singleton(_class)
        self._classes[_class.__name__] = class_wrapper
        self.__inject(_class, self._classes[_class.__name__])
        return _class

    def get_method_parameter_classes(self, _method: Callable) -> Dict[str, Callable]:
        parameters = inspect.getfullargspec(_method).annotations
        for name in parameters:
            _class = parameters[name]
            parameters[name] = self._classes[_class.__name__]()
        return parameters

    def __inject(self, _class: Callable, wrapper: Callable):
        parameter_classes = self.get_method_parameter_classes(_class.__init__)
        wrapper(**parameter_classes)
