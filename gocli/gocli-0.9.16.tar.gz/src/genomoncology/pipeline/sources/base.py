from cytoolz.curried import map, curry
from .smart_lazy_file import SmartLazyFile

from genomoncology.pipeline.converters import (
    from_json_str,
    clean_str,
    non_null,
)


class Source(object):
    @staticmethod
    def is_source_class(obj):
        is_source = isinstance(obj, type) and issubclass(obj, Source)
        is_source = is_source or (
            isinstance(obj, curry)
            and isinstance(obj.func, type)
            and issubclass(obj.func, Source)
        )
        return is_source


class LazyFileSource(SmartLazyFile, Source):
    def __init__(self, filename):
        super().__init__(filename, mode="r")


class JsonlFileSource(LazyFileSource):
    def __iter__(self):
        iterator = super(JsonlFileSource, self).__iter__()
        return map(from_json_str, iterator)


class TextFileSource(LazyFileSource):
    def __iter__(self):
        iterator = super(TextFileSource, self).__iter__()
        return filter(non_null, map(clean_str, iterator))


class NullSource(LazyFileSource):
    """
    Returns back a single None to allow pipeline process to work
    for cases where records aren't being loaded like refresh_annotations.
    """

    def __iter__(self):
        return iter([None])
