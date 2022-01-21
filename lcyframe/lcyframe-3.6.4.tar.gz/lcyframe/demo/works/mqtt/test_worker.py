from lcyframe import MqttTask
from lcyframe import ReadMqtt
from lcyframe import BaseModel

@MqttTask(topic="#", qos=2)
class ExampleEvent2(ReadMqtt, BaseModel):

    @classmethod
    def on_test_mqtt(cls, **msg):
        print(msg, "this is mqtt message")
