from pathlib import Path
from typing import (
    List,
    Mapping,
)

from begin.constants import ExitCodeEnum


class ExitCodeMeta(type):
    """ Exceptions cannot be combined with abstract base classes, see:
    https://stackoverflow.com/questions/2862153/python-2-6-3-abstract-base-class-misunderstanding/2862419#2862419
    This is a minimal interface which ensures classes which fail to implement an `cls._exit_code_enum`
    of type `ExitCodeEnum` raise *at instantiation time*, but which does not implement any of the
    other functionality of `abc`. """

    def __call__(cls, *args, **kwargs):
        # Raise if cls._exit_code_enum was not implemented
        if not hasattr(cls, '_exit_code_enum'):
            raise NotImplementedError(f'{cls.__name__} does not implement _exit_code_enum')

        # Raise if cls._exit_code_enum has wrong type
        if not isinstance(cls._exit_code_enum, ExitCodeEnum):
            raise ValueError(f'{cls.__name__}._exit_code_enum does not have type ExitCodeEnum')

        return super(ExitCodeMeta, cls).__call__(*args, **kwargs)


class BeginError(Exception, metaclass=ExitCodeMeta):
    """ A base class for all custom exceptions. Anticipated exceptions should not
    be raised to the user-level, but be caught at the cli-level and handled with an
    appropriate message and exit code. All inheriting classes must implement
    `cls._exit_code_enum` (see: `ExitCodeMeta`). """
    _exit_code_enum: ExitCodeEnum

    @property
    def exit_code(self) -> int:
        return self._exit_code_enum.value

    @property
    def message(self) -> str:
        return str(self)


class RegistryNameCollisionError(BeginError):

    _exit_code_enum = ExitCodeEnum.REGISTRY_NAME_COLLISION

    def __init__(self, colliding_namespaces: Mapping[str, List[Path]]) -> None:
        """ `colliding_namespaces` has registry names for keys and a list of paths
        for values. The paths in the list point to files where the namespace was defined.
        The length of each list is assumed to be greater than 1 (otherwise there is no
        namespace collision. """
        lines = []
        for name, paths in colliding_namespaces.items():
            lines.append(f'Found multiple registries with name `{name}` in files:')
            for path in paths:
                lines.append(f'\t{path}')
        message = '\n'.join(lines)
        super().__init__(message)
