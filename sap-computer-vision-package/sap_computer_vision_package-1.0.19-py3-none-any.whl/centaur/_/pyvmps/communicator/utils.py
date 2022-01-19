from typing import Dict

import ujson

from centaur._.pyvmps.cfg.config import GowebProtocolConst


def split_x_of_parts(x_of_parts: bytes):
    s = x_of_parts.decode()
    return s[:2] == s[2:]


def check_last_part(flag: bytes):
    # take into account ascii '0' and \0x00
    return flag == GowebProtocolConst.PY_LAST_PKT_FLAG or flag == GowebProtocolConst._PY_LAST_PKT_FLAG


def ujson_dumps_wrap(data: Dict) -> str:
    """ujson_dumps_wrap wraps ujson to dumps data that may contain bytes.
    This is a breaking change introduced in ujson==3.0 see https://newreleases.io/project/pypi/ujson/release/3.0.0

    :param data:
    """
    try:
        output = ujson.dumps(data, reject_bytes=False)  # type: ignore
        return output
    except Exception:
        output = ujson.dumps(data)
        return output


def ujson_loads_wrap(json_string: str) -> Dict:
    return ujson.loads(json_string)
