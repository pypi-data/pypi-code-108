import threading


class Cache:
    def __init__(self):
        self.data = {}
        threading.Timer(10, self.clearCache).start()

    def setCache(self, name, data):
        self.data[name] = data

    def getCache(self, name):
        try:
            return self.data[name]
        except:
            return None

    def clearCache(self):
        self.data = {}
