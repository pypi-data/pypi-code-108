from .core import Primitive, synchronized

class Escrow(Primitive):

    def __init__(self):
        Primitive.__init__(self)
        self.WaitingGet = False
        self.Value = None
        self.GetLock = Primitive()
        self.PutLock = Primitive()

    def get(self, timeout = None):
        with self.GetLock:
            try:
                self.WaitingGet = True
                self.wakeup()                   # notify the thread, which it waiting to put
                while self.Value is None:
                    self.sleep(timeout)         # will raise exception on timeout
                value = self.Value
                self.Value = None
                self.wakeup()                   # tell the putter that the package was received
                return value
            finally:
                self.WaitingGet = False

    def put(self, value, timeout = None):
        assert value is not None
        with self.PutLock:
            try:
                while not self.WaitingGet:      # wait for the receiver
                    self.sleep(timeout)
                self.Value = value
                self.wakeup()
                while self.Value is not None:   # wait for pickup
                    self.sleep()
            finally:
                self.Value = None               # time-out or something else


            
        