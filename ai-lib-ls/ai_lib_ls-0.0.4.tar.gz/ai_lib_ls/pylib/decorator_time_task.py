"""
*@File    : decorator_time_task.py
*@Time    :8/1/21 6:16 下午
*author:QauFue ,技术改变未来
"""
import time
from functools import wraps


# 定时任务
def timed_task_go(func):
    run_count = 0  # 执行运行次数统计

    @wraps(func)  # 保持原有函数的内容不变
    def wrapper(*args, **kw):  # *args 可自动扩展参数 如果函数有传值可实现 ,  **kw ：f3 关键字的传参
        nonlocal run_count
        run_count = run_count + 1
        taskRun(run_count)
        func(*args, **kw)

    return wrapper


def taskRun(run_count):
    print(f'次数：{run_count}')


def timed_run_time(func):
    run_count = 0  # 执行运行次数统计
    @wraps(func)  # 保持原有函数的内容不变
    def wrapper(*args, **kw):  # *args 可自动扩展参数 如果函数有传值可实现 ,  **kw ：f3 关键字的传参
        nonlocal run_count
        run_count = run_count + 1
        start_time = time.perf_counter()
        func(*args, **kw)
        end_time = time.perf_counter()
        taskRunTime(end_time - start_time, run_count)

    return wrapper


def taskRunTime(run_time, run_count):
    print(f'运行次数{run_count}', '--------', f'运行时间:{run_time}')
