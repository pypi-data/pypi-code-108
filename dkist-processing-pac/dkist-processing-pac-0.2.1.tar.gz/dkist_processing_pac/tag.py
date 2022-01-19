import inspect
import multiprocessing as mp
import os


def tag():
    """Designed to be called from within other functions and return their module:func signature"""
    calling = inspect.stack()[1]
    info = inspect.getframeinfo(calling[0])
    proc = '{} - '.format(mp.current_process().name)
    if proc == 'MainProcess - ':
        proc = ''
    return '{}{}:{}:{}'.format(proc, os.path.basename(calling[1]), calling[3], info.lineno)


def is_mp():
    proc = '{} - '.format(mp.current_process().name)
    return not proc == 'MainProcess - '
