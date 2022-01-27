# coding=utf-8
""" Utilities for the paralang_cli module """
import functools
import os
import shutil
import sys
from os import PathLike
from pathlib import Path
from typing import Union, Tuple, Optional, List

from paralang_base import (UserInputError, InternalError, InterruptError,
                      ParaCompilerError)
from paralang_base.compiler import CompileProcess, CompileResult
from paralang_base.util import decode_if_bytes, escape_ansi
from rich import get_console
from rich.progress import Progress

from . import RUNTIME_COMPILER
from .logging import (cli_get_rich_console as console, cli_log_traceback,
                      cli_print_abort_banner, cli_print_result_banner)

__all__ = [
    "cli_err_dir_already_exists",
    "cli_run_output_dir_validation",
    "cli_check_destination",
    "cli_resolve_path",
    "cli_keep_open_callback",
    "cli_abortable",
    "cli_escape_ansi_args",
    'cli_create_process',
    'cli_run_process_with_logging',
]


def cli_abortable(
        _func=None,
        *,
        reraise: bool,
        preserve_exception: bool = False,
        abort_on_internal_errors: bool = False,
        print_abort: bool = True,
        step: str = "Process"
):
    """
    Marks the function as abortable and adds traceback logging to it.

    Raised InterruptError will close the program entirely!

    :param _func: Function to apply the decorator
    :param reraise: If set to True, any exception will be reraised. If False,
     it will close the program and write the error onto the console.
    :param preserve_exception: If set to True, the original exception will be
     returned and not the wrapped exception using InternalError or
     InterruptError
    :param abort_on_internal_errors: If set to True when receiving an
     InternalError it will treat it as a call for aborting the process. This
     means it will stop the program and print the abort banner if print_abort
     is True.
    :param print_abort: If True, it will print the abort banner when closing
    :param step: The step that should be passed onto print_abort_banner.
     Only valid argument when print_abort is True
    """

    def _decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            def _handle_abort(print_out: bool):
                if print_out:
                    cli_print_abort_banner(step)
                exit(1)

            try:
                from . import RUNTIME_COMPILER
                try:
                    return func(*args, **kwargs)
                except InterruptError:
                    _handle_abort(print_abort)

                except KeyboardInterrupt as e:
                    if preserve_exception:
                        raise e
                    else:
                        raise InterruptError(exc=e) from e

                except ParaCompilerError as e:
                    if not RUNTIME_COMPILER.is_cli_logger_ready:
                        RUNTIME_COMPILER.init_cli_logging()

                    cli_log_traceback(
                        level="critical",
                        brief="Encountered unexpected exception while running",
                        exc_info=sys.exc_info()
                    )
                    if preserve_exception:
                        raise e
                    else:
                        raise InterruptError(exc=e) from e

                except Exception as e:
                    if not RUNTIME_COMPILER.is_cli_logger_ready:
                        RUNTIME_COMPILER.init_cli_logging()

                    if preserve_exception:
                        raise e
                    else:
                        raise InternalError(
                            "Encountered unexpected exception while running",
                            exc=e
                        ) from e

            except Exception as e:
                if abort_on_internal_errors and type(e) is InternalError:
                    _handle_abort(print_abort)
                elif reraise:
                    raise e
                else:
                    _handle_abort(print_abort)

        return _wrapper

    if _func is None:
        return _decorator
    else:
        return _decorator(_func)


@cli_abortable(step="Validating Output", reraise=True)
def cli_err_dir_already_exists(folder: Union[str, PathLike]) -> bool:
    """ Asks the user whether the build folder should be overwritten """
    _input = console().input(
        f"[bright_yellow] > [bright_white]The {folder} "
        "folder already exists. Overwrite data? (y\\N): "
    ).lower() == 'y'
    return _input


@cli_abortable(step="Setup", reraise=True, preserve_exception=True)
def cli_create_process(
        files: List[Union[str, bytes, PathLike, Path]],
        log_path: Union[str, bytes, PathLike, Path],
        encoding: str,
) -> CompileProcess:
    """
    Creates a compilation process, which can be used for compiling Para code
    and returns it.

    This will activate CLI logging and styling per default!
    """
    if not RUNTIME_COMPILER.is_cli_logger_ready:
        RUNTIME_COMPILER.init_cli_logging(log_path)

    return CompileProcess(
        files, os.getcwd(), encoding
    )


@cli_abortable(step="Compilation", reraise=True, preserve_exception=True)
async def cli_run_process(
        p: CompileProcess,
        log_path: Union[str, PathLike] = None
) -> CompileResult:
    """
    Runs the process and returns the finished compilation process
    Calls p.compile(), adds additional formatting and returns the result

    This will activate CLI logging and styling per default!
    """
    if not RUNTIME_COMPILER.is_cli_logger_ready:
        RUNTIME_COMPILER.init_cli_logging(log_path)

    finished_process = await p.compile()
    cli_print_result_banner()

    return finished_process


async def cli_run_process_with_logging(
        p: CompileProcess,
        log_path: Union[str, PathLike] = None
) -> CompileResult:
    """
    Runs the compilation process with console logs and formatting. This will
    add a progress bar to the console as well, showing the progress of the
    compilation.

    This will activate CLI logging and styling per default!
    """
    if not RUNTIME_COMPILER.is_cli_logger_ready:
        RUNTIME_COMPILER.init_cli_logging(log_path)

    finished_process: Optional[CompileResult] = None

    # Some testing for now
    with Progress(console=get_console(), refresh_per_second=30) as progress:
        max_progress = 100
        current_progress = 0
        main_task = progress.add_task(
            "[green]Processing...",
            total=max_progress
        )

        async for p, status, level, end in p.compile_gen():
            if end is not None:
                finished_process = end
                progress.update(main_task, advance=p - current_progress)
            else:
                RUNTIME_COMPILER.logger.log(level=level, msg=status)
                progress.update(main_task, advance=p - current_progress)
                current_progress = p

    get_console().print("\n", end="")
    cli_print_result_banner()
    return finished_process


def cli_resolve_path(path: Union[bytes, str, Path, PathLike]) -> str:
    """
    If the path is a pathlib.Path it will resolve it, including all symlinks
    and return it as a string, else it will be passed through decode_if_bytes,
    made to a pathlib.Path to resolve all symlinks and then returned as a
    string

    :raise UserInputError: If the inserted path can not be resolved due to an
    invalid format
    """
    if str(path).strip() == "":
        raise UserInputError("Path can not be empty")
    if type(path) in (bytes, str, PathLike):
        try:
            path = Path(decode_if_bytes(path))
        # pathlib.Path raised error -> Invalid path
        except Exception as e:
            raise UserInputError("Path is in an invalid format") from e
    return str(path.resolve())


def cli_check_destination(
        output_type: str,
        default_path: Union[str, PathLike],
        overwrite: bool,
        work_dir: Union[str, PathLike, Path] = os.getcwd()
) -> str:
    """
    Validates the destination and checks whether the specified output
    folder is available. If the folder already exists it will show a prompt
    to the user what should be done about the existing folder.

    :returns: The path to the folder
    """
    output = default_path
    if not os.path.exists(output):
        os.mkdir(output)
    elif len(os.listdir(output)) > 0:
        # If the overwrite is set to False then a prompt will appear
        if overwrite is False:
            overwrite = cli_err_dir_already_exists(output_type)

        if overwrite:
            shutil.rmtree(output)
            os.mkdir(output)
        else:
            counter = 2
            while os.path.exists(f"{work_dir}/{output_type}_{counter}"):
                counter += 1
            output = f"{work_dir}/{output_type}_{counter}"
            os.mkdir(output)
    return output


def cli_run_output_dir_validation(
        overwrite_build: bool,
        overwrite_dist: bool,
        work_dir: Union[str, PathLike, Path] = os.getcwd()
) -> Tuple[str, str]:
    """
    Validates whether the output folder /build/ and /dist/ can be used and
    creates a prompt if one of the folder already exists

    :param overwrite_build: If set to True if a build folder already exists
     it will be deleted and overwritten
    :param overwrite_dist: If set to True if a dist folder already exists
     it will be deleted and overwritten
    :param work_dir: Work Directory that should be used for the check
    """
    from paralang_base import const

    build_path = cli_check_destination(
        "build",
        default_path=const.DEFAULT_BUILD_PATH,
        overwrite=overwrite_build,
        work_dir=work_dir
    )
    dist_path = cli_check_destination(
        "dist",
        default_path=const.DEFAULT_DIST_PATH,
        overwrite=overwrite_dist,
        work_dir=work_dir
    )
    return build_path, dist_path


def cli_keep_open_callback(_func=None):
    """ Keeps the console open after finishing until the user presses a key """

    def _decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            keep_open = kwargs.pop('keep_open')
            r = func(*args, **kwargs)

            # If keep_open is True -> the user passed --keep_open as an option
            # then the console will stay open until a key is pressed
            if keep_open:
                console().print("\n", end="")
                console().input("Press any key to close the program ...")
                console().print("")
            return r

        return _wrapper

    if _func is None:
        return _decorator
    else:
        return _decorator(_func)


def cli_escape_ansi_args(_func):
    """
    Calls the function but removes ansi colouring on the args and kwargs on str
    items if it exists
    """

    def _decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            new_args = []
            for i in args:
                if type(i) is str:
                    new_args.append(escape_ansi(i))
                else:
                    new_args.append(i)

            new_kwargs = {}
            for key, value in kwargs.items():
                if type(value) is str:
                    value = escape_ansi(value)
                new_kwargs[key] = value

            return func(*new_args, **new_kwargs)

        return _wrapper

    if _func is None:
        return _decorator
    else:
        return _decorator(_func)
