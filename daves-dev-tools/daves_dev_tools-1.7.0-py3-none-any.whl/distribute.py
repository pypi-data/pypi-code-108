import functools
import os
import re
import sys
from distutils.core import run_setup
from time import time
from typing import (
    Any,
    Callable,
    FrozenSet,
    Iterable,
    List,
    Optional,
    Tuple,
)
from .utilities import run, sys_argv_get, sys_argv_pop, run_module_as_main

try:
    from .cerberus import apply_sys_argv_cerberus_arguments
except ImportError:
    apply_sys_argv_cerberus_arguments = None  # type: ignore

lru_cache: Callable[..., Any] = functools.lru_cache


def _list_dist(root: str, modified_at_or_after: float = 0.0) -> FrozenSet[str]:
    dist_root: str = os.path.join(root, "dist")
    dist_file: str
    dist_sub_directories: List[str]
    dist_files: Iterable[str]
    try:
        dist_root, dist_sub_directories, dist_files = next(
            iter(os.walk(dist_root))
        )
    except StopIteration:
        raise FileNotFoundError(
            f"No distributions could be found in {dist_root}"
        )
    dist_files = (
        os.path.join(dist_root, dist_file) for dist_file in dist_files
    )
    if modified_at_or_after:
        dist_files = filter(
            lambda dist_file: (  # noqa
                os.path.getmtime(dist_file) >= modified_at_or_after
            ),
            dist_files,
        )
    try:
        return frozenset(dist_files)
    except (NotADirectoryError, FileNotFoundError):
        return frozenset()


def _setup(root: str) -> FrozenSet[str]:
    start_time: float = time()
    current_directory: str = os.path.abspath(os.path.curdir)
    os.chdir(root)
    try:
        abs_setup: str = os.path.join(root, "setup.py")
        setup_args: List[str] = ["sdist", "bdist_wheel"]
        print(f'{sys.executable} {abs_setup} {" ".join(setup_args)}')
        run_setup(abs_setup, setup_args)
    finally:
        os.chdir(current_directory)
    return _list_dist(root, modified_at_or_after=start_time)


def _get_help() -> bool:
    """
    If `-h` or `--help` keyword arguments are provided,
    retrieve the repository credentials and store them in the "TWINE_USERNAME"
    and "TWINE_PASSWORD" environment variables.
    """
    if set(sys.argv) & {"-h", "--help", "-H", "--HELP"}:
        help_: str = run(f"{sys.executable} -m twine upload -h", echo=False)
        help_ = re.sub(
            r"\btwine upload\b( \[-h\])?",
            (
                "daves-dev-tools distribute\\1 "
                "[-cu CERBERUS_URL]\n"
                "                    [-cup CERBERUS_USERNAME_PATH]\n"
                "                    [-cpp CERBERUS_PASSWORD_PATH]\n"
                "                   "
            ),
            help_,
        )
        help_ = (
            f"{help_.rstrip()}\n"
            "  -cu CERBERUS_URL, --cerberus-url CERBERUS_URL\n"
            "                        The base URL of a Cerberus REST API.\n"
            "                        See: https://swoo.sh/3DBW2Vb\n"
            "  -cup CERBERUS_USERNAME_PATH, --cerberus-username-path "
            "CERBERUS_USERNAME_PATH\n"
            "                        A Cerberus secure data path (including "
            "/key) wherein a\n"
            "                        username with which to authenticate can "
            "be found.\n"
            "                        See: https://swoo.sh/3DBW2Vb\n"
            "  -cpp CERBERUS_PASSWORD_PATH, --cerberus-password-path "
            "CERBERUS_PASSWORD_PATH\n"
            "                        A Cerberus secure data path (including "
            "/key) wherein a\n"
            "                        password with which to authenticate can "
            "be found.\n"
            "                        If no USERNAME or CERBERUS_USERNAME_PATH "
            "is provided,\n"
            "                        the last part of this path \n"
            "                        (the secure data path entry key) is "
            "inferred as your\n"
            "                        username. See: https://swoo.sh/3DBW2Vb\n"
        )
        print(help_)
        return True
    return False


def _get_credentials_from_cerberus() -> None:
    """
    If `--cerberus-url` and `--cerberus-path` keyword arguments are provided,
    retrieve the repository credentials and apply them to their corresponding
    static arguments.
    """
    # If this package was not installed with the [cerberus] option, none
    # this function is not applicable
    if apply_sys_argv_cerberus_arguments is None:
        return
    cerberus_password_path_keywords: Tuple[str, str, str, str] = (
        "-cpp",
        "--cerberus-password-path",
        # For backwards compatibility
        "-cp",
        "--cerberus-path",
    )
    username: Optional[str] = sys_argv_get(  # type: ignore
        ("-u", "--username")
    )
    cerberus_password_path: Optional[str] = sys_argv_get(  # type: ignore
        cerberus_password_path_keywords
    )
    if cerberus_password_path:
        cerberus_password_path = cerberus_password_path.strip("/ ")
        cerberus_password_path_list: List[str] = cerberus_password_path.split(
            "/"
        )
        path_length: int = len(cerberus_password_path_list)
        if path_length == 3 and username:
            # Append the SDB key
            sys_argv_pop(cerberus_password_path_keywords, flag=False)
            sys.argv += [
                cerberus_password_path_keywords[0],
                f"{cerberus_password_path}/{username}",
            ]
        elif path_length == 4:
            if not username:
                # Infer the username to be the SDB key
                sys.argv += ["-u", cerberus_password_path_list[-1]]
        else:
            raise ValueError(
                "The value for -cpp or --cerberus-password-path must be "
                "formatted either as:\n"
                '- "namespace/safe-deposit-box/secret" '
                "(if a `--username` is provided) or\n"
                '- "namespace/safe-deposit-box/secret/key"\n'
                f"...not: {repr(cerberus_password_path)}"
            )
    apply_sys_argv_cerberus_arguments(
        ("-cu", "--cerberus-url"),
        {
            "-u": ("-cup", "--cerberus-username-path"),
            "-p": cerberus_password_path_keywords,
        },
    )


def _dist(root: str, distributions: FrozenSet[str], echo: bool = True) -> None:
    run_module_as_main(
        "twine",
        arguments=(["upload"] + sys.argv[1:] + list(sorted(distributions))),
        directory=root,
        echo=False,
    )


def _cleanup(root: str) -> None:
    current_directory: str = os.path.abspath(os.path.curdir)
    os.chdir(root)
    try:
        run_setup(os.path.join(root, "setup.py"), ["clean", "--all"])
    finally:
        os.chdir(current_directory)


def main() -> None:
    if not _get_help():
        _get_credentials_from_cerberus()
        root = sys_argv_pop(depth=2, default=".")  # type: ignore
        root = os.path.abspath(root).rstrip("/")
        try:
            _dist(root, _setup(root))
        finally:
            _cleanup(root)


if __name__ == "__main__":
    main()
