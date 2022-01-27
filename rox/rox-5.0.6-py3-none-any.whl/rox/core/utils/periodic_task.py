from threading import Event
from time import sleep

from concurrent.futures import ThreadPoolExecutor


def run(action, period):
    cancel_event = Event()
    period = int(round(period))
    executor = ThreadPoolExecutor(1)

    def run_timer():
        while True:
            for i in range(0, period):
                if cancel_event.is_set():
                    return
                sleep(1)
            if cancel_event.is_set():
                return
            action()

    executor.submit(run_timer)
    return cancel_event
