"""test_se_lock.py module."""

########################################################################
# Standard Library
########################################################################
from dataclasses import dataclass
import logging
import threading
import time
from typing import Any, cast, Optional

########################################################################
# Third Party
########################################################################
from scottbrian_utils.flower_box import print_flower_box_msg as flowers
from scottbrian_utils.msgs import Msgs
from scottbrian_utils.stop_watch import StopWatch
import pytest

########################################################################
# Local
########################################################################
from scottbrian_locking.se_lock import SELock, SELockShare, SELockExcl
from scottbrian_locking.se_lock import AttemptedReleaseByExclusiveWaiter
from scottbrian_locking.se_lock import AttemptedReleaseBySharedWaiter
from scottbrian_locking.se_lock import AttemptedReleaseOfUnownedLock
from scottbrian_locking.se_lock import SELockObtainTimeout
from scottbrian_locking.se_lock import SELockOwnerNotAlive


########################################################################
# Set up logging
########################################################################
logger = logging.getLogger(__name__)
logger.debug('about to start the tests')


########################################################################
# SELock test exceptions
########################################################################
class ErrorTstSELock(Exception):
    """Base class for exception in this module."""
    pass


class InvalidRouteNum(ErrorTstSELock):
    """InvalidRouteNum exception class."""
    pass


class Invalid_ModeNum(ErrorTstSELock):
    """Invalid_ModeNum exception class."""
    pass


class BadRequestStyleArg(ErrorTstSELock):
    """BadRequestStyleArg exception class."""
    pass


########################################################################
# number_requests_arg fixture
########################################################################
number_requests_arg_list = [0, 1, 2, 3]


@pytest.fixture(params=number_requests_arg_list)  # type: ignore
def num_share_requests1_arg(request: Any) -> int:
    """Using different requests.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(int, request.param)


@pytest.fixture(params=number_requests_arg_list)  # type: ignore
def num_share_requests2_arg(request: Any) -> int:
    """Using different requests.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(int, request.param)


@pytest.fixture(params=number_requests_arg_list)  # type: ignore
def num_excl_requests1_arg(request: Any) -> int:
    """Using different requests.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(int, request.param)


@pytest.fixture(params=number_requests_arg_list)  # type: ignore
def num_excl_requests2_arg(request: Any) -> int:
    """Using different requests.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(int, request.param)


########################################################################
# release_position_arg fixture
########################################################################
release_position_arg_list = [0, 1, 2]


@pytest.fixture(params=release_position_arg_list)  # type: ignore
def release_position_arg(request: Any) -> int:
    """Using different release positions.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(int, request.param)


########################################################################
# use_context_arg fixture
########################################################################
use_context_arg_list = [0, 1, 2]


@pytest.fixture(params=use_context_arg_list)  # type: ignore
def use_context_arg(request: Any) -> int:
    """Use context lock obtain.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(int, request.param)


########################################################################
# use_context2_arg fixture
########################################################################
use_context2_arg_list = [0, 1, 2, 3]


@pytest.fixture(params=use_context2_arg_list)  # type: ignore
def use_context2_arg(request: Any) -> int:
    """Use context lock obtain.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(int, request.param)


########################################################################
# use_timeout_arg fixture
########################################################################
use_timeout_arg_list = [True, False]


@pytest.fixture(params=use_timeout_arg_list)  # type: ignore
def use_timeout_arg(request: Any) -> bool:
    """Using timeout.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(bool, request.param)


########################################################################
# timeout_arg fixture
########################################################################
timeout_arg_list = [0.1, 0.5, 12]


@pytest.fixture(params=timeout_arg_list)  # type: ignore
def timeout_arg(request: Any) -> float:
    """Using different timeout values.

    Args:
        request: special fixture that returns the fixture params

    Returns:
        The params values are returned one at a time
    """
    return cast(float, request.param)


########################################################################
# TestSELockBasic class to test SELock methods
########################################################################
class TestSELockErrors:
    """TestSELock class."""

    def test_se_lock_release_unowned_lock(self) -> None:
        """Test release of unowned lock."""
        ################################################################
        # AttemptedReleaseOfUnownedLock
        ################################################################
        with pytest.raises(AttemptedReleaseOfUnownedLock):
            a_lock = SELock()
            a_lock.release()

    def test_se_lock_release_owner_not_alive(self) -> None:
        """Test owner become not alive while waiting for lock."""
        ################################################################
        # SELockOwnerNotAlive
        ################################################################
        def f1() -> None:
            """Function that obtains lock and end still holding it."""
            # a_lock.obtain(mode=SELock._Mode.EXCL)
            a_lock.obtain_excl()

        with pytest.raises(SELockOwnerNotAlive):
            a_lock = SELock()
            f1_thread = threading.Thread(target=f1)
            f1_thread.start()
            f1_thread.join()

            # f1 obtained the lock and exited
            # a_lock.obtain(mode=SELock._Mode.EXCL)
            a_lock.obtain_excl()

        f1_thread.join()

    def test_se_lock_release_by_exclusive_waiter(self) -> None:
        """Test release by exclusive waiter."""
        ################################################################
        # AttemptedReleaseByExclusiveWaiter
        ################################################################
        def f2() -> None:
            """Function that gets lock exclusive to cause contention."""
            # a_lock.obtain(mode=SELock._Mode.EXCL)
            a_lock.obtain_excl()
            a_event.set()
            a_event2.wait()

        def f3() -> None:
            """Function that tries to release lock while waiting."""
            # a_lock.obtain(mode=SELock._Mode.EXCL)
            a_lock.obtain_excl()
            with pytest.raises(AttemptedReleaseByExclusiveWaiter):
                a_lock.release()

        a_lock = SELock()
        a_event = threading.Event()
        a_event2 = threading.Event()
        f2_thread = threading.Thread(target=f2)
        f3_thread = threading.Thread(target=f3)

        # start f2 to get the lock exclusive
        f2_thread.start()

        # wait for f2 to tell us it has the lock
        a_event.wait()

        # start f3 to queue up for the lock behind f2
        f3_thread.start()

        # post (prematurely) the event in the SELock for f3
        a_lock.owner_wait_q[1].event.set()

        # tell f2 to end - we will leave the lock damaged
        a_event2.set()

        f2_thread.join()
        f3_thread.join()

    def test_se_lock_release_by_shared_waiter(self) -> None:
        """Test release by shared waiter."""
        ################################################################
        # AttemptedReleaseBySharedWaiter
        ################################################################
        def f4() -> None:
            """Function that gets lock exclusive to cause contention."""
            # a_lock.obtain(mode=SELock._Mode.EXCL)
            a_lock.obtain_excl()
            a_event.set()
            a_event2.wait()

        def f5() -> None:
            """Function that tries to release lock while waiting."""
            # a_lock.obtain(mode=SELock._Mode.SHARE)
            a_lock.obtain_share()
            with pytest.raises(AttemptedReleaseBySharedWaiter):
                a_lock.release()

        a_lock = SELock()
        a_event = threading.Event()
        a_event2 = threading.Event()
        f4_thread = threading.Thread(target=f4)
        f5_thread = threading.Thread(target=f5)

        # start f2 to get the lock exclusive
        f4_thread.start()

        # wait for f2 to tell us it has the lock
        a_event.wait()

        # start f3 to queue up for the lock behind f1
        f5_thread.start()

        # post (prematurely) the event in the SELock for f5
        a_lock.owner_wait_q[1].event.set()

        # tell f4 to end - we will leave the lock damaged
        a_event2.set()

        f4_thread.join()
        f5_thread.join()


########################################################################
# TestSELockBasic class to test SELock methods
########################################################################
class TestSELockBasic:
    """Class TestSELockBasic."""

    ####################################################################
    # repr
    ####################################################################
    def test_se_lock_repr(self) -> None:
        """Test the repr of SELock."""
        a_se_lock = SELock()

        expected_repr_str = 'SELock()'

        assert repr(a_se_lock) == expected_repr_str


###############################################################################
# TestSELock class
###############################################################################
class TestSELock:
    """Class TestSELock."""

    ###########################################################################
    # test_se_lock_timeout
    ###########################################################################
    def test_se_lock_timeout(self,
                             timeout_arg: float,
                             use_timeout_arg: int,
                             use_context2_arg: int) -> None:
        """Method to test se_lock without using context manager.

        Args:
            timeout_arg: number of seconds to use for timeout value
            use_timeout_arg: indicates whether to use timeout
            use_context2_arg: indicates whether to obtain lock using
                               the context obtain

        """
        def f1(use_timeout_tf: bool,
               use_context_tf: bool) -> None:
            """Function to get the lock and wait.

            Args:
                use_timeout_tf: indicates whether to specify timeout
                                  on the lock requests
                use_context_tf: indicate whether to use context manager
                    lock obtain or to make the call directly

            """
            logger.debug('f1 entered')
            if use_context_tf:
                if use_timeout_tf:
                    logger.debug('f1 about to obtain excl c with timeout')
                    with SELockExcl(a_lock, timeout=timeout_arg):
                        logger.debug('f1 obtained excl c with timeout')
                        msgs.queue_msg('alpha')
                        msgs.get_msg('beta', timeout=msgs_get_to)
                else:
                    logger.debug('f1 about to obtain excl c without timeout')
                    with SELockExcl(a_lock):
                        logger.debug('f1 obtained excl c without timeout')
                        msgs.queue_msg('alpha')
                        msgs.get_msg('beta', timeout=msgs_get_to)
            else:
                if use_timeout_tf:
                    logger.debug('f1 about to obtain excl with timeout')
                    a_lock.obtain_excl(timeout=timeout_arg)
                    logger.debug('f1 obtained excl with timeout')
                else:
                    logger.debug('f1 about to obtain excl without timeout')
                    a_lock.obtain_excl()
                    logger.debug('f1 obtained excl without timeout')

                msgs.queue_msg('alpha')
                msgs.get_msg('beta', timeout=msgs_get_to)

                a_lock.release()

            if use_context_tf:
                if use_timeout_tf:
                    logger.debug('f1 about to obtain share c with timeout')
                    with SELockShare(a_lock, timeout=timeout_arg):
                        logger.debug('f1 obtained share c with timeout')
                        msgs.queue_msg('alpha')
                        msgs.get_msg('beta', timeout=msgs_get_to)
                else:
                    logger.debug('f1 about to obtain share c without timeout')
                    with SELockShare(a_lock):
                        logger.debug('f1 obtained share c without timeout')
                        msgs.queue_msg('alpha')
                        msgs.get_msg('beta', timeout=msgs_get_to)
            else:
                if use_timeout_tf:
                    logger.debug('f1 about to obtain share with timeout')
                    a_lock.obtain_share(timeout=timeout_arg)
                    logger.debug('f1 obtained share with timeout')
                else:
                    logger.debug('f1 about to obtain share without timeout')
                    a_lock.obtain_share()
                    logger.debug('f1 obtained share without timeout')

                msgs.queue_msg('alpha')
                msgs.get_msg('beta', timeout=msgs_get_to)

            logger.debug('f1 exiting')

        logger.debug('mainline entered')

        msgs = Msgs()
        stop_watch = StopWatch()

        a_lock = SELock()

        to_low = timeout_arg
        to_high = timeout_arg * 1.2

        msgs_get_to = timeout_arg * 4 * 2

        if use_context2_arg == 0:
            ml_use_context_tf = False
            f1_use_context_tf = False
        elif use_context2_arg == 1:
            ml_use_context_tf = False
            f1_use_context_tf = True
        elif use_context2_arg == 2:
            ml_use_context_tf = True
            f1_use_context_tf = False
        else:
            ml_use_context_tf = True
            f1_use_context_tf = True

        f1_thread = threading.Thread(target=f1,
                                     args=(use_timeout_arg,
                                           f1_use_context_tf))
        f1_thread.start()

        logger.debug('mainline about to wait 1')
        msgs.get_msg('alpha')

        logger.debug('mainline about to request excl 1')

        stop_watch.start_clock(clock_iter=1)
        with pytest.raises(SELockObtainTimeout):
            if ml_use_context_tf:
                with SELockExcl(a_lock, timeout=timeout_arg):
                    pass
            else:
                a_lock.obtain_excl(timeout=timeout_arg)
        assert to_low <= stop_watch.duration() <= to_high

        logger.debug('mainline about to request share 1')
        stop_watch.start_clock(clock_iter=2)
        with pytest.raises(SELockObtainTimeout):
            if ml_use_context_tf:
                with SELockShare(a_lock, timeout=timeout_arg):
                    pass
            else:
                a_lock.obtain_share(timeout=timeout_arg)
        assert to_low <= stop_watch.duration() <= to_high

        logger.debug('mainline about to request excl 2')
        stop_watch.start_clock(clock_iter=3)
        with pytest.raises(SELockObtainTimeout):
            if ml_use_context_tf:
                with SELockExcl(a_lock, timeout=timeout_arg):
                    pass
            else:
                a_lock.obtain_excl(timeout=timeout_arg)
        assert to_low <= stop_watch.duration() <= to_high

        logger.debug('mainline about to request share 2')
        stop_watch.start_clock(clock_iter=4)
        with pytest.raises(SELockObtainTimeout):
            if ml_use_context_tf:
                with SELockShare(a_lock, timeout=timeout_arg):
                    pass
            else:
                a_lock.obtain_share(timeout=timeout_arg)
        assert to_low <= stop_watch.duration() <= to_high

        msgs.queue_msg('beta')

        logger.debug('mainline about to wait 2')
        msgs.get_msg('alpha')

        logger.debug('mainline about to request excl 3')
        stop_watch.start_clock(clock_iter=5)
        with pytest.raises(SELockObtainTimeout):
            if ml_use_context_tf:
                with SELockExcl(a_lock, timeout=timeout_arg):
                    pass
            else:
                a_lock.obtain_excl(timeout=timeout_arg)
        assert to_low <= stop_watch.duration() <= to_high

        logger.debug('mainline about to request share 3')
        if ml_use_context_tf:
            with SELockShare(a_lock, timeout=timeout_arg):
                pass
        else:
            a_lock.obtain_share(timeout=timeout_arg)
            a_lock.release()

        logger.debug('mainline about to request excl 4')
        stop_watch.start_clock(clock_iter=6)
        with pytest.raises(SELockObtainTimeout):
            if ml_use_context_tf:
                with SELockExcl(a_lock, timeout=timeout_arg):
                    pass
            else:
                a_lock.obtain_excl(timeout=timeout_arg)
        assert to_low <= stop_watch.duration() <= to_high

        logger.debug('mainline about to request share 4')
        if ml_use_context_tf:
            with SELockShare(a_lock, timeout=timeout_arg):
                pass
        else:
            a_lock.obtain_share(timeout=timeout_arg)
            a_lock.release()

        msgs.queue_msg('beta')
        f1_thread.join()
        logger.debug('mainline exiting')

    ###########################################################################
    # test_se_lock_combos
    ###########################################################################
    def test_se_lock_combos(self,
                            num_share_requests1_arg: int,
                            num_excl_requests1_arg: int,
                            num_share_requests2_arg: int,
                            num_excl_requests2_arg: int,
                            release_position_arg: int,
                            use_context_arg: int) -> None:
        """Method to test se_lock without using context manager.

        The following section tests various scenarios of shared and
        exclusive locking.

        We will try combinations of shared and exclusive obtains and
        verify that the order in requests is maintained.

        Scenario:
           1) obtain 0 to 3 shared - verify
           2) obtain 0 to 3 exclusive - verify
           3) obtain 0 to 3 shared - verify
           4) obtain 0 to 3 exclusive - verify

        Args:
            num_share_requests1_arg: number of first share requests
            num_excl_requests1_arg: number of first excl requests
            num_share_requests2_arg: number of second share requests
            num_excl_requests2_arg: number of second excl requests
            release_position_arg: indicates the position among the lock
                                    owners that will release the lock
            use_context_arg: indicate whether to use context manager
                               to request the lock

        """
        num_groups = 4

        def f1(a_event: threading.Event,
               mode: SELock._Mode,
               req_num: int,
               use_context_tf: bool) -> None:
            """Function to get the lock and wait.

            Args:
                a_event: instance of threading.Event
                mode: shared or exclusive
                req_num: request number assigned
                use_context_tf: indicate whether to use context manager
                    lock obtain or to make the call directly

            """
            def f1_verify() -> None:
                """Verify the thread item contains expected info."""
                for f1_item in thread_event_list:
                    if f1_item.req_num == req_num:
                        assert f1_item.thread is threading.current_thread()
                        assert f1_item.mode == mode
                        assert f1_item.lock_obtained is False
                        f1_item.lock_obtained = True
                        break

            if use_context_tf:
                if mode == SELock._Mode.SHARE:
                    with SELockShare(a_lock):
                        f1_verify()
                        a_event.wait()
                else:
                    with SELockExcl(a_lock):
                        f1_verify()
                        a_event.wait()

            else:
                if mode == SELock._Mode.SHARE:
                    a_lock.obtain_share()
                else:
                    a_lock.obtain_excl()
                f1_verify()
                # for f1_item in thread_event_list:
                #     if f1_item.req_num == req_num:
                #         assert f1_item.thread is threading.current_thread()
                #         assert f1_item.mode == mode
                #         assert f1_item.lock_obtained is False
                #         f1_item.lock_obtained = True
                #         break

                a_event.wait()
                a_lock.release()

        @dataclass
        class ThreadEvent:
            thread: threading.Thread
            event: threading.Event
            mode: SELock._Mode
            req_num: int
            lock_obtained: bool

        a_lock = SELock()

        thread_event_list = []

        request_number = -1
        num_requests_list = [num_share_requests1_arg,
                             num_excl_requests1_arg,
                             num_share_requests2_arg,
                             num_excl_requests2_arg]

        num_initial_owners = 0
        initial_owner_mode: Optional[SELock._Mode] = None
        if num_share_requests1_arg:
            num_initial_owners = num_share_requests1_arg
            initial_owner_mode = SELock._Mode.SHARE
            if num_excl_requests1_arg == 0:
                num_initial_owners += num_share_requests2_arg
        elif num_excl_requests1_arg:
            num_initial_owners = 1
            initial_owner_mode = SELock._Mode.EXCL
        elif num_share_requests2_arg:
            num_initial_owners = num_share_requests2_arg
            initial_owner_mode = SELock._Mode.SHARE
        elif num_excl_requests2_arg:
            num_initial_owners = 1
            initial_owner_mode = SELock._Mode.EXCL

        for shr_excl in range(num_groups):
            num_requests = num_requests_list[shr_excl]
            for idx in range(num_requests):
                request_number += 1
                a_event1 = threading.Event()
                if shr_excl == 0 or shr_excl == 2:
                    req_mode = SELock._Mode.SHARE
                else:
                    req_mode = SELock._Mode.EXCL

                if use_context_arg == 0:
                    use_context = False
                elif use_context_arg == 1:
                    use_context = True
                else:
                    if request_number % 2 == 0:
                        use_context = False
                    else:
                        use_context = True

                a_thread = threading.Thread(target=f1,
                                            args=(a_event1,
                                                  req_mode,
                                                  request_number,
                                                  use_context))
                # save for verification and release
                thread_event_list.append(ThreadEvent(thread=a_thread,
                                                     event=a_event1,
                                                     mode=req_mode,
                                                     req_num=request_number,
                                                     lock_obtained=False))

                a_thread.start()

                # make sure the request has been queued
                while ((not a_lock.owner_wait_q) or
                       (not a_lock.owner_wait_q[-1].thread is a_thread)):
                    time.sleep(0.1)
                # logger.debug(f'shr_excl = {shr_excl}, '
                #              f'idx = {idx}, '
                #              f'num_requests_made = {request_number}, '
                #              f'len(a_lock) = {len(a_lock)}')
                assert len(a_lock) == request_number+1

                # verify
                assert a_lock.owner_wait_q[-1].thread is a_thread
                assert not a_lock.owner_wait_q[-1].event.is_set()

        work_shr1 = num_share_requests1_arg
        work_excl1 = num_excl_requests1_arg
        work_shr2 = num_share_requests2_arg
        work_excl2 = num_excl_requests2_arg
        while thread_event_list:
            exp_num_owners = 0
            if work_shr1:
                exp_num_owners = work_shr1
                if work_excl1 == 0:
                    exp_num_owners += work_shr2
            elif work_excl1:
                exp_num_owners = 1
            elif work_shr2:
                exp_num_owners = work_shr2
            elif work_excl2:
                exp_num_owners = 1

            while True:
                exp_num_owners_found = 0
                for idx in range(exp_num_owners):  # wait for next owners
                    if thread_event_list[idx].lock_obtained:
                        exp_num_owners_found += 1
                    else:
                        break
                if exp_num_owners_found == exp_num_owners:
                    break
                time.sleep(0.0001)

            for idx, thread_event in enumerate(thread_event_list):
                assert thread_event.thread == thread_event_list[idx].thread
                assert thread_event.thread == a_lock.owner_wait_q[idx].thread
                assert thread_event.mode == thread_event_list[idx].mode
                assert thread_event.mode == a_lock.owner_wait_q[idx].mode

                if idx + 1 <= num_initial_owners:
                    # we expect the event to not have been posted
                    assert not a_lock.owner_wait_q[idx].event.is_set()
                    assert thread_event.mode == initial_owner_mode
                    assert thread_event.lock_obtained is True
                elif idx + 1 <= exp_num_owners:
                    assert a_lock.owner_wait_q[idx].event.is_set()
                    assert thread_event.lock_obtained is True
                else:
                    assert not a_lock.owner_wait_q[idx].event.is_set()
                    assert thread_event.lock_obtained is False

            release_position = min(release_position_arg, exp_num_owners - 1)
            thread_event = thread_event_list.pop(release_position)

            thread_event.event.set()  # tell owner to release and return
            thread_event.thread.join()  # ensure release is complete
            num_initial_owners -= 1
            request_number -= 1
            if work_shr1:
                work_shr1 -= 1
            elif work_excl1:
                work_excl1 -= 1
            elif work_shr2:
                work_shr2 -= 1
            elif work_excl2:
                work_excl2 -= 1

            assert len(a_lock) == request_number+1


###############################################################################
# TestSELockDocstrings class
###############################################################################
class TestSELockDocstrings:
    """Class TestSELockDocstrings."""

    def test_se_lock_with_example_1(self) -> None:
        """Method test_se_lock_with_example_1."""
        flowers('Example of SELock for README:')

        from scottbrian_locking.se_lock import SELock, SELockShare, SELockExcl
        a_lock = SELock()
        # Get lock in exclusive mode
        with SELockExcl(a_lock):  # write to a
            a = 1
            print(f'under exclusive lock, a = {a}')
        # Get lock in shared mode
        with SELockShare(a_lock):  # read a
            print(f'under shared lock, a = {a}')
