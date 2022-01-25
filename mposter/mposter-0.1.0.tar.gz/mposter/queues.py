from threading import Thread
from queue import Queue
import threading


class Queues(object):
    def __init__(self, threads: int, target):
        self.target = target
        self.queues = Queue()
        self.workers = list()

        for _idx in range(threads):
            self.add_thread()

    def add_thread(self, **kwargs):
        _stop_event = threading.Event()
        _worker = Thread(target=self._thread_get, args=(len(self.workers), self.queues, _stop_event, kwargs))
        _worker.setDaemon(True)
        _worker.start()

        self.workers.append((_worker, _stop_event))

    def remove_thread(self):
        self.workers[-1][1].set()
        del self.workers[-1]

    def _thread_get(self, threading_idx, q, stop_event, kwargs):
        while not stop_event.is_set():
            try:
                print(f'{threading_idx} / {len(self.workers)}')
                if self.target.__code__.co_argcount == 2:
                    self.target(q.get(), kwargs)

                elif self.target.__code__.co_argcount == 1:
                    self.target(q.get())

                print(f'{threading_idx} / {len(self.workers)}; done')

            except Exception as ex:
                print(ex)

            finally:
                q.task_done()

    def join(self):
        self.queues.join()

    def put(self, data):
        self.queues.put(data)
