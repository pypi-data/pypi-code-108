import importlib.util
import logging
import sys
from importlib.machinery import ModuleSpec
from pathlib import Path
from types import ModuleType
from typing import (
    Iterator,
    List,
    NoReturn,
)

from begin.cli.parser import (
    ParsedCommand,
    parse_command,
)
from begin.exceptions import BeginError
from begin.registry import (
    Registry,
    RegistryManager,
)


logger = logging.getLogger(__name__)


def collect_target_file_paths() -> Iterator[Path]:
    cwd = Path.cwd()
    yield from cwd.rglob('*targets.py')
    global_targets_dir = Path.home().joinpath('.begin')
    if global_targets_dir.exists():
        yield from global_targets_dir.rglob('*targets.py')


def load_module_from_path(path: Path) -> ModuleType:
    # Create a ModuleSpec instance based on the path to the file
    spec: ModuleSpec = importlib.util.spec_from_file_location(path.stem, path)

    # Create a new module based on spec
    module = importlib.util.module_from_spec(spec)

    # Execute the module in its own namespace
    spec.loader.exec_module(module)  # type: ignore
    return module


def get_registries_for_module(module: ModuleType) -> List[Registry]:
    registries_in_module = []
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)
        if isinstance(attribute, Registry):
            registries_in_module.append(attribute)
    return registries_in_module


def load_registries() -> List[Registry]:
    registries = []
    for path in collect_target_file_paths():
        module = load_module_from_path(path)
        registries_for_module = get_registries_for_module(module)
        registries.extend(registries_for_module)
    return registries


def _main():
    parsed_command: ParsedCommand = parse_command()
    registries = load_registries()
    manager = RegistryManager.create(registries)
    for request in parsed_command.requests:
        target = manager.get_target(
            request.target_name,
            request.registry_namespace,
        )
        target.execute(**request.options)


def main() -> NoReturn:
    try:
        _main()
    except BeginError as ex:
        logger.error(ex.message)
        sys.exit(ex.exit_code)
    else:
        sys.exit(0)
