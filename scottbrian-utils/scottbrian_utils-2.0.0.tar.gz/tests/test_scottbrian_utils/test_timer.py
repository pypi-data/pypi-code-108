"""test_timer.py module."""

########################################################################
# Standard Library
########################################################################
import inspect
import logging
import threading
import time
from typing import Any, cast, Optional, Union

########################################################################
# Third Party
########################################################################
import pytest

########################################################################
# Local
########################################################################
from scottbrian_utils.timer import Timer
from scottbrian_utils.stop_watch import StopWatch

logger = logging.getLogger(__name__)

########################################################################
# type aliases
########################################################################
IntFloat = Union[int, float]
OptIntFloat = Optional[IntFloat]


########################################################################
# Timer test exceptions
########################################################################
class ErrorTstTimer(Exception):
    """Base class for exception in this module."""
    pass


########################################################################
# timeout arg fixtures
# greater_than_zero_timeout_arg fixture
########################################################################
zero_or_less_timeout_arg_list = [-1.1, -1, 0, 0.0]
greater_than_zero_timeout_arg_list = [0.3, 0.5, 1, 1.5, 2, 4]


########################################################################
# timeout_arg fixture
########################################################################
@pytest.fixture(params=greater_than_zero_timeout_arg_list)  # type: ignore
def timeout_arg(request: Any) -> IntFloat:
    """Using different seconds for timeout.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(IntFloat, request.param)


########################################################################
# zero_or_less_timeout_arg fixture
########################################################################
@pytest.fixture(params=zero_or_less_timeout_arg_list)  # type: ignore
def zero_or_less_timeout_arg(request: Any) -> IntFloat:
    """Using different seconds for timeout.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(IntFloat, request.param)


########################################################################
# greater_than_zero_timeout_arg fixture
########################################################################
@pytest.fixture(params=greater_than_zero_timeout_arg_list)  # type: ignore
def greater_than_zero_timeout_arg(request: Any) -> IntFloat:
    """Using different seconds for timeout.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(IntFloat, request.param)


########################################################################
# zero_or_less_default_timeout_arg fixture
########################################################################
@pytest.fixture(params=zero_or_less_timeout_arg_list)  # type: ignore
def zero_or_less_default_timeout_arg(request: Any) -> IntFloat:
    """Using different seconds for timeout_default.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(IntFloat, request.param)


########################################################################
# greater_than_zero_default_timeout_arg fixture
########################################################################
@pytest.fixture(params=greater_than_zero_timeout_arg_list)  # type: ignore
def greater_than_zero_default_timeout_arg(request: Any) -> IntFloat:
    """Using different seconds for timeout_default.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(IntFloat, request.param)


########################################################################
# TestTimerExamples class
########################################################################
class TestTimerExamples:
    """Test examples of Timer."""

    ####################################################################
    # test_timer_example1
    ####################################################################
    def test_timer_example1(self,
                            capsys: Any) -> None:
        """Test timer example1.

        Args:
            capsys: pytest fixture to capture print output

        """
        print('mainline entered')
        timer = Timer(timeout=3)
        for idx in range(10):
            print(f'idx = {idx}')
            time.sleep(1)
            if timer.is_expired():
                print('timer has expired')
                break
        print('mainline exiting')

        expected_result = 'mainline entered\n'
        expected_result += 'idx = 0\n'
        expected_result += 'idx = 1\n'
        expected_result += 'idx = 2\n'
        expected_result += 'timer has expired\n'
        expected_result += 'mainline exiting\n'

        captured = capsys.readouterr().out

        assert captured == expected_result

    ####################################################################
    # test_timer_example2
    ####################################################################
    def test_timer_example2(self,
                            capsys: Any) -> None:
        """Test timer example2.

        Args:
            capsys: pytest fixture to capture print output

        """
        class A:
            def __init__(self) -> None:
                self.a = 1

            def m1(self, sleep_time: float) -> bool:
                timer = Timer(timeout=1)
                time.sleep(sleep_time)
                if timer.is_expired():
                    return False
                return True

        print('mainline entered')
        my_a = A()
        print(my_a.m1(0.5))
        print(my_a.m1(1.5))
        print('mainline exiting')

        expected_result = 'mainline entered\n'
        expected_result += 'True\n'
        expected_result += 'False\n'
        expected_result += 'mainline exiting\n'

        captured = capsys.readouterr().out

        assert captured == expected_result

    ####################################################################
    # test_timer_example3
    ####################################################################
    def test_timer_example3(self,
                            capsys: Any) -> None:
        """Test timer example3.

        Args:
            capsys: pytest fixture to capture print output

        """
        class A:
            def __init__(self) -> None:
                self.a = 1

            def m1(self, sleep_time: float, timeout: float) -> bool:
                timer = Timer(timeout=timeout)
                time.sleep(sleep_time)
                if timer.is_expired():
                    return False
                return True

        print('mainline entered')
        my_a = A()
        print(my_a.m1(sleep_time=0.5, timeout=0.7))
        print(my_a.m1(sleep_time=1.5, timeout=1.2))
        print(my_a.m1(sleep_time=1.5, timeout=1.8))
        print('mainline exiting')

        expected_result = 'mainline entered\n'
        expected_result += 'True\n'
        expected_result += 'False\n'
        expected_result += 'True\n'
        expected_result += 'mainline exiting\n'

        captured = capsys.readouterr().out

        assert captured == expected_result

    ####################################################################
    # test_timer_example4
    ####################################################################
    def test_timer_example4(self,
                            capsys: Any) -> None:
        """Test timer example4.

        Args:
            capsys: pytest fixture to capture print output

        """
        class A:
            def __init__(self, default_timeout: float):
                self.a = 1
                self.default_timeout = default_timeout

            def m1(self,
                   sleep_time: float,
                   timeout: Optional[float] = None) -> bool:
                timer = Timer(timeout=timeout,
                              default_timeout=self.default_timeout)
                time.sleep(sleep_time)
                if timer.is_expired():
                    return False
                return True

        print('mainline entered')
        my_a = A(default_timeout=1.2)
        print(my_a.m1(sleep_time=0.5))
        print(my_a.m1(sleep_time=1.5))
        print(my_a.m1(sleep_time=0.5, timeout=0.3))
        print(my_a.m1(sleep_time=1.5, timeout=1.8))
        print(my_a.m1(sleep_time=1.5, timeout=0))
        print('mainline exiting')

        expected_result = 'mainline entered\n'
        expected_result += 'True\n'
        expected_result += 'False\n'
        expected_result += 'False\n'
        expected_result += 'True\n'
        expected_result += 'True\n'
        expected_result += 'mainline exiting\n'

        captured = capsys.readouterr().out

        assert captured == expected_result

    ####################################################################
    # test_timer_example5
    ####################################################################
    def test_timer_example5(self,
                            capsys: Any) -> None:
        """Test timer example5.

        Args:
            capsys: pytest fixture to capture print output

        """
        def f1() -> None:
            print('f1 entered')
            time.sleep(1)
            f1_event.set()
            time.sleep(1)
            f1_event.set()
            time.sleep(1)
            f1_event.set()
            print('f1 exiting')

        print('mainline entered')
        timer = Timer(timeout=2.5)
        f1_thread = threading.Thread(target=f1)
        f1_event = threading.Event()
        f1_thread.start()
        wait_result = f1_event.wait(timeout=timer.remaining_time())
        print(f'wait1 result = {wait_result}')
        f1_event.clear()
        print(f'remaining time = {timer.remaining_time():0.1f}')
        print(f'timer expired = {timer.is_expired()}')
        wait_result = f1_event.wait(timeout=timer.remaining_time())
        print(f'wait2 result = {wait_result}')
        f1_event.clear()
        print(f'remaining time = {timer.remaining_time():0.1f}')
        print(f'timer expired = {timer.is_expired()}')
        wait_result = f1_event.wait(timeout=timer.remaining_time())
        print(f'wait3 result = {wait_result}')
        f1_event.clear()
        print(f'remaining time = {timer.remaining_time():0.4f}')
        print(f'timer expired = {timer.is_expired()}')
        f1_thread.join()
        print('mainline exiting')

        expected_result = 'mainline entered\n'
        expected_result += 'f1 entered\n'
        expected_result += 'wait1 result = True\n'
        expected_result += 'remaining time = 1.5\n'
        expected_result += 'timer expired = False\n'
        expected_result += 'wait2 result = True\n'
        expected_result += 'remaining time = 0.5\n'
        expected_result += 'timer expired = False\n'
        expected_result += 'wait3 result = False\n'
        expected_result += 'remaining time = 0.0001\n'
        expected_result += 'timer expired = True\n'
        expected_result += 'f1 exiting\n'
        expected_result += 'mainline exiting\n'

        captured = capsys.readouterr().out

        assert captured == expected_result

    ####################################################################
    # test_timer_example6
    ####################################################################
    def test_timer_example6(self,
                            capsys: Any) -> None:
        """Test timer example6.

        Args:
            capsys: pytest fixture to capture print output

        """
        print('mainline entered')
        timer = Timer(timeout=2.5)
        time.sleep(1)
        print(f'timer expired = {timer.is_expired()}')
        time.sleep(1)
        print(f'timer expired = {timer.is_expired()}')
        time.sleep(1)
        print(f'timer expired = {timer.is_expired()}')
        print('mainline exiting')

        expected_result = 'mainline entered\n'
        expected_result += 'timer expired = False\n'
        expected_result += 'timer expired = False\n'
        expected_result += 'timer expired = True\n'
        expected_result += 'mainline exiting\n'

        captured = capsys.readouterr().out

        assert captured == expected_result


########################################################################
# TestTimerBasic class
########################################################################
class TestTimerBasic:
    """Test basic functions of Timer."""

    ####################################################################
    # test_timer_case1a
    ####################################################################
    def test_timer_correct_source(self) -> None:
        """Test timer correct source."""
        print('\nmainline entered')
        print(f'{inspect.getsourcefile(Timer)=}')
        exp1 = ('C:\\Users\\Tiger\\PycharmProjects\\scottbrian_utils\\.tox'
                '\\py39-pytest\\lib\\site-packages\\scottbrian_utils\\timer'
                '.py')
        exp2 = ('C:\\Users\\Tiger\\PycharmProjects\\scottbrian_utils\\.tox'
                '\\py39-coverage\\lib\\site-packages\\scottbrian_utils\\timer'
                '.py')
        actual = inspect.getsourcefile(Timer)
        assert (actual == exp1) or (actual == exp2)
        print('mainline exiting')

    ####################################################################
    # test_timer_case1a
    ####################################################################
    def test_timer_case1a(self) -> None:
        """Test timer case1a."""
        print('mainline entered')
        timer = Timer()
        time.sleep(1)
        assert not timer.is_expired()
        time.sleep(1)
        assert not timer.is_expired()
        print('mainline exiting')

    ####################################################################
    # test_timer_case1b
    ####################################################################
    def test_timer_case1b(self) -> None:
        """Test timer case1b."""
        print('mainline entered')
        timer = Timer(default_timeout=None)
        time.sleep(1)
        assert not timer.is_expired()
        time.sleep(1)
        assert not timer.is_expired()
        print('mainline exiting')

    ####################################################################
    # test_timer_case1c
    ####################################################################
    def test_timer_case1c(self) -> None:
        """Test timer case1c."""
        print('mainline entered')
        timer = Timer(timeout=None)
        time.sleep(1)
        assert not timer.is_expired()
        time.sleep(1)
        assert not timer.is_expired()
        print('mainline exiting')

    ####################################################################
    # test_timer_case1d
    ####################################################################
    def test_timer_case1d(self) -> None:
        """Test timer case1d."""
        print('mainline entered')
        timer = Timer(timeout=None, default_timeout=None)
        time.sleep(1)
        assert not timer.is_expired()
        time.sleep(1)
        assert not timer.is_expired()
        print('mainline exiting')

    ####################################################################
    # test_timer_case2a
    ####################################################################
    def test_timer_case2a(self,
                          zero_or_less_default_timeout_arg: IntFloat
                          ) -> None:
        """Test timer case2a.

        Args:
            zero_or_less_default_timeout_arg: pytest fixture for timeout
                                                seconds

        """
        print('mainline entered')
        timer = Timer(default_timeout=zero_or_less_default_timeout_arg)
        time.sleep(abs(zero_or_less_default_timeout_arg * 0.9))
        assert not timer.is_expired()
        time.sleep(abs(zero_or_less_default_timeout_arg))
        assert not timer.is_expired()
        print('mainline exiting')

    ####################################################################
    # test_timer_case2b
    ####################################################################

    def test_timer_case2b(self,
                          zero_or_less_default_timeout_arg: IntFloat
                          ) -> None:
        """Test timer case2b.

        Args:
            zero_or_less_default_timeout_arg: pytest fixture for timeout
                                                seconds

        """
        print('mainline entered')
        timer = Timer(timeout=None,
                      default_timeout=zero_or_less_default_timeout_arg)
        time.sleep(abs(zero_or_less_default_timeout_arg * 0.9))
        assert not timer.is_expired()
        time.sleep(abs(zero_or_less_default_timeout_arg))
        assert not timer.is_expired()
        print('mainline exiting')

    ####################################################################
    # test_timer_case3a
    ####################################################################
    def test_timer_case3a(self,
                          greater_than_zero_default_timeout_arg: IntFloat
                          ) -> None:
        """Test timer case3a.

        Args:
            greater_than_zero_default_timeout_arg: pytest fixture for
                                                     timeout seconds

        """
        print('mainline entered')
        timer = Timer(default_timeout=greater_than_zero_default_timeout_arg)
        time.sleep(greater_than_zero_default_timeout_arg * 0.9)
        assert not timer.is_expired()
        time.sleep(greater_than_zero_default_timeout_arg)
        assert timer.is_expired()
        print('mainline exiting')

    ####################################################################
    # test_timer_case3b
    ####################################################################
    def test_timer_case3b(self,
                          greater_than_zero_default_timeout_arg: IntFloat
                          ) -> None:
        """Test timer case3b.

        Args:
            greater_than_zero_default_timeout_arg: pytest fixture for
                                                     timeout seconds

        """
        print('mainline entered')
        timer = Timer(timeout=None,
                      default_timeout=greater_than_zero_default_timeout_arg)
        time.sleep(greater_than_zero_default_timeout_arg * 0.9)
        assert not timer.is_expired()
        time.sleep(greater_than_zero_default_timeout_arg)
        assert timer.is_expired()
        print('mainline exiting')

    ####################################################################
    # test_timer_case4a
    ####################################################################
    def test_timer_case4a(self,
                          zero_or_less_timeout_arg: IntFloat) -> None:
        """Test timer case4a.

        Args:
            zero_or_less_timeout_arg: pytest fixture for timeout seconds

        """
        print('mainline entered')
        timer = Timer(timeout=zero_or_less_timeout_arg)
        time.sleep(abs(zero_or_less_timeout_arg * 0.9))
        assert not timer.is_expired()
        time.sleep(abs(zero_or_less_timeout_arg))
        assert not timer.is_expired()
        print('mainline exiting')

    ####################################################################
    # test_timer_case4b
    ####################################################################
    def test_timer_case4b(self,
                          zero_or_less_timeout_arg: IntFloat) -> None:
        """Test timer case4b.

        Args:
            zero_or_less_timeout_arg: pytest fixture for timeout seconds

        """
        print('mainline entered')
        timer = Timer(timeout=zero_or_less_timeout_arg,
                      default_timeout=None)
        time.sleep(abs(zero_or_less_timeout_arg * 0.9))
        assert not timer.is_expired()
        time.sleep(abs(zero_or_less_timeout_arg))
        assert not timer.is_expired()
        print('mainline exiting')

    ####################################################################
    # test_timer_case5
    ####################################################################
    def test_timer_case5(self,
                         zero_or_less_timeout_arg: IntFloat,
                         zero_or_less_default_timeout_arg: IntFloat
                         ) -> None:
        """Test timer case5.

        Args:
            zero_or_less_timeout_arg: pytest fixture for timeout seconds
            zero_or_less_default_timeout_arg: pytest fixture for timeout
                                                seconds

        """
        print('mainline entered')
        timer = Timer(timeout=zero_or_less_timeout_arg,
                      default_timeout=zero_or_less_default_timeout_arg)
        time.sleep(abs(zero_or_less_timeout_arg * 0.9))
        assert not timer.is_expired()
        time.sleep(abs(zero_or_less_timeout_arg))
        assert not timer.is_expired()
        print('mainline exiting')

    ####################################################################
    # test_timer_case6
    ####################################################################
    def test_timer_case6(self,
                         zero_or_less_timeout_arg: IntFloat,
                         greater_than_zero_default_timeout_arg: IntFloat
                         ) -> None:
        """Test timer case6.

        Args:
            zero_or_less_timeout_arg: pytest fixture for timeout seconds
            greater_than_zero_default_timeout_arg: pytest fixture for
                                                     timeout seconds

        """
        print('mainline entered')
        timer = Timer(timeout=zero_or_less_timeout_arg,
                      default_timeout=greater_than_zero_default_timeout_arg)
        time.sleep(abs(zero_or_less_timeout_arg * 0.9))
        assert not timer.is_expired()
        time.sleep(abs(zero_or_less_timeout_arg))
        assert not timer.is_expired()
        print('mainline exiting')

    ####################################################################
    # test_timer_case7a
    ####################################################################
    def test_timer_case7a(self,
                          greater_than_zero_timeout_arg: IntFloat) -> None:
        """Test timer case7a.

        Args:
            greater_than_zero_timeout_arg: pytest fixture for timeout
                                             seconds

        """
        print('mainline entered')
        timer = Timer(timeout=greater_than_zero_timeout_arg)
        time.sleep(greater_than_zero_timeout_arg * 0.9)
        assert not timer.is_expired()
        time.sleep(greater_than_zero_timeout_arg)
        assert timer.is_expired()
        print('mainline exiting')

    ####################################################################
    # test_timer_case7b
    ####################################################################
    def test_timer_case7b(self,
                          greater_than_zero_timeout_arg: IntFloat) -> None:
        """Test timer case7b.

        Args:
            greater_than_zero_timeout_arg: pytest fixture for timeout
                                             seconds

        """
        print('mainline entered')
        timer = Timer(timeout=greater_than_zero_timeout_arg,
                      default_timeout=None)
        time.sleep(greater_than_zero_timeout_arg * 0.9)
        assert not timer.is_expired()
        time.sleep(greater_than_zero_timeout_arg)
        assert timer.is_expired()
        print('mainline exiting')

    ####################################################################
    # test_timer_case8
    ####################################################################
    def test_timer_case8(self,
                         greater_than_zero_timeout_arg: IntFloat,
                         zero_or_less_default_timeout_arg: IntFloat
                         ) -> None:
        """Test timer case8.

        Args:
            greater_than_zero_timeout_arg: pytest fixture for timeout
                                             seconds
            zero_or_less_default_timeout_arg: pytest fixture for timeout
                                                seconds

        """
        print('mainline entered')
        timer = Timer(timeout=greater_than_zero_timeout_arg,
                      default_timeout=zero_or_less_default_timeout_arg)
        time.sleep(greater_than_zero_timeout_arg * 0.9)
        assert not timer.is_expired()
        time.sleep(greater_than_zero_timeout_arg)
        assert timer.is_expired()
        print('mainline exiting')

    ####################################################################
    # test_timer_case9
    ####################################################################
    def test_timer_case9(self,
                         greater_than_zero_timeout_arg: IntFloat,
                         greater_than_zero_default_timeout_arg: IntFloat
                         ) -> None:
        """Test timer case9.

        Args:
            greater_than_zero_timeout_arg: pytest fixture for timeout
                                             seconds
            greater_than_zero_default_timeout_arg: pytest fixture for
                                                     timeout seconds
        """
        print('mainline entered')
        timer = Timer(timeout=greater_than_zero_timeout_arg,
                      default_timeout=greater_than_zero_default_timeout_arg)
        time.sleep(greater_than_zero_timeout_arg * 0.9)
        assert not timer.is_expired()
        time.sleep(greater_than_zero_timeout_arg)
        assert timer.is_expired()
        print('mainline exiting')


########################################################################
# TestTimerBasic class
########################################################################
class TestTimerRemainingTime:
    """Test remaining_time method of Timer."""

    ####################################################################
    # test_timer_remaining_time1
    ####################################################################
    def test_timer_remaining_time1(self,
                                   timeout_arg: IntFloat) -> None:
        """Test timer remaining time1.

        Args:
            timeout_arg: number of seconds to use for timer timeout arg

        """
        tolerance_factor = 0.80
        logger.debug('mainline entered')
        stop_watch = StopWatch()
        sleep_time = timeout_arg/3
        exp_remaining_time1: float = timeout_arg - sleep_time
        exp_remaining_time2: float = timeout_arg - sleep_time * 2
        exp_remaining_time3 = 0.0001

        timer = Timer(timeout=timeout_arg)
        stop_watch.start_clock(clock_iter=1)
        stop_watch.pause(sleep_time, clock_iter=1)

        rem_time = timer.remaining_time()
        assert ((exp_remaining_time1 * tolerance_factor)
                <= cast(float, rem_time)
                <= exp_remaining_time1)
        assert not timer.is_expired()
        logger.debug(f'after third 1: '
                     f'{exp_remaining_time1=}, {rem_time=}')

        stop_watch.pause(sleep_time * 2, clock_iter=1)

        rem_time = timer.remaining_time()
        assert ((exp_remaining_time2 * tolerance_factor)
                <= cast(float, rem_time)
                <= exp_remaining_time2)
        assert not timer.is_expired()
        logger.debug(f'after third 2: '
                     f'{exp_remaining_time2=}, {rem_time=}')

        time.sleep(sleep_time + 0.1)

        rem_time = timer.remaining_time()
        assert exp_remaining_time3 == cast(float, rem_time)
        assert timer.is_expired()

        logger.debug(f'after third 3: '
                     f'{exp_remaining_time3=}, {rem_time=}')

        logger.debug(f'{stop_watch.start_time=} '
                     f'{timer.start_time=}')

        logger.debug('mainline exiting')

    ####################################################################
    # test_timer_remaining_time_none
    ####################################################################
    def test_timer_remaining_time_none(self) -> None:
        """Test timer remaining time none2."""
        logger.debug('mainline entered')

        timer = Timer(timeout=None)
        time.sleep(1)
        assert timer.remaining_time() is None
        assert not timer.is_expired()

        time.sleep(1)

        assert timer.remaining_time() is None
        assert not timer.is_expired()

        logger.debug('mainline exiting')
