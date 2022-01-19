#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Décorateur timeout
^^^^^^^^^^^^^^^^^^

Created on Mon Nov 23 10:47:50 2020

@author: Cyrile Delestre
"""

import signal
from functools import wraps

def _handler_timeout(signum, frame):
    raise TimeoutError

def timeout(time: int, *args, **kwargs):
    r"""
    Décorateur simple d'utilisation permettant l'implémentation d'un timeout 
    sur une fonction, timeout exprimé en en milli-seconde.
    
    Parameters
    ----------
    time : int
        temps en milli-seconde
    
    Examples
    --------
    >>> import time
    >>> from dstk.utils import timeout
    
    >>> @time_out(100)
    >>> def fun(time_wait: int=10):
    >>>     time.sleep(time_wait/1000)
    >>>     print("ok!")
    
    >>> fun(10)
    ok!
    >>> fun(150)
    TimeoutError: Timeout de la fonction fun déclanchée après 100 ms !
    """
    def decorator(fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handler_timeout)
            signal.setitimer(signal.ITIMER_REAL, time/1000)
            try:
                res = fun(*args, **kwargs)
            except TimeoutError:
                signal.alarm(0)
                raise TimeoutError(
                    f"Timeout de la fonction {fun.__name__} déclanchée "
                    f"après {time} ms !"
                )
            signal.alarm(0)
            return res
        return wrapper
    return decorator
