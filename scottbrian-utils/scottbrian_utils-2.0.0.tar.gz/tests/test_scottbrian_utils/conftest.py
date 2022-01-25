"""conftest.py module for testing."""

import threading
import traceback
import pytest
from typing import Any, cast, Generator

import logging

########################################################################
# logging
########################################################################
logging.basicConfig(filename='MyLogFile.log',
                    filemode='w',
                    level=logging.DEBUG,
                    format='%(asctime)s '
                           '[%(levelname)8s] '
                           '%(filename)s:'
                           '%(funcName)s:'
                           '%(lineno)d '
                           '%(message)s')

logger = logging.getLogger(__name__)


########################################################################
# Thread exceptions
# The following fixture depends on the following pytest specification:
# -p no:threadexception

# For PyCharm, the above specification goes into field Additional
# Arguments found at Run -> edit configurations
#
# For tox, the above specification goes into tox.ini in the string for
# the commands=
# For example, in tox.ini for the pytest section:
# [testenv:py{36, 37, 38, 39}-pytest]
# description = invoke pytest on the package
# deps =
#     pytest
#
# commands =
#     pytest --import-mode=importlib -p no:threadexception {posargs}
#
# Usage:
# The thread_exc is an autouse fixture which means it does not need to
# be specified as an argument in the test case methods. If a thread
# fails, such as an assert error, then thread_exc will capture the error
# and raise it for the thread, and will also raise it during cleanup
# processing for the mainline to ensure the test case fails. Without
# thread_exc, any uncaptured thread failure will appear in the output,
# but the test case itself will not fail.
# Also, if you need to issue the thread error earlier, before cleanup,
# then specify thread_exc as an argument on the test method and then in
# mainline issue:
#     thread_exc.raise_exc_if_one()
#
# When the above is done, cleanup will not raise the error again.
#
########################################################################
class ExcHook:
    """ExcHook class."""

    def __init__(self) -> None:
        """Initialize the ExcHook class instance."""
        self.exc_err_msg1 = ''

    def raise_exc_if_one(self) -> None:
        """Raise and error is we have one.

        Raises:
            Exception: exc_msg

        """
        if self.exc_err_msg1:
            exc_msg = self.exc_err_msg1
            self.exc_err_msg1 = ''
            raise Exception(f'{exc_msg}')


@pytest.fixture(autouse=True)  # type: ignore
def thread_exc(monkeypatch: Any) -> Generator[ExcHook, None, None]:
    """Instantiate and return a ThreadExc for testing.

    Args:
        monkeypatch: pytest fixture used to modify code for testing

    Yields:
        a thread exception handler

    """
    # class ExcHook:
    #     """ExcHook class."""
    #     def __init__(self) -> None:
    #         """Initialize the ExcHook class instance."""
    #         self.exc_err_msg1 = ''
    #
    #     def raise_exc_if_one(self) -> None:
    #         """Raise and error is we have one.
    #
    #         Raises:
    #             Exception: exc_msg
    #
    #         """
    #         if self.exc_err_msg1:
    #             exc_msg = self.exc_err_msg1
    #             self.exc_err_msg1 = ''
    #             raise Exception(f'{exc_msg}')

    logger.debug(f'hook before: {threading.excepthook}')
    exc_hook = ExcHook()

    def mock_threading_excepthook(args: Any) -> None:
        """Build error message from exception.

        Args:
            args: contains:
                      args.exc_type: Optional[Type[BaseException]]
                      args.exc_value: Optional[BaseException]
                      args.exc_traceback: Optional[TracebackType]

        Raises:
            Exception: Test case thread test error

        """
        exc_err_msg = (f'Test case excepthook: {args.exc_type}, '
                       f'{args.exc_value}, {args.exc_traceback},'
                       f' {args.thread}')
        traceback.print_tb(args.exc_traceback)
        logger.debug(exc_err_msg)
        current_thread = threading.current_thread()
        logger.debug(f'excepthook current thread is {current_thread}')
        # ExcHook.exc_err_msg1 = exc_err_msg
        exc_hook.exc_err_msg1 = exc_err_msg
        raise Exception(f'Test case thread test error: {exc_err_msg}')

    monkeypatch.setattr(threading, "excepthook", mock_threading_excepthook)
    logger.debug(f'hook after: {threading.excepthook}')
    new_hook = threading.excepthook

    yield exc_hook
    exc_hook.raise_exc_if_one()

    # the following assert ensures -p no:threadexception was specified
    assert threading.excepthook == new_hook


########################################################################
# dt_format_arg_list
########################################################################
dt_format_arg_list = [None,
                      '%H:%M',
                      '%H:%M:%S',
                      '%m/%d %H:%M:%S',
                      '%b %d %H:%M:%S',
                      '%m/%d/%y %H:%M:%S',
                      '%m/%d/%Y %H:%M:%S',
                      '%b %d %Y %H:%M:%S',
                      '%a %b %d %Y %H:%M:%S',
                      '%a %b %d %H:%M:%S.%f',
                      '%A %b %d %H:%M:%S.%f',
                      '%A %B %d %H:%M:%S.%f'
                      ]


@pytest.fixture(params=dt_format_arg_list)  # type: ignore
def dt_format_arg(request: Any) -> str:
    """Using different time formats.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(str, request.param)


# from scottbrian_algo1.diag_msg import DiagMsg
# # from threading import Thread  #, Event
# from datetime import datetime
# import time
#
#
# # def ptm(*args, **kwargs):
# #     """return time.
# #
# #     Returns:
# #         time as str
# #     """
# #     current_time = datetime.now()
# #     strtime = current_time.strftime("%H:%M:%S.%f")
# #     a, *b = args
# #     a = strtime + ' ' + str(a)
# #     print(a, *b, **kwargs)
# #     return
#
#
# class TAlgoApp(AlgoApp):
#     def __init__(self):
#         """TAlgoApp init."""
#
#         # ptm('SBT TAlgoApp:__init__ entered')
#         AlgoApp.__init__(self)
#         # self.run_thread = Thread(target=self.run)
#         # ptm('SBT TAlgoApp:__init__ exiting')
#
#     def run(self):
#         ptm( 'SBT TAlgoApp: run entered')
#         for i in range(5):
#             time.sleep(1)
#             if i == 3:
#                 ptm('SBT TAlgoApp: about to call nextValidId')
#                 self.nextValidId(1)
#
#
#
# @pytest.fixture(scope='session')
# def diag_msg() -> "AlgoApp":
#     """Instantiate and return an AlgoApp for testing.
#
#     Returns:
#         An instance of AlgoApp
#     """
#     a_algo_app = TAlgoApp()
#     return a_algo_app
