"""
*@File    : day_timed_task.py
*@Time    :8/1/21 4:40 下午
*author:QauFue ,技术改变未来
"""

import datetime
import threading
from decorator_time_task import timed_task_go


class DayTask():
    """一天24小时 总共 86400秒 """
    DAYMINUTE = 86400
    data_time = " 19:21:11"  # day_time : 设置每天几点钟开始执行

    def __init__(self, other_func):
        self.other_func = other_func

    def time_seting(self):
        # 获取现在时间
        now_time = datetime.datetime.now()
        # 获取明天时间
        next_time = now_time + datetime.timedelta(days=+1)

        next_year = next_time.date().year
        next_month = next_time.date().month
        next_day = next_time.date().day
        # 获取明天3点时间
        next_time = datetime.datetime.strptime(
            str(next_year) + "-" + str(next_month) + "-" + str(next_day) + str(self.data_time), "%Y-%m-%d %H:%M:%S")
        # # 获取昨天时间
        # last_time = now_time + datetime.timedelta(days=-1)

        # 获取距离明天3点时间，单位为秒
        timer_start_time = (next_time - now_time).total_seconds()
        print(timer_start_time)
        return timer_start_time

    @timed_task_go  # 定时任务；
    def func(self):
        self.other_func()
        # 如果需要循环调用，就要添加以下方法
        timer = threading.Timer(self.DAYMINUTE, self.func)
        timer.start()

    def go(self):
        timer = threading.Timer(self.DAYMINUTE, self.func)
        timer.start()


if __name__ == '__main__':
    # def func():
    #     i = i+1
    #     print('kaix'+i)
    #     timer = threading.Timer(0.1, func)
    #     timer.start()
    #
    #
    # func()
    #
    #
    item = 1


    def other_func():
        print('test')


    daytask = DayTask(other_func)
    daytask.DAYMINUTE = 0.001
    daytask.func()
