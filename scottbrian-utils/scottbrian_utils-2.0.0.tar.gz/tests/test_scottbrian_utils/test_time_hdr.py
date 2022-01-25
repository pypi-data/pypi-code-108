"""test_time_hdr.py module."""

########################################################################
# Standard Library
########################################################################
from datetime import datetime, timedelta, timezone
import logging
import re
import sys

from typing import Any, Callable, cast, Tuple, Union
from typing_extensions import Final

########################################################################
# Third Party
########################################################################
import pytest

########################################################################
# Local
########################################################################
from scottbrian_utils.time_hdr import StartStopHeader as StartStopHeader
from scottbrian_utils.time_hdr import time_box as time_box
from scottbrian_utils.time_hdr import DT_Format as DT_Format
from scottbrian_utils.time_hdr import get_datetime_match_string

logger = logging.getLogger(__name__)


class ErrorTstTimeHdr(Exception):
    """Base class for exception in this module."""
    pass


class InvalidRouteNum(ErrorTstTimeHdr):
    """InvalidRouteNum exception class."""
    pass


dt_format_arg_list = ['0',
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


dt_format_char_arg_list = ['',
                           '%a',
                           '%A',
                           '%w',
                           '%d',
                           '%b',
                           '%B',
                           '%m',
                           '%y',
                           '%Y',
                           '%H',
                           '%I',
                           '%p',
                           '%M',
                           '%S',
                           '%f',
                           '%z',
                           '%Z'
                           '%j',
                           '%U',
                           '%W',
                           '%c',
                           '%x',
                           '%X',
                           '%%',
                           '%G',
                           '%u',
                           '%V']


@pytest.fixture(params=dt_format_char_arg_list)  # type: ignore
def dt_format_char_arg(request: Any) -> str:
    """Using different time formats.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(str, request.param)


dt_datetime_arg_list = [datetime(1999,  1,  1,  0,  0,  0,  0,
                                 tzinfo=timezone.utc
                                 ),
                        datetime(2000,  2,  2,  1,  1,  1,  1,
                                 tzinfo=timezone.utc
                                 ),
                        datetime(2001,  3,  9,  9,  9,  9,  9,
                                 tzinfo=timezone(timedelta(hours=-23,
                                                           minutes=-59))
                                 ),
                        datetime(2002,  4, 10, 10, 10, 10, 10,
                                 tzinfo=timezone(timedelta(hours=-23))
                                 ),
                        datetime(2009,  5, 11, 11, 11, 11, 11,
                                 tzinfo=timezone(timedelta(hours=-5))
                                 ),
                        datetime(2010,  6, 19, 19, 19, 19, 19,
                                 tzinfo=timezone(timedelta(hours=-5)),
                                 ),
                        datetime(2011,  7, 20, 20, 20, 20, 20,
                                 tzinfo=timezone(timedelta(hours=0))
                                 ),
                        datetime(2019,  9, 21, 21, 21, 21, 21,
                                 tzinfo=timezone(timedelta(minutes=1))
                                 ),
                        datetime(2020, 10, 29, 22, 29, 29, 29,
                                 tzinfo=timezone(timedelta(hours=1))
                                 ),
                        datetime(2021, 11, 30, 23, 30, 30, 30,
                                 tzinfo=timezone(timedelta(hours=23,
                                                           minutes=59))
                                 ),
                        datetime(2022, 12, 31, 23, 59, 59, 999999,
                                 tzinfo=timezone(timedelta(hours=23,
                                                           minutes=59)),
                                 )]


@pytest.fixture(params=dt_datetime_arg_list)  # type: ignore
def dt_datetime_arg(request: Any) -> datetime:
    """Using different time formats.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(datetime, request.param)


dt_datetime_month_arg_list = [1, 5, 9, 10, 11, 12]


@pytest.fixture(params=dt_datetime_month_arg_list)  # type: ignore
def dt_datetime_month_arg(request: Any) -> int:
    """Using different time formats.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(int, request.param)


dt_datetime_day_arg_list = [1, 2, 9, 10, 11, 19, 20, 21, 29, 30, 31]


@pytest.fixture(params=dt_datetime_day_arg_list)  # type: ignore
def dt_datetime_day_arg(request: Any) -> int:
    """Using different time formats.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(int, request.param)


dt_format_date_arg_list = ['',
                           'weekday: %w, %m/%y',
                           '(weekday): %w, %m/%Y',
                           '%m/%d/%y',
                           '%m/%d/%Y',
                           '%a %b %Y',
                           '%a %B %Y',
                           '%A %b %Y',
                           '%A %B %Y',
                           '%d %b %Y'
                           ]

dt_format_time_arg_list = ['',
                           'hour: %H',
                           '[hour/min]: %H:%M',
                           '%H:%M',
                           '%H:%M:%S',
                           '%I:%M %p',
                           '%I:%M:%S %p',
                           '%H:%M:%S.%f',
                           '%H:%M:%S.%f%z',
                           '%H:%M:%S.%f %Z'
                           ]


@pytest.fixture(params=dt_format_date_arg_list)  # type: ignore
def dt_format_date_arg(request: Any) -> str:
    """Using different time formats.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(str, request.param)


@pytest.fixture(params=dt_format_time_arg_list)  # type: ignore
def dt_format_time_arg(request: Any) -> str:
    """Using different time formats.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(str, request.param)


style_num_list = [1, 2, 3]


@pytest.fixture(params=style_num_list)  # type: ignore
def style_num(request: Any) -> int:
    """Using different time_box styles.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(int, request.param)


end_arg_list = ['0', '\n', '\n\n']


@pytest.fixture(params=end_arg_list)  # type: ignore
def end_arg(request: Any) -> str:
    """Choose single or double space.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(str, request.param)


file_arg_list = ['0', 'None', 'sys.stdout', 'sys.stderr']


@pytest.fixture(params=file_arg_list)  # type: ignore
def file_arg(request: Any) -> str:
    """Using different file arg.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(str, request.param)


flush_arg_list = ['0', 'True', 'False']


@pytest.fixture(params=flush_arg_list)  # type: ignore
def flush_arg(request: Any) -> str:
    """False: do not flush print stream, True: flush print stream.

     Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(str, request.param)


enabled_arg_list = ['0',
                    'static_true',
                    'static_false',
                    'dynamic_true',
                    'dynamic_false'
                    ]


@pytest.fixture(params=enabled_arg_list)  # type: ignore
def enabled_arg(request: Any) -> str:
    """Determines how to specify time_box_enabled.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(str, request.param)


class TestGetMatchStr:
    """Test formatted re strings."""

    ####################################################################
    # test_get_datetime_match_string_mid
    ####################################################################
    def test_get_datetime_char_match(self,
                                     dt_format_char_arg: str,
                                     dt_datetime_arg: datetime
                                     ) -> None:
        """Test the datetime match string for one char.

        Args:
            dt_format_char_arg: pytest fixture for char arg
            dt_datetime_arg: pytest fixture for datetime arg

        """
        print(f'\n{dt_format_char_arg=}')

        old_datetime = dt_datetime_arg.strftime(dt_format_char_arg)

        new_datetime = datetime.now(
            timezone(timedelta(hours=1))).strftime(dt_format_char_arg)

        formatted_old_dt = (f"{old_datetime} was a good time.")
        print(f'{formatted_old_dt=}')

        formatted_new_dt = (f"{new_datetime} was a good time.")
        print(f'{formatted_new_dt=}')

        match_str = get_datetime_match_string(dt_format_char_arg)
        print(f'{match_str=}')

        adjusted_old_dt = re.sub(match_str, new_datetime, formatted_old_dt)
        print(f'{adjusted_old_dt=}')

        assert formatted_new_dt == adjusted_old_dt

    ####################################################################
    # test_get_datetime_match_string_mid
    ####################################################################
    def test_get_datetime_match_string_start(self,
                                             dt_format_date_arg: str,
                                             dt_format_time_arg: str,
                                             dt_datetime_arg: datetime
                                             ) -> None:
        """Test the datetime match string at start of text.

        Args:
            dt_format_date_arg: pytest fixture for date arg
            dt_format_time_arg: pytest fixture for time arg
            dt_datetime_arg: pytest fixture for datetime arg

        """
        if dt_format_date_arg == '':
            dt_format = f'{dt_format_time_arg}'
        else:
            dt_format = f'{dt_format_date_arg} {dt_format_time_arg}'

        print(f'\n{dt_format=}')

        old_datetime = dt_datetime_arg.strftime(dt_format)

        new_datetime = datetime.now(
            timezone(timedelta(hours=1))).strftime(dt_format)

        formatted_old_dt = (f"{old_datetime} was a good time.")
        print(f'{formatted_old_dt=}')

        formatted_new_dt = (f"{new_datetime} was a good time.")
        print(f'{formatted_new_dt=}')

        match_str = get_datetime_match_string(dt_format)
        print(f'{match_str=}')

        adjusted_old_dt = re.sub(match_str, new_datetime, formatted_old_dt)
        print(f'{adjusted_old_dt=}')

        assert formatted_new_dt == adjusted_old_dt

    ####################################################################
    # test_get_datetime_match_string_mid
    ####################################################################
    def test_get_datetime_match_string_mid(self,
                                           dt_format_date_arg: str,
                                           dt_format_time_arg: str,
                                           dt_datetime_arg: datetime
                                           ) -> None:
        """Test the datetime match string.

        Args:
            dt_format_date_arg: pytest fixture for date arg
            dt_format_time_arg: pytest fixture for time arg
            dt_datetime_arg: pytest fixture for datetime arg

        """
        if dt_format_date_arg == '':
            dt_format = f'{dt_format_time_arg}'
        else:
            dt_format = f'{dt_format_date_arg} {dt_format_time_arg}'

        print(f'\n{dt_format=}')

        old_datetime = dt_datetime_arg.strftime(dt_format)

        new_datetime = datetime.now(
            timezone(timedelta(hours=1))).strftime(dt_format)

        formatted_old_dt = (f"Here it is: {old_datetime} with "
                            f"the formatting we want.")
        print(f'{formatted_old_dt=}')

        formatted_new_dt = (f"Here it is: {new_datetime} with "
                            f"the formatting we want.")
        print(f'{formatted_new_dt=}')

        match_str = get_datetime_match_string(dt_format)
        print(f'{match_str=}')

        adjusted_old_dt = re.sub(match_str, new_datetime, formatted_old_dt)
        print(f'{adjusted_old_dt=}')

        assert formatted_new_dt == adjusted_old_dt

    ####################################################################
    # test_get_datetime_match_string_end
    ####################################################################
    def test_get_datetime_match_string_end(self,
                                           dt_format_date_arg: str,
                                           dt_format_time_arg: str,
                                           dt_datetime_arg: datetime
                                           ) -> None:
        """Test the datetime match string at end of test.

        Args:
            dt_format_date_arg: pytest fixture for date arg
            dt_format_time_arg: pytest fixture for time arg
            dt_datetime_arg: pytest fixture for datetime arg

        """
        if dt_format_date_arg == '':
            dt_format = f'{dt_format_time_arg}'
        else:
            dt_format = f'{dt_format_date_arg} {dt_format_time_arg}'

        print(f'\n{dt_format=}')

        old_datetime = dt_datetime_arg.strftime(dt_format)

        new_datetime = datetime.now(
            timezone(timedelta(hours=1))).strftime(dt_format)

        formatted_old_dt = (f"Time is on your side:"
                            f" {old_datetime}")
        print(f'{formatted_old_dt=}')

        formatted_new_dt = (f"Time is on your side:"
                            f" {new_datetime}")
        print(f'{formatted_new_dt=}')

        match_str = get_datetime_match_string(dt_format)
        print(f'{match_str=}')

        adjusted_old_dt = re.sub(match_str, new_datetime, formatted_old_dt)
        print(f'{adjusted_old_dt=}')

        assert formatted_new_dt == adjusted_old_dt


class TestStartStopHeader:
    """TestStartStopHeader class."""

    @pytest.fixture(scope='class')  # type: ignore
    def hdr(self) -> "StartStopHeader":
        """Method hdr.

        Returns:
            StartStopHeader instance
        """
        return StartStopHeader('TestName')

    def test_print_start_msg(self, hdr: "StartStopHeader", capsys: Any,
                             dt_format_arg: DT_Format,
                             end_arg: str,
                             file_arg: str,
                             flush_arg: str) -> None:
        """test_print_start_msg method.

        Args:
            hdr: instance of StartStopHeader
            capsys: instance of the capture sys fixture
            dt_format_arg: specifies dt_format_arg fixture
            end_arg: specifies end_arg fixture
            file_arg: specifies file_arg fixture
            flush_arg: specifies the flush_arg fixture
        """
        route_num, expected_dt_format, end, file, \
            flush, enabled_tf = TestTimeBox.get_arg_flags(
                      dt_format=dt_format_arg,
                      end=end_arg,
                      file=file_arg,
                      flush=flush_arg,
                      enabled='0')

        if route_num == TestTimeBox.DT0_END0_FILE0_FLUSH0_ENAB0:
            hdr.print_start_msg()
        elif route_num == TestTimeBox.DT0_END0_FILE0_FLUSH1_ENAB0:
            hdr.print_start_msg(flush=flush)
        elif route_num == TestTimeBox.DT0_END0_FILE1_FLUSH0_ENAB0:
            hdr.print_start_msg(file=eval(file_arg))
        elif route_num == TestTimeBox.DT0_END0_FILE1_FLUSH1_ENAB0:
            hdr.print_start_msg(file=eval(file_arg), flush=flush)
        elif route_num == TestTimeBox.DT0_END1_FILE0_FLUSH0_ENAB0:
            hdr.print_start_msg(end=end_arg)
        elif route_num == TestTimeBox.DT0_END1_FILE0_FLUSH1_ENAB0:
            hdr.print_start_msg(end=end_arg, flush=flush)
        elif route_num == TestTimeBox.DT0_END1_FILE1_FLUSH0_ENAB0:
            hdr.print_start_msg(end=end_arg, file=eval(file_arg))
        elif route_num == TestTimeBox.DT0_END1_FILE1_FLUSH1_ENAB0:
            hdr.print_start_msg(end=end_arg, file=eval(file_arg),
                                flush=flush)
        elif route_num == TestTimeBox.DT1_END0_FILE0_FLUSH0_ENAB0:
            hdr.print_start_msg(dt_format=dt_format_arg)
        elif route_num == TestTimeBox.DT1_END0_FILE0_FLUSH1_ENAB0:
            hdr.print_start_msg(dt_format=dt_format_arg, flush=flush)
        elif route_num == TestTimeBox.DT1_END0_FILE1_FLUSH0_ENAB0:
            hdr.print_start_msg(dt_format=dt_format_arg, file=eval(file_arg))
        elif route_num == TestTimeBox.DT1_END0_FILE1_FLUSH1_ENAB0:
            hdr.print_start_msg(dt_format=dt_format_arg, file=eval(file_arg),
                                flush=flush)
        elif route_num == TestTimeBox.DT1_END1_FILE0_FLUSH0_ENAB0:
            hdr.print_start_msg(dt_format=dt_format_arg, end=end_arg)
        elif route_num == TestTimeBox.DT1_END1_FILE0_FLUSH1_ENAB0:
            hdr.print_start_msg(dt_format=dt_format_arg, end=end_arg,
                                flush=flush)
        elif route_num == TestTimeBox.DT1_END1_FILE1_FLUSH0_ENAB0:
            hdr.print_start_msg(dt_format=dt_format_arg, end=end_arg,
                                file=eval(file_arg))
        else:  # route_num == TestTimeBox.DT1_END1_FILE1_FLUSH1_ENAB0:
            hdr.print_start_msg(dt_format=dt_format_arg, end=end_arg,
                                file=eval(file_arg), flush=flush)

        if file == 'sys.stdout':
            captured = capsys.readouterr().out
        else:
            captured = capsys.readouterr().err

        start_dt = hdr.start_DT
        formatted_dt = start_dt.strftime(expected_dt_format)
        msg = '* Starting TestName on ' + formatted_dt + ' *'
        flowers = '*' * len(msg)
        expected = '\n' + flowers + end + msg + end + flowers + end
        assert captured == expected

    def test_print_end_msg(self, hdr: "StartStopHeader", capsys: Any,
                           dt_format_arg: DT_Format,
                           end_arg: str,
                           file_arg: str,
                           flush_arg: str) -> None:
        """Method test_print_end_msg.

        Args:
            hdr: instance of StartStopHeader
            capsys: instance of the capture sys fixture
            dt_format_arg: specifies dt_format_arg fixture
            end_arg: specifies end_arg fixture
            file_arg: specifies file_arg fixture
            flush_arg: specifies the flush_arg fixture
        """
        route_num, expected_dt_format, end, file, \
            flush, enabled_tf = TestTimeBox.get_arg_flags(
                      dt_format=dt_format_arg,
                      end=end_arg,
                      file=file_arg,
                      flush=flush_arg,
                      enabled='0')

        if route_num == TestTimeBox.DT0_END0_FILE0_FLUSH0_ENAB0:
            hdr.print_end_msg()
        elif route_num == TestTimeBox.DT0_END0_FILE0_FLUSH1_ENAB0:
            hdr.print_end_msg(flush=flush)
        elif route_num == TestTimeBox.DT0_END0_FILE1_FLUSH0_ENAB0:
            hdr.print_end_msg(file=eval(file_arg))
        elif route_num == TestTimeBox.DT0_END0_FILE1_FLUSH1_ENAB0:
            hdr.print_end_msg(file=eval(file_arg), flush=flush)
        elif route_num == TestTimeBox.DT0_END1_FILE0_FLUSH0_ENAB0:
            hdr.print_end_msg(end=end_arg)
        elif route_num == TestTimeBox.DT0_END1_FILE0_FLUSH1_ENAB0:
            hdr.print_end_msg(end=end_arg, flush=flush)
        elif route_num == TestTimeBox.DT0_END1_FILE1_FLUSH0_ENAB0:
            hdr.print_end_msg(end=end_arg, file=eval(file_arg))
        elif route_num == TestTimeBox.DT0_END1_FILE1_FLUSH1_ENAB0:
            hdr.print_end_msg(end=end_arg, file=eval(file_arg),
                              flush=flush)
        elif route_num == TestTimeBox.DT1_END0_FILE0_FLUSH0_ENAB0:
            hdr.print_end_msg(dt_format=dt_format_arg)
        elif route_num == TestTimeBox.DT1_END0_FILE0_FLUSH1_ENAB0:
            hdr.print_end_msg(dt_format=dt_format_arg, flush=flush)
        elif route_num == TestTimeBox.DT1_END0_FILE1_FLUSH0_ENAB0:
            hdr.print_end_msg(dt_format=dt_format_arg, file=eval(file_arg))
        elif route_num == TestTimeBox.DT1_END0_FILE1_FLUSH1_ENAB0:
            hdr.print_end_msg(dt_format=dt_format_arg, file=eval(file_arg),
                              flush=flush)
        elif route_num == TestTimeBox.DT1_END1_FILE0_FLUSH0_ENAB0:
            hdr.print_end_msg(dt_format=dt_format_arg, end=end_arg)
        elif route_num == TestTimeBox.DT1_END1_FILE0_FLUSH1_ENAB0:
            hdr.print_end_msg(dt_format=dt_format_arg, end=end_arg,
                              flush=flush)
        elif route_num == TestTimeBox.DT1_END1_FILE1_FLUSH0_ENAB0:
            hdr.print_end_msg(dt_format=dt_format_arg, end=end_arg,
                              file=eval(file_arg))
        else:  # route_num == TestTimeBox.DT1_END1_FILE1_FLUSH1_ENAB0:
            hdr.print_end_msg(dt_format=dt_format_arg, end=end_arg,
                              file=eval(file_arg), flush=flush)

        if file == 'sys.stdout':
            captured = capsys.readouterr().out
        else:
            captured = capsys.readouterr().err

        start_dt = hdr.start_DT
        end_dt = hdr.end_DT
        formatted_delta = str(end_dt - start_dt)
        formatted_dt = end_dt.strftime(expected_dt_format)
        msg1: str = '* Ending TestName on ' + formatted_dt
        msg2: str = '* Elapsed time: ' + formatted_delta

        assert captured == TestStartStopHeader.get_flower_box(msg1, msg2, end)

    @staticmethod
    def get_flower_box(msg1: str, msg2: str, end: str) -> str:
        """Method get_flower_box.

        Args:
            msg1: first message to issue
            msg2: second message to issue
            end: specifies the end arg to use on the print statement

        Returns:
            The flower box with the messages inside
        """
        flower_len: int = max(len(msg1), len(msg2)) + 2
        flowers: str = '*' * flower_len
        msg1 += ' ' * (flower_len - len(msg1) - 1) + '*'
        msg2 += ' ' * (flower_len - len(msg2) - 1) + '*'
        expected: str = '\n' + flowers + end + msg1 + end + msg2 + end + \
                        flowers + end
        return expected


class TestTimeBox:
    """Class TestTimeBox."""
    DT1: Final = 0b00010000
    END1: Final = 0b00001000
    FILE1: Final = 0b00000100
    FLUSH1: Final = 0b00000010
    ENAB1: Final = 0b00000001

    DT0_END0_FILE0_FLUSH0_ENAB0: Final = 0b00000000
    DT0_END0_FILE0_FLUSH0_ENAB1: Final = 0b00000001
    DT0_END0_FILE0_FLUSH1_ENAB0: Final = 0b00000010
    DT0_END0_FILE0_FLUSH1_ENAB1: Final = 0b00000011
    DT0_END0_FILE1_FLUSH0_ENAB0: Final = 0b00000100
    DT0_END0_FILE1_FLUSH0_ENAB1: Final = 0b00000101
    DT0_END0_FILE1_FLUSH1_ENAB0: Final = 0b00000110
    DT0_END0_FILE1_FLUSH1_ENAB1: Final = 0b00000111
    DT0_END1_FILE0_FLUSH0_ENAB0: Final = 0b00001000
    DT0_END1_FILE0_FLUSH0_ENAB1: Final = 0b00001001
    DT0_END1_FILE0_FLUSH1_ENAB0: Final = 0b00001010
    DT0_END1_FILE0_FLUSH1_ENAB1: Final = 0b00001011
    DT0_END1_FILE1_FLUSH0_ENAB0: Final = 0b00001100
    DT0_END1_FILE1_FLUSH0_ENAB1: Final = 0b00001101
    DT0_END1_FILE1_FLUSH1_ENAB0: Final = 0b00001110
    DT0_END1_FILE1_FLUSH1_ENAB1: Final = 0b00001111
    DT1_END0_FILE0_FLUSH0_ENAB0: Final = 0b00010000
    DT1_END0_FILE0_FLUSH0_ENAB1: Final = 0b00010001
    DT1_END0_FILE0_FLUSH1_ENAB0: Final = 0b00010010
    DT1_END0_FILE0_FLUSH1_ENAB1: Final = 0b00010011
    DT1_END0_FILE1_FLUSH0_ENAB0: Final = 0b00010100
    DT1_END0_FILE1_FLUSH0_ENAB1: Final = 0b00010101
    DT1_END0_FILE1_FLUSH1_ENAB0: Final = 0b00010110
    DT1_END0_FILE1_FLUSH1_ENAB1: Final = 0b00010111
    DT1_END1_FILE0_FLUSH0_ENAB0: Final = 0b00011000
    DT1_END1_FILE0_FLUSH0_ENAB1: Final = 0b00011001
    DT1_END1_FILE0_FLUSH1_ENAB0: Final = 0b00011010
    DT1_END1_FILE0_FLUSH1_ENAB1: Final = 0b00011011
    DT1_END1_FILE1_FLUSH0_ENAB0: Final = 0b00011100
    DT1_END1_FILE1_FLUSH0_ENAB1: Final = 0b00011101
    DT1_END1_FILE1_FLUSH1_ENAB0: Final = 0b00011110
    DT1_END1_FILE1_FLUSH1_ENAB1: Final = 0b00011111

    @staticmethod
    def get_arg_flags(*,
                      dt_format: str,
                      end: str,
                      file: str,
                      flush: str,
                      enabled: str
                      ) -> Tuple[int, DT_Format, str, str, bool, bool]:
        """Static method get_arg_flags.

        Args:
            dt_format: 0 or the dt_format arg to use
            end: 0 or the end arg to use
            file: 0 or the file arg to use (stdout or stderr)
            flush: 0 or the flush arg to use
            enabled: 0 or the enabled arg to use

        Returns:
              the expected results based on the args
        """
        route_num = TestTimeBox.DT0_END0_FILE0_FLUSH0_ENAB0

        expected_dt_format = DT_Format(StartStopHeader.default_dt_format)
        if dt_format != '0':
            route_num = route_num | TestTimeBox.DT1
            expected_dt_format = DT_Format(dt_format)

        expected_end = '\n'
        if end != '0':
            route_num = route_num | TestTimeBox.END1
            expected_end = end

        expected_file = 'sys.stdout'
        if file != '0':
            route_num = route_num | TestTimeBox.FILE1
            if file != 'None':
                expected_file = file

        # Note: we can specify flush, but we can't verify that it works
        expected_flush = False
        if flush != '0':
            route_num = route_num | TestTimeBox.FLUSH1
            if flush == 'True':
                expected_flush = True

        expected_enabled_tf = True
        if enabled != '0':
            route_num = route_num | TestTimeBox.ENAB1
            if (enabled == 'static_false') or (enabled == 'dynamic_false'):
                expected_enabled_tf = False

        return (route_num, expected_dt_format, expected_end, expected_file,
                expected_flush, expected_enabled_tf)

    @staticmethod
    def get_expected_msg(*,
                         expected_func_msg: str,
                         actual: str,
                         expected_dt_format: DT_Format =
                         DT_Format('%a %b %d %Y %H:%M:%S'),
                         # StartStopHeader.default_dt_format,
                         expected_end: str = '\n',
                         expected_enabled_tf: bool = True) -> str:
        """Static method get_expected_msg.

        Helper function to build the expected message to compare
        with the actual message captured with capsys.

        Args:
            expected_func_msg: message issued by wrapped function
            actual: the message captured by capsys
            expected_dt_format: dt_format to use to build expected
                                  message
            expected_end: end arg to use to build expected message
            expected_enabled_tf: expected enabled arg to use to build
                                   expected message

        Returns:
            the expected message that is built based on the input args
        """
        if expected_enabled_tf is False:
            if expected_func_msg == '':
                return ''
            else:
                return expected_func_msg + '\n'

        match_fmt_string = get_datetime_match_string(expected_dt_format)

        # get start time
        match_re = re.compile('Starting func on ' + match_fmt_string)
        match_obj = match_re.search(actual)
        assert match_obj
        start_time = match_obj.group()

        # get end time
        match_re = re.compile('Ending func on ' + match_fmt_string)
        match_obj = match_re.search(actual)
        assert match_obj
        end_time = match_obj.group()

        # get elapsed time
        match_re = re.compile('Elapsed time: '
                              '[0-9]:[0-9]{2}:[0-9]{2}( |.[0-9]{1,6} )')
        match_obj = match_re.search(actual)
        assert match_obj
        elapsed_time = match_obj.group()[0:-1]

        msg0 = '* ' + start_time

        flower_len = len(msg0) + len(' *')
        flowers = '*' * flower_len

        msg0 += ' ' * (flower_len - len(msg0) - 1) + '*'

        expected0 = ('\n' + flowers + expected_end + msg0 + expected_end
                     + flowers + expected_end)

        # build expected1
        msg1 = '* ' + end_time
        msg2 = '* ' + elapsed_time

        expected1 = TestStartStopHeader.get_flower_box(msg1, msg2,
                                                       expected_end)

        if expected_func_msg == '':
            expected = expected0 + expected1
        else:
            expected = expected0 + expected_func_msg + '\n' + expected1

        return expected

    """
    The following section tests each combination of arguments to the
    time_box decorator for three styles of decoration (using pie,
    calling with the function as the first parameter, and calling the
    decorator with the function specified after the call. This test is
    especially useful to ensure that the type hints are working
    correctly, and that all combinations are accepted by python.

    The following keywords with various values and in all combinations
    are tested:
        dt_format - several different datetime formats - see format_list
        end - either '\n' for single space, and '\n\n' for double space
        file - either sys.stdout or sys.stderr
        flush - true/false
        time_box_enabled - true/false

    """

    def test_timebox_router(self,
                            capsys: Any,
                            style_num: int,
                            dt_format_arg: str,
                            end_arg: str,
                            file_arg: str,
                            flush_arg: str,
                            enabled_arg: str
                            ) -> None:
        """Method test_timebox_router.

        Args:
            capsys: instance of the capture sysout fixture
            style_num: style from fixture
            dt_format_arg: dt_format to use from fixture
            end_arg: end arg from fixture for the print invocation
            file_arg: file arg from fixture
            flush_arg: flush arg from fixture to use on print statement
            enabled_arg: specifies whether decorator is enabled
        """
        # func: Union[Callable[[int, str], int],
        #              Callable[[int, str], None],
        #              Callable[[], int],
        #              Callable[[], None]]

        a_func: Callable[..., Any]

        expected_return_value: Union[int, None]

        route_num, expected_dt_format, expected_end_arg, expected_file_arg, \
            flush, enabled_tf = TestTimeBox.get_arg_flags(
                      dt_format=dt_format_arg,
                      end=end_arg,
                      file=file_arg,
                      flush=flush_arg,
                      enabled=enabled_arg)

        enabled_spec: Union[bool, Callable[..., bool]] = enabled_tf
        def enabled_func() -> bool: return enabled_tf

        if (enabled_arg == 'dynamic_true') or (enabled_arg == 'dynamic_false'):
            enabled_spec = enabled_func

        if style_num == 1:
            for func_style in range(1, 5):
                a_func = TestTimeBox.build_style1_func(
                    route_num,
                    dt_format=DT_Format(dt_format_arg),
                    end=end_arg,
                    file=file_arg,
                    flush=flush,
                    enabled=enabled_spec,
                    f_style=func_style
                    )

                if func_style == 1:
                    func_msg = 'The answer is: ' + str(route_num)
                    expected_return_value = route_num * style_num
                    actual_return_value = a_func(route_num,
                                                 func_msg)
                elif func_style == 2:
                    func_msg = 'The answer is: ' + str(route_num)
                    expected_return_value = None
                    actual_return_value = a_func(route_num, func_msg)
                elif func_style == 3:
                    func_msg = ''
                    expected_return_value = 42
                    actual_return_value = a_func()
                else:  # func_style == 4:
                    func_msg = ''
                    expected_return_value = None
                    actual_return_value = a_func()

                TestTimeBox.check_results(
                    capsys=capsys,
                    func_msg=func_msg,
                    expected_dt_format=expected_dt_format,
                    expected_end=expected_end_arg,
                    expected_file=expected_file_arg,
                    expected_enabled_tf=enabled_tf,
                    expected_return_value=expected_return_value,
                    actual_return_value=actual_return_value
                    )
                if route_num > TestTimeBox.DT0_END0_FILE1_FLUSH1_ENAB1:
                    break
            return

        elif style_num == 2:
            a_func = TestTimeBox.build_style2_func(
                route_num,
                dt_format=DT_Format(dt_format_arg),
                end=end_arg,
                file=file_arg,
                flush=flush,
                enabled=enabled_spec
                )
        else:  # style_num = 3
            a_func = TestTimeBox.build_style3_func(
                route_num,
                dt_format=DT_Format(dt_format_arg),
                end=end_arg,
                file=file_arg,
                flush=flush,
                enabled=enabled_spec
                )

        func_msg = 'The answer is: ' + str(route_num)
        expected_return_value = route_num * style_num
        actual_return_value = a_func(route_num, func_msg)
        TestTimeBox.check_results(
            capsys=capsys,
            func_msg=func_msg,
            expected_dt_format=expected_dt_format,
            expected_end=expected_end_arg,
            expected_file=expected_file_arg,
            expected_enabled_tf=enabled_tf,
            expected_return_value=expected_return_value,
            actual_return_value=actual_return_value
            )

    @staticmethod
    def check_results(capsys: Any,
                      func_msg: str,
                      expected_dt_format: DT_Format,
                      expected_end: str,
                      expected_file: str,
                      expected_enabled_tf: bool,
                      expected_return_value: Union[int, None],
                      actual_return_value: Union[int, None]
                      ) -> None:
        """Static method check_results.

        Args:
            capsys: instance of the capture sysout fixture
            func_msg: message issued by wrapped function
            expected_dt_format: dt_format that is used
            expected_end: end arg for the print invocation
            expected_file: sys.stdout or sys.stderr
            expected_enabled_tf: specifies whether decorator is enabled
            expected_return_value: the expected func return value
            actual_return_value: the actual func return value
        """
        if expected_file == 'sys.stdout':
            actual = capsys.readouterr().out
        else:
            actual = capsys.readouterr().err
            func_msg = ''

        expected = TestTimeBox.get_expected_msg(
            expected_func_msg=func_msg,
            actual=actual,
            expected_dt_format=expected_dt_format,
            expected_end=expected_end,
            expected_enabled_tf=expected_enabled_tf)

        assert actual == expected

        # check that func returns the correct value

        message = "Expected return value: {0}, Actual return value: {1}"\
            .format(expected_return_value, actual_return_value)
        assert expected_return_value == actual_return_value, message

    @staticmethod
    def build_style1_func(route_num: int,
                          dt_format: DT_Format,
                          end: str,
                          file: str,
                          flush: bool,
                          enabled: Union[bool, Callable[..., bool]],
                          f_style: int
                          ) -> Callable[..., Any]:
        """Static method build_style1_func.

        Args:
            route_num: specifies how to build the decorator
            dt_format: dt format to use
            end: end to use
            file: specifies sys.stdout or sys.stderr for print statement
            flush: specifies flush to use on print statement
            enabled: specifies whether the decorator is enabled
            f_style: type of call to build

        Returns:
              callable decorated function

        Raises:
              InvalidRouteNum: 'route_num was not recognized'
        """
        # func: Union[Callable[[int, str], int],
        #              Callable[[int, str], None],
        #              Callable[[], int],
        #              Callable[[], None]]

        if route_num == TestTimeBox.DT0_END0_FILE0_FLUSH0_ENAB0:
            if f_style == 1:
                @time_box
                def func(a_int: int, a_str: str) -> int:
                    print(a_str)
                    return a_int * 1
            elif f_style == 2:
                @time_box
                def func(a_int: int, a_str: str) -> None:
                    print(a_str)
            elif f_style == 3:
                @time_box
                def func() -> int:
                    return 42
            else:  # f_style == 4:
                @time_box
                def func() -> None:
                    pass
        elif route_num == TestTimeBox.DT0_END0_FILE0_FLUSH0_ENAB1:
            if f_style == 1:
                @time_box(time_box_enabled=enabled)
                def func(a_int: int, a_str: str) -> int:
                    print(a_str)
                    return a_int * 1
            elif f_style == 2:
                @time_box(time_box_enabled=enabled)
                def func(a_int: int, a_str: str) -> None:
                    print(a_str)
            elif f_style == 3:
                @time_box(time_box_enabled=enabled)
                def func() -> int:
                    return 42
            else:  # f_style == 4:
                @time_box(time_box_enabled=enabled)
                def func() -> None:
                    pass
        elif route_num == TestTimeBox.DT0_END0_FILE0_FLUSH1_ENAB0:
            if f_style == 1:
                @time_box(flush=flush)
                def func(a_int: int, a_str: str) -> int:
                    print(a_str)
                    return a_int * 1
            elif f_style == 2:
                @time_box(flush=flush)
                def func(a_int: int, a_str: str) -> None:
                    print(a_str)
            elif f_style == 3:
                @time_box(flush=flush)
                def func() -> int:
                    return 42
            else:  # f_style == 4:
                @time_box(flush=flush)
                def func() -> None:
                    pass
        elif route_num == TestTimeBox.DT0_END0_FILE0_FLUSH1_ENAB1:
            if f_style == 1:
                @time_box(flush=flush, time_box_enabled=enabled)
                def func(a_int: int, a_str: str) -> int:
                    print(a_str)
                    return a_int * 1
            elif f_style == 2:
                @time_box(flush=flush, time_box_enabled=enabled)
                def func(a_int: int, a_str: str) -> None:
                    print(a_str)
            elif f_style == 3:
                @time_box(flush=flush, time_box_enabled=enabled)
                def func() -> int:
                    return 42
            else:  # f_style == 4:
                @time_box(flush=flush, time_box_enabled=enabled)
                def func() -> None:
                    pass
        elif route_num == TestTimeBox.DT0_END0_FILE1_FLUSH0_ENAB0:
            if f_style == 1:
                @time_box(file=eval(file))
                def func(a_int: int, a_str: str) -> int:
                    print(a_str)
                    return a_int * 1
            elif f_style == 2:
                @time_box(file=eval(file))
                def func(a_int: int, a_str: str) -> None:
                    print(a_str)
            elif f_style == 3:
                @time_box(file=eval(file))
                def func() -> int:
                    return 42
            else:  # f_style == 4:
                @time_box(file=eval(file))
                def func() -> None:
                    pass
        elif route_num == TestTimeBox.DT0_END0_FILE1_FLUSH0_ENAB1:
            if f_style == 1:
                @time_box(file=eval(file), time_box_enabled=enabled)
                def func(a_int: int, a_str: str) -> int:
                    print(a_str)
                    return a_int * 1
            elif f_style == 2:
                @time_box(file=eval(file), time_box_enabled=enabled)
                def func(a_int: int, a_str: str) -> None:
                    print(a_str)
            elif f_style == 3:
                @time_box(file=eval(file), time_box_enabled=enabled)
                def func() -> int:
                    return 42
            else:  # f_style == 4:
                @time_box(file=eval(file), time_box_enabled=enabled)
                def func() -> None:
                    pass
        elif route_num == TestTimeBox.DT0_END0_FILE1_FLUSH1_ENAB0:
            if f_style == 1:
                @time_box(file=eval(file), flush=flush)
                def func(a_int: int, a_str: str) -> int:
                    print(a_str)
                    return a_int * 1
            elif f_style == 2:
                @time_box(file=eval(file), flush=flush)
                def func(a_int: int, a_str: str) -> None:
                    print(a_str)
            elif f_style == 3:
                @time_box(file=eval(file), flush=flush)
                def func() -> int:
                    return 42
            else:  # f_style == 4:
                @time_box(file=eval(file), flush=flush)
                def func() -> None:
                    pass
        elif route_num == TestTimeBox.DT0_END0_FILE1_FLUSH1_ENAB1:
            if f_style == 1:
                @time_box(file=eval(file), flush=flush,
                          time_box_enabled=enabled)
                def func(a_int: int, a_str: str) -> int:
                    print(a_str)
                    return a_int * 1
            elif f_style == 2:
                @time_box(file=eval(file), flush=flush,
                          time_box_enabled=enabled)
                def func(a_int: int, a_str: str) -> None:
                    print(a_str)
            elif f_style == 3:
                @time_box(file=eval(file), flush=flush,
                          time_box_enabled=enabled)
                def func() -> int:
                    return 42
            else:  # f_style == 4:
                @time_box(file=eval(file), flush=flush,
                          time_box_enabled=enabled)
                def func() -> None:
                    pass
        elif route_num == TestTimeBox.DT0_END1_FILE0_FLUSH0_ENAB0:
            @time_box(end=end)
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 1
        elif route_num == TestTimeBox.DT0_END1_FILE0_FLUSH0_ENAB1:
            @time_box(end=end, time_box_enabled=enabled)
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 1
        elif route_num == TestTimeBox.DT0_END1_FILE0_FLUSH1_ENAB0:
            @time_box(end=end, flush=flush)
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 1
        elif route_num == TestTimeBox.DT0_END1_FILE0_FLUSH1_ENAB1:
            @time_box(end=end, flush=flush, time_box_enabled=enabled)
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 1
        elif route_num == TestTimeBox.DT0_END1_FILE1_FLUSH0_ENAB0:
            @time_box(end=end, file=eval(file))
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 1
        elif route_num == TestTimeBox.DT0_END1_FILE1_FLUSH0_ENAB1:
            @time_box(end=end, file=eval(file), time_box_enabled=enabled)
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 1
        elif route_num == TestTimeBox.DT0_END1_FILE1_FLUSH1_ENAB0:
            @time_box(end=end, file=eval(file), flush=flush)
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 1
        elif route_num == TestTimeBox.DT0_END1_FILE1_FLUSH1_ENAB1:
            @time_box(end=end, file=eval(file), flush=flush,
                      time_box_enabled=enabled)
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 1
        elif route_num == TestTimeBox.DT1_END0_FILE0_FLUSH0_ENAB0:
            @time_box(dt_format=dt_format)
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 1
        elif route_num == TestTimeBox.DT1_END0_FILE0_FLUSH0_ENAB1:
            @time_box(dt_format=dt_format, time_box_enabled=enabled)
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 1
        elif route_num == TestTimeBox.DT1_END0_FILE0_FLUSH1_ENAB0:
            @time_box(dt_format=dt_format, flush=flush)
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 1
        elif route_num == TestTimeBox.DT1_END0_FILE0_FLUSH1_ENAB1:
            @time_box(dt_format=dt_format, flush=flush,
                      time_box_enabled=enabled)
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 1
        elif route_num == TestTimeBox.DT1_END0_FILE1_FLUSH0_ENAB0:
            @time_box(dt_format=dt_format, file=eval(file))
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 1
        elif route_num == TestTimeBox.DT1_END0_FILE1_FLUSH0_ENAB1:
            @time_box(dt_format=dt_format, file=eval(file),
                      time_box_enabled=enabled)
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 1
        elif route_num == TestTimeBox.DT1_END0_FILE1_FLUSH1_ENAB0:
            @time_box(dt_format=dt_format, file=eval(file), flush=flush)
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 1
        elif route_num == TestTimeBox.DT1_END0_FILE1_FLUSH1_ENAB1:
            @time_box(dt_format=dt_format, file=eval(file), flush=flush,
                      time_box_enabled=enabled)
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 1
        elif route_num == TestTimeBox.DT1_END1_FILE0_FLUSH0_ENAB0:
            @time_box(dt_format=dt_format, end=end)
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 1
        elif route_num == TestTimeBox.DT1_END1_FILE0_FLUSH0_ENAB1:
            @time_box(dt_format=dt_format, end=end, time_box_enabled=enabled)
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 1
        elif route_num == TestTimeBox.DT1_END1_FILE0_FLUSH1_ENAB0:
            @time_box(dt_format=dt_format, end=end, flush=flush)
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 1
        elif route_num == TestTimeBox.DT1_END1_FILE0_FLUSH1_ENAB1:
            @time_box(dt_format=dt_format, end=end, flush=flush,
                      time_box_enabled=enabled)
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 1
        elif route_num == TestTimeBox.DT1_END1_FILE1_FLUSH0_ENAB0:
            @time_box(dt_format=dt_format, end=end, file=eval(file))
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 1
        elif route_num == TestTimeBox.DT1_END1_FILE1_FLUSH0_ENAB1:
            @time_box(dt_format=dt_format, end=end, file=eval(file),
                      time_box_enabled=enabled)
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 1
        elif route_num == TestTimeBox.DT1_END1_FILE1_FLUSH1_ENAB0:
            @time_box(dt_format=dt_format, end=end, file=eval(file),
                      flush=flush)
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 1
        elif route_num == TestTimeBox.DT1_END1_FILE1_FLUSH1_ENAB1:
            @time_box(dt_format=dt_format, end=end, file=eval(file),
                      flush=flush, time_box_enabled=enabled)
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 1
        else:
            raise InvalidRouteNum('route_num was not recognized')

        return func

    @staticmethod
    def build_style2_func(route_num: int,
                          dt_format: DT_Format,
                          end: str,
                          file: str,
                          flush: bool,
                          enabled: Union[bool, Callable[..., bool]]
                          ) -> Callable[[int, str], int]:
        """Static method build_style2_func.

        Args:
            route_num: specifies how to build the decorator
            dt_format: dt format to use
            end: end to use
            file: specifies sys.stdout or sys.stderr for print statement
            flush: specifies flush to use on print statement
            enabled: specifies whether the decorator is enabled

        Returns:
              callable decorated function

        Raises:
              InvalidRouteNum: 'route_num was not recognized'
        """
        if route_num == TestTimeBox.DT0_END0_FILE0_FLUSH0_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func)
        elif route_num == TestTimeBox.DT0_END0_FILE0_FLUSH0_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, time_box_enabled=enabled)
        elif route_num == TestTimeBox.DT0_END0_FILE0_FLUSH1_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, flush=flush)
        elif route_num == TestTimeBox.DT0_END0_FILE0_FLUSH1_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, flush=flush, time_box_enabled=enabled)
        elif route_num == TestTimeBox.DT0_END0_FILE1_FLUSH0_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, file=eval(file))
        elif route_num == TestTimeBox.DT0_END0_FILE1_FLUSH0_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, file=eval(file), time_box_enabled=enabled)
        elif route_num == TestTimeBox.DT0_END0_FILE1_FLUSH1_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, file=eval(file), flush=flush)
        elif route_num == TestTimeBox.DT0_END0_FILE1_FLUSH1_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, file=eval(file), flush=flush,
                            time_box_enabled=enabled)
        elif route_num == TestTimeBox.DT0_END1_FILE0_FLUSH0_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, end=end)
        elif route_num == TestTimeBox.DT0_END1_FILE0_FLUSH0_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, end=end, time_box_enabled=enabled)
        elif route_num == TestTimeBox.DT0_END1_FILE0_FLUSH1_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, end=end, flush=flush)
        elif route_num == TestTimeBox.DT0_END1_FILE0_FLUSH1_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, end=end, flush=flush,
                            time_box_enabled=enabled)
        elif route_num == TestTimeBox.DT0_END1_FILE1_FLUSH0_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, end=end, file=eval(file))
        elif route_num == TestTimeBox.DT0_END1_FILE1_FLUSH0_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, end=end, file=eval(file),
                            time_box_enabled=enabled)
        elif route_num == TestTimeBox.DT0_END1_FILE1_FLUSH1_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, end=end, file=eval(file), flush=flush)
        elif route_num == TestTimeBox.DT0_END1_FILE1_FLUSH1_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, end=end, file=eval(file), flush=flush,
                            time_box_enabled=enabled)
        elif route_num == TestTimeBox.DT1_END0_FILE0_FLUSH0_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, dt_format=dt_format)
        elif route_num == TestTimeBox.DT1_END0_FILE0_FLUSH0_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, dt_format=dt_format,
                            time_box_enabled=enabled)
        elif route_num == TestTimeBox.DT1_END0_FILE0_FLUSH1_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, dt_format=dt_format, flush=flush)
        elif route_num == TestTimeBox.DT1_END0_FILE0_FLUSH1_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, dt_format=dt_format, flush=flush,
                            time_box_enabled=enabled)
        elif route_num == TestTimeBox.DT1_END0_FILE1_FLUSH0_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, dt_format=dt_format, file=eval(file))
        elif route_num == TestTimeBox.DT1_END0_FILE1_FLUSH0_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, dt_format=dt_format, file=eval(file),
                            time_box_enabled=enabled)
        elif route_num == TestTimeBox.DT1_END0_FILE1_FLUSH1_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, dt_format=dt_format, file=eval(file),
                            flush=flush)
        elif route_num == TestTimeBox.DT1_END0_FILE1_FLUSH1_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, dt_format=dt_format, file=eval(file),
                            flush=flush, time_box_enabled=enabled)
        elif route_num == TestTimeBox.DT1_END1_FILE0_FLUSH0_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, dt_format=dt_format, end=end)
        elif route_num == TestTimeBox.DT1_END1_FILE0_FLUSH0_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, dt_format=dt_format, end=end,
                            time_box_enabled=enabled)
        elif route_num == TestTimeBox.DT1_END1_FILE0_FLUSH1_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, dt_format=dt_format, end=end, flush=flush)
        elif route_num == TestTimeBox.DT1_END1_FILE0_FLUSH1_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, dt_format=dt_format, end=end, flush=flush,
                            time_box_enabled=enabled)
        elif route_num == TestTimeBox.DT1_END1_FILE1_FLUSH0_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, dt_format=dt_format, end=end,
                            file=eval(file))
        elif route_num == TestTimeBox.DT1_END1_FILE1_FLUSH0_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, dt_format=dt_format, end=end,
                            file=eval(file), time_box_enabled=enabled)
        elif route_num == TestTimeBox.DT1_END1_FILE1_FLUSH1_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, dt_format=dt_format, end=end,
                            file=eval(file), flush=flush)
        elif route_num == TestTimeBox.DT1_END1_FILE1_FLUSH1_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 2
            func = time_box(func, dt_format=dt_format, end=end,
                            file=eval(file), flush=flush,
                            time_box_enabled=enabled)
        else:
            raise InvalidRouteNum('route_num was not recognized')

        return func

    @staticmethod
    def build_style3_func(route_num: int,
                          dt_format: DT_Format,
                          end: str,
                          file: str,
                          flush: bool,
                          enabled: Union[bool, Callable[..., bool]]
                          ) -> Callable[[int, str], int]:
        """Static method build_style3_func.

        Args:
            route_num: specifies how to build the decorator
            dt_format: dt format to use
            end: end to use
            file: specifies sys.stdout or sys.stderr for print statement
            flush: specifies flush to use on print statement
            enabled: specifies whether the decorator is enabled

        Returns:
              callable decorated function

        Raises:
              InvalidRouteNum: 'route_num was not recognized'
        """
        if route_num == TestTimeBox.DT0_END0_FILE0_FLUSH0_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box()(func)
        elif route_num == TestTimeBox.DT0_END0_FILE0_FLUSH0_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(time_box_enabled=enabled)(func)
        elif route_num == TestTimeBox.DT0_END0_FILE0_FLUSH1_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(flush=flush)(func)
        elif route_num == TestTimeBox.DT0_END0_FILE0_FLUSH1_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(flush=flush, time_box_enabled=enabled)(func)
        elif route_num == TestTimeBox.DT0_END0_FILE1_FLUSH0_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(file=eval(file))(func)
        elif route_num == TestTimeBox.DT0_END0_FILE1_FLUSH0_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(file=eval(file), time_box_enabled=enabled)(func)
        elif route_num == TestTimeBox.DT0_END0_FILE1_FLUSH1_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(file=eval(file), flush=flush)(func)
        elif route_num == TestTimeBox.DT0_END0_FILE1_FLUSH1_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(file=eval(file), flush=flush,
                            time_box_enabled=enabled)(func)
        elif route_num == TestTimeBox.DT0_END1_FILE0_FLUSH0_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(end=end)(func)
        elif route_num == TestTimeBox.DT0_END1_FILE0_FLUSH0_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(end=end, time_box_enabled=enabled)(func)
        elif route_num == TestTimeBox.DT0_END1_FILE0_FLUSH1_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(end=end, flush=flush)(func)
        elif route_num == TestTimeBox.DT0_END1_FILE0_FLUSH1_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(end=end, flush=flush,
                            time_box_enabled=enabled)(func)
        elif route_num == TestTimeBox.DT0_END1_FILE1_FLUSH0_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(end=end, file=eval(file))(func)
        elif route_num == TestTimeBox.DT0_END1_FILE1_FLUSH0_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(end=end, file=eval(file),
                            time_box_enabled=enabled)(func)
        elif route_num == TestTimeBox.DT0_END1_FILE1_FLUSH1_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(end=end, file=eval(file), flush=flush)(func)
        elif route_num == TestTimeBox.DT0_END1_FILE1_FLUSH1_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(end=end, file=eval(file), flush=flush,
                            time_box_enabled=enabled)(func)
        elif route_num == TestTimeBox.DT1_END0_FILE0_FLUSH0_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(dt_format=dt_format)(func)
        elif route_num == TestTimeBox.DT1_END0_FILE0_FLUSH0_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(dt_format=dt_format,
                            time_box_enabled=enabled)(func)
        elif route_num == TestTimeBox.DT1_END0_FILE0_FLUSH1_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(dt_format=dt_format, flush=flush)(func)
        elif route_num == TestTimeBox.DT1_END0_FILE0_FLUSH1_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(dt_format=dt_format, flush=flush,
                            time_box_enabled=enabled)(func)
        elif route_num == TestTimeBox.DT1_END0_FILE1_FLUSH0_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(dt_format=dt_format, file=eval(file))(func)
        elif route_num == TestTimeBox.DT1_END0_FILE1_FLUSH0_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(dt_format=dt_format, file=eval(file),
                            time_box_enabled=enabled)(func)
        elif route_num == TestTimeBox.DT1_END0_FILE1_FLUSH1_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(dt_format=dt_format, file=eval(file),
                            flush=flush)(func)
        elif route_num == TestTimeBox.DT1_END0_FILE1_FLUSH1_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(dt_format=dt_format, file=eval(file), flush=flush,
                            time_box_enabled=enabled)(func)
        elif route_num == TestTimeBox.DT1_END1_FILE0_FLUSH0_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(dt_format=dt_format, end=end)(func)
        elif route_num == TestTimeBox.DT1_END1_FILE0_FLUSH0_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(dt_format=dt_format, end=end,
                            time_box_enabled=enabled)(func)
        elif route_num == TestTimeBox.DT1_END1_FILE0_FLUSH1_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(dt_format=dt_format, end=end,
                            flush=flush)(func)
        elif route_num == TestTimeBox.DT1_END1_FILE0_FLUSH1_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(dt_format=dt_format, end=end, flush=flush,
                            time_box_enabled=enabled)(func)
        elif route_num == TestTimeBox.DT1_END1_FILE1_FLUSH0_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(dt_format=dt_format, end=end,
                            file=eval(file))(func)
        elif route_num == TestTimeBox.DT1_END1_FILE1_FLUSH0_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(dt_format=dt_format, end=end, file=eval(file),
                            time_box_enabled=enabled)(func)
        elif route_num == TestTimeBox.DT1_END1_FILE1_FLUSH1_ENAB0:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(dt_format=dt_format, end=end, file=eval(file),
                            flush=flush)(func)
        elif route_num == TestTimeBox.DT1_END1_FILE1_FLUSH1_ENAB1:
            def func(a_int: int, a_str: str) -> int:
                print(a_str)
                return a_int * 3
            func = time_box(dt_format=dt_format, end=end, file=eval(file),
                            flush=flush, time_box_enabled=enabled)(func)
        else:
            raise InvalidRouteNum('route_num was not recognized')

        return func


class TestTimeBoxDocstrings:
    """Class TestTimeBoxDocstrings."""
    def test_timebox_with_example_1(self) -> None:
        """Method test_timebox_with_example_1."""
        print()
        print('#' * 50)
        print('Example for StartStopHeader:')
        print()

        def func1() -> None:
            print('2 + 2 =', 2+2)

        hdr = StartStopHeader('func1')
        hdr.print_start_msg(file=sys.stdout)

        func1()

        hdr.print_end_msg(file=sys.stdout)

    def test_timebox_with_example_2(self) -> None:
        """Method test_timebox_with_example_2."""
        print()
        print('#' * 50)
        print('Example for time_box decorator:')
        print()

        @time_box(file=sys.stdout)
        def func2() -> None:
            print('2 * 3 =', 2*3)

        func2()

    def test_timebox_with_example_3(self) -> None:
        """Method test_timebox_with_example_3."""
        print()
        print('#' * 50)
        print('Example of printing to stderr:')
        print()

        @time_box(file=sys.stderr)
        def func3() -> None:
            print('this text printed to stdout, not stderr')

        func3()

    def test_timebox_with_example_4(self) -> None:
        """Method test_timebox_with_example_4."""
        print()
        print('#' * 50)
        print('Example of statically wrapping function with time_box:')
        print()

        _tbe = False

        @time_box(time_box_enabled=_tbe, file=sys.stdout)
        def func4a() -> None:
            print('this is sample text for _tbe = False static example')

        func4a()  # func4a is not wrapped by time box

        _tbe = True

        @time_box(time_box_enabled=_tbe, file=sys.stdout)
        def func4b() -> None:
            print('this is sample text for _tbe = True static example')

        func4b()  # func4b is wrapped by time box

    def test_timebox_with_example_5(self) -> None:
        """Method test_timebox_with_example_5."""
        print()
        print('#' * 50)
        print('Example of dynamically wrapping function with time_box:')
        print()

        _tbe = True
        def tbe() -> bool: return _tbe

        @time_box(time_box_enabled=tbe, file=sys.stdout)
        def func5() -> None:
            print('this is sample text for the tbe dynamic example')

        func5()  # func5 is wrapped by time box

        _tbe = False
        func5()  # func5 is not wrapped by time_box

    def test_timebox_with_example_6(self) -> None:
        """Method test_timebox_with_example_6."""
        print()
        print('#' * 50)
        print('Example of using different datetime format:')
        print()

        a_datetime_format: DT_Format = cast(DT_Format, '%m/%d/%y %H:%M:%S')

        @time_box(dt_format=a_datetime_format)
        def func6() -> None:
            print('this is sample text for the datetime format example')

        func6()
