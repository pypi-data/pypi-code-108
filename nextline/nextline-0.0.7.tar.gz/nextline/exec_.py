import sys
import threading


##__________________________________________________________________||
def exec_with_trace(code, trace, done=None):
    """execute code with trace

    Parameters
    ----------
    code : object
        A code to be executed. This must be an object that can be
        executed by the Python built-in Function exec().
    trace: callable
        A trace function.
    done: callable, optional
        A callable with two arguments. It will to be called after the
        code exits. The first argument is the return value, which is
        always None in the current implementation, because the
        built-in function exec() returns None. The second argument is
        the exception if an exception occurs or otherwise None.
    """

    ret = None
    exc = None

    globals_ = {"__name__": __name__}
    # To be given to exec() in order to address the issue
    # https://github.com/simonsobs/nextline/issues/7
    # __name__ is used in modules_to_trace in Trace.

    trace_org = sys.gettrace()
    threading.settrace(trace)
    sys.settrace(trace)
    try:
        ret = exec(code, globals_)
        # ret is always None
    except BaseException as e:
        exc = e
    finally:
        sys.settrace(trace_org)
        threading.settrace(trace_org)
        if done:
            done(ret, exc)


##__________________________________________________________________||
