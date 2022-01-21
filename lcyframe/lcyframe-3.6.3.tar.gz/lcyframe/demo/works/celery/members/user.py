# -*- coding: utf-8 -*-
from celery import shared_task
import random, time
from lcyframe.libs.celery_route import BaseTask
from lcyframe.libs.celery_route import BaseEvent

@shared_task(ignore_result=False)  # 普通函数装饰为 celery task
def save_image(x):
    """
    seleep时间随机
    任务多线程并发执行，谁先执行完毕，谁先输出结果
    :param x:
    :return:
    """
    n = round(random.random(), 2)
    time.sleep(n)

    # model.UserModel.get_xxx()
    return x, n


class UserEvent(BaseEvent):
    @staticmethod
    @shared_task(ignore_result=False)  # 普通函数装饰为 celery task
    def register(x):
        """
        sleep时间随机
        任务多线程并发执行，谁先执行完毕，谁先输出结果
        :use self.application.celery.DefaultEvent.add.delay(111)
        :param x:
        :return:

        """
        n = round(random.random(), 2)
        time.sleep(n)

        return x, n
