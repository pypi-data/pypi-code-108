from infosystem.common.input import RouteResource
from typing import Any, Callable, Dict, List

from infosystem.common.subsystem import Subsystem
from infosystem.common.subsystem.manager import Manager


class Api(object):

    def __init__(self, managers: Dict[str, Callable[[], Manager]],
                 bootstrap_resources: List[Any]) -> None:
        self.__instances: Dict[str, Manager] = dict()
        self.__bootstrap_resources = bootstrap_resources

        for name, fn in managers.items():
            setattr(self, name, self.__get_instance(name, fn))

    def __get_instance(self, name: str,
                       fn: Callable[[], Manager]) -> Callable[[], Manager]:
        def wrapper():
            manager = self.__instances.get(name)

            if not manager:
                manager = fn()
                setattr(manager, 'api', self)
                setattr(manager,
                        'bootstrap_resources',
                        self.__bootstrap_resources)
                self.__instances[name] = manager

            return manager

        return wrapper


class ApiHandler(object):

    def __init__(self, subsystems: Dict[str, Subsystem],
                 bootstrap_resources: Dict[str, RouteResource]) -> None:
        self.__managers_dict = {name: s.lazy_manager
                                for name, s in subsystems.items()}
        self.__bootstrap_resources = self.__get_resources(bootstrap_resources)

    def api(self) -> Api:
        return Api(self.__managers_dict, self.__bootstrap_resources)

    def __get_resources(self, bootstrap_resources):
        def resources():
            None

        for key, resource in bootstrap_resources.items():
            setattr(resources, key, resource)

        return resources
