"""test_log_verifier.py module."""

########################################################################
# Standard Library
########################################################################
import logging
import datetime
import re
import threading
from typing import Any, cast, Optional, Union

########################################################################
# Third Party
########################################################################
import pytest

########################################################################
# Local
########################################################################
from scottbrian_utils.diag_msg import get_formatted_call_sequence
from scottbrian_utils.log_verifier import LogVer
from scottbrian_utils.log_verifier import UnmatchedExpectedMessages
from scottbrian_utils.log_verifier import UnmatchedActualMessages
from scottbrian_utils.time_hdr import get_datetime_match_string

logger = logging.getLogger(__name__)

########################################################################
# type aliases
########################################################################
IntFloat = Union[int, float]
OptIntFloat = Optional[IntFloat]


########################################################################
# LogVer test exceptions
########################################################################
class ErrorTstLogVer(Exception):
    """Base class for exception in this module."""
    pass


########################################################################
# log_enabled_arg
########################################################################
log_enabled_arg_list = [True, False]


@pytest.fixture(params=log_enabled_arg_list)  # type: ignore
def log_enabled_arg(request: Any) -> bool:
    """Using enabled and disabled logging.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(bool, request.param)


########################################################################
# simple_str_arg
########################################################################
simple_str_arg_list = ['a', 'ab', 'a1', 'xyz123']


@pytest.fixture(params=simple_str_arg_list)  # type: ignore
def simple_str_arg(request: Any) -> str:
    """Using different string messages.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(str, request.param)


########################################################################
# number of log messages arg fixtures
########################################################################
num_msgs_arg_list = [0, 1, 2, 3]


@pytest.fixture(params=num_msgs_arg_list)  # type: ignore
def num_exp_msgs1(request: Any) -> int:
    """Using different number of messages.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(int, request.param)


@pytest.fixture(params=num_msgs_arg_list)  # type: ignore
def num_exp_msgs2(request: Any) -> int:
    """Using different number of messages.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(int, request.param)


@pytest.fixture(params=num_msgs_arg_list)  # type: ignore
def num_exp_msgs3(request: Any) -> int:
    """Using different number of messages.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(int, request.param)


@pytest.fixture(params=num_msgs_arg_list)  # type: ignore
def num_act_msgs1(request: Any) -> int:
    """Using different number of messages.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(int, request.param)


@pytest.fixture(params=num_msgs_arg_list)  # type: ignore
def num_act_msgs2(request: Any) -> int:
    """Using different number of messages.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(int, request.param)


@pytest.fixture(params=num_msgs_arg_list)  # type: ignore
def num_act_msgs3(request: Any) -> int:
    """Using different number of messages.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(int, request.param)


########################################################################
# TestLogVerExamples class
########################################################################
class TestLogVerExamples:
    """Test examples of LogVer."""

    ####################################################################
    # test_log_verifier_example1
    ####################################################################
    def test_log_verifier_example1(self,
                                   capsys: pytest.CaptureFixture[str],
                                   caplog: pytest.CaptureFixture[str]
                                   ) -> None:
        """Test log_verifier example1.

        Args:
            capsys: pytest fixture to capture print output
            caplog: pytest fixture to capture log output

        """
        # one message expected, one message logged
        t_logger = logging.getLogger('example_1')
        log_ver = LogVer(log_name='example_1')
        log_msg = 'hello'
        log_ver.add_msg(log_msg=log_msg)
        t_logger.debug(log_msg)
        log_results = log_ver.get_match_results(caplog)
        log_ver.print_match_results(log_results)
        log_ver.verify_log_results(log_results)

        expected_result = '\n'
        expected_result += '**********************************\n'
        expected_result += '* number expected log records: 1 *\n'
        expected_result += '* number expected unmatched  : 0 *\n'
        expected_result += '* number actual log records  : 1 *\n'
        expected_result += '* number actual unmatched    : 0 *\n'
        expected_result += '* number matched records     : 1 *\n'
        expected_result += '**********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* unmatched expected records    *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* unmatched actual records      *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* matched records               *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += "('example_1', 10, 'hello')\n"

        captured = capsys.readouterr().out

        assert captured == expected_result

    ####################################################################
    # test_log_verifier_example2
    ####################################################################
    def test_log_verifier_example2(self,
                                   capsys: pytest.CaptureFixture[str],
                                   caplog: pytest.CaptureFixture[str]
                                   ) -> None:
        """Test log_verifier example2.

        Args:
            capsys: pytest fixture to capture print output
            caplog: pytest fixture to capture log output

        """
        # two log messages expected, only one is logged
        t_logger = logging.getLogger('example_2')
        log_ver = LogVer(log_name='example_2')
        log_msg1 = 'hello'
        log_ver.add_msg(log_msg=log_msg1)
        log_msg2 = 'goodbye'
        log_ver.add_msg(log_msg=log_msg2)
        t_logger.debug(log_msg1)
        log_results = log_ver.get_match_results(caplog)
        log_ver.print_match_results(log_results)
        with pytest.raises(UnmatchedExpectedMessages):
            log_ver.verify_log_results(log_results)

        expected_result = '\n'
        expected_result += '**********************************\n'
        expected_result += '* number expected log records: 2 *\n'
        expected_result += '* number expected unmatched  : 1 *\n'
        expected_result += '* number actual log records  : 1 *\n'
        expected_result += '* number actual unmatched    : 0 *\n'
        expected_result += '* number matched records     : 1 *\n'
        expected_result += '**********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* unmatched expected records    *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += "('example_2', 10, 'goodbye')\n"
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* unmatched actual records      *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* matched records               *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += "('example_2', 10, 'hello')\n"

        captured = capsys.readouterr().out

        assert captured == expected_result

    ####################################################################
    # test_log_verifier_example3
    ####################################################################
    def test_log_verifier_example3(self,
                                   capsys: pytest.CaptureFixture[str],
                                   caplog: pytest.CaptureFixture[str]
                                   ) -> None:
        """Test log_verifier example3.

        Args:
            capsys: pytest fixture to capture print output
            caplog: pytest fixture to capture log output

        """
        # one message expected, two messages logged
        t_logger = logging.getLogger('example_3')
        log_ver = LogVer(log_name='example_3')
        log_msg1 = 'hello'
        log_ver.add_msg(log_msg=log_msg1)
        log_msg2 = 'goodbye'
        t_logger.debug(log_msg1)
        t_logger.debug(log_msg2)
        log_ver.print_match_results(
            log_results := log_ver.get_match_results(caplog))
        with pytest.raises(UnmatchedActualMessages):
            log_ver.verify_log_results(log_results)

        expected_result = '\n'
        expected_result += '**********************************\n'
        expected_result += '* number expected log records: 1 *\n'
        expected_result += '* number expected unmatched  : 0 *\n'
        expected_result += '* number actual log records  : 2 *\n'
        expected_result += '* number actual unmatched    : 1 *\n'
        expected_result += '* number matched records     : 1 *\n'
        expected_result += '**********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* unmatched expected records    *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* unmatched actual records      *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += "('example_3', 10, 'goodbye')\n"
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* matched records               *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += "('example_3', 10, 'hello')\n"

        captured = capsys.readouterr().out

        assert captured == expected_result

    ####################################################################
    # test_log_verifier_example4
    ####################################################################
    def test_log_verifier_example4(self,
                                   capsys: pytest.CaptureFixture[str],
                                   caplog: pytest.CaptureFixture[str]
                                   ) -> None:
        """Test log_verifier example4.

        Args:
            capsys: pytest fixture to capture print output
            caplog: pytest fixture to capture log output

        """
        # two log messages expected, two logged, one different
        # logged
        t_logger = logging.getLogger('example_4')
        log_ver = LogVer(log_name='example_4')
        log_msg1 = 'hello'
        log_ver.add_msg(log_msg=log_msg1)
        log_msg2a = 'goodbye'
        log_ver.add_msg(log_msg=log_msg2a)
        log_msg2b = 'see you soon'
        t_logger.debug(log_msg1)
        t_logger.debug(log_msg2b)
        log_ver.print_match_results(
            log_results := log_ver.get_match_results(caplog))
        with pytest.raises(UnmatchedExpectedMessages):
            log_ver.verify_log_results(log_results)

        expected_result = '\n'
        expected_result += '**********************************\n'
        expected_result += '* number expected log records: 2 *\n'
        expected_result += '* number expected unmatched  : 1 *\n'
        expected_result += '* number actual log records  : 2 *\n'
        expected_result += '* number actual unmatched    : 1 *\n'
        expected_result += '* number matched records     : 1 *\n'
        expected_result += '**********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* unmatched expected records    *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += "('example_4', 10, 'goodbye')\n"
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* unmatched actual records      *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += "('example_4', 10, 'see you soon')\n"
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* matched records               *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += "('example_4', 10, 'hello')\n"

        captured = capsys.readouterr().out

        assert captured == expected_result

    ####################################################################
    # test_log_verifier_example5
    ####################################################################
    def test_log_verifier_example5(self,
                                   capsys: pytest.CaptureFixture[str],
                                   caplog: pytest.CaptureFixture[str]
                                   ) -> None:
        """Test log_verifier example5 for add_msg.

        Args:
            capsys: pytest fixture to capture print output
            caplog: pytest fixture to capture log output

        """
        # add two log messages, each different level
        t_logger = logging.getLogger('add_msg')
        log_ver = LogVer('add_msg')
        log_msg1 = 'hello'
        log_msg2 = 'goodbye'
        log_ver.add_msg(log_msg=log_msg1)
        log_ver.add_msg(log_msg=log_msg2, log_level=logging.ERROR)
        t_logger.debug(log_msg1)
        t_logger.error(log_msg2)
        match_results = log_ver.get_match_results(caplog=caplog)
        log_ver.print_match_results(match_results)
        log_ver.verify_log_results(match_results)

        expected_result = '\n'
        expected_result += '**********************************\n'
        expected_result += '* number expected log records: 2 *\n'
        expected_result += '* number expected unmatched  : 0 *\n'
        expected_result += '* number actual log records  : 2 *\n'
        expected_result += '* number actual unmatched    : 0 *\n'
        expected_result += '* number matched records     : 2 *\n'
        expected_result += '**********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* unmatched expected records    *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* unmatched actual records      *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* matched records               *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += "('add_msg', 10, 'hello')\n"
        expected_result += "('add_msg', 40, 'goodbye')\n"

        captured = capsys.readouterr().out

        assert captured == expected_result


########################################################################
# TestLogVerBasic class
########################################################################
class TestLogVerBasic:
    """Test basic functions of LogVer."""

    ####################################################################
    # test_log_verifier_time_match
    ####################################################################
    def test_log_verifier_simple_match(self,
                                       simple_str_arg: str,
                                       capsys: pytest.CaptureFixture[str],
                                       caplog: pytest.CaptureFixture[str]
                                       ) -> None:
        """Test log_verifier time match.

        Args:
            simple_str_arg: string to use in the message
            capsys: pytest fixture to capture print output
            caplog: pytest fixture to capture log output
        """
        t_logger = logging.getLogger('simple_match')
        log_ver = LogVer(log_name='simple_match')

        log_ver.add_msg(log_msg=simple_str_arg)
        t_logger.debug(simple_str_arg)
        log_ver.print_match_results(
            log_results := log_ver.get_match_results(caplog))
        log_ver.verify_log_results(log_results)

        expected_result = '\n'
        expected_result += '**********************************\n'
        expected_result += '* number expected log records: 1 *\n'
        expected_result += '* number expected unmatched  : 0 *\n'
        expected_result += '* number actual log records  : 1 *\n'
        expected_result += '* number actual unmatched    : 0 *\n'
        expected_result += '* number matched records     : 1 *\n'
        expected_result += '**********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* unmatched expected records    *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* unmatched actual records      *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* matched records               *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += f"('simple_match', 10, '{simple_str_arg}')\n"

        captured = capsys.readouterr().out

        assert captured == expected_result

    ####################################################################
    # test_log_verifier_time_match
    ####################################################################
    def test_log_verifier_time_match(self,
                                     capsys: pytest.CaptureFixture[str],
                                     caplog: pytest.CaptureFixture[str]
                                     ) -> None:
        """Test log_verifier time match.

        Args:
            capsys: pytest fixture to capture print output
            caplog: pytest fixture to capture log output
        """
        t_logger = logging.getLogger('time_match')
        log_ver = LogVer(log_name='time_match')
        fmt_str = '%d %b %Y %H:%M:%S'

        match_str = get_datetime_match_string(fmt_str)
        time_str = datetime.datetime.now().strftime(fmt_str)

        exp_msg = f'the date and time is: {match_str}'
        act_msg = f'the date and time is: {time_str}'
        log_ver.add_msg(log_msg=exp_msg, log_name='time_match')
        t_logger.debug(act_msg)
        log_ver.print_match_results(
            log_results := log_ver.get_match_results(caplog))
        log_ver.verify_log_results(log_results)

        expected_result = '\n'
        expected_result += '**********************************\n'
        expected_result += '* number expected log records: 1 *\n'
        expected_result += '* number expected unmatched  : 0 *\n'
        expected_result += '* number actual log records  : 1 *\n'
        expected_result += '* number actual unmatched    : 0 *\n'
        expected_result += '* number matched records     : 1 *\n'
        expected_result += '**********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* unmatched expected records    *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* unmatched actual records      *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* matched records               *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        log_msg = f'the date and time is: {time_str}'
        expected_result += f"('time_match', 10, '{log_msg}')\n"

        captured = capsys.readouterr().out

        assert captured == expected_result

    ####################################################################
    # test_log_verifier_add_call_seq
    ####################################################################
    def test_log_verifier_add_call_seq(self,
                                       simple_str_arg: str,
                                       capsys: pytest.CaptureFixture[str],
                                       caplog: pytest.CaptureFixture[str]
                                       ) -> None:
        """Test log_verifier add_call_seq method.

        Args:
            simple_str_arg: string to use in the message
            capsys: pytest fixture to capture print output
            caplog: pytest fixture to capture log output
        """
        t_logger = logging.getLogger('call_seq')
        log_ver = LogVer(log_name='call_seq')

        log_ver.add_call_seq(name='alpha',
                             seq=simple_str_arg)
        log_ver.add_msg(log_msg=log_ver.get_call_seq('alpha'))
        t_logger.debug(f'{simple_str_arg}:{123}')
        log_ver.print_match_results(
            log_results := log_ver.get_match_results(caplog))
        log_ver.verify_log_results(log_results)

        expected_result = '\n'
        expected_result += '**********************************\n'
        expected_result += '* number expected log records: 1 *\n'
        expected_result += '* number expected unmatched  : 0 *\n'
        expected_result += '* number actual log records  : 1 *\n'
        expected_result += '* number actual unmatched    : 0 *\n'
        expected_result += '* number matched records     : 1 *\n'
        expected_result += '**********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* unmatched expected records    *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* unmatched actual records      *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* matched records               *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += f"('call_seq', 10, '{simple_str_arg}:{123}')\n"

        captured = capsys.readouterr().out

        assert captured == expected_result

    ####################################################################
    # test_log_verifier_add_call_seq2
    ####################################################################
    def test_log_verifier_add_call_seq2(self,
                                        simple_str_arg: str,
                                        capsys: pytest.CaptureFixture[str],
                                        caplog: pytest.CaptureFixture[str]
                                        ) -> None:
        """Test log_verifier add_call_seq method.

        Args:
            simple_str_arg: string to use in the message
            capsys: pytest fixture to capture print output
            caplog: pytest fixture to capture log output
        """
        t_logger = logging.getLogger('call_seq2')
        log_ver = LogVer(log_name='call_seq2')

        log_ver.add_call_seq(
            name='alpha',
            seq=('test_log_verifier.py::TestLogVerBasic'
                 '.test_log_verifier_add_call_seq2'))
        log_ver.add_msg(log_msg=log_ver.get_call_seq('alpha'))
        # t_logger.debug(f'{simple_str_arg}:{get_formatted_call_sequence()}')
        my_seq = get_formatted_call_sequence(depth=1)
        t_logger.debug(f'{my_seq}')
        log_ver.print_match_results(
            log_results := log_ver.get_match_results(caplog))
        log_ver.verify_log_results(log_results)

        expected_result = '\n'
        expected_result += '**********************************\n'
        expected_result += '* number expected log records: 1 *\n'
        expected_result += '* number expected unmatched  : 0 *\n'
        expected_result += '* number actual log records  : 1 *\n'
        expected_result += '* number actual unmatched    : 0 *\n'
        expected_result += '* number matched records     : 1 *\n'
        expected_result += '**********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* unmatched expected records    *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* unmatched actual records      *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* matched records               *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += f"('call_seq2', 10, '{my_seq}')\n"

        captured = capsys.readouterr().out

        assert captured == expected_result

    ####################################################################
    # test_log_verifier_add_call_seq3
    ####################################################################
    def test_log_verifier_add_call_seq3(self,
                                        simple_str_arg: str,
                                        capsys: pytest.CaptureFixture[str],
                                        caplog: pytest.CaptureFixture[str]
                                        ) -> None:
        """Test log_verifier add_call_seq method.

        Args:
            simple_str_arg: string to use in the message
            capsys: pytest fixture to capture print output
            caplog: pytest fixture to capture log output
        """
        t_logger = logging.getLogger('call_seq3')
        log_ver = LogVer(log_name='call_seq3')

        log_ver.add_call_seq(
            name='alpha',
            seq=('test_log_verifier.py::TestLogVerBasic'
                 '.test_log_verifier_add_call_seq3'))

        esc_thread_str = re.escape(f'{threading.current_thread()}')
        add_msg = (f'{esc_thread_str} '
                   f'{simple_str_arg} '
                   f'{log_ver.get_call_seq(name="alpha")}')
        log_ver.add_msg(log_msg=add_msg)

        log_msg = (f'{threading.current_thread()} '
                   f'{simple_str_arg} '
                   f'{get_formatted_call_sequence(depth=1)}')
        t_logger.debug(log_msg)

        log_ver.print_match_results(
            log_results := log_ver.get_match_results(caplog))
        log_ver.verify_log_results(log_results)

        expected_result = '\n'
        expected_result += '**********************************\n'
        expected_result += '* number expected log records: 1 *\n'
        expected_result += '* number expected unmatched  : 0 *\n'
        expected_result += '* number actual log records  : 1 *\n'
        expected_result += '* number actual unmatched    : 0 *\n'
        expected_result += '* number matched records     : 1 *\n'
        expected_result += '**********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* unmatched expected records    *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* unmatched actual records      *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* matched records               *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += f"('call_seq3', 10, '{log_msg}')\n"

        captured = capsys.readouterr().out

        assert captured == expected_result

    ####################################################################
    # test_log_verifier_no_log
    ####################################################################
    def test_log_verifier_no_log(self,
                                 log_enabled_arg: bool,
                                 capsys: pytest.CaptureFixture[str],
                                 caplog: pytest.CaptureFixture[str]
                                 ) -> None:
        """Test log_verifier with logging disabled and enabled.

        Args:
            log_enabled_arg: fixture to indicate whether log is enabled
            capsys: pytest fixture to capture print output
            caplog: pytest fixture to capture log output
        """
        t_logger = logging.getLogger('no_log')
        log_ver = LogVer(log_name='no_log')
        if log_enabled_arg:
            t_logger.setLevel(logging.DEBUG)
        else:
            t_logger.setLevel(logging.INFO)

        log_msg = f'the log_enabled_arg is: {log_enabled_arg}'
        log_ver.add_msg(log_msg=log_msg)
        t_logger.debug(log_msg)
        log_ver.print_match_results(
            log_results := log_ver.get_match_results(caplog))
        if log_enabled_arg:
            log_ver.verify_log_results(log_results)
        else:
            with pytest.raises(UnmatchedExpectedMessages):
                log_ver.verify_log_results(log_results)

        expected_result = '\n'
        expected_result += '**********************************\n'
        expected_result += '* number expected log records: 1 *\n'

        if log_enabled_arg:
            expected_result += '* number expected unmatched  : 0 *\n'
            expected_result += '* number actual log records  : 1 *\n'
        else:
            expected_result += '* number expected unmatched  : 1 *\n'
            expected_result += '* number actual log records  : 0 *\n'

        expected_result += '* number actual unmatched    : 0 *\n'

        if log_enabled_arg:
            expected_result += '* number matched records     : 1 *\n'
        else:
            expected_result += '* number matched records     : 0 *\n'

        expected_result += '**********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* unmatched expected records    *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        if not log_enabled_arg:
            expected_result += ("('no_log', "
                                "10, 'the log_enabled_arg is: False')\n")

        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* unmatched actual records      *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* matched records               *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'

        if log_enabled_arg:
            expected_result += ("('no_log', "
                                "10, 'the log_enabled_arg is: True')\n")

        captured = capsys.readouterr().out

        assert captured == expected_result


########################################################################
# TestLogVerBasic class
########################################################################
class TestLogVerCombos:
    """Test LogVer with various combinations."""

    ####################################################################
    # test_log_verifier_remaining_time1
    ####################################################################
    def test_log_verifier_combos(self,
                                 num_exp_msgs1: int,
                                 num_exp_msgs2: int,
                                 num_exp_msgs3: int,
                                 num_act_msgs1: int,
                                 num_act_msgs2: int,
                                 num_act_msgs3: int,
                                 capsys: pytest.CaptureFixture[str],
                                 caplog: pytest.CaptureFixture[str]
                                 ) -> None:
        """Test log_verifier combos.

        Args:
            num_exp_msgs1: number of expected messages for msg1
            num_exp_msgs2: number of expected messages for msg2
            num_exp_msgs3: number of expected messages for msg3
            num_act_msgs1: number of actual messages for msg1
            num_act_msgs2: number of actual messages for msg2
            num_act_msgs3: number of actual messages for msg3
            capsys: pytest fixture to capture print output
            caplog: pytest fixture to capture log output

        """
        t_logger = logging.getLogger('combos')
        log_ver = LogVer(log_name='combos')

        total_num_exp_msgs = 0
        total_num_act_msgs = 0
        total_num_exp_unmatched = 0
        total_num_act_unmatched = 0
        total_num_matched = 0

        exp_unmatched_msgs = []
        act_unmatched_msgs = []
        matched_msgs = []

        msg_table = [(num_exp_msgs1, num_act_msgs1, 'msg one'),
                     (num_exp_msgs2, num_act_msgs2, 'msg two'),
                     (num_exp_msgs3, num_act_msgs3, 'msg three')]

        for num_exp, num_act, the_msg in msg_table:
            total_num_exp_msgs += num_exp
            total_num_act_msgs += num_act
            num_exp_unmatched = max(0, num_exp - num_act)
            total_num_exp_unmatched += num_exp_unmatched
            num_act_unmatched = max(0, num_act - num_exp)
            total_num_act_unmatched += num_act_unmatched
            num_matched_msgs = num_exp - num_exp_unmatched
            total_num_matched += num_matched_msgs

            for _ in range(num_exp):
                log_ver.add_msg(log_msg=the_msg)

            for _ in range(num_act):
                t_logger.debug(the_msg)

            for _ in range(num_exp_unmatched):
                exp_unmatched_msgs.append(the_msg)

            for _ in range(num_act_unmatched):
                act_unmatched_msgs.append(the_msg)

            for _ in range(num_matched_msgs):
                matched_msgs.append(the_msg)

        max_of_totals = max(total_num_exp_msgs,
                            total_num_act_msgs,
                            total_num_exp_unmatched,
                            total_num_act_unmatched,
                            total_num_matched)

        len_max_total = len(str(max_of_totals))
        asterisks = '*********************************' + '*' * len_max_total

        num_exp_space = len_max_total - len(str(total_num_exp_msgs))
        num_exp_unm_space = len_max_total - len(str(total_num_exp_unmatched))
        num_act_space = len_max_total - len(str(total_num_act_msgs))
        num_act_unm_space = len_max_total - len(str(total_num_act_unmatched))
        num_matched_space = len_max_total - len(str(total_num_matched))

        log_ver.print_match_results(
            log_results := log_ver.get_match_results(caplog))

        if total_num_exp_unmatched:
            with pytest.raises(UnmatchedExpectedMessages):
                log_ver.verify_log_results(log_results)
        elif total_num_act_unmatched:
            with pytest.raises(UnmatchedActualMessages):
                log_ver.verify_log_results(log_results)
        else:
            log_ver.verify_log_results(log_results)

        expected_result = '\n'
        expected_result += asterisks + '\n'
        expected_result += ('* number expected log records: '
                            + ' ' * num_exp_space
                            + f'{total_num_exp_msgs} *\n')
        expected_result += ('* number expected unmatched  : '
                            + ' ' * num_exp_unm_space
                            + f'{total_num_exp_unmatched} *\n')
        expected_result += ('* number actual log records  : '
                            + ' ' * num_act_space
                            + f'{total_num_act_msgs} *\n')
        expected_result += ('* number actual unmatched    : '
                            + ' ' * num_act_unm_space
                            + f'{total_num_act_unmatched} *\n')
        expected_result += ('* number matched records     : '
                            + ' ' * num_matched_space
                            + f'{total_num_matched} *\n')
        expected_result += asterisks + '\n'
        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* unmatched expected records    *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'

        for msg in exp_unmatched_msgs:
            expected_result += f"('combos', 10, '{msg}')\n"

        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* unmatched actual records      *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'

        for msg in act_unmatched_msgs:
            expected_result += f"('combos', 10, '{msg}')\n"

        expected_result += '\n'
        expected_result += '*********************************\n'
        expected_result += '* matched records               *\n'
        expected_result += '* (logger name, level, message) *\n'
        expected_result += '*********************************\n'

        for msg in matched_msgs:
            expected_result += f"('combos', 10, '{msg}')\n"

        captured = capsys.readouterr().out

        assert captured == expected_result
