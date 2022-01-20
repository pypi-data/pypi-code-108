import datetime as dt
from decimal import Decimal
from json import JSONEncoder, dumps, dump, JSONDecoder, loads, load
from typing import Any, Iterable
from uuid import UUID
from collections import namedtuple
from jcramda import (is_a, has_attr, is_a_int, when, camelcase, key_map, flat_concat, b64_encode,
                     compose, identity, attr, partial, is_a_mapper)
from .pdtools import TYPE_REGS


_str_to_type = {
    'true': True,
    'false': False,
}

__all__ = (
    'SafeJsonEncoder',
    'SafeJsonDecoder',
    'to_json',
    'to_json_file',
    'pp_json',
    'fix_document',
    'to_obj',
    'from_json_file',
)


_type_regs = (
    *TYPE_REGS,
    (is_a((UUID, )), str),
    (is_a(dt.datetime), lambda o: o.strftime('%Y-%m-%d %H:%M:%S')),
    (is_a(bytes), b64_encode),
    (is_a(memoryview), compose(b64_encode, bytes)),
    (is_a(dict), flat_concat),
    (is_a_int, int),
    (has_attr('__html__'), compose(identity, attr('__html__'))),
    (is_a(str), lambda s: _str_to_type.get(s, s))
)


class SafeJsonEncoder(JSONEncoder):

    def default(self, object_: Any) -> Any:
        r = when(*_type_regs, str)(object_)
        return key_map(camelcase, r)


class SafeJsonDecoder(JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=fix_document, *args, **kwargs)


to_json = partial(dumps, cls=SafeJsonEncoder, ensure_ascii=False)
to_json_file = partial(dump, cls=SafeJsonEncoder, ensure_ascii=False)

DocFixedOpt = namedtuple('DocFixedOpt', 'where, fixed')


def fix_document(doc, fix_options: Iterable[DocFixedOpt]):
    if is_a_mapper(doc):
        r = {}
        for k, v in doc.items():
            new_key, new_v = k, v
            if str(k).startswith('$'):
                if len(doc) == 1:
                    return fix_document(v, fix_options)
                new_key = k[1:]
            r[new_key] = fix_document(new_v, fix_options)
        return r
    elif is_a((list, tuple, set), doc):
        return [fix_document(x, fix_options) for x in doc]

    if str(doc).lower() in ('nan', 'nat', 'null'):
        return None

    return when(
        *fix_options,
        (is_a(Decimal), identity),
        else_=doc
    )(doc)


to_obj = partial(loads, cls=SafeJsonDecoder)


def from_json_file(file_path):
    with open(file_path, 'r') as fp:
        s = load(fp, cls=SafeJsonDecoder)
    if is_a(str, s):
        s = to_obj(s)
    return s


def pp_json(obj):
    printed_str = dumps(obj, indent=2, ensure_ascii=False)
    try:
        from pygments import highlight, lexers, formatters
        colorful_json = highlight(printed_str, lexers.JsonLexer(),
                                formatters.TerminalFormatter())
    except ModuleNotFoundError:
        from jcutil.chalk import GreenChalk
        colorful_json = GreenChalk(printed_str)
    return colorful_json
