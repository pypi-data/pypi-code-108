from functools import reduce
import json
import sys


def read_json(path):
    with open(path) as f:
        return json.load(f)


class Config:
    def __init__(self, data):
        self.__data = data

    def __getitem__(self, path):
        return reduce(lambda data, key: data[key], path.split("."), self.__data)

    def configure(self, parser, table):
        defaults = {}
        for src, dest in table.items():
            try:
                defaults[dest] = self[src]
            except KeyError:
                pass
        parser.set_defaults(**defaults)

    @classmethod
    def read(cls, path, load=read_json):
        return cls(load(path))

    @classmethod
    def read_from_option(
        cls, parser, field, args=sys.argv, help_flags=["-h", "--help"], **kwargs
    ):
        args, _ = parser.parse_known_args(
            args=[arg for arg in args if arg not in help_flags]
        )
        path = getattr(args, field)
        if path is None:
            return None
        return cls.read(path, **kwargs)

    @classmethod
    def load(cls, parser, field, table, **kwargs):
        config = cls.read_from_option(parser, field, **kwargs)
        if config is not None:
            config.configure(parser, table)
