from multiprocessing.pool import ThreadPool
import time
import os



class TestTargetFunction:

    def test_func(self, *args, **kwargs):
        print("[1 time] parameter args: ", args)
        print("[1 time] parameter kwargs: ", kwargs)
        print("This is testing function. - ", os.getpid())
        time.sleep(3)
        print("[2 time] parameter args: ", args)
        print("[2 time] parameter kwargs: ", kwargs)
        return "Return value"


    def test_func_with_param(self, param_1, param_2, param_3):
        print("[1 time] parameter args: ", param_1, param_2, param_3)
        print("This is testing function. - ", os.getpid())
        time.sleep(3)
        print("[1 time] parameter args: ", param_1, param_2, param_3)
        return "Return value"


    @classmethod
    def main_code(cls, *args, **kwargs):
        print("[1 time] parameter args: ", args)
        print("[1 time] parameter kwargs: ", kwargs)
        print("This is testing function with classmethod. - ", os.getpid())
        time.sleep(3)
        print("[2 time] parameter args: ", args)
        print("[2 time] parameter kwargs: ", kwargs)
        return "Classmethod return value"



if __name__ == '__main__':

    # __pool = ThreadPool(processes=2)
    __pool = ThreadPool()

    # # # # Implement multi-processes by 'apply'
    # __map_result = [__pool.apply(func=TestTargetFunction.main_code, args=(f"param_{i}",)) for i in range(13)]
    # __map_result = __pool.apply(func=TestTargetFunction.main_code, args=(f"param_1", f"param_2", f"param_3", f"param_4"))

    # # # # Implement multi-processes by 'apply_async'
    # __process_list = [__pool.apply_async(func=TestTargetFunction.main_code, args=(f"param_{i}",)) for i in range(13)]
    # for __process in __process_list:
    #     __process.get()

    # # # # Implement multi-processes by 'map' with one argument
    # __map_result = __pool.map(TestTargetFunction.main_code, ("param_1", "param_2", "param_3"))
    # __map_list = [__pool.map_async(func=TestTargetFunction.main_code, iterable=("param_1", "param_2", "param_3")) for _ in range(3)]
    # for __process in __map_list:
    #     __result = __process.get()
    #     print("Result: ",  __result)

    # # # # Implement multi-processes by 'map' with multiple arguments
    # __map_result = __pool.map(TestTargetFunction.main_code,
    #                               # [("param_1",), ("arg_1",), ("index_1",)])
    #                                 ["param_1", "arg_1", "index_1"])

    # # # # Implement multi-processes by 'map' with multiple arguments
    # __map_result = __pool.map(TestTargetFunction.main_code,
    #                               [("param_1","param_2"), ("arg_1","arg_2"), ("index_1","index_2")])

    # # # # Implement multi-processes by 'starmap' with one argument
    # __map_result = __pool.starmap(TestTargetFunction.main_code,
    #                               [("param_1",), ("arg_1",), ("index_1",)])

    # # # # Implement multi-processes by 'starmap' with multiple arguments
    # __map_result = __pool.starmap(TestTargetFunction.main_code,
    #                               [("param_1", "param_2", "param_3"),
    #                                ("arg_1", "arg_2", "arg_3"),
    #                                ("index_1", "index_2", "index_3")])
    # __map_result = __pool.starmap(TestTargetFunction.main_code,
    #                               (("param_1", "param_2", "param_3"),
    #                                ("arg_1", "arg_2", "arg_3"),
    #                                ("index_1", "index_2", "index_3")))

    # # # # Implement multi-processes by 'imap' with one arguments
    # imap_result = []
    # # __map_result = __pool.imap(TestTargetFunction.main_code,
    # #                            [("param_1",), ("arg_1",), ("index_1",)])
    # __map_result = __pool.imap(TestTargetFunction.main_code,
    #                            # ("param_1", "arg_1", "index_1"))
    #                            ["param_1", "arg_1", "index_1"])
    # for __imap_r in __map_result:
    #     imap_result.append(__imap_r)
    # print("Result imap_result: ", imap_result)

    # # # # Implement multi-processes by 'imap' with one arguments
    imap_result = []
    # __map_result = __pool.imap_unordered(TestTargetFunction.main_code,
    #                            [("param_1",), ("arg_1",), ("index_1",)])
    __map_result = __pool.imap_unordered(TestTargetFunction.main_code,
                                         ("param_1", "arg_1", "index_1"))
    for __imap_r in __map_result:
        imap_result.append(__imap_r)
    print("Result imap_result: ", imap_result)

    __pool.close()
    __pool.join()

    print("Result: ", __map_result)

