import gevent
import threading


class Singleton(object):
    _instance_lock = threading.Lock()
    is_start = False
    start = None

    def __init__(self):
        pass

    def __new__(cls, *args, **kwargs):
        if not hasattr(Singleton, "_instance"):
            with Singleton._instance_lock:
                if not hasattr(Singleton, "_instance"):
                    Singleton._instance = object.__new__(cls)
        return Singleton._instance

    def run(self):
        if self.is_start is False:
            self.start()
            self.is_start = True

    def set_start(self, start):
        if self.start is None:
            self.start = start


singleton = Singleton()


class Case(object):

    def __init__(self):
        self.base_url = None
        self.singleton = singleton
        self.singleton.set_start(self.on_locust_setup)

    def on_locust_setup(self) -> object:
        """
        前置条件，只会执行一次
        :return:
        """
        self.logger.error('执行用例前置条件')
        self.singleton.base_url = self.settings.base_url
        self.singleton.index = 0
        self.setup_class()

    def append_task(self, func, *args):
        gevent.spawn(func, *args)
