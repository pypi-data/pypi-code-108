import random
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

from multirunnable.parallel.shared import set_manager, get_manager
from multirunnable import SimpleExecutor, RunningMode
import multiprocessing

get_manager()
# set_manager(multiprocessing.Manager())

from test_module import (
    TestSimpleFunCls,
    TestSimpleCls,
    TestMetaCls, TestMetaDiffCls,
    TestNamedMetaCls, TestNamedMetaDiffCls,
    TestCls,
    TestNamedCls, TestDiffNamedCls,
    NoSingletonTestCls)



class TestTargetCls(multiprocessing.Process):
    
    def __init__(self, common_cls=None, no_singleton_cls=None):
        super(TestTargetCls, self).__init__()
        self.common_cls = common_cls
        self.no_singleton_cls = no_singleton_cls


    def run(self) -> None:
        if self.common_cls is None:
            print("Does not have object.")
            if "5" in str(multiprocessing.current_process()):
                # tc = TestDiffNamedCls()
                tc = TestMetaDiffCls()
                print(f"before tc.index: {tc.index_parm} - {multiprocessing.current_process()}")
                # sleep_random_sec()
                tc.index_parm = "Value be modified by *TestMetaDiffCls*"
                # print(f"first version tc.index: {tc.index} - {multiprocessing.current_process()}")
            else:
                # tc = TestSimpleFunCls()
                # tc = TestSimpleCls()
                tc = TestMetaCls()
                print(f"before tc.index: {tc.index_parm} - {multiprocessing.current_process()}")
                # sleep_random_sec()
                if "TestMetaDiffCls" not in tc.index_parm:
                    tc.index_parm = "Value be modified by *TestMetaCls*"
                # tc = TestMetaCls(index=multiprocessing.current_process())
                # tc = TestCls()
                # tc = TestNamedCls()
                # print(f"first version tc.index: {tc.index} - {multiprocessing.current_process()}")
        else:
            print("New a instance ...")
            tc = self.common_cls()
        tc_id = id(tc)

        if self.no_singleton_cls is None:
            nstc = NoSingletonTestCls()
        else:
            nstc = self.no_singleton_cls()
        nstc_id = id(nstc)

        print(f"id(tc): {tc_id}, id(nstc): {nstc_id} - {multiprocessing.current_process()}")
        print(f"tc.index: {tc.index_parm} - {multiprocessing.current_process()}")

        # tc.test()
        # nstc.test()


class TargetCls:

    def __init__(self, common_cls=None, no_singleton_cls=None):
        self.common_cls = common_cls
        self.no_singleton_cls = no_singleton_cls

    def run(self) -> None:
        if self.common_cls is None:
            print("Does not have object.")
            if "5" in str(multiprocessing.current_process()):
                # tc = TestDiffNamedCls()
                # tc = TestMetaDiffCls()
                tc = TestNamedMetaDiffCls()
                print(f"before tc.index: {tc.index_parm} - {multiprocessing.current_process()}")
                # sleep_random_sec()
                tc.index_parm = "Value be modified by *TestMetaDiffCls*"
                # print(f"first version tc.index: {tc.index} - {multiprocessing.current_process()}")
            else:
                # tc = TestSimpleFunCls()
                # tc = TestSimpleCls()
                # tc = TestMetaCls()
                tc = TestNamedMetaCls()
                print(f"before tc.index: {tc.index_parm} - {multiprocessing.current_process()}")
                # sleep_random_sec()
                if "TestMetaDiffCls" not in tc.index_parm:
                    tc.index_parm = "Value be modified by *TestMetaCls*"
                # tc = TestMetaCls(index=multiprocessing.current_process())
                # tc = TestCls()
                # tc = TestNamedCls()
                # print(f"first version tc.index: {tc.index} - {multiprocessing.current_process()}")
        else:
            print("New a instance ...")
            tc = self.common_cls()
        tc_id = id(tc)

        if self.no_singleton_cls is None:
            nstc = NoSingletonTestCls()
        else:
            nstc = self.no_singleton_cls()
        nstc_id = id(nstc)

        print(f"id(tc): {tc_id}, id(nstc): {nstc_id} - {multiprocessing.current_process()}")
        print(f"tc.index: {tc.index_parm} - {multiprocessing.current_process()}")

        # tc.test()
        # nstc.test()


def sleep_random_sec():
    sleep_time = random.randrange(1, 10)
    print(f"Will sleep for {sleep_time} seconds.")
    time.sleep(sleep_time)


def test_target():
    tc = TestCls()
    tc_id = id(tc)
    nstc = NoSingletonTestCls()
    nstc_id = id(nstc)
    print(f"id(tc): {tc_id}, id(nstc): {nstc_id} - {multiprocessing.current_process()}")



if __name__ == '__main__':

    # tc_1 = TestMetaCls()
    # tc_2 = TestMetaCls()
    # print(f"[DEBUG] tc_1 memory space: {id(tc_1)}")
    # print(f"[DEBUG] tc_2 memory space: {id(tc_2)}")

    print("Start testing task.")

    # processes = [multiprocessing.Process(target=test_target) for _ in range(20)]
    # processes = [TestTargetCls() for _ in range(20)]
    # manager = multiprocessing.Manager()
    # set_manager()
    manager = get_manager()
    manager.NoSingletonTestCls = NoSingletonTestCls
    # processes = [TestTargetCls(common_cls=TestCls, no_singleton_cls=manager.NoSingletonTestCls) for _ in range(3)]
    # processes = [TestTargetCls(common_cls=None, no_singleton_cls=manager.NoSingletonTestCls) for _ in range(5)]
    # for _process in processes:
    #     _process.start()
    #
    # for _process in processes:
    #     _process.join()

    executor = SimpleExecutor(mode=RunningMode.Parallel, executors=5)
    tc_instance = TargetCls(common_cls=None, no_singleton_cls=manager.NoSingletonTestCls)
    executor.run(function=tc_instance.run)

    print("Finish testing task.")
