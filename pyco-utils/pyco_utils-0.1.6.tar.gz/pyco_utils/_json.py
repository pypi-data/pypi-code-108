import json
import uuid
from collections import OrderedDict
from pprint import pformat, saferepr
import difflib
from datetime import datetime


class CustomJSONEncoder(json.JSONEncoder):
    """
    default support datetime.datetime and uuid.UUID
    enable convert object by custom `http exception`
    usually:
        "to_json":  Common Class
        "to_dict":  Custom Model
        "as_dict"： SQLAlchemy Rows
        "get_json": json response
        "__html__": jinja templates

    """
    _jsonify_methods = [
        "to_json",
        "get_json",  # json response
        "to_dict",
        "as_dict",  # SQLAlchemy Rows
        "__html__",  # jinja templates
        # "toJson",
        # "getJson",  # json response
        # "toDict",
        # "asDict",  # SQLAlchemy Rows
    ]

    _jsonify_strict = False
    _pformat_depth = 2

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S.%f')
        elif isinstance(obj, uuid.UUID):
            return str(obj)
        else:
            for k in self._jsonify_methods:
                fn = getattr(obj, k, None)
                if callable(fn):
                    return fn()
                elif isinstance(fn, (str, int, float, dict)):
                    return fn

            m = pformat_any(obj, depth=self._pformat_depth)
            print("JsonEncoded???", m)
            if self._jsonify_strict:
                m = json.JSONEncoder.default(self, obj)
            return m


def pformat_any(data, depth=2, width=80, indent=2, **kwargs):
    return " :: ".join([str(type(data)), pformat(data, indent=indent, width=width, depth=depth)])


def pformat_json(data, cls=CustomJSONEncoder, indent=2, ensure_ascii=False, **kwargs):
    return json.dumps(data, cls=cls, indent=indent, ensure_ascii=ensure_ascii, **kwargs)


def save_plain_file(data, filename: str, indent=2, mode="w", **kwargs):
    fext = filename.rsplit('.', 1)[-1]
    if fext.startswith("json"):
        if isinstance(data, bytes):
            data = data.decode()
        elif not isinstance(data, str):
            data = pformat_json(data, indent=indent, **kwargs)
    elif not isinstance(data, str):
        data = pformat_any(data, indent=indent, **kwargs)
    with open(filename, mode) as fr:
        fr.write(data)
    return fext, data


def ordered_obj(obj, sorted_ary=False):
    # if sorted_ary is True, disorderd array is equal.
    if isinstance(obj, dict):
        return sorted((k, ordered_obj(v)) for k, v in obj.items())
    elif isinstance(obj, list):
        if sorted_ary:
            return sorted(ordered_obj(x) for x in obj)
        else:
            return list(ordered_obj(x) for x in obj)
    elif isinstance(obj, set):
        return sorted(ordered_obj(x) for x in obj)
    else:
        return obj


def compare_json(obj1, obj2, sorted_ary=False):
    m1 = ordered_obj(obj1, sorted_ary=sorted_ary)
    m2 = ordered_obj(obj2, sorted_ary=sorted_ary)
    return m1 == m2


def compare_json_content(text1: str, text2: str, sorted_ary=False):
    obj1 = json.loads(text1)
    obj2 = json.loads(text2)
    return compare_json(obj1, obj2, sorted_ary=sorted_ary)


def diff_json(obj1, obj2):
    m1 = ordered_obj(obj1)
    m2 = ordered_obj(obj2)
    is_eq = m1 == m2
    differ = difflib.Differ()
    if not is_eq:
        tm1 = json.dumps(m1, indent=2, cls=CustomJSONEncoder)
        tm2 = json.dumps(m2, indent=2, cls=CustomJSONEncoder)
        diff = ''.join(differ.compare(tm1.splitlines(True), tm2.splitlines(True)))
        return diff


def diff_json_content(text1, text2):
    # diff1 = ''.join(differ.compare(text1.splitlines(True), text2.splitlines(True)))
    obj1 = json.loads(text1)
    obj2 = json.loads(text2)
    return diff_json(obj1, obj2)
