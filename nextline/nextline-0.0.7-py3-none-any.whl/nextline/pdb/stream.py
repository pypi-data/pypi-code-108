##__________________________________________________________________||
class StreamOut:
    def __init__(self, queue):
        self.queue = queue

    def write(self, s):
        self.queue.put(s)

    def flush(self):
        pass


class StreamIn:
    def __init__(self, queue):
        self.queue = queue

    def readline(self):
        return self.queue.get()


##__________________________________________________________________||
