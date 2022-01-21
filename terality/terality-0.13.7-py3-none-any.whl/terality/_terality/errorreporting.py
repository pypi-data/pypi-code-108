import os
from typing import List, Tuple
from terality._terality.httptransport import HttpTransport
import inspect
from inspect import FrameInfo
import traceback
import pathlib

from common_client_scheduler.requests import ClientErrorContext

from .constants import TERALITY_DISABLE_TELEMETRY_ENV_VAR


class ErrorReporter:
    """Reports errors (with context) to the Terality API.

    As a companion to Sentry error reporting, we add our own error reporter with a different focus:
    * we control our server-side sampling strategy
    * we can set our own limits on the metadata sent by this class

    This class is much less powerful than Sentry, and it's not obvious we'll keep it in the long run (this
    will depends on how our error reporting needs evolve). When adding metadata to errors, always consider
    adding them to Sentry events instead.
    """

    def __init__(self, http_transport: HttpTransport):
        self._http_transport = http_transport

    def report_exception(self, e: Exception) -> None:
        """Report a client exception to Terality servers.

        This method will retry to retrieve the code of the client module (whether running in a Python
        interpreter, a REPL, or a Jupyter notebook) that triggered the error. It does so by inspecting
        the current stack frame, and finding the first parent frame that's not inside the terality module.
        This is not foolproof (the terality module could call into a third party lib that calls back to
        the terality module) but should cover most of the actual case encountered in actual user scripts.

        Args:
            e: the exception to report. The exception traceback itself is ignored (the current stack frame
            is used instead, see above).

        See:
            report_exception_noexcept
        """
        if os.environ.get(TERALITY_DISABLE_TELEMETRY_ENV_VAR, "0") == "1":
            return

        tb = e.__traceback__  # pylint: disable=invalid-name
        if tb is None or not _originates_from_terality_module(traceback.extract_tb(tb)):
            return

        if _is_ipython():
            name = "ipython"
            code = _get_ipython_history()
        else:
            name, code = _get_calling_module_name_and_code()

        module_error_context = ClientErrorContext(
            code=code, filename=name, exception_str=f"{type(e).__name__}: {str(e)}"
        )
        self._http_transport.request("errors/contexts", payload=module_error_context)

    def report_exception_noexcept(self, e: Exception) -> None:
        """Report a client exception to Terality servers.

        This method will not raise any Exception (or subclass thereof).

        Args:
            e: the exception to report
        """
        try:
            self.report_exception(e)
        except Exception:
            pass  # silently ignore exceptions during error reporting


def _get_terality_module_filesystem_root():
    root_path = pathlib.Path(__file__).parent.parent
    assert (root_path / "version.py").exists()  # sanity check
    return root_path


def _originates_from_terality_module(stack_summary: traceback.StackSummary) -> bool:
    terality_module_root = _get_terality_module_filesystem_root()
    for frame in stack_summary:
        if str(terality_module_root) in frame.filename:
            return True
    return False


def _get_first_non_terality_module_path_from_stack(stack: List[FrameInfo]) -> str:
    terality_module_root = _get_terality_module_filesystem_root()

    first_frame_outside_terality_module = None
    for frame in stack:
        if str(terality_module_root) not in frame.filename:
            first_frame_outside_terality_module = frame
            break

    assert first_frame_outside_terality_module is not None
    return first_frame_outside_terality_module.filename


def _is_ipython() -> bool:
    """Return true if the current execution environment is a IPython kernel.

    This will return true when Terality is called from a Jupyter notebook.
    """
    try:
        # IPython injects the `get_ipython` method in the namespace
        get_ipython()  # type: ignore # noqa # pylint: disable=undefined-variable
        return True
    except NameError:
        return False


def _get_calling_module_name_and_code() -> Tuple[str, str]:
    """Return the code of the first module that's not `terality` in the current call stack.

    Raise:
        FileNotFoundError: if the code from the calling module can't be read.
    """
    current_stack = inspect.stack()
    calling_module_path = _get_first_non_terality_module_path_from_stack(current_stack)
    with open(calling_module_path) as f:
        calling_module_code = f.read()
    return calling_module_path, calling_module_code


def _get_ipython_history() -> str:
    """Return the content of the last 500 cells (or lines) executed by a IPython kernel.

    Only includes the user input, not the cell output.
    """
    # `get_ipython` will be defined in a IPython (used by a Jupyter notebook) context
    # as a safety check, only get the last 500 cells ran by the user
    input_cells = get_ipython().user_ns["_ih"][  # type: ignore # noqa # pylint: disable=undefined-variable
        -500:
    ]
    # cells can contain "\n", so add our own explicit delimiter between cells ("\n".join(...) would
    # lose the cell boundary information)
    return "\n\n##~ Cell delimiter ~##\n\n".join(input_cells)
