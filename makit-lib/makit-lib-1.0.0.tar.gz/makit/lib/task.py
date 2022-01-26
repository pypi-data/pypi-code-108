# coding=utf-8

"""
@Author: LiangChao
@Email: kevinleong1011@hotmail.com
@Desc: 
"""
import threading
import time
import traceback
import uuid
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import datetime
from typing import List, Optional

from .logging import logger

__all__ = [
    'TaskPool'
]

WAITING = 'waiting'  # 等待执行
RUNNING = 'running'  # 执行中
TERMINATED = 'terminated'  # 终止
PAUSED = 'paused'  # 暂停
FINISHED = 'finished'  # 已完成
CANCELED = 'canceled'  # 已取消


class TaskHandler(object):
    """
    任务控制器，控制任务执行、暂停、恢复
    """

    def __init__(self):
        self._thread_event = threading.Event()
        self._thread_event.set()
        self._force_stop = False
        self._stop_reason = None
        self._pause_timeout = None

    def wait(self, timeout=None):
        self._thread_event.wait(timeout or self._pause_timeout)
        if self._force_stop:
            raise TaskTerminatedError(self._stop_reason)

    def pause(self, timeout=None):
        """
        暂停执行

        :return:
        """
        self._pause_timeout = timeout
        self._thread_event.clear()

    def resume(self):
        """
        恢复执行

        :return:
        """
        self._thread_event.set()

    def force_stop(self, reason=None):
        """
        强行停止
        :param reason:
        :return:
        """
        self._force_stop = True
        self._stop_reason = reason
        self.resume()

    def handle(self, target, *args, **kwargs):
        obj = target(*args, **kwargs) if isinstance(target, type) else target
        setattr(obj, 'task_handler', self)
        return obj


class Task:
    """
    测试任务
    """

    def __init__(self, func, *args, **kwargs):
        self.id = str(uuid.uuid4())
        self.thread_id = None
        self.runtime = None
        self.func, self.args, self.kwargs = func, args, kwargs
        self._status = None
        self.parent: Optional[Task] = None
        self._handler = TaskHandler()
        self.subs: List[Task] = []
        self._sub_finish_count = 0
        self.future = None
        self.related_threads = set()  # 一个测试可能会根据需要开启多个线程，这些线程需要在测试完成后停止，或在执行期交互数据
        self.pool = None

    @property
    def status(self):
        """测试任务状态"""
        return self._status

    @status.setter
    def status(self, value):
        self._status = value
        if value == FINISHED and self.parent:
            self.parent._sub_finish()
        logger.debug(f'task {value}: {self.id}')

    @property
    def ready(self):
        """任务是否就绪"""
        if self.runtime:
            return self.runtime <= datetime.now()
        return True

    def pause(self, timeout=None, include_subs=True):
        """
        暂停任务
        :param timeout:
        :param include_subs:
        :return:
        """
        if self.status != RUNNING:
            return False
        self._handler.pause(timeout)
        if include_subs:
            for sub in self.subs:
                sub.pause(timeout, include_subs)
        self.status = PAUSED
        return True

    def resume(self):
        """
        恢复任务
        :return:
        """
        if self.status != PAUSED:
            return False
        if self.subs:
            for sub in self.subs:
                sub.resume()
        logger.debug(f'唤醒任务：{self.id}')
        self._handler.resume()
        self.status = RUNNING
        return True

    def terminate(self, reason=None):
        """
        终止任务
        :param reason:
        :return:
        """
        assert self.status == RUNNING, f'Task [{self.id}] is not running!'
        self.status = TERMINATED
        self._handler.force_stop(reason)
        for thread in self.related_threads:
            thread.join()

    def cancel(self):
        """
        取消任务
        :return:
        """
        if self.future:
            if not self.future.cancel():
                return False
        if not self.status:  # 如果任务没有开始执行，直接取消
            self.status = CANCELED
            return True
        return self.status == CANCELED

    def wait(self, timeout=None):
        """
        等待测试任务
        :param timeout:
        :return:
        """
        self._handler.wait(timeout)

    def wait_sub_finished(self):
        """
        等待子任务完成

        :return:
        """
        if self.subs:
            logger.debug('等待子任务完成')
            self.pause(include_subs=False)
            self._handler.wait()

    def run(self):
        """
        执行任务
        :return:
        """
        if self.status:
            return
        if not self.ready:
            raise TaskNotReadyError(self.id)
        self.thread_id = threading.current_thread().ident
        self.status = RUNNING
        try:
            self.func(*self.args, **self.kwargs)
        except TaskTerminatedError:
            self.status = TERMINATED
        except Exception:
            self.status = FINISHED
            logger.error(traceback.format_exc())
        finally:
            self.status = FINISHED
            if not self.pool.has_unfinished_tasks():
                self.pool.stop()

    def _sub_finish(self):
        self._sub_finish_count += 1
        if self._sub_finish_count >= len(self.subs) and self._status == PAUSED:
            self._handler.resume()

    def start_thread(self, thread):
        self.related_threads.add(thread)
        thread.start()

    def bind_thread(self, thread_id):
        self.related_threads.add(thread_id)

    def __lt__(self, other):
        return other and self.runtime < other.runtime

    def __repr__(self):
        return f'<TestTask {self.id}>'


class TaskPool:
    """任务池"""

    def __init__(
            self,
            max_workers=None,
            thread_name_prefix='',
            initializer=None,
            init_args=()
    ):
        self.tasks = {}
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix=thread_name_prefix,
            initializer=initializer,
            initargs=init_args
        )
        self._running = False
        self.__event = threading.Event()
        self.__event.set()
        self._lock = threading.Lock()

    def get_task(self, task_id):
        """
        根据ID获取任务
        :param task_id: 任务ID
        :return:
        """
        for task, args, kwargs in self.tasks:
            if task.id == task_id:
                return task
        # raise TaskNotFoundError(task_id)

    def submit(self, test, *args, **kwargs):
        task = Task(test, *args, **kwargs)
        task.pool = self
        self.tasks[task.id] = task
        if not self._running:
            self.start()
        return task

    def remove(self, task):
        """
        移除任务
        :param task:
        :return:
        """
        with self._lock:
            self.tasks.pop(task.id, None)

    def start(self):
        """开始任务池线程"""

        def _work():
            while self._running:
                for task in self.__get_ready_tasks():
                    task.future = future = self.executor.submit(task.run)
                    setattr(future, 'task_id', task.id)
                    # future.result()
                time.sleep(1)

        if not self._running:
            self._running = True
            threading.Thread(target=_work, daemon=True).start()

    def stop(self):
        """
        停止任务池线程
        :return:
        """
        self._running = False
        self.__event.set()

    def has_unfinished_tasks(self):
        """是否还有正在执行的任务"""
        with self._lock:
            for task, _ in [*self.tasks.values()]:
                if task.status != FINISHED:
                    return True
            self._running = False
            return False

    def wait_all_tasks_complete(self, timeout=None):
        """
        等待所有任务执行完成
        :param timeout: 超时
        :return:
        """
        self.__event.clear()
        self.__event.wait(timeout)

    def current_task(self) -> Task:
        thread_id = threading.current_thread().ident
        for _, task in self.tasks.items():
            if task.status == RUNNING and task.thread_id == thread_id:
                return task

    def wait(self, timeout=None):
        """
        线程任务进入等待状态
        :param timeout:
        :return:
        """
        task = self.current_task()
        if task:
            task.wait(timeout)

    def pause(self, timeout=None):
        """
        暂停任务，若设置超时，那么到时间会自动恢复
        :param timeout: 暂停超时
        :return:
        """
        task = self.current_task()
        if task:
            task.pause(timeout)

    def resume(self):
        """
        恢复任务
        :return:
        """
        task = self.current_task()
        if task:
            task.resume()

    def terminate(self, reason=None):
        """
        终止任务
        :param reason:
        :return:
        """
        task = self.current_task()
        if task:
            task.terminate(reason=reason)

    def cancel(self):
        """
        取消任务
        :return:
        """
        task = self.current_task()
        if task:
            task.cancel()

    def __get_ready_tasks(self):
        for task, _ in [*self.tasks.values()]:
            if task.ready and not task.status:
                yield task


class TaskError(Exception):
    """"""


class TaskCancelError(TaskError):
    """
    任务取消异常
    """


class TaskTerminatedError(TaskError):
    """"""


class TaskNotReadyError(TaskError):
    """"""
