from typing import Any, Callable, List, Optional, Type

import flask
from infosystem.common.subsystem.controller import Controller
from infosystem.common.subsystem.driver import Driver
from infosystem.common.subsystem.entity import Entity
from infosystem.common.subsystem.manager import Manager
from infosystem.common.subsystem.router import Router


class Subsystem(flask.Blueprint):

    def __init__(self, resource: Optional[Type[Entity]] = None,
                 router: Optional[Type[Router]] = None,
                 controller: Optional[Type[Controller]] = None,
                 manager: Optional[Type[Manager]] = None,
                 driver: Optional[Type[Driver]] = None,
                 individual_name: Optional[str] = None,
                 collection_name: Optional[str] = None,
                 operations: List[Any] = []) -> None:

        self.__individual_name: str = individual_name or resource.individual()
        self.__collection_name: str = collection_name or resource.collection()

        super().__init__(name=self.__collection_name,
                         import_name=self.__collection_name)

        self.name = self.__collection_name
        self.__resource = resource
        self.__driver = driver if driver else Driver
        self.__controller = controller if controller else Controller
        self.__manager = manager if manager else Manager
        self.__router = router if router else Router
        self.router = self.__router(self.__collection_name, routes=operations)

        self.register_routes(self.router.routes)

        self.api = None

    def __validate_routes(self, routes: List[Router],
                          controller: Type[Controller]) -> List[str]:
        errors: List[str] = []
        for route in routes:
            callback_str = route['callback']

            if not hasattr(controller, callback_str):
                message = '{name} controller has no function {function}'.\
                    format(name=self.name, function=callback_str)
                errors.append(message)
                return errors

            fn = getattr(controller, callback_str)
            if not callable(fn):
                message = '{x} in {name} controller is not a function'.\
                    format(name=self.name, x=callback_str)
                errors.append(message)
        return errors

    def __view_func(self, callback_str: str) -> Callable:
        def wrapper(*args, **kwargs):
            controller = self.controller

            if not hasattr(controller, callback_str):
                message = '{name} controller has no function {function}'.\
                    format(name=self.name, function=callback_str)
                raise Exception(message)

            fn = getattr(controller, callback_str)
            if not callable(fn):
                message = '{x} in {name} controller is not a function'.\
                    format(name=self.name, x=callback_str)
                raise Exception(message)

            return fn(*args, **kwargs)
        wrapper.__name__ = callback_str

        return wrapper

    def register_routes(self, routes: List[Router]) -> None:
        for route in self.router.routes:
            self.add_url_rule(rule=route['url'],
                              view_func=self.__view_func(route['callback']),
                              methods=[route['method']])

    def validate_routes(self) -> List[str]:
        return self.__validate_routes(self.router.routes, self.__controller)

    def lazy_manager(self) -> Callable[[], Manager]:
        return self.manager

    @property
    def manager(self) -> Manager:
        def instantiate() -> Manager:
            driver = self.driver
            manager = self.__manager(driver)
            return manager

        return instantiate()

    @property
    def controller(self) -> Controller:
        def instantiate() -> Controller:
            if self.api is not None:
                api = self.api()
                manager_cls = getattr(api, self.name)
                manager = manager_cls()
            else:
                manager = self.manager
            return self.__controller(manager,
                                     self.__individual_name,
                                     self.__collection_name)

        return instantiate()

    @property
    def driver(self) -> Optional[Driver]:
        def instantiate() -> Optional[Driver]:
            return self.__driver(self.__resource) if self.__resource else None

        return instantiate()
