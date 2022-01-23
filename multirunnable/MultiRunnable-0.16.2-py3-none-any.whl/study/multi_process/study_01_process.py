"""
Implement multiprocessing via inheriting 'multiprocessing.Process'.
"""

from multiprocessing import Process



class TestProcess(Process):

    def run(self) -> None:
        print("This is test process function.")



if __name__ == '__main__':

    __process_list = [TestProcess() for _ in range(5)]
    for __p in __process_list:
        __p.start()
