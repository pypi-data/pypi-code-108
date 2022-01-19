import multiprocessing
import random
import time
import os


def target_func(*args, **kwargs):
    print(f"This is target function ... - {os.getpid()}")
    print(f"Target function args: {args} - {os.getpid()}")
    print(f"Target function kwargs: {kwargs} - {os.getpid()}")
    sleep_time = random.randrange(1, 15)
    print(f"It will sleep for {sleep_time} seconds. - {os.getpid()}")
    time.sleep(sleep_time)
    return "Test Result"


def other_func(*args, **kwargs):
    print(f"This is other function with {args} ... - {os.getpid()}")
    sleep_time = random.randrange(1, 5)
    print(f"It will sleep for {sleep_time} seconds. - {os.getpid()}")
    time.sleep(sleep_time)
    return "Other Test Result"



if __name__ == '__main__':

    # p_pool = multiprocessing.Pool(processes=10)
    p_pool = multiprocessing.Pool()
    # params_list = [f"param_{i}" for i in range(100)]
    result = p_pool.map(target_func, ["1", "2", "3"])
    # result = p_pool.map(target_func, params_list)
    o_result = p_pool.map(other_func, ["param_1", "param_2", "param_3"])
    p_pool.close()
    p_pool.join()

    print("Result: ", result)
    print("Result: ", o_result)
