from .message import Message
from threading import Event


class MessageEvent:
    def __init__(self, call_back=None):
        self.event = Event()
        self.message = None
        self.call_back = call_back

    def trigger(self, message: Message):
        self.message = message
        self.event.set()
        if self.call_back:
            self.call_back(self.message)

    def wait(self, time_out: int = 0):
        time_out_sec = None
        if time_out:
            time_out_sec = float(time_out) / 1000
        if self.event.wait(timeout=time_out_sec):
            return self.message
        return None
