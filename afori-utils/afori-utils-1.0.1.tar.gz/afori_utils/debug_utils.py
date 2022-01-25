from time import time
from collections import deque, defaultdict
import time
from functools import partial
import numpy as np


class StatsAgg:
    def __init__(self, stat_name_list=(), maxlen=None, sig_digits=3):
        self.stat_name_list = stat_name_list
        self.maxlen = maxlen
        self.sig_digits = sig_digits

        self.stats_dict = defaultdict(partial(deque, maxlen=maxlen))
        self.clear()

    def __getitem__(self, item):
        return self.stats_dict[item]

    def get_all_stats(self, req_list=None) -> dict:
        if req_list is None:
            req_list = self.get_default_stat_names()
        return {stat_name: self.get_one_stat(stat_name, req_list=req_list)
                for stat_name in self.stats_dict}

    def get_one_stat(self, stat_name, req_list=None) -> dict:
        if req_list is None:
            req_list = self.get_default_stat_names()
        return {req: self.get_info(stat_name, req) for req in req_list}

    def get_all_stats_string(self, req_list=None) -> dict:
        if req_list is None:
            req_list = self.get_default_stat_names()
        return {stat_name: self.get_one_stat_string(stat_name, req_list=req_list)
                for stat_name in self.stats_dict}

    def get_one_stat_string(self, stat_name, req_list=None) -> str:
        if req_list is None:
            req_list = self.get_default_stat_names()
        agg_str = ''
        for req in req_list:
            agg_str += f'{req}: {self.get_info(stat_name, req)},  '
        return agg_str

    @staticmethod
    def get_default_stat_names():
        return 'avg', 'min', 'max'

    def get_info(self, stat_name, info):
        stat_deque = self.stats_dict[stat_name]
        if len(stat_deque) == 0:
            return np.nan
        if info == 'avg':
            val = np.mean(stat_deque)
        elif info == 'min':
            val = np.min(stat_deque)
        elif info == 'max':
            val = np.max(stat_deque)
        elif info == 'last':
            val = stat_deque[-1]
        elif info == 'sum':
            val = np.sum(stat_deque)
        elif info == 'std':
            val = np.std(stat_deque)
        elif info == 'diff_avg':
            val = np.mean(np.diff(stat_deque))
        elif info == 'len':
            val = len(stat_deque)
        else:
            raise ValueError

        return np.round(val, self.sig_digits)

    def append(self, stat_name, info):
        self.stats_dict[stat_name].append(info)

    def clear(self):
        for stat_name in self.stat_name_list:
            self.stats_dict[stat_name] = deque(maxlen=self.maxlen)


class TimesAgg(StatsAgg):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key_lifo = deque()
        self.time_lifo = deque()

    def __call__(self, key):
        self.key_lifo.append(key)
        return self

    def __enter__(self):
        self.time_lifo.append(time.time())

    def __exit__(self, exc_type, exc_val, exc_tb):
        key = self.key_lifo.pop()
        start_time = self.time_lifo.pop()
        self[key].append(time.time() - start_time)


class LineTimer:
    """ One line, simple timer"""
    def __init__(self):
        self.start_time = None
        self.is_working = False

    def start(self):
        if not self.is_working:
            self.start_time = time()
            self.is_working = True
        else:
            print('Timer already working')

    def elapsed(self):
        if self.is_working:
            return time() - self.start_time
        else:
            print('Timer is not working')

    def stop(self):
        elapsed = self.elapsed()
        self.is_working = False
        self.start_time = None
        return elapsed