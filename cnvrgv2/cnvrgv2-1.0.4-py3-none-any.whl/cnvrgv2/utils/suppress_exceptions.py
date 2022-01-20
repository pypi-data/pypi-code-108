import os
import traceback
from functools import wraps


def suppress_exceptions(f):
    """
    Used to suppress exceptions across the sdk to not interrupt client script runs
    @param f: the function we wish to suppress
    @return: suppressed function
    """

    suppress = os.environ.get('CNVRG_SUPPRESS_EXCEPTIONS')

    @wraps(f)
    def func(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            if suppress:
                traceback.print_exc()
            else:
                raise e
    return func
