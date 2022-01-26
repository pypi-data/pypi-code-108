import typing

from functools import partial

CONSUME_DESCRIPTOR_ATTR = 'consume'


def register(fn, entrypoint):
    descriptors = getattr(fn, CONSUME_DESCRIPTOR_ATTR, None)

    if descriptors is None:
        descriptors = set()
        setattr(fn, CONSUME_DESCRIPTOR_ATTR, descriptors)
    descriptors.add(entrypoint)


class Consumer:
    def __init__(self, topics: typing.List[str], bootstrap_server):
        self.topics = topics
        self.bootstrap_server = bootstrap_server

    def get_topics(self):
        return self.topics

    @classmethod
    def decorator(cls, *args, **kwargs):
        def registering_decorator(fn, args, kwargs):
            instance = cls(*args, **kwargs)
            register(fn, instance)
            return fn

        return partial(registering_decorator, args=args, kwargs=kwargs)


consume = Consumer.decorator
