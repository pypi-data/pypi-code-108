import threading


class ThreadSafeDict(dict) :

    def __init__(self, * p_arg, ** n_arg) :
        dict.__init__(self, * p_arg, ** n_arg)
        self._lock = threading.Lock()

    def __enter__(self) :
        self._lock.acquire()
        return self

    def __exit__(self, type, value, traceback) :
        self._lock.release()

def time_to_seconds(input):
    if input.isnumeric(): return int(input)
    unit = input[-1].lower()
    if unit == 's': return int(input[:-1])
    if unit == 'm': return 60 * int(input[:-1])
    if unit == 'h': return 60 * 60 * int(input[:-1])
    raise Exception("The time unit is not defined")