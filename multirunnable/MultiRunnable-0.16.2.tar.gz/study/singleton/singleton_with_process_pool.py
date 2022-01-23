from test_module import TestSimpleFunCls, TestSimpleCls, TestMetaCls, TestCls, TestNamedCls, TestDiffNamedCls, NoSingletonTestCls
import multiprocessing



class TestTargetCls:
    
    def __init__(self, common_cls=None, no_singleton_cls=None):
        self.common_cls = common_cls
        self.no_singleton_cls = no_singleton_cls


    def run(self) -> None:
        if self.common_cls is None:
            print("Does not have object.")
            if "5" in str(multiprocessing.current_process()):
                tc = TestDiffNamedCls()
            else:
                # tc = TestSimpleFunCls()
                # tc = TestSimpleCls()
                # tc = TestMetaCls()
                # tc = TestCls()
                tc = TestNamedCls()
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

        # tc.test()
        # nstc.test()



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
    manager = multiprocessing.Manager()
    manager.NoSingletonTestCls = NoSingletonTestCls
    pp = multiprocessing.Pool(processes=5)
    test_target_cls = TestTargetCls(common_cls=None, no_singleton_cls=manager.NoSingletonTestCls)
    # processes_r = [pp.apply_async(func=test_target_cls.run) for _ in range(5)]
    processes_r = [pp.apply_async(func=test_target_cls.run) for _ in range(5)]
    for _process in processes_r:
        result = _process.get()
        run_good = _process.successful()
        print(f"result: {result}")
        print(f"run_good: {run_good}")

    pp.close()
    print("Finish testing task.")
