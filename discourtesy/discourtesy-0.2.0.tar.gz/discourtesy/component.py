class Component:
    def __init__(self, name, coroutine, timeout):
        self.name = name
        self.coroutine = coroutine
        self.timeout = timeout


def component(name, timeout=0):
    def decorator(coroutine):
        return Component(name, coroutine, timeout)

    return decorator
