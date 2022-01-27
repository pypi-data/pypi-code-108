import time

from heartbeat.heartbeat_observer import HeartbeatObserver
from heartbeat.heatbeat_reporter import HeartbeatReporter
from heartbeat.model.heartbeat_event import HeartbeatEvent

host = '61.160.36.168'
port = 4032


def callback(result: HeartbeatEvent):
    print("test", result)




while True:
    time.sleep(1)
