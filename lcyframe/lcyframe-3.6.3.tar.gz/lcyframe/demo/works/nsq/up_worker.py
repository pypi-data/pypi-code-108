from lcyframe.libs.nsq_route import NsqTask, ReadNsq
from lcyframe import BaseModel

@NsqTask(topic="test",  # 订阅同一个topic的不同channel的消费者，均可收到消息
         channel="channel")
class ExampleEvent(ReadNsq, BaseModel):

    @classmethod
    def on_create_user(cls, **msg):
        print(msg, "channel 1")
        return True     # 必须返回True False None之一
