from multiprocessing import current_process, cpu_count, Pool, Process
from g_manager import GManager, GlobalManager
from test_module import TestA, TestB, TestAWithDecorator, TestBWithDecorator
from test_decorator import assign_to_manager
from os import getpid


# g_manager = GlobalManager()
# test_a = g_manager.TestA
# test_b = g_manager.TestB

# # # # Initial directly by the instance.
# GManager.register("TestA", TestA)
# GManager.register("TestB", TestB)
# print(f"TestA: {TestA}")    # <class 'test_module.TestA'>
# GManager.register(TestA.__name__, TestA)
# GManager.register(TestB.__name__, TestB)
# _gm = GManager()
# _gm.start()

# # # # Initial the instance via functions
# assign_to_manager(TestA)
# assign_to_manager(TestB)

g_manager = GlobalManager()



class TestSingleton:

    @classmethod
    def test_singleton_by_manager(cls, thread_id):
        # assign_to_manager(TestA)
        # assign_to_manager(TestB)

        # g_manager = GlobalManager()
        # # # Initial the instance via functions
        test_a = g_manager.TestA
        test_b = g_manager.TestB

        # # # # Initial directly by the instance.
        # test_a = _gm.TestA
        # test_b = _gm.TestB

        print(f"Instaiate - {current_process}::PID: {getpid()}")
        _test_a_instance = test_a()
        _test_b_instance = test_b()

        print(f"start to run function - {current_process}::PID: {getpid()}")
        _test_a_instance.fun_a()
        _test_b_instance.fun_b()

        print('This is t%s' % thread_id, current_process().name)
        print(f"End  - {current_process}::PID: {getpid()}")



def test_singleton_by_manager(thread_id):
    # assign_to_manager(TestA)
    # assign_to_manager(TestB)
    #
    # g_manager = GlobalManager()
    # # # # Initial the instance via functions
    test_a = g_manager.TestA
    test_b = g_manager.TestB

    # # # # Initial directly by the instance.
    # test_a = _gm.TestA
    # test_b = _gm.TestB

    print(f"Instaiate - {current_process}::PID: {getpid()}")
    _test_a_instance = test_a()
    _test_b_instance = test_b()

    print(f"start to run function - {current_process}::PID: {getpid()}")
    _test_a_instance.fun_a()
    _test_b_instance.fun_b()

    print('This is t%s' % thread_id, current_process().name)
    print(f"End  - {current_process}::PID: {getpid()}")


def test_singleton_by_manager_with_decorator(thread_id):
    print(f"Instaiate - {current_process}::PID: {getpid()}")
    # _test_a_instance = TestAWithDecorator(param="test_param")
    _test_a_instance = TestAWithDecorator(param=20)
    _test_b_instance = TestBWithDecorator()

    print(f"start to run function - {current_process}::PID: {getpid()}")
    _test_a_instance.fun_a()
    _test_b_instance.fun_b()

    print('This is t%s' % thread_id, current_process().name)
    print(f"End  - {current_process}::PID: {getpid()}")


def test_nested_singleton_by_manager_with_decorator(thread_id):
    print(f"Instaiate - {current_process}::PID: {getpid()}")
    _test_b_instance = TestBWithDecorator()
    _test_a_instance = TestAWithDecorator(param=20, nested_cls=_test_b_instance)

    print(f"start to run function - {current_process}::PID: {getpid()}")
    _test_a_instance.fun_a()
    _test_b_instance.fun_b()

    print('This is t%s' % thread_id, current_process().name)
    print(f"End  - {current_process}::PID: {getpid()}")


def test_singleton_general(thread_id):
    print(f"Instaiate - {current_process}::PID: {getpid()}")
    _test_a_instance = TestA()
    _test_b_instance = TestB()

    print(f"start to run function - {current_process}::PID: {getpid()}")
    _test_a_instance.fun_a()
    _test_b_instance.fun_b()

    print('This is t%s' % thread_id, current_process().name)
    print(f"End  - {current_process}::PID: {getpid()}")



def pool_main():
    pool = Pool(cpu_count())
    for i in range(10):
        pool.apply(func=test_singleton_by_manager, args=(i,))
        # pool.apply(func=test_singleton_by_manager_with_decorator, args=(i,))
        # pool.apply(func=test_singleton_general, args=(i,))
    pool.close()
    pool.join()


def process_main():
    # processes = [Process(target=test_singleton_by_manager, args=(i,)) for i in range(3)]
    # processes = [Process(target=test_singleton_by_manager_with_decorator, args=(i,)) for i in range(3)]
    # processes = [Process(target=test_singleton_general, args=(i,)) for i in range(3)]
    # processes = [Process(target=TestSingleton.test_singleton_by_manager, args=(i,)) for i in range(3)]
    processes = [Process(target=test_nested_singleton_by_manager_with_decorator, args=(i,)) for i in range(3)]

    for _p in processes:
        _p.start()

    for _p in processes:
        _p.join()
        _p.close()



if __name__ == '__main__':

    # pool_main()
    process_main()

