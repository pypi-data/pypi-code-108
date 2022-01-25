import dataclasses
import logging
import typing


class RefStr(str):
    def __init__(self, s):
        """ Split a [<service>:]<entity>:<action_type>:<action> """
        result = s.split(":")
        self.service = None
        if len(result) == 4:
            self.service = result.pop(0)
        self.entity = result.pop(0)
        self.action_type = result.pop(0)
        self.action = result.pop(0)
        str.__init__(self)


def shoot_and_forget(handler, msg):
    try:
        handler(msg)
    except Exception as e:
        logging.warning(e, exc_info=True)


@dataclasses.dataclass
class Subscriber:
    topic: typing.Any
    handler: callable

    def __call__(self, *args, **kwargs):
        return self.handler(*args, **kwargs)

    def accepts(self, topic, msg):
        try:
            assert topic == self.topic
            return True
        except AssertionError:
            return False


class Registry(list):
    def get(self, topic, msg):
        for sub in self:
            if sub.accepts(topic, msg):
                yield sub


class Broadcaster:
    def __init__(self, executor=None):
        self.registry = Registry()
        self.subscriber_cls = Subscriber
        self.executor = executor or shoot_and_forget

    def subscribe(self, topic, func):
        self.registry.append(
            self.subscriber_cls(topic, func)
        )

    def accept(self, topic, msg):
        for sub in self.registry.get(topic, msg):
            self.executor(
                sub, msg
            )
