from multiprocessing import Pool, Queue, Manager
import os


Running_Queue = None
# __Ｍanager = Manager()
# _Queue = __Ｍanager.Queue()


class TestQueue:

    def target_fun(self, task: Queue):
        print("task.empty(): ", task.empty())
        while not task.empty():
            # val = Running_Queue.get()
            # val = _Queue.get()
            val = task.get()
            print(f"Get queue value: {val} - {os.getpid()}")
        task.close()
        task.join()



class TestWorker:

    def __init__(self, process_num: int):
        self.process_num = process_num


    def run(self, task_queue):
        # global Running_Queue
        self.queue_handling()

        __test = TestQueue()

        pool = Pool(processes=self.process_num)
        process_list = [
            pool.apply_async(
                func=__test.target_fun, kwds={"task": task_queue})
            for _ in range(self.process_num)]

        for __process in process_list:
            __result = __process.get()
            __successful = __process.successful()
            print("result: ", __result)
            print("successful: ", __successful)

        pool.close()
        pool.join()


    def queue_handling(self):
        __Ｍanager = Manager()
        _Queue = __Ｍanager.Queue()
        sql_query = "select * from stock_data_2330 limit 3;"
        sql_tasks = [sql_query for _ in range(20)]
        for sql in sql_tasks:
            _Queue.put(sql)
            # queue.put(sql)
        return _Queue



if __name__ == '__main__':

    process_number = 10

    # __Ｍanager = Manager()
    # _Queue = __Ｍanager.Queue()
    # # _Queue = Queue()
    # sql_query = "select * from stock_data_2330 limit 3;"
    # sql_tasks = [sql_query for _ in range(20)]
    # for sql in sql_tasks:
    #     _Queue.put(sql)

    __worker = TestWorker(process_num=process_number)
    running_queue = __worker.queue_handling()
    __worker.run(task_queue=running_queue)
