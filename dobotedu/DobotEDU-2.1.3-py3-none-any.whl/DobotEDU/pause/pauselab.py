class PauseLab(object):
    def __init__(self) -> None:
        super().__init__()
        self.on_pause = None

    def set_pause(self, on_pause):
        self.on_pause = on_pause
        if self.on_pause is not None and not callable(self.on_pause):
            raise Exception("on_disconnected should callable")


def pause(func):
    def wrapper(self, *args, **kwargs):
        self.on_pause()
        return func(self, *args, **kwargs)

    return wrapper
