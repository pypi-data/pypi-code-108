import threading
import time

Thread_Number = 5


class SampleThread(threading.Thread):

    def __init__(self, lock):
        super().__init__()
        self.__lock = lock

    def run(self):
        print(f"Here is sample function running with lock. - {self.getName()}")
        self.__lock.acquire()
        print(f"Process in lock and it will sleep 2 seconds. - {self.getName()}")
        time.sleep(2)
        print(f"Wake up process and release lock. - {self.getName()}")
        self.__lock.release()


if __name__ == '__main__':

    lock = threading.Lock()
    thread_list = [SampleThread(lock=lock) for _ in range(Thread_Number)]
    for __thread in thread_list:
        __thread.start()

    for __thread in thread_list:
        __thread.join()

