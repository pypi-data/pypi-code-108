"""conftest.py module for testing."""

########################################################################
# Standard Library
########################################################################
import logging
import threading
import traceback
from typing import Any, Generator, Optional, Union

########################################################################
# Third Party
########################################################################
import pytest

########################################################################
# Local
########################################################################

########################################################################
# type aliases
########################################################################
OptIntFloat = Optional[Union[int, float]]

########################################################################
# logging
########################################################################
logging.basicConfig(filename='Lock.log',
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
# For tox, the above specification goes into tox.ini in the
# the string for the commands=
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
# thread_exc, any uncaptured thread failures will appear in the output,
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
        """Raise an error is we have one.

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
        exc_err_msg = (f'thread_exc excepthook: {args.exc_type}, '
                       f'{args.exc_value}, {args.exc_traceback},'
                       f' {args.thread}')
        traceback.print_tb(args.exc_traceback)
        logger.debug(exc_err_msg)
        current_thread = threading.current_thread()
        logger.debug(f'excepthook current thread is {current_thread}')
        # ExcHook.exc_err_msg1 = exc_err_msg
        exc_hook.exc_err_msg1 = exc_err_msg
        raise Exception(f'thread_exc thread test error: {exc_err_msg}')

    monkeypatch.setattr(threading, "excepthook", mock_threading_excepthook)
    logger.debug(f'hook after: {threading.excepthook}')
    new_hook = threading.excepthook

    yield exc_hook

    # clean the registry in SELock class
    # SELock._registry = {}

    # clean the registry in ThreadPair class
    # ThreadPair._registry = {}

    # the following check ensures that the test case waited via join for
    # any started threads to come home
    assert threading.active_count() == 1
    exc_hook.raise_exc_if_one()

    # the following assert ensures -p no:threadexception was specified
    assert threading.excepthook == new_hook


########################################################################
# ExpLogMsg class
########################################################################
# class ExpLogMsgs:
#     """Expected Log Messages Class."""
#
#     def __init__(self,
#                  alpha_call_seq: str,
#                  beta_call_seq: str) -> None:
#         """Initialize object.
#
#         Args:
#              alpha_call_seq: expected alpha call seq for log messages
#              beta_call_seq: expected beta call seq for log messages
#
#         """
#         self.exp_alpha_call_seq = alpha_call_seq + ':[0-9]* '
#         self.exp_beta_call_seq = beta_call_seq + ':[0-9]* '
#         self.pair_with_req = r'pair_with\(\) '
#         self.sync_req = r'sync\(\) '
#         self.resume_req = r'resume\(\) '
#         self.wait_req = r'wait\(\) '
#         self.entered_str = 'entered '
#         self.with_code = 'with code: '
#         self.exit_str = 'exiting with ret_code '
#         self.expected_messages = []
#
#     def add_req_msg(self,
#                     l_msg: str,
#                     who: str,
#                     req: str,
#                     ret_code: Optional[bool] = None,
#                     code: Optional[Any] = None,
#                     pair: Optional[list[str]] = None,
#                     group_name: Optional[str] = 'group1'
#                     ) -> None:
#         """Add an expected request message to the expected log messages.
#
#         Args:
#             l_msg: message to add
#             who: either 'alpha or 'beta'
#             req: one of 'pair_with', 'sync', 'resume', or 'wait'
#             ret_code: bool
#             code: code for resume or None
#             pair: names the two threads that are in the paired log
#                     message
#
#         """
#         l_enter_msg = req + r'\(\) entered '
#         if code is not None:
#             l_enter_msg += f'with code: {code} '
#         if pair is not None:
#             l_enter_msg += (f'by {pair[0]} to pair with {pair[1]} '
#                             f'in group {group_name}. ')
#
#         l_exit_msg = req + r'\(\) exiting with ret_code '
#         if ret_code is not None:
#             if ret_code:
#                 l_exit_msg += 'True '
#             else:
#                 l_exit_msg += 'False '
#
#         if pair is not None:
#             l_exit_msg = (req + r'\(\)' + f' exiting - {pair[0]} now '
#                                           f'paired with {pair[1]}. ')
#
#         if who == 'alpha':
#             l_enter_msg += self.exp_alpha_call_seq + l_msg
#             l_exit_msg += self.exp_alpha_call_seq + l_msg
#         else:
#             l_enter_msg += self.exp_beta_call_seq + l_msg
#             l_exit_msg += self.exp_beta_call_seq + l_msg
#
#         self.expected_messages.append(re.compile(l_enter_msg))
#         self.expected_messages.append(re.compile(l_exit_msg))
#
#     def add_msg(self, l_msg: str) -> None:
#         """Add a general message to the expected log messages.
#
#         Args:
#             l_msg: message to add
#         """
#         self.expected_messages.append(re.compile(l_msg))
#
#     def add_alpha_pair_with_msg(self,
#                                 l_msg: str,
#                                 pair: list[str]) -> None:
#         """Add alpha pair with message to expected log messages.
#
#         Args:
#             l_msg: log message to add
#             pair: the paired by and paired to names
#
#         """
#         self.add_req_msg(l_msg=l_msg,
#                          who='alpha',
#                          req='pair_with',
#                          pair=pair)
#
#     def add_alpha_sync_msg(self,
#                            l_msg: str,
#                            ret_code: Optional[bool] = True) -> None:
#         """Add alpha sync message to expected log messages.
#
#         Args:
#             l_msg: log message to add
#             ret_code: True or False
#
#         """
#         self.add_req_msg(l_msg=l_msg,
#                          who='alpha',
#                          req='sync',
#                          ret_code=ret_code)
#
#     def add_alpha_resume_msg(self,
#                              l_msg: str,
#                              ret_code: Optional[bool] = True,
#                              code: Optional[Any] = None) -> None:
#         """Add alpha resume message to expected log messages.
#
#         Args:
#             l_msg: log message to add
#             ret_code: True or False
#             code: code to add to message
#
#         """
#         self.add_req_msg(l_msg=l_msg,
#                          who='alpha',
#                          req='resume',
#                          ret_code=ret_code,
#                          code=code)
#
#     def add_alpha_wait_msg(self,
#                            l_msg: str,
#                            ret_code: Optional[bool] = True) -> None:
#         """Add alpha wait message to expected log messages.
#
#         Args:
#             l_msg: log message to add
#             ret_code: True or False
#
#         """
#         self.add_req_msg(l_msg=l_msg,
#                          who='alpha',
#                          req='wait',
#                          ret_code=ret_code)
#
#     def add_beta_pair_with_msg(self,
#                                l_msg: str,
#                                pair: list[str]) -> None:
#         """Add beta pair with message to expected log messages.
#
#         Args:
#             l_msg: log message to add
#             pair: the paired by and paired to names
#
#         """
#         self.add_req_msg(l_msg=l_msg,
#                          who='beta',
#                          req='pair_with',
#                          pair=pair)
#
#     def add_beta_sync_msg(self,
#                           l_msg: str,
#                           ret_code: Optional[bool] = True) -> None:
#         """Add beta sync message to expected log messages.
#
#         Args:
#             l_msg: log message to add
#             ret_code: True or False
#
#         """
#         self.add_req_msg(l_msg=l_msg,
#                          who='beta',
#                          req='sync',
#                          ret_code=ret_code)
#
#     def add_beta_resume_msg(self,
#                             l_msg: str,
#                             ret_code: Optional[bool] = True,
#                             code: Optional[Any] = None) -> None:
#         """Add beta resume message to expected log messages.
#
#         Args:
#             l_msg: log message to add
#             ret_code: True or False
#             code: code to add to message
#
#         """
#         self.add_req_msg(l_msg=l_msg,
#                          who='beta',
#                          req='resume',
#                          ret_code=ret_code,
#                          code=code)
#
#     def add_beta_wait_msg(self,
#                           l_msg: str,
#                           ret_code: Optional[bool] = True) -> None:
#         """Add beta wait message to expected log messages.
#
#         Args:
#             l_msg: log message to add
#             ret_code: True or False
#
#         """
#         self.add_req_msg(l_msg=l_msg,
#                          who='beta',
#                          req='wait',
#                          ret_code=ret_code)
#
#     ####################################################################
#     # verify log messages
#     ####################################################################
#     def verify_log_msgs(self,
#                         caplog: Any,
#                         log_enabled_tf: bool) -> None:
#         """Verify that each log message issued is as expected.
#
#         Args:
#             caplog: pytest fixture that captures log messages
#             log_enabled_tf: indicated whether log is enabled
#
#         """
#         num_log_records_found = 0
#         log_records_found = []
#         caplog_recs = []
#         for record in caplog.records:
#             caplog_recs.append(record.msg)
#
#         for idx, record in enumerate(caplog.records):
#             # print(record.msg)
#             # print(self.exp_log_msgs)
#             for idx2, l_msg in enumerate(self.expected_messages):
#                 if l_msg.match(record.msg):
#                     # print(l_msg.match(record.msg))
#                     self.expected_messages.pop(idx2)
#                     caplog_recs.remove(record.msg)
#                     log_records_found.append(record.msg)
#                     num_log_records_found += 1
#                     break
#
#         print(f'\nnum_log_records_found: '
#               f'{num_log_records_found} of {len(caplog.records)}')
#
#         print(('*' * 8) + ' matched log records found ' + ('*' * 8))
#         for log_msg in log_records_found:
#             print(log_msg)
#
#         print(('*' * 8) + ' remaining unmatched log records ' + ('*' * 8))
#         for log_msg in caplog_recs:
#             print(log_msg)
#
#         print(('*' * 8) + ' remaining expected log records ' + ('*' * 8))
#         for exp_lm in self.expected_messages:
#             print(exp_lm)
#
#         if log_enabled_tf:
#             assert not self.expected_messages
#             assert num_log_records_found == len(caplog.records)
#         else:
#             assert self.expected_messages
#             assert num_log_records_found == 0
