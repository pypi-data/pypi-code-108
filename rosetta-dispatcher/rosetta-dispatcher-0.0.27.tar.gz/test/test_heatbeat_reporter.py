import time

from heartbeat.heatbeat_reporter import HeartbeatReporter

host = '61.160.36.168'
port = 4032

hbr = HeartbeatReporter(namespace="SERVICE_NMT_ZH_EN",
                        service_name="heartbeat_service_name",
                        host_ip="0.0.0.0",
                        host_name="heatbeat_host_name",
                        redis_host=host,
                        redis_port=port,
                        interval=1)
hbr.start()

while True:
    time.sleep(1)
