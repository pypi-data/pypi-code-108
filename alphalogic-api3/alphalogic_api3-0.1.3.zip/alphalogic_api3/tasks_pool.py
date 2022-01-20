# -*- coding: utf-8 -*-
from multiprocessing.dummy import Pool as ThreadPool
from threading import Thread, Event, Lock
from queue import PriorityQueue, Empty
import time


class PriorityTasks(object):
    """
    This class issues a task that must be executed immediately
    """
    def __init__(self):
        self.peak = None
        self.queue = PriorityQueue()
        self.mutex = Lock()

    def get_tasks(self, current_time):
        with self.mutex:
            if self.peak is None:
                return None
            elif current_time < self.peak[0]:
                return None
            else:
                result = [self.peak[1]]
                self.peak = None
                while not(self.queue.empty()):
                    tmp = self.queue.get()
                    if current_time >= tmp[0]:
                        result.append(tmp[1])
                    else:
                        self.peak = tmp
                        break
                return result

    def put(self, item):
        with self.mutex:
            if self.peak is None:
                self.peak = item
            elif item[0] < self.peak[0]:
                self.queue.put(self.peak)
                self.peak = item
            else:
                self.queue.put(item)

    def empty(self):
        with self.mutex:
            return (self.peak is None) and (self.queue.empty())

    def clear(self):
        with self.mutex:
            while not self.queue.empty():
                try:
                    self.queue.get(False)
                except Empty:
                    continue
                self.queue.task_done()


class TasksPool(object):
    """
    This class distribute tasks with the use thread pool
    """
    def __init__(self, num_thread=None):
        self.thread_pool = ThreadPool(processes=num_thread)  # if processes=None, number of thread define automatically
        self.operation_thread = Thread(target=self.run_operation_thread)
        self.shutdown_flag = Event()
        self.queue_tasks = PriorityTasks()  # tasks with timestamps
        self.list_futures = []
        self.operation_thread.start()

    def run_operation_thread(self):
        while not self.shutdown_flag.is_set():
            tasks = self.queue_tasks.get_tasks(time.time())
            if not(tasks is None):
                result = self.thread_pool.map_async(lambda f: f(call_again=True), tasks)
                self.list_futures.append(result)
            self.clear_done_futures()
            time.sleep(0.001)
        map(lambda x: x.wait(), self.list_futures)
        self.list_futures = []
        self.queue_tasks.clear()

    def add_task(self, time_stamp, task):
        if not self.shutdown_flag.is_set():
            self.queue_tasks.put((time_stamp, task))

    def stop_operation_thread(self):
        if self.operation_thread.is_alive():
            self.shutdown_flag.set()
            self.operation_thread.join()

    def restart_operation_thread(self):
        self.stop_operation_thread()
        self.operation_thread = Thread(target=self.run_operation_thread)
        self.queue_tasks = PriorityTasks()
        self.shutdown_flag.clear()
        self.operation_thread.start()

    def clear_done_futures(self):
        self.list_futures = list(filter(lambda x: not x.ready(), self.list_futures))