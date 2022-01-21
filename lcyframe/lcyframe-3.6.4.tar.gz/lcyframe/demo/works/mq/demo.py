from lcyframe import MqRoute
from lcyframe import BaseModel
from tornado.gen import Return, coroutine

@MqRoute.tasks
class Demo(BaseModel):
    @classmethod
    @coroutine
    def event1(cls, **msg):
        print(msg)
        raise Return(True)

    @classmethod
    @coroutine
    def event2(cls, **msg):
        print(msg)
        raise Return(True)
