from lcyframe import MqRoute
from lcyframe import BaseModel
from tornado.gen import Return, coroutine

@MqRoute.tasks
class UserEvent(BaseModel):
    @classmethod
    @coroutine
    def update_header(cls, **msg):
        print(msg)
        raise Return(True)
