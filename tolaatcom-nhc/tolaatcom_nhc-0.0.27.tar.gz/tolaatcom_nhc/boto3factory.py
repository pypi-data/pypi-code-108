import boto3
import threading

class ThreadLocalFactory:

    def __init__(self):
        self.local = threading.local()

    def Session(self):

        if not hasattr(self.local, 'session'):
            boto3.Session()
            setattr(self.local, 'session', boto3.Session())

        return getattr(self.local, 'session')

    def client(self, name):
        if not hasattr(self.local, name):
            setattr(self.local, name, self.Session().client(name))

        return getattr(self.local, name)

_singleton = ThreadLocalFactory()

def client(name):
    global _singleton
    return _singleton.client(name)