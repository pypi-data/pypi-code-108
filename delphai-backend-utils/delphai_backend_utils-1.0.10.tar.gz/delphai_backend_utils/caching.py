
from multiprocessing import current_process
from threading import Thread
from time import perf_counter, sleep
from abc import ABC, abstractmethod


class Cacher(ABC):
    """
    Implements an autorenewable cache for some data
    """
    name = 'Abstract cache'
    renew_interval = None
    timeout = 60
    _data = None

    def __init__(self):
        Thread(target=cache_renewer_worker, daemon=True, args=[self]).start()

    def get_data(self):
        """
        Returnes data from cache.
        """
        start = perf_counter()
        while self._data is None:
            if perf_counter() - start > self.timeout:
                raise Exception(f'Data acqisition timeout for cache "{self.name}"')
            sleep(0.2)
        return self._data

    def is_ready(self):
        """Returns True if data acquired and ready to use"""
        return self._data is not None

    @abstractmethod
    def get_data_func(self):
        """Must return something that will be stored into _data"""
        pass


def cache_renewer_worker(cacher: Cacher):
    cacher._data = cacher.get_data_func()
    if cacher.renew_interval:
        while True:
            sleep(cacher.renew_interval)
            cacher._data = cacher.get_data_func()


CACHES_BY_PID = {}  # process id -> cache name -> Cacher

REGISTERED_CACHERS = {}  # cache name -> (Cacher class, autoload)


def register_cacher(cacher_class, autoload: bool = False):
    name = cacher_class.name
    REGISTERED_CACHERS[name] = (cacher_class, autoload)
    if autoload:
        get_cache(name)


def get_cache(name) -> Cacher:
    pid = current_process().pid
    if pid not in CACHES_BY_PID:
        names2init = set(k for k, v in REGISTERED_CACHERS.items() if v[1])
        names2init.add(name)
        CACHES_BY_PID[pid] = {n: REGISTERED_CACHERS[n][0]() for n in names2init}
    elif name not in CACHES_BY_PID[pid]:
        CACHES_BY_PID[pid][name] = REGISTERED_CACHERS[name][0]()

    return CACHES_BY_PID[pid][name]
