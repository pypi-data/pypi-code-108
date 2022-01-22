import os
import sys
import time

PATH = os.path.abspath(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
sys.path.append(PATH)
print(PATH)

from src.winhye_common.mqtt.mqtt_base import MqttClint, MqttSendMessageException


def mqtt_test():
    mqtt_config = {
        "broker": "mqtt-cn-i7m2ceaxt07.mqtt.aliyuncs.com",
        "port": 1883,
        "topic": "reported_kaifa/AGV-S/#",
        "AccessKey_ID": "LTAI5tFbpMr1R4CVCbUePMWy",
        "AccessKey_Secret": "MJ2WWUbIKDg4UY5EbEsgQ983Lkfwff",
        "instance_id": "mqtt-cn-i7m2ceaxt07",
        "group_id": "GID_kaifa"
    }
    data = {
        "type": 1,
        "code": 200,
        "payload": {
            "id": "E41203294",
            "armed": "arm"
        }
    }
    handler = MqttClint(mqtt_config)
    time.sleep(1)
    try:
        while True:
            handler.send_message("send_kaifa/AGV-S/aa", data)
            time.sleep(60)
    except MqttSendMessageException:
        print(111111111111111111)


if __name__ == '__main__':
    mqtt_test()
