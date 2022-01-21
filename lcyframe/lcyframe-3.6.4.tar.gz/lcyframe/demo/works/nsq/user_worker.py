from lcyframe import NsqTask
from lcyframe import ReadNsq
from lcyframe import BaseModel

@NsqTask(topic="test", channel="channel2")
class ExampleEvent2(ReadNsq, BaseModel):

    @classmethod
    def on_create_user(cls, **msg):
        print(msg, "channel2")
        return True     # 必须返回True False None之一

