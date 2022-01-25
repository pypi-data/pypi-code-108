"""test_stop_watch.py module."""

########################################################################
# Standard Library
########################################################################
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
from scottbrian_utils.stop_watch import StopWatch

########################################################################
# type aliases
########################################################################
IntFloat = Union[int, float]
OptIntFloat = Optional[IntFloat]

########################################################################
# Set up logging
########################################################################
logger = logging.getLogger(__name__)
logger.debug('about to start the tests')


########################################################################
# StopWatch test exceptions
########################################################################
class ErrorTstStopWatch(Exception):
    """Base class for exceptions in this module."""
    pass


########################################################################
# timeout_arg fixture
########################################################################
timeout_arg_list = [0.0, 0.3, 0.5, 1, 2, 4]


@pytest.fixture(params=timeout_arg_list)  # type: ignore
def timeout_arg(request: Any) -> float:
    """Using different seconds for timeout.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(float, request.param)


#######################################################################
# sleep_arg fixture
########################################################################
sleep_arg_list = [0.3, 1.0, 2, 2.5]


@pytest.fixture(params=sleep_arg_list)  # type: ignore
def sleep_arg(request: Any) -> float:
    """Using different remote thread start points.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(float, request.param)


########################################################################
# TestStopWatchClock class
########################################################################
class TestBasicStopWatch:
    """Test StopWatch repr."""

    ####################################################################
    # test_stop_watch_repr
    ####################################################################
    def test_stop_watch_repr(self) -> None:
        """Test StopWatch repr."""
        logger.debug('mainline entered')

        stop_watch = StopWatch()
        expected_repr_string = 'StopWatch()'
        assert repr(stop_watch) == expected_repr_string

        logger.debug('mainline exiting')

    ####################################################################
    # test_stop_watch_pause
    ####################################################################
    def test_stop_watch_pause(self,
                              sleep_arg: IntFloat) -> None:
        """Test StopWatch pause.

        Args:
            sleep_arg: pytest fixture for number seconds to pause

        """
        logger.debug('mainline entered')

        stop_watch = StopWatch()
        start_time = time.time()
        stop_watch.start_clock(clock_iter=1)
        stop_watch.pause(seconds=sleep_arg, clock_iter=1)
        duration = stop_watch.duration()
        time_paused = time.time() - start_time

        assert (sleep_arg
                <= duration
                <= (sleep_arg * 1.1)
                )
        assert (sleep_arg
                <= time_paused
                <= (sleep_arg * 1.1)
                )

        logger.debug('mainline exiting')


########################################################################
# TestStopWatchExamples class
########################################################################
class TestStopWatchExamples:
    """Test examples of StopWatch."""

    ####################################################################
    # test_stop_watch_example
    ####################################################################
    def test_stop_watch_example(self,
                                capsys: Any) -> None:
        """Test stop_watch example.

        Args:
            capsys: pytest fixture to capture print output

        """
        def f1() -> None:
            """Beta f1 function."""
            print('f1 entered')
            stop_watch.start_clock(clock_iter=1)
            print('f1 about to wait')
            f1_event.wait()
            print('f1 back from wait')
            assert 2.5 <= stop_watch.duration() <= 2.6
            print('f1 exiting')

        print('mainline entered')
        stop_watch = StopWatch()
        f1_event = threading.Event()
        f1_thread = threading.Thread(target=f1)
        print('mainline about to start f1')
        f1_thread.start()
        stop_watch.pause(2.5, clock_iter=1)
        print('mainline about set f1_event')
        f1_event.set()
        f1_thread.join()
        print('mainline exiting')

        expected_result = 'mainline entered\n'
        expected_result += 'mainline about to start f1\n'
        expected_result += 'f1 entered\n'
        expected_result += 'f1 about to wait\n'
        expected_result += 'mainline about set f1_event\n'
        expected_result += 'f1 back from wait\n'
        expected_result += 'f1 exiting\n'
        expected_result += 'mainline exiting\n'
        captured = capsys.readouterr().out

        assert captured == expected_result


########################################################################
# TestStopWatchClock class
########################################################################
class TestStopWatch:
    """Test start_clock, pause, and duration methods of StopWatch."""

    ####################################################################
    # test_stop_watch1
    ####################################################################
    def test_stop_watch1(self,
                         sleep_arg: float) -> None:
        """Test start_clock and duration methods.

        Args:
            sleep_arg: how long to sleep to test duration

        """

        def f1() -> None:
            """Beta f1 function."""
            logger.debug('f1 beta entered')
            stop_watch.start_clock(clock_iter=2)
            f1_event.set()
            time.sleep(sleep_arg)
            assert sleep_arg <= stop_watch.duration() <= late_time
            logger.debug('f1 beta exiting')

        def f2() -> None:
            """Charlie f2 function."""
            logger.debug('f2 charlie entered')
            f2a_event.set()
            f2b_event.wait()
            stop_watch.start_clock(clock_iter=5)
            time.sleep(sleep_arg)
            assert sleep_arg <= stop_watch.duration() <= late_time
            logger.debug('f2 charlie exiting')

        logger.debug('mainline entered')
        stop_watch = StopWatch()
        f1_event = threading.Event()
        f2a_event = threading.Event()
        f2b_event = threading.Event()

        late_time = sleep_arg * 1.1
        stop_watch.start_clock(clock_iter=1)
        time.sleep(sleep_arg)
        assert sleep_arg <= stop_watch.duration() <= late_time

        f1_thread = threading.Thread(target=f1)
        logger.debug('mainline starting beta')
        f1_thread.start()
        f1_event.wait()
        stop_watch.start_clock(clock_iter=3)
        time.sleep(sleep_arg)
        assert sleep_arg <= stop_watch.duration() <= late_time

        logger.debug('mainline about to join f1 beta')
        f1_thread.join()

        f2_thread = threading.Thread(target=f2)
        logger.debug('mainline starting charlie')
        f2_thread.start()
        f2a_event.wait()
        stop_watch.start_clock(clock_iter=4)
        f2b_event.set()
        time.sleep(sleep_arg)
        assert sleep_arg <= stop_watch.duration() <= late_time

        logger.debug('mainline about to join f2 charlie')
        f2_thread.join()

        logger.debug('mainline exiting')

    ####################################################################
    # test_stop_watch2
    ####################################################################
    def test_stop_watch2(self,
                         sleep_arg: float) -> None:
        """Test start_clock and duration methods.

        Args:
            sleep_arg: how long to sleep to test duration

        """

        def f1() -> None:
            """Beta f1 function."""
            logger.debug('f1 beta entered')
            stop_watch.start_clock(clock_iter=1)
            f1_event.set()
            time.sleep(f1_sleep_time)
            assert f1_sleep_time <= stop_watch.duration() <= f1_late_time
            logger.debug('f1 beta exiting')

        def f2() -> None:
            """Charlie f2 function."""
            logger.debug('f2 charlie entered')
            assert stop_watch.clock_in_use is True
            assert stop_watch.clock_iter == 1
            iter1_start_time = stop_watch.start_time
            assert stop_watch.clock_in_use is True
            assert stop_watch.clock_iter == 1
            stop_watch.start_clock(clock_iter=2)
            time.sleep(f2_sleep_time)
            assert f2_sleep_time <= stop_watch.duration() <= f2_late_time
            assert (sum_sleep_time
                    <= (time.time() - iter1_start_time)
                    <= sum_late_sleep_time)
            logger.debug('f2 charlie exiting')

        logger.debug('mainline entered')
        stop_watch = StopWatch()
        assert stop_watch.clock_in_use is False

        f1_sleep_time = sleep_arg * 2
        f1_late_time = f1_sleep_time * 1.1

        f2_sleep_time = sleep_arg
        f2_late_time = f2_sleep_time * 1.1

        sum_sleep_time = f1_sleep_time + f2_sleep_time
        sum_late_sleep_time = sum_sleep_time * 1.1

        f1_event = threading.Event()

        f1_thread = threading.Thread(target=f1)
        f2_thread = threading.Thread(target=f2)

        logger.debug('mainline starting beta')
        f1_thread.start()
        f1_event.wait()
        assert stop_watch.clock_in_use is True
        assert stop_watch.clock_iter == 1

        logger.debug('mainline starting charlie')
        f2_thread.start()

        logger.debug('mainline about to join f1 beta')
        f1_thread.join()

        logger.debug('mainline about to join f2 charlie')
        f2_thread.join()

        assert stop_watch.clock_in_use is False
        assert stop_watch.clock_iter == 2

        logger.debug('mainline exiting')

    ####################################################################
    # test_stop_watch3
    ####################################################################
    def test_stop_watch3(self,
                         sleep_arg: float) -> None:
        """Test start_clock and pause methods.

        Args:
            sleep_arg: how long to sleep to test duration

        """

        def f1() -> None:
            """Beta f1 function."""
            logger.debug('f1 beta entered')
            stop_watch.start_clock(clock_iter=1)
            f1_event.set()
            time.sleep(f1_sleep_time)
            assert f1_sleep_time <= stop_watch.duration() <= f1_late_time

            stop_watch.start_clock(clock_iter=2)
            time.sleep(f1_sleep_time)
            assert f1_sleep_time <= stop_watch.duration() <= f1_late_time
            logger.debug('f1 beta exiting')

        def f2() -> None:
            """Charlie f2 function."""
            logger.debug('f2 charlie entered')
            assert stop_watch.clock_in_use is True
            assert stop_watch.clock_iter == 1
            iter1_start_time = stop_watch.start_time
            assert stop_watch.clock_in_use is True
            assert stop_watch.clock_iter == 1
            stop_watch.pause(f2_pause_time, clock_iter=2)
            f2_pause_duration = time.time() - iter1_start_time
            assert f2_exp_pause_duration <= f2_pause_duration <= f2_late_time

            logger.debug('f2 charlie exiting')

        logger.debug('mainline entered')
        stop_watch = StopWatch()
        assert stop_watch.clock_in_use is False

        f1_sleep_time = sleep_arg
        f1_late_time = f1_sleep_time * 1.1

        f2_pause_time = sleep_arg * 0.5
        f2_exp_pause_duration = f1_sleep_time + f2_pause_time
        f2_late_time = f2_exp_pause_duration * 1.1

        f1_event = threading.Event()

        f1_thread = threading.Thread(target=f1)
        f2_thread = threading.Thread(target=f2)

        logger.debug('mainline starting beta')
        f1_thread.start()
        f1_event.wait()
        assert stop_watch.clock_in_use is True
        assert stop_watch.clock_iter == 1

        logger.debug('mainline starting charlie')
        f2_thread.start()

        logger.debug('mainline about to join f1 beta')
        f1_thread.join()

        logger.debug('mainline about to join f2 charlie')
        f2_thread.join()

        assert stop_watch.clock_in_use is False
        assert stop_watch.clock_iter == 2

        logger.debug('mainline exiting')

    ####################################################################
    # test_stop_watch_start_multi
    ####################################################################
    def test_stop_watch_start_multi(self,
                                    sleep_arg: IntFloat) -> None:
        """Test StopWatch repr.

        Args:
            sleep_arg: pytest fixture for number seconds to pause

        """
        def f1() -> None:
            """F1 thread."""
            logger.debug('f1 entered')
            ml_event.set()
            f1_event.wait()
            f1_start_time = time.time()
            stop_watch.start_clock(clock_iter=2)
            f1_start_clock_wait_time = time.time() - f1_start_time

            stop_watch.pause(seconds=sleep_arg, clock_iter=2)
            f1_duration = stop_watch.duration()

            assert (sleep_arg
                    <= f1_start_clock_wait_time
                    <= (sleep_arg * 1.1)
                    )
            assert (sleep_arg
                    <= f1_duration
                    <= (sleep_arg * 1.1)
                    )

            f1_start_time = time.time()
            ml_event.set()
            stop_watch.pause(seconds=sleep_arg, clock_iter=3)
            f1_total_pause_time = time.time() - f1_start_time
            f1_duration = stop_watch.duration()

            assert ((sleep_arg * 2)
                    <= f1_total_pause_time
                    <= (sleep_arg * 2 * 1.1)
                    )
            assert (sleep_arg
                    <= f1_duration
                    <= (sleep_arg * 1.1)
                    )

            logger.debug('f1 exiting')

        logger.debug('mainline entered')
        ml_event = threading.Event()
        f1_event = threading.Event()
        stop_watch = StopWatch()

        f1_thread = threading.Thread(target=f1)

        start_time = time.time()

        f1_thread.start()
        ml_event.wait()
        ml_event.clear()
        stop_watch.start_clock(clock_iter=1)
        f1_event.set()
        stop_watch.pause(seconds=sleep_arg, clock_iter=1)
        duration = stop_watch.duration()
        time_paused = time.time() - start_time

        assert (sleep_arg
                <= duration
                <= (sleep_arg * 1.1)
                )
        assert (sleep_arg
                <= time_paused
                <= (sleep_arg * 1.1)
                )

        ml_event.wait()
        time.sleep(sleep_arg)
        stop_watch.start_clock(clock_iter=3)
        f1_thread.join()
        logger.debug('mainline exiting')
