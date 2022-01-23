import threading
import random
import time



class ProducerThread(threading.Thread):

    def __init__(self, thread_condition: threading.Condition):
        threading.Thread.__init__(self)
        self.__condition = thread_condition


    def run(self):
        print(f"[Producer] It will keep producing something useless message.", self.getName())
        while True:
            # # # # # 1. Method
            # __sleep_time = random.randrange(1, 10)
            # print(f"[Producer] It will sleep for {__sleep_time} seconds.", self.getName())
            # time.sleep(__sleep_time)
            # self.__condition.acquire()
            # self.__condition.notifyAll()
            # self.__condition.release()

            # # # # 2. Method
            __sleep_time = random.randrange(1, 10)
            print(f"[Producer] It will sleep for {__sleep_time} seconds.", self.getName())
            time.sleep(__sleep_time)
            with self.__condition:
                self.__condition.notifyAll()



class ConsumerThread(threading.Thread):

    def __init__(self, thread_condition: threading.Condition):
        threading.Thread.__init__(self)
        self.__condition = thread_condition


    def run(self):
        print(f"[Consumer] It detects the message which be produced by ProducerThread.", self.getName())
        while True:
            # # # # # 1. Method
            # self.__condition.acquire()
            # time.sleep(1)
            # print("[Consumer] ConsumerThread waiting ...", self.getName())
            # self.__condition.wait()
            # print("[Consumer] ConsumerThread wait up.", self.getName())
            # self.__condition.release()

            # # # # 2. Method
            with self.__condition:
                time.sleep(1)
                print("[Consumer] ConsumerThread waiting ...", self.getName())
                self.__condition.wait()
                print("[Consumer] ConsumerThread wait up.", self.getName())



if __name__ == '__main__':

    condition = threading.Condition()

    __producer = ProducerThread(condition)
    __consumer = ConsumerThread(condition)

    __producer.start()
    __consumer.start()

    __producer.join()
    __consumer.join()
