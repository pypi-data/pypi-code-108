"""
Implement multiprocessing via inheriting 'multiprocessing.Process'.
It also test with the data mapping feature with 'multipledispatch.dispatch'.
"""

from multiprocessing import Process
from multiprocessing.process import BaseProcess
from multipledispatch import dispatch
from typing import List, Type, TypeVar, Iterable as IterableType
from collections import Iterable
import random
import time



class TestProcess:

    @classmethod
    def run(cls) -> None:
        print("This is test process function.")
        __sleep_time = random.randrange(1, 10)
        print("Will sleep for ", __sleep_time)
        time.sleep(__sleep_time)
        print("Wake up!  ")


BaseProcessType = TypeVar("BaseProcessType", bound=BaseProcess)
ProcessType = TypeVar("ProcessType", bound=Process)


class ProcessOpt:

    def generate_process(self, target, *args, **kwargs):
        print("Generate the process")
        return Process(target=target, args=args, kwargs=kwargs)


    @dispatch(Process)
    def activate_worker(self, worker: Process):
        print("Start the one process")
        print(f"Start the {worker}")
        worker.start()


    @dispatch(Iterable)
    def activate_worker(self, worker: IterableType[Process]):
        print("Start the process")
        for w in worker:
            print(f"Start the {w}")
            # w.start()
            self.activate_worker(w)


    @dispatch(Process)
    def join_worker(self, worker: Process):
        print("Join the one process")
        print(f"Join the {worker}")
        worker.join()


    @dispatch(Iterable)
    def join_worker(self, worker: IterableType[Process]):
        print("Join the process")
        for w in worker:
            print(f"Join the {w}")
            # w.join()
            self.join_worker(w)


    def start_new_worker(self, target, *args, **kwargs):
        __process = self.generate_process(target=target, *args, **kwargs)
        print(f"[DEBUG] __process: {__process}")
        self.activate_worker(__process)
        self.join_worker(__process)
        return __process



if __name__ == '__main__':

    # General.
    # __process_list = [Process(target=TestProcess.run) for _ in range(5)]
    # for __p in __process_list:
    #     __p.start()
    #
    # for __p in __process_list:
    #     __p.join()

    # By method.
    __process_opt = ProcessOpt()
    print("+++++++++++ One Process +++++++++++")
    one_process = __process_opt.generate_process(target=TestProcess.run)
    __process_opt.activate_worker(one_process)
    print("begin join ...")
    print("process_list: ", one_process)
    __process_opt.join_worker(one_process)

    print("+++++++++++ Multiple Process +++++++++++")
    # process_list = [__process_opt.start_new_worker(target=TestProcess.run) for _ in range(5)]
    process_list = [__process_opt.generate_process(target=TestProcess.run) for _ in range(5)]
    __process_opt.activate_worker(process_list)
    print("begin join ...")
    print("process_list: ", process_list)
    __process_opt.join_worker(process_list)
