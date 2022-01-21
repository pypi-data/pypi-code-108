from importlib import import_module
from importlib import invalidate_caches as importlib_invalidate_caches
from importlib import reload
from pathlib import Path
from pkgutil import walk_packages
from shutil import copyfile
from sys import modules

from pygit2 import Repository, discover_repository

from deckz.exceptions import DeckzException


def get_git_dir(path: Path) -> Path:
    repository = discover_repository(str(path))
    if repository is None:
        raise DeckzException(
            "Could not find the path of the current git working directory. "
            "Are you in one?"
        )
    return Path(Repository(repository).workdir).resolve()


def copy_file_if_newer(original: Path, copy: Path) -> None:
    if copy.exists() and copy.stat().st_mtime > original.stat().st_mtime:
        return
    else:
        copy.parent.mkdir(parents=True, exist_ok=True)
        copyfile(original, copy)


def import_module_and_submodules(package_name: str) -> None:
    """
    From https://github.com/allenai/allennlp/blob/master/allennlp/common/util.py
    """
    importlib_invalidate_caches()

    if package_name in modules:
        module = modules[package_name]
        reload(module)
    else:
        module = import_module(package_name)
    path = getattr(module, "__path__", [])
    path_string = "" if not path else path[0]

    for module_finder, name, _ in walk_packages(path):
        if (
            path_string
            and hasattr(module_finder, "path")
            and module_finder.path != path_string  # type: ignore
        ):
            continue
        subpackage = f"{package_name}.{name}"
        import_module_and_submodules(subpackage)
