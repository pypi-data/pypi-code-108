import abc
import importlib
import inspect
from pathlib import Path
from typing import Any, Generic, Optional, TypeVar


class _Finder(abc.ABC):
    def __init__(self, path: Path, root: Path = None):
        self.path = path
        self._targets = {}
        self.root = root or path

    def find(self):
        if self.path.is_dir():
            self.find_from_dir()
        else:
            self.find_from_file()

    def find_from_dir(self, path: Optional[Path] = None):
        if path is None:
            path = self.path
        if 'pycache' in path.name or '.pyc' in path.name:
            return
        for item in path.iterdir():
            if item.is_dir():
                self.find_from_dir(item)
                continue
            if '.py' in path.name and path.name != '__init__.py':
                continue
            self.find_from_file(item)

    def find_from_file(self, path: Optional[Path] = None):
        if path is None:
            path = self.path
        if not path.is_file():
            return
        mod = importlib.import_module(self.get_import(path))
        for name, obj in inspect.getmembers(mod):
            if self.is_valid_object(obj):
                self._targets[name] = obj

    def get_import(self, target: Path):
        target_str = target.as_posix()
        return (
            target_str.replace(self.root.as_posix(), self.root.name)
            .replace('/', '.')
            .replace('.py', '')
        )

    @abc.abstractmethod
    def is_valid_object(self, target: Any) -> bool:
        """Returns if :param:`target` meets the search criteria"""

    @abc.abstractmethod
    def __getitem__(self, name: str) -> Any:
        """Returns target by :param:`name`"""


T = TypeVar('T')


class InstanceFinder(_Finder, Generic[T]):
    def __init__(self, instance_of: type[T], path: Path, root: Path = None):
        self._instance_of = instance_of
        super().__init__(path, root=root)

    def is_valid_object(self, target: Any) -> bool:
        return isinstance(target, self._instance_of)

    def __getitem__(self, name: str) -> T:
        return self._targets[name]


class ClassFinder(_Finder, Generic[T]):
    def __init__(self, child_of: type[T], path: Path, root: Path = None):
        self._child_of = child_of
        super().__init__(path, root=root)

    def is_valid_object(self, target: Any) -> bool:
        if not inspect.isclass(target):
            return False
        is_child_of = issubclass(target, self._child_of)
        is_not_parent = target is not self._child_of
        return is_child_of and is_not_parent

    def __getitem__(self, name: str) -> type[T]:
        return self._targets[name]
