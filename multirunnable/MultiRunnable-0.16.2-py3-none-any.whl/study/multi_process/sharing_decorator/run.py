import multiprocessing as mp
from instance_main import TestCls


if __name__ == '__main__':

    _test_cls = TestCls()

    processes = [mp.Process(target=_test_cls.test_fun) for _ in range(3)]

    print("Run process ")
    for _p in processes:
        # _p.run()
        _p.start()

    print("End process ")
    for _p in processes:
        _p.join()
        _p.close()

