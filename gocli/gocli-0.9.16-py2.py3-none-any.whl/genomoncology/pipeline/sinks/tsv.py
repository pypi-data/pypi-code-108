from cytoolz.curried import curry
from glom import glom

from genomoncology.parse import DocType
from genomoncology.parse.ensures import ensure_collection
from .base import FileSink
from ..converters import to_str


@curry
class TsvFileSink(FileSink):
    def __init__(
        self, filename, columns=None, include_header=False, delimiter="\t"
    ):
        super().__init__(filename)
        self.delimiter = delimiter
        self.columns = ensure_collection(columns)
        self.include_header = include_header

    def write(self, unit):
        if self.include_header or DocType.HEADER.is_not(unit):
            super(TsvFileSink.func, self).write(unit)

    def convert(self, unit):
        self.columns = self.columns or DocType.get_default_columns(unit)

        if DocType.HEADER.is_a(unit):
            data = DocType.get_header_names(self.columns)
        else:
            data = [to_str(glom(unit, g, default="")) for g in self.columns]

        return self.delimiter.join(data)
