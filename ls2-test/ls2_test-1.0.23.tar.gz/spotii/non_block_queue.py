import queue
class NonBlockQue():
    def __init__(self):
        self.nQue=queue.Queue()
    def put(self, item):
        self.nQue.put(item, True, 0.01)        
    def get(self):  
        try:
            data = self.nQue.get(True, 0.01)
        except queue.Empty:
            data = None
        return data
    def getTimeout(self, timeout):  
        try:
            data = self.nQue.get(True, timeout)
        except queue.Empty:
            data = None
        return data
    def clear(self):
        self.nQue.queue.clear()
