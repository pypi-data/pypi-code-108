import time
from zumidashboard import screen


def drive_open_eyes(t):
    time.sleep(t)
    screen.clear()
    screen.hello()
