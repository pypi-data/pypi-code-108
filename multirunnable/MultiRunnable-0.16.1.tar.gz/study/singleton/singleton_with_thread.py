from typing import List
import time
import os

DEVELOPMENT_MODE = os.getenv("DEVELOPMENT_MODE", True)

if DEVELOPMENT_MODE:
    # Import package multirunnable
    import pathlib
    import sys
    package_pyocean_path = str(pathlib.Path(__file__).absolute().parent.parent.parent)
    sys.path.append(package_pyocean_path)

import threading

from test_module import (
    TestSimpleFunCls,
    TestSimpleCls,
    TestMetaCls, TestMetaDiffCls,
    TestCls,
    TestNamedCls, TestDiffNamedCls,
    NoSingletonTestCls)


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



class TestTargetCls(threading.Thread):

    def __init__(self, common_cls=None, no_singleton_cls=None):
        super(TestTargetCls, self).__init__()
        self.common_cls = common_cls
        self.no_singleton_cls = no_singleton_cls

    def run(self) -> None:
        if self.common_cls is None:
            print("Does not have object.")
            if "5" in str(threading.current_thread()):
                # tc = TestDiffNamedCls()
                tc = TestMetaDiffCls()
            else:
                # tc = TestSimpleFunCls()
                # tc = TestSimpleCls()
                tc = TestMetaCls()
                # tc = TestCls()
                # tc = TestNamedCls()
        else:
            print("New a instance ...")
            tc = self.common_cls()
        tc_id = id(tc)

        if self.no_singleton_cls is None:
            nstc = NoSingletonTestCls()
        else:
            nstc = self.no_singleton_cls()
        nstc_id = id(nstc)

        print(f"id(tc): {tc_id}, id(nstc): {nstc_id} - {threading.current_thread()}")

        # tc.test()
        # nstc.test()


if __name__ == '__main__':

    print("Start testing task.")

    # threads = [threading.Thread(target=test_target) for _ in range(20)]
    threads = [TestTargetCls(common_cls=None, no_singleton_cls=NoSingletonTestCls) for _ in range(5)]
    for _thread in threads:
        _thread.start()

    for _thread in threads:
        _thread.join()

    print("Finish testing task.")
