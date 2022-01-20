import atexit
import threading
import multiprocessing


class AsyncHandler:
    _open_threads = []
    _open_processes = []
    _registered = False

    @classmethod
    def check_registered(cls):
        if not cls._registered:
            atexit.register(AsyncHandler.wait_fot_threads)
            cls._registered = True

    @classmethod
    def register_async(cls, obj, mode):
        cls.check_registered()
        if mode == "thread":
            cls._open_processes.append(obj)
        elif mode == "process":
            cls._open_threads.append(obj)

    @classmethod
    def wait_fot_threads(cls):
        for t in cls._open_threads:
            t.join()

        for p in cls._open_processes:
            p.join()


def run_async(mode="thread"):
    """
    This decorator with arguments can be used to run functions asynchronously
    :param mode: thread/process
    return: decorator function
    """

    # Validate developer errors
    assert mode in ["thread", "process"], "run_async: mode must be either thread or process"

    # Build the decorator function
    def decorator(f):
        def wrapping_function(*args, **kwargs):
            if mode == "thread":
                obj = threading.Thread(target=f, args=args, kwargs=kwargs)
            else:
                obj = multiprocessing.Process(target=f, args=args, kwargs=kwargs)

            obj.start()
            AsyncHandler.register_async(obj, mode)
            return obj

        return wrapping_function
    return decorator
