import threading
import random
import time



class ProducerThread(threading.Thread):

    def __init__(self, thread_event: threading.Event):
        threading.Thread.__init__(self)
        self.__event = thread_event


    def run(self):
        print(f"[Producer] It will keep producing something useless message.")
        while True:
            __sleep_time = random.randrange(1, 10)
            print(f"[Producer] It will sleep for {__sleep_time} seconds.")
            time.sleep(__sleep_time)
            self.__event.set()



class ConsumerThread(threading.Thread):

    def __init__(self, thread_event: threading.Event):
        threading.Thread.__init__(self)
        self.__event = thread_event


    def run(self):
        print(f"[Consumer] It detects the message which be produced by ProducerThread.")
        while True:
            time.sleep(1)
            print("[Consumer] ConsumerThread waiting ...")
            self.__event.wait()
            print("[Consumer] ConsumerThread wait up.")
            self.__event.clear()



if __name__ == '__main__':

    event = threading.Event()

    __producer = ProducerThread(event)
    __consumer = ConsumerThread(event)

    for __process in [__producer, __consumer]:
        __process.start()

    # __producer.start()
    # __consumer.start()
