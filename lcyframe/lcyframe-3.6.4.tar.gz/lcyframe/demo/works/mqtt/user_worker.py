from lcyframe import MqttTask, ReadMqtt
from lcyframe import BaseModel

@MqttTask(topic="topic1", qos=2)
class ExampleEvent(ReadMqtt, BaseModel):

    @classmethod
    def on_create_user(cls, **msg):
        print(msg, "mqtt")
        return msg

