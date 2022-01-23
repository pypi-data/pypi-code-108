from gevent.greenlet import Greenlet
import gevent.monkey

gevent.monkey.patch_thread()

import threading


def singleton(_class):

    class _SingletonClass(_class):

        _Instance = None

        def __new__(_class, *args, **kwargs):
            if _SingletonClass._Instance is None:
                _SingletonClass._Instance = super(_SingletonClass, _class).__new__(_class, *args, **kwargs)
                _SingletonClass._Instance._sealed = False
            return _SingletonClass._Instance


        def __init__(self, *args, **kwargs):
            if self._sealed:
                return
            super(_SingletonClass, self).__init__(*args, **kwargs)
            self._sealed = True

    _SingletonClass.__name__ = _class.__name__
    return _SingletonClass



@singleton
class TestCls:

    def test(self):
        print("This is test function.")



def test_target():
    tc = TestCls()
    tc_id = id(tc)
    print(f"id(tc): {tc_id} - {threading.current_thread()}")



if __name__ == '__main__':

    print("Start testing task.")

    green_threads = [Greenlet(test_target) for _ in range(20)]
    for _thread in green_threads:
        _thread.start()

    for _thread in green_threads:
        _thread.join()

    print("Finish testing task.")
