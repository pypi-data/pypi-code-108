from cytoolz.curried import curry, assoc, filter

from genomoncology.parse import ensures, DocType, __TYPE__, __CHILD__
from .base import LazyFileSource
import csv


def do_split(delimiter, s):
    s = s.strip()
    if delimiter == ",":
        # reference: https://stackoverflow.com/a/35822856
        val = next(csv.reader([s]))
    else:
        val = s.split(delimiter)
    return val


@curry
def str_to_dict(columns, meta, delimiter, skip_comment, comment_char, s):
    if skip_comment:
        if s.startswith(comment_char):
            return None
    # note: warning, doesn't handle escaping for CSVs yet.
    d = dict(zip(columns, do_split(delimiter, s)))
    d.update(meta)
    return d


@curry
class DelimitedFileSource(LazyFileSource):
    def __init__(
        self,
        filename,
        columns,
        delimiter="\t",
        skip_comment=False,
        comment_char="#",
        include_header=True,
        **meta
    ):
        self._mapper = None
        self.columns = ensures.ensure_collection(columns)
        self.delimiter = delimiter
        self.skip_comment = skip_comment
        self.comment_char = comment_char
        self.include_header = include_header
        self.meta = meta

        if __TYPE__ not in meta:
            self.meta = assoc(self.meta, __TYPE__, DocType.TSV.value)

        super().__init__(filename)

    def __iter__(self):
        # noinspection PyUnresolvedReferences
        iterator = super(DelimitedFileSource.func, self).__iter__()

        if not self.columns:
            data_line = next(iterator).strip()
            self.columns = do_split(self.delimiter, data_line)

        if self.include_header:
            yield self.create_header()

        # noinspection PyTypeChecker
        yield from filter(lambda x: x is not None, map(self.mapper, iterator))

    def create_header(self):
        return {
            __TYPE__: DocType.HEADER.value,
            __CHILD__: self.meta.get(__TYPE__),
            "columns": self.columns,
            "meta": self.meta,
            "file_path": self.name,
        }

    @property
    def mapper(self):
        if self._mapper is None:
            self._mapper = str_to_dict(
                self.columns,
                self.meta,
                self.delimiter,
                self.skip_comment,
                self.comment_char,
            )
        return self._mapper
