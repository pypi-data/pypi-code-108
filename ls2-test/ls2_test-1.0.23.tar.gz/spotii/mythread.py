import threading
import time
from datetime import datetime,timezone


# sent =threading.Event()
# answered=threading.Event()
# sring=threading.Event()
# deRegistered=threading.Event()
# incomeData=[]
    

class MyThread (threading.Thread):
    def __init__(self, threadID, name, counter, *args):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.args = args
    def run (self):
#        while True:
        time.sleep(self.args[0])
        print('in thread {:10}{:10}'.format(self.name,time.ctime()))
                        



