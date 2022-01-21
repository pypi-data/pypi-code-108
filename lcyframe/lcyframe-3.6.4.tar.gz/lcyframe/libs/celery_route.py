# -*- coding: utf-8 -*-
import os
import logging
from celery import Task
from celery import Celery, shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class MyCelery(Celery):
    def gen_task_name(self, name, module):
        """
        重新命名
        python3.6.5下, 在pycharm里debug模式运行，存在BUG:Fatal Python error: PyCOND_WAIT(gil_cond) failed
        :param name:
        :param module:
        :return:
        """
        module = module.split(".")[-1]
        # if module.endswith('.tasks'):
        #     module = module[:-6]
        return super(MyCelery, self).gen_task_name(name, module)


class Events(object):
    """
    生产者
    """

    # tasks_dict = {}
    #
    # def __setattr__(self, key, value):
    #     self.tasks_dict[key] = value

    def __getattr__(self, name):
        if name not in self.__dict__:
            raise Exception("task '%s' is not exists" % name)
        else:
            return self.__dict__[name]


# 统一处理成功、失败、重试的基类
class BaseTask(Task):
    abstract = True

    def on_success(self, retval, task_id, args, kwargs):
        print('task done: {0}'.format(retval))
        return super(BaseTask, self).on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # 捕获异常信息 sentrycli.captureException(exc)
        super(BaseTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        # sentrycli.captureException(exc)
        super(BaseTask, self).on_retry(exc, task_id, args, kwargs, einfo)

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        # print('Task returned: {0!r}'.format(self.request))
        logger.info("Task returned")

    @classmethod
    def backoff(cls, attempts):
        """
        重试间隔根据次数递增
        1, 2, 4, 8, 16, 32, ...
        """
        return 2 ** attempts


class BaseEvent(object):
    queue = ""




def shared_task(*args, **kwargs):
    """
    接管装饰
    :param args:
    :param kwargs:
    :return:
    """
    return shared_task(*args, **kwargs)
