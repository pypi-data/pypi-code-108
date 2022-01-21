import subprocess
import threading

import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#sys.path.insert(0, currentdir)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from define import *
import main_paras

class OffLineDetectionThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run (self):
        print('OffLineDetectionThread')
        while True:
            print('polling start')
            image=main_paras.queueForOffLine.get()
            print('from off line queue ',image)
            if image == CLOSE_NOW:
                break;
            ls=image.split('_')
            resultForGui = [int(ls[2]), int(ls[0]), ls[1], 'Off line test', 0 ]
            main_paras.queueForGui.put(resultForGui)
            main_paras.queueForOffLine.task_done()
            
if __name__ == "__main__":
    off_line_detection  = OffLineDetectionThread(4,"OnOff")

    off_line_detection.start()
