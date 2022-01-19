from multirunnable.mode import RunningMode, FeatureMode
from multirunnable.api.decorator import async_retry, AsyncRunWith
from multirunnable.adapter.lock import Lock, RLock, Semaphore, BoundedSemaphore
from multirunnable.adapter.communication import Event, Condition
from multirunnable.adapter.strategy import ExecutorStrategyAdapter, PoolStrategyAdapter
from multirunnable.api.operator import (
    LockAsyncOperator,
    SemaphoreAsyncOperator, BoundedSemaphoreAsyncOperator,
    EventAsyncOperator, ConditionAsyncOperator)
from multirunnable.coroutine.strategy import AsynchronousStrategy

from ..test_config import Worker_Size, Worker_Pool_Size, Task_Size, Semaphore_Value

import importlib
import asyncio
import pytest
import time


_Worker_Size = Worker_Size
_Worker_Pool_Size = Worker_Pool_Size
_Task_Size = Task_Size

_Semaphore_Value = Semaphore_Value

_Sleep_Time: int = 1
_Random_Start_Time: int = 60
_Random_End_Time: int = 80

_Async_Running_Result = {}

# _Async_Event_Loop = asyncio.get_event_loop()


def instantiate_lock(_mode, **kwargs):
    # if _mode is FeatureMode.Asynchronous:
        # if kwargs.get("event_loop", None) is None:
            # kwargs["event_loop"] = _Async_Event_Loop
    _lock = Lock()
    return _initial(_lock, _mode, **kwargs)


def instantiate_rlock(_mode):
    _rlock = RLock()
    return _initial(_rlock, _mode)


def instantiate_semaphore(_mode):
    _semaphore = Semaphore(value=_Semaphore_Value)
    return _initial(_semaphore, _mode)


def instantiate_bounded_semaphore(_mode):
    _bounded_semaphore = BoundedSemaphore(value=_Semaphore_Value)
    return _initial(_bounded_semaphore, _mode)


def instantiate_event(_mode):
    _event = Event()
    return _initial(_event, _mode)


def instantiate_condition(_mode):
    _condition = Condition()
    return _initial(_condition, _mode)


def _initial(_feature_factory, _mode, **kwargs):
    _feature_factory.feature_mode = _mode
    _feature_instn = _feature_factory.get_instance(**kwargs)
    _feature_factory.globalize_instance(_feature_instn)
    print(f"[DEBUG] _feature_instn: {_feature_instn}")
    return _feature_instn


@pytest.fixture(scope="class")
def lock_async_opts():
    return LockAsyncOperator()


def run_async(_function):

    _strategy_adapter = ExecutorStrategyAdapter(mode=RunningMode.Asynchronous, executors=_Worker_Size)
    _strategy = _strategy_adapter.get_simple()

    async def __process():
        await _strategy.initialization(queue_tasks=None, features=Lock())
        _ps = [_strategy.generate_worker(_function) for _ in range(Worker_Size)]
        await _strategy.activate_workers(_ps)

    asyncio.run(__process(), debug=True)
    # asyncio.run_coroutine_threadsafe(__process(), asyncio.get_event_loop())


class TestAsyncLockAdapterOperator:

    def test_feature_in_asynchronous_tasks(self, lock_async_opts: LockAsyncOperator):

        _event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop=_event_loop)
        _done_timestamp = {}
        instantiate_lock(FeatureMode.Asynchronous, event_loop=_event_loop)

        async def _target_testing():
            # Save a timestamp into list
            await lock_async_opts.acquire()
            await asyncio.sleep(_Sleep_Time)
            _time = float(time.time())
            _async_task = asyncio.current_task()
            _async_task_id = id(_async_task)
            _done_timestamp[_async_task_id] = _time
            lock_async_opts.release()

        run_async(_target_testing)

        TestAsyncLockAdapterOperator._chk_done_timestamp(_done_timestamp)
        print(f"[DEBUG] _done_timestamp: {_done_timestamp}")


    def test_feature_by_pykeyword_with_in_asynchronous_task(self):
        _event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop=_event_loop)

        _done_timestamp = {}

        instantiate_lock(FeatureMode.Asynchronous, event_loop=_event_loop)
        _lock_async_opts = LockAsyncOperator()

        async def _target_testing_with():
            # Save a time stamp into list
            print(f"[DEBUG] Start to run _target_testing_with ...")
            try:
                print(f"[DEBUG] Acquire a Lock ...")
                async with _lock_async_opts:
                    print(f"[DEBUG] Into Lock logic")
                    _async_task = asyncio.current_task()
                    print(f"[DEBUG ]_async_task: {_async_task}")
                    _async_task_id = id(_async_task)
                    await asyncio.sleep(_Sleep_Time)
                    _time = float(time.time())
                    _done_timestamp[_async_task_id] = _time
                    print(f"[DEBUG] _Async_Running_Result: {_done_timestamp}")
                    print(f"[DEBUG] Release Lock logic")
            except Exception as e:
                assert False, f"Occur something unexpected issue. Please check it. \n" \
                              f"Exception: {e}"
            else:
                assert True, f"Testing code successfully."

        # # # # Run multiple workers and save something info at the right time
        run_async(_target_testing_with)

        TestAsyncLockAdapterOperator._chk_done_timestamp(_done_timestamp)
        print(f"[DEBUG] _done_timestamp: {_done_timestamp}")
        assert False, f"Just for demo."


    @staticmethod
    def _chk_done_timestamp(_done_timestamp):
        assert len(_done_timestamp.keys()) == _Worker_Size, f"The amount of thread ID keys (no de-duplicate) should be equal to worker size '{_Worker_Size}'."
        assert len(set(_done_timestamp.keys())) == _Worker_Size, f"The amount of thread ID keys (de-duplicate) should be equal to worker size '{_Worker_Size}'."
        _previous_v = None
        for _v in sorted(_done_timestamp.values()):
            if _previous_v is None:
                _previous_v = _v
            if _previous_v != _v:
                assert int(abs(float(_v) - float(_previous_v))) == _Sleep_Time, \
                    f"The different time betweeen them should be {_Sleep_Time} second(s). One is {_v} and another one is {_previous_v}. All of them are {_done_timestamp}"
                _previous_v = _v


Running_Target_Function_Counter: int = 0
Initial_Handling_Flag_Counter: int = 0
Done_Handling_Flag_Counter: int = 0
Final_Handling_Flag_Counter: int = 0
Error_Handling_Flag_Counter: int = 0


def init_flag() -> None:
    global Running_Target_Function_Counter, Initial_Handling_Flag_Counter, Done_Handling_Flag_Counter, Final_Handling_Flag_Counter, Error_Handling_Flag_Counter
    Running_Target_Function_Counter = 0
    Initial_Handling_Flag_Counter = 0
    Done_Handling_Flag_Counter = 0
    Final_Handling_Flag_Counter = 0
    Error_Handling_Flag_Counter = 0



class TargetBoundedAsyncFunction:

    @async_retry
    async def target_method(self):
        global Running_Target_Function_Counter
        Running_Target_Function_Counter += 1


    @target_method.initialization
    async def initial_function(self, *args, **kwargs):
        global Initial_Handling_Flag_Counter
        Initial_Handling_Flag_Counter += 1


    @target_method.done_handling
    async def done_function(self, result):
        global Done_Handling_Flag_Counter
        Done_Handling_Flag_Counter += 1
        return result


    @target_method.final_handling
    async def final_function(self):
        global Final_Handling_Flag_Counter
        Final_Handling_Flag_Counter += 1


    @target_method.error_handling
    async def error_function(self, e: Exception):
        global Error_Handling_Flag_Counter
        Error_Handling_Flag_Counter += 1
        return e



class JustTestException(Exception):

    def __str__(self):
        return "Just for testing to raise an exception."



class TargetErrorBoundedAsyncFunction:

    @async_retry
    async def target_error_method_with_1_timeout(self):
        global Running_Target_Function_Counter
        Running_Target_Function_Counter += 1
        raise JustTestException


    @async_retry(timeout=3)
    async def target_error_method(self):
        global Running_Target_Function_Counter
        Running_Target_Function_Counter += 1
        raise JustTestException


    @target_error_method.initialization
    async def _initial(self, *args, **kwargs):
        global Initial_Handling_Flag_Counter
        Initial_Handling_Flag_Counter += 1


    @target_error_method.done_handling
    async def _done(self, result):
        global Done_Handling_Flag_Counter
        Done_Handling_Flag_Counter += 1
        return result


    @target_error_method.final_handling
    async def _final(self):
        global Final_Handling_Flag_Counter
        Final_Handling_Flag_Counter += 1


    @target_error_method.error_handling
    async def _error(self, e: Exception):
        global Error_Handling_Flag_Counter
        Error_Handling_Flag_Counter += 1
        assert isinstance(e, JustTestException), f""
        return e


@pytest.fixture(scope="class")
def target_bounded_async_function() -> TargetBoundedAsyncFunction:
    return TargetBoundedAsyncFunction()


@pytest.fixture(scope="class")
def target_error_bounded_async_function() -> TargetErrorBoundedAsyncFunction:
    return TargetErrorBoundedAsyncFunction()


@pytest.fixture(scope="class")
def async_strategy() -> AsynchronousStrategy:
    return AsynchronousStrategy(executors=_Worker_Size)


class TestRetryMechanism:

    @pytest.mark.skip(reason="Consider about the requirement necessary. It fail currently.")
    def test_retry_decorating_at_function(self):
        pass
        # init_flag()
        #
        # ta()
        # assert Initial_Handling_Flag_Counter == 1, F"The initial handling flag should be 'True'."
        # assert Done_Handling_Flag_Counter == 1, F"The done handling flag should be 'True'"
        # assert Final_Handling_Flag_Counter == 1, F"The final handling flag should be 'True'"
        # assert Error_Handling_Flag_Counter == 0, F"The error handling flag should be 'False'"


    def test_retry_decorating_at_bounded_function(self, async_strategy: AsynchronousStrategy, target_bounded_async_function: TargetBoundedAsyncFunction):
        init_flag()

        async_strategy.run(function=target_bounded_async_function.target_method)
        assert Initial_Handling_Flag_Counter == _Worker_Size, F"The count of initial handling flag should be '{_Worker_Size}'."
        assert Done_Handling_Flag_Counter == _Worker_Size, F"The count of done handling flag should be '{_Worker_Size}'"
        assert Final_Handling_Flag_Counter == _Worker_Size, F"The count of final handling flag should be '{_Worker_Size}'"
        assert Error_Handling_Flag_Counter == 0, F"The count of error handling flag should be '0'"


    def test_retry_decorating_at_bounded_function_raising_an_exception(self, async_strategy: AsynchronousStrategy, target_error_bounded_async_function: TargetErrorBoundedAsyncFunction):
        init_flag()

        async_strategy.run(function=target_error_bounded_async_function.target_error_method)
        assert Initial_Handling_Flag_Counter == 3 * _Worker_Size, F"The count of initial handling flag should be '{3 * _Worker_Size}'."
        assert Done_Handling_Flag_Counter == 0, F"The count of done handling flag should be 'False'"
        assert Final_Handling_Flag_Counter == 3 * _Worker_Size, F"The count of final handling flag should be '{3 * _Worker_Size}'"
        assert Error_Handling_Flag_Counter == 3 * _Worker_Size, F"The count of error handling flag should be '{3 * _Worker_Size}'"


    @pytest.mark.skip(reason="Not implement testing logic.")
    def test_retry_decorating_at_classmethod_function(self, target_bounded_async_function: TargetBoundedAsyncFunction):
        pass


    @pytest.mark.skip(reason="Not implement testing logic.")
    def test_retry_decorating_at_staticmethod_function(self, target_bounded_async_function: TargetBoundedAsyncFunction):
        pass




