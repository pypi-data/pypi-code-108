import functools
import threading
import ctypes
import time


class TerminableThread(threading.Thread):
    """a thread that can be stopped by forcing an exception in the execution context"""

    def terminate(self, exception_cls, repeat_sec=2.0):
        if self.is_alive() is False:
            return True
        killer = ThreadKiller(self, exception_cls, repeat_sec=repeat_sec)
        killer.start()


class ThreadKiller(threading.Thread):
    """separate thread to kill TerminableThread"""

    def __init__(self, target_thread, exception_cls, repeat_sec=2.0):
        threading.Thread.__init__(self)
        self.target_thread = target_thread
        self.exception_cls = exception_cls
        self.repeat_sec = repeat_sec
        self.daemon = True

    def run(self):
        """loop raising exception incase it's caught hopefully this breaks us far out"""
        while self.target_thread.is_alive():
            ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self.target_thread.ident),
                                                       ctypes.py_object(self.exception_cls))
            self.target_thread.join(self.repeat_sec)


class Retry:
    @classmethod
    def trying(cls, retry_times: int = 3, retry_sleep: int = 0, retry_exceptions: tuple = None, logger=print,
               sleep_func=time.sleep):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except (retry_exceptions or Exception) as e:
                    return cls.__retry(func, retry_times, e, retry_sleep, logger, sleep_func, *args, **kwargs)
            return wrapper
        return decorator

    @classmethod
    def __retry(cls, func, retry_times, error, retry_sleep, logger, sleep_func=time.sleep, *args, **kwargs):
        if retry_times >= 1:
            try:
                retry_times -= 1
                logger(f'Retry remaining times: {retry_times}; Will sleep {retry_sleep}s; Error: {error};')
                sleep_func(retry_sleep)
                return func(*args, **kwargs)
            except Exception as e:
                return cls.__retry(func, retry_times, e, retry_sleep, logger, sleep_func, *args, **kwargs)
        else:
            raise


class RunTime:
    @classmethod
    def run_time(cls, logger=print, show_short_result: int = None):
        """
        :param logger: logger func, default is python print
        :param show_short_result: displays the result of the number of characters.
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start = time.time()
                res = func(*args, **kwargs)
                end = time.time()
                str_res = f'{res}'
                logger(
                    f'\n##########################################'
                    f'\nFUNC: {func.__name__}'
                    f'\nSTART: {round(start, 2)} END: {round(end, 2)}'
                    f'\nTOTAL TIME: {round(end - start, 2)}'
                    f'\n##########################################'
                    f'\nRESULT: '+(str_res[:show_short_result]+'......'
                                   if show_short_result and len(str_res) > show_short_result else str_res))
                return res
            return wrapper
        return decorator

    @classmethod
    def loop_time(cls, loop_times: int = None, loop_sleep: int = 0, logger=print, show_short_result: int = None,
                  sleep_func=time.sleep):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                n, flag = {'time': 1}, True
                start = time.time()
                try:
                    (cls.__rangetime(loop_times, n, func, loop_sleep, logger, show_short_result, sleep_func,
                                     args, **kwargs)
                     if loop_times else
                     cls.__whiletime(flag, n, func, loop_sleep, logger, show_short_result, sleep_func, *args, **kwargs))

                except KeyboardInterrupt:
                    pass
                finally:
                    end = time.time()
                    n['time'] -= 1
                    logger(
                        f'\n##########################################'
                        f'\nFUNC: {func.__name__}'
                        f'\nSTART: {round(start, 2)} END: {round(end, 2)}'
                        f'\nTOTAL_TIME: {round(end - start, 2)} RUN_TIMES: {n["time"]}'
                        f'\n##########################################')
            return wrapper
        return decorator

    @classmethod
    def __rangetime(cls, times, n, func, sleep, logger=print, show_short_result: int = None, sleep_func=time.sleep,
                    *args, **kwargs):
        res = True
        for _ in range(times):
            if res:
                start = time.time()
                res = func(*args, **kwargs)
                end = time.time()
                str_res = f'{res}'
                show_res = (f'{res}'[:show_short_result]+'......'
                            if show_short_result and len(str_res) > show_short_result else f'{res}')
                logger(f'Times: {n["time"]}, Time_cost: {end - start}\n'
                       f'RESULT: {show_res or "Range loop: Nothing returned."}\n')
                sleep_func(sleep)
                n["time"] += 1
            else:
                break

    @classmethod
    def __whiletime(cls, flag, n, func, sleep, logger=print, show_short_result: int = None, sleep_func=time.sleep,
                    *args, **kwargs):
        while flag:
            start = time.time()
            res = func(*args, **kwargs)
            end = time.time()
            str_res = f'{res}'
            show_res = (f'{res}'[:show_short_result] + '......'
                        if show_short_result and len(str_res) > show_short_result else f'{res}')
            logger(f'Times: {n["time"]}, Time_cost: {end - start}\n'
                   f'RESULT: {show_res or "While loop: Nothing returned."}\n')
            sleep_func(sleep)
            n["time"] += 1

    @classmethod
    def timeout(cls, sec, raise_sec=1):
        """
        timeout decorator
        :param sec: function raise TimeoutError after ? seconds
        :param raise_sec: retry kill thread per ? seconds. default: 1 second
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapped_func(*args, **kwargs):
                err_msg = f'Function {func.__name__} timed out after {sec} seconds'

                class FuncTimeoutError(TimeoutError):
                    def __init__(self):
                        TimeoutError.__init__(self, err_msg)

                result, exception = [], []

                def run_func():
                    try:
                        res = func(*args, **kwargs)
                    except FuncTimeoutError:
                        pass
                    except Exception as e:
                        exception.append(e)
                    else:
                        result.append(res)

                # typically, a python thread cannot be terminated, use TerminableThread instead
                thread = TerminableThread(target=run_func, daemon=True)
                thread.start()
                thread.join(timeout=sec)

                if thread.is_alive():
                    # a timeout thread keeps alive after join method, terminate and raise TimeoutError
                    exc = type('TimeoutError', FuncTimeoutError.__bases__, dict(FuncTimeoutError.__dict__))
                    thread.terminate(exception_cls=exc, repeat_sec=raise_sec)
                    raise TimeoutError(err_msg)
                elif exception:
                    # if exception occurs during the thread running, raise it
                    raise exception[0]
                else:
                    # if the thread successfully finished, return its results
                    return result[0]
            return wrapped_func
        return decorator
