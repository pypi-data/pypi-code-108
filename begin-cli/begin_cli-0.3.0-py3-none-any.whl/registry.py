import inspect
import logging
from collections import defaultdict
from pathlib import Path
from typing import (
    Callable,
    Dict,
    List,
    Set,
)

from begin.exceptions import RegistryNameCollisionError


logger = logging.getLogger(__name__)


class Target:

    def __init__(self, function: Callable, registry_namespace: str) -> None:
        self._function = function
        self._registry_namespace = registry_namespace

    @property
    def registry_namespace(self) -> str:
        return self._registry_namespace

    @property
    def function_name(self) -> str:
        return self._function.__name__

    def execute(self) -> None:
        self._function()

    def __repr__(self) -> str:
        class_name = f'{self.__class__.__module__}.{self.__class__.__name__}'
        return f'<{class_name}(registry_namespace={self.registry_namespace},function_name={self.function_name})>'

    def __hash__(self) -> int:
        return hash(repr(self))


class Registry:

    def __init__(self, name: str = 'default') -> None:
        self.name: str = name
        self.targets: Set[Target] = set()
        self.path: Path = self._get_calling_context_path()

    @staticmethod
    def _get_calling_context_path() -> Path:
        """ Gets the `Path` of the first context in the stack to not be __file__.
        Intended to be called at instantiation-time to track the filenames of different
        targets.py files.
        Example:
            # /path/to/foo.py
            Registry._get_calling_context_path()  # Path('/path/to/foo.py')
        """
        stack = inspect.stack()
        calling_context = next(context for context in stack if context.filename != __file__)
        return Path(calling_context.filename)

    def register_target(self, *args, **kwargs) -> Callable:
        if args:
            # For calls like @registry.register_target
            function = args[0]
            self._register_target(function)
            return function
        else:
            # For calls like @registry.register_target(...)
            def decorator(function):
                self._register_target(function, **kwargs)
                return function
            return decorator

    def _register_target(self, function: Callable, **kwargs) -> None:
        new_target = Target(
            function=function,
            registry_namespace=self.name,
        )
        self.targets.add(new_target)


class TargetMap:

    def __init__(self, registries: List[Registry]) -> None:
        self._registries: List[Registry] = registries
        self._map: Dict[str, Dict[str, Target]] = {}

    @classmethod
    def create(cls, registries: List[Registry]) -> 'TargetMap':
        target_map = cls(registries)
        target_map.compile()
        return target_map

    def compile(self) -> None:
        for registry in self._registries:
            self.unpack_registry(registry)

    def unpack_registry(self, registry: Registry) -> None:
        for target in registry.targets:
            self.add(target)

    def add(self, target: Target) -> None:
        target_name = target.function_name
        namespace = target.registry_namespace
        if target_name not in self._map:
            self._map[target_name] = {
                namespace: target,
            }
        else:
            self._map[target_name][namespace] = target

    def get(self, target_name: str, namespace: str) -> Target:
        return self._map[target_name][namespace]


class RegistryManager:

    def __init__(self, registries: List[Registry]) -> None:
        self._target_map: TargetMap = TargetMap.create(registries)

    @classmethod
    def create(cls, registries: List[Registry]) -> 'RegistryManager':
        cls.find_namespace_collisions(registries)
        return cls(registries)

    @staticmethod
    def find_namespace_collisions(registries: List[Registry]) -> None:
        registry_path_map = defaultdict(list)
        for registry in registries:
            registry_path_map[registry.name].append(registry.path)

        colliding_namespaces = {name: paths for name, paths in registry_path_map.items() if len(paths) > 1}

        if colliding_namespaces:
            raise RegistryNameCollisionError(colliding_namespaces=colliding_namespaces)

    def get_target(self, requested_target_name: str, requested_namespace: str) -> Target:
        return self._target_map.get(requested_target_name, requested_namespace)
