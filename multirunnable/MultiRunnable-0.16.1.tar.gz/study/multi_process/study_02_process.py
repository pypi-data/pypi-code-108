"""
Implement multiprocessing via calling 'multiprocessing.Process'.
"""

from multiprocessing import Process
from multipledispatch import dispatch
from multimethod import overload, isa, multimethod
from typing import List, Type, TypeVar, NewType, Iterable



class TestProcess:

    @classmethod
    def run(cls) -> None:
        print("This is test process function.")


# ProcessType = NewType("ProcessType", Process)
ProcessType = TypeVar("ProcessType", bound=Process)


class ProcessOpt:

    def generate_process(self, target, *args, **kwargs):
        print("Generate the process")
        return Process(target=target, args=args, kwargs=kwargs)


    @overload
    def activate_worker(self, worker: isa(ProcessType)):
        print("Start the one process")
        print(f"Start the {worker}")
        worker.start()


    @overload
    def activate_worker(self, worker: isa(List[ProcessType])):
        print("Start the process")
        for w in worker:
            print(f"Start the {w}")
            # w.start()
            self.activate_worker(w)


    @overload
    def join_worker(self, worker: isa(ProcessType)):
        print("Join the one process")
        print(f"Join the {worker}")
        worker.join()


    @overload
    def join_worker(self, worker: isa(List[ProcessType])):
        print("Join the process")
        for w in worker:
            print(f"Join the {w}")
            # w.join()
            self.join_worker(w)


    def start_new_worker(self, target, *args, **kwargs):
        __process = self.generate_process(target=target, *args, **kwargs)
        print(f"[DEBUG] __process: {__process}")
        print(f"[DEBUG] type of __process: {type(__process)}")
        print(f"[DEBUG] type of __process: {type(__process) is Process}")
        print(f"[DEBUG] type of __process: {type(__process) is Type[Process]}")
        self.activate_worker(__process)
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
    process_list = [__process_opt.start_new_worker(target=TestProcess.run) for _ in range(5)]
    print("begin join ...")
    print("process_list: ", process_list)
    __process_opt.join_worker(worker=list(process_list))

    # for process in process_list:
    #     __process_opt.join_worker(worker=process)

