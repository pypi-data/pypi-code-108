from pathlib import Path


class OutputBase:
    output_type = None

    def __init__(self, builder, path: Path):
        self.builder = builder
        self.path: Path = path

    def begin(self):
        raise NotImplemented()

    def finish(self):
        raise NotImplemented()

    @property
    def created(self):
        raise NotImplementedError()
