import argparse
import os
from pathlib import Path
from typing import Iterable, IO
from typing import Tuple
from configparser import ConfigParser
from .requirements.utilities import (
    iter_distribution_location_file_paths,
)


def _get_project_and_setup_cfg_paths(path: str = ".") -> Tuple[str, str]:
    setup_cfg_path: str
    project_path: str
    if not os.path.isdir(path):
        assert os.path.basename(path).lower() == "setup.cfg"
        setup_cfg_path = path
        project_path = os.path.dirname(path)
    else:
        setup_cfg_path = os.path.join(path, "setup.cfg")
        project_path = path
    return project_path, setup_cfg_path


def _touch_packages_py_typed(project_path: str) -> Iterable[str]:
    def touch_py_typed(path: str) -> str:
        if os.path.basename(path).lower() == "__init__.py":
            py_typed_path: str = os.path.join(
                os.path.dirname(path), "py.typed"
            )
            print(f"touch {py_typed_path}")
            Path(py_typed_path).touch()
            return os.path.relpath(py_typed_path, project_path)
        return ""

    return filter(
        None,
        map(
            touch_py_typed, iter_distribution_location_file_paths(project_path)
        ),
    )


def _update_setup_cfg(
    setup_cfg_path: str, py_typed_paths: Iterable[str]
) -> None:
    parser: ConfigParser = ConfigParser()
    if os.path.isfile(setup_cfg_path):
        parser.read(setup_cfg_path)
    if not parser.has_section("options"):
        parser.add_section("options")
    parser.set("options", "include_package_data", "True")
    if not parser.has_section("options.data_files"):
        parser.add_section("options.data_files")
    py_typed_path: str
    for py_typed_path in map(os.path.normpath, py_typed_paths):  # type: ignore
        package_directory: str = os.path.dirname(py_typed_path)
        package_directory_data_files: str = parser.get(
            "options.data_files", package_directory, fallback=""
        ).rstrip()
        if py_typed_path in filter(  # type: ignore
            None,
            map(
                os.path.normpath,  # type: ignore
                map(str.strip, package_directory_data_files.split("\n")),
            ),
        ):
            print(f"Data file already specified in setup.cfg: {py_typed_path}")
        else:
            print(f"Adding data file to setup.cfg: {py_typed_path}")
            parser.set(
                "options.data_files",
                package_directory,
                f"{package_directory_data_files}\n{py_typed_path}",
            )
    print(f"Writing {setup_cfg_path}")
    setup_cfg_io: IO[str]
    with open(setup_cfg_path, "w") as setup_cfg_io:
        parser.write(setup_cfg_io)


def make_typed(path: str = ".") -> None:
    """
    Create (if needed) **/py.typed files and alter the setup.cfg file such that
    a distribution's packages will be identified as being fully type-hinted
    """
    project_path: str
    setup_cfg_path: str
    project_path, setup_cfg_path = _get_project_and_setup_cfg_paths(path)
    # Parse and update setup.cfg
    _update_setup_cfg(setup_cfg_path, _touch_packages_py_typed(project_path))


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="daves-dev-tools make-typed",
        description=(
            "Add **/py.typed files and alter the setup.cfg such that a "
            "distribution's packages will be identifiable as fully type-hinted"
        ),
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        type=str,
        help=(
            "A project directory (where the setup.py and/or setup.cfg file "
            "are located)"
        ),
    )
    arguments: argparse.Namespace = parser.parse_args()
    make_typed(arguments.path)


if __name__ == "__main__":
    main()
