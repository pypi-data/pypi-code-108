from click.utils import LazyFile
from cytoolz.curried import curry

from genomoncology.pipeline.converters import to_json_str


class Sink(object):
    def write(self, unit):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    @staticmethod
    def is_sink_class(obj):
        is_sink = isinstance(obj, type) and issubclass(obj, Sink)
        is_sink = is_sink or (
            isinstance(obj, curry)
            and isinstance(obj.func, type)
            and issubclass(obj.func, Sink)
        )
        return is_sink


class FileSink(Sink):
    def __init__(self, filename, insert_newlines=True):
        self.output = LazyFile(filename, mode="w")
        self.insert_newlines = insert_newlines

    def convert(self, unit):
        raise NotImplementedError

    def write(self, unit):
        if unit is not None:

            unit = self.convert(unit)

            if unit is not None:
                self.output.write(unit)

                if self.insert_newlines:
                    self.output.write("\n")

        return unit

    def close(self):
        if self.output.name != "-":
            self.output.close()


class JsonlFileSink(FileSink):
    def convert(self, unit):
        return to_json_str(unit)


class TextFileSink(FileSink):
    def convert(self, unit):
        return str(unit)
