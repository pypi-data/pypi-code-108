"""
pyape.uwsgiproxy
~~~~~~~~~~~~~~~~~~~
代理 uwsgi 模块的方法
"""
import warnings
import pickle
import importlib


in_uwsgi = False
uwsgi = None


try:
    uwsgi = importlib.import_module('uwsgi')
    in_uwsgi = True
except:
    in_uwsgi = False


def cache_get(key):
    if in_uwsgi:
        return uwsgi.cache_get(key)
    return None


def cache_set(key, value):
    if in_uwsgi:
        return uwsgi.cache_set(key, value)
    return None


def cache_del(key):
    if in_uwsgi:
        return uwsgi.cache_del(key)
    return None


def cache_exists(key):
    if in_uwsgi:
        return uwsgi.cache_exists(key)
    return None


def cache_update(key, value):
    if in_uwsgi:
        return uwsgi.cache_update(key, value)
    return None


def mule_msg(msg, mule_id=1):
    if in_uwsgi:
        try:
            uwsgi.mule_msg(pickle.dumps(msg, protocol=pickle.HIGHEST_PROTOCOL), mule_id)
        except Exception as e:
            warnings.warn(str(e))
    return None


def worker_id():
    if in_uwsgi:
        return uwsgi.worker_id()
    return -1


def register_signal(signum, target, func):
    """ 注册一个 uwsgi 信号
    :param signum: 信号量
    :param target: 字符串
        worker/worker0 将发送信号给第一个可用worker。如果你指定过一个空字符串，那么这是默认值。
        workers 会发送信号给每个worker。
        workerN (N > 0) 会发送信号给worker N。
        mule/mule0 会发送信号给第一个可用mule。 (见 uWSGI Mule)
        mules 会发送信号给所有mule。
        muleN (N > 0) 会发送信号给mule N。
    """
    if in_uwsgi:
        return uwsgi.register_signal(signum, target, func)
    return -1


def signal_registered(signum):
    """ 一个信号是否被注册
    """
    if not in_uwsgi:
        return None
    return uwsgi.signal_registered(signum)


def get_free_signal():
    """ 获取没有被注册的信号量，否则抛出一个错误
    """
    if not in_uwsgi:
        return None
    for signum in range(0, 256):
        if not uwsgi.signal_registered(signum):
            return signum
    raise IndexError("No free uwsgi signal available!")


def add_timer(signum, seconds):
    """ 注册一个定时器
    """
    if not in_uwsgi:
        return None
    return uwsgi.add_timer(signum, seconds)


class signal(object):
    """ register_signal 的装饰器模式
    """
    def __init__(self, signum, **kwargs):
        self.signum = signum
        self.target = kwargs.get('target', '')

    def __call__(self, f):
        uwsgi.register_signal(self.signum, self.target, f)
        return f


class timer(object):
    """ add_timer 的装饰器模式
    """
    def __init__(self, secs, **kwargs):
        self.signum = kwargs.get('signum', get_free_signal())
        self.secs = secs
        self.target = kwargs.get('target', '')

    def __call__(self, f):
        uwsgi.register_signal(self.signum, self.target, f)
        uwsgi.add_timer(self.signum, self.secs)
        return f