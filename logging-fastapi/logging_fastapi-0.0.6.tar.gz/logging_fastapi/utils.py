import inspect
import traceback
import pydash
import sys


def format_exc():
    etype, value, tb = sys.exc_info()
    lines = traceback.format_exception(etype=etype, value=value, tb=tb)

    error = {
        "message": str(value),
        "stack": pydash.map_(
            lines[-2:], lambda line: line.replace("\n", "").replace('"', "'")
        )[::-1],
    }

    return error


def is_obj_or_dict(obj):
    return inspect.isclass(obj) or type(obj) is dict
