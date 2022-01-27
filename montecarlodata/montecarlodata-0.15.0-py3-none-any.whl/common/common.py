import base64
import ipaddress
import json
from collections import Mapping
from functools import wraps
from typing import Optional, Dict, List, Any

from box import Box


def normalize_gql(field: str) -> Optional[str]:
    if field:
        return field.replace('_', '-').lower()


def read_as_base64(path: str) -> bytes:
    with open(path, 'rb') as fp:
        return base64.b64encode(fp.read())


def read_as_json(path: str) -> Dict:
    with open(path) as file:
        return json.load(file)


def read_as_json_string(path: str) -> str:
    """"Read and validate JSON file"""
    return json.dumps(read_as_json(path))


def struct_match(s1: Dict, s2: Dict) -> bool:
    return json.dumps(s1, sort_keys=True) == json.dumps(s2, sort_keys=True)


def boxify(use_snakes: Optional[bool] = False, default_box_attr: Optional[Any] = object()):
    """
    Convenience decorator to convert a dict into Box for ease of use.

    Set `use_snakes` to convert camelCase to snake_case. Use `default_box_attr` to set a default value.
    """
    def _boxify(func):
        @wraps(func)
        def _impl(self, *args, **kwargs):
            dict_ = func(self, *args, **kwargs)
            if dict_ and isinstance(dict_, Mapping):
                return Box(dict_, camel_killer_box=use_snakes, default_box_attr=default_box_attr)
            return dict_
        return _impl
    return _boxify


def chunks(lst: List, n: int):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def is_overlap(r1: str, r2: str) -> bool:
    """Check if two CIDR ranges overlap"""
    r1 = ipaddress.ip_network(r1)
    r2 = ipaddress.ip_network(r2)
    return r1.overlaps(r2) or r2.overlaps(r1)
