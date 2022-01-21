import dataclasses
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Union, List, Iterable, Dict, Any
from uuid import UUID

from dataclass_dict_convert import dataclass_dict_convert, dataclass_auto_type_check, dataclass_copy_method, \
    dataclass_multiline_repr
from dataclass_dict_convert.convert import SimpleTypeConvertor

from stringcase import camelcase
from imecilabt_utils.urn_util import URN, check_valid_urn_bytype, always_optional_urn
from imecilabt_utils.validation_utils import is_valid_email


def urn_to_user_mini_id(urn: Optional[Union[str, URN]]) -> Optional[str]:
    if not urn:
        return None
    u = always_optional_urn(urn)
    if u and u.authority and u.name:
        auth = u.authority
        if auth == 'wall2.ilabt.iminds.be':
            auth = 'w2'
        if auth == 'ilabt.imec.be':
            auth = 'ilabt'
        if auth == 'example.com':  # used in tests
            auth = 'ex'
        return '{name}@{auth}'.format(auth=auth, name=u.name)
    else:
        return None


def urn_to_auth(urn: Optional[Union[str, URN]]) -> Optional[str]:
    if not urn:
        return None
    u = always_optional_urn(urn)
    if u and u.authority:
        return u.authority
    else:
        return None


def urn_to_name(urn: Optional[Union[str, URN]]) -> Optional[str]:
    if not urn:
        return None
    u = always_optional_urn(urn)
    if u and u.name:
        return u.name
    else:
        return None


def urn_from_dict_convertor(urn_str: str) -> URN:
    if urn_str is None:
        # not really allowed, but this way we typically move the failure to where it is a cleaner error
        return None
    assert isinstance(urn_str, str), f'not a str as expected, but {urn_str!r}'
    return URN(urn=urn_str)


def urn_to_dict_convertor(urn: URN) -> str:
    assert isinstance(urn, URN), f'not an urn as expected, but {urn!r}'
    return str(urn)


def urn_list_from_dict_convertor(urn_strs: List[str]) -> List[URN]:
    assert isinstance(urn_strs, Iterable)
    return [URN(urn=urn_str) for urn_str in urn_strs]


def urn_list_to_dict_convertor(urns: List[URN]) -> List[str]:
    assert isinstance(urns, Iterable)
    return [str(urn) for urn in urns]


def uuid_from_dict_convertor(uuid_str: str) -> UUID:
    if uuid_str is None:
        # not really allowed, but this way we typically move the failure to where it is a cleaner error
        return None
    assert isinstance(uuid_str, str), f'not a str as expected, but {uuid_str!r}'
    try:
        return UUID(uuid_str)
    except:
        logging.exception(f'Error converting {uuid_str!r} to UUID')
        raise


def uuid_to_dict_convertor(uuid: UUID) -> str:
    assert isinstance(uuid, UUID), f'not a UUID as expected, but {uuid!r}'
    return str(uuid)


UUID_TYPE_CONVERTOR = SimpleTypeConvertor(
    type=UUID,
    to_dict=uuid_to_dict_convertor,
    from_dict=uuid_from_dict_convertor
)

URN_TYPE_CONVERTOR = SimpleTypeConvertor(
    type=URN,
    to_dict=urn_to_dict_convertor,
    from_dict=urn_from_dict_convertor
)


def stringify_embedded_urns(orig: Union[Dict, List]) -> Any:
    # recursive, so only meant for small dicts/lists!
    if isinstance(orig, List):
        res = []
        for i in orig:
            if isinstance(i, URN):
                i = str(i)
            elif isinstance(i, Dict) or isinstance(i, List):
                i = stringify_embedded_urns(i)
            res.append(i)
        return res
    elif isinstance(orig, Dict):
        res = {}
        for k, v in orig.items():
            if isinstance(v, URN):
                v = str(v)
            elif isinstance(v, Dict) or isinstance(v, List):
                v = stringify_embedded_urns(v)
            res[k] = v
        return res
    else:
        if isinstance(orig, URN):
            return str(orig)
        return orig


def _is_json_compatible_type(orig: Any) -> bool:
    if orig is None:
        return True
    if isinstance(orig, str):
        return True
    if isinstance(orig, Dict):
        return True
    if isinstance(orig, List):
        return True
    if isinstance(orig, float):
        return True
    if isinstance(orig, int):
        return True
    if isinstance(orig, bool):
        return True
    return False


def is_json_compatible(orig: Union[Dict, List, str, float, int, bool]) -> bool:
    """
     Return True if this object can be converted to JSON.
     Returns false if the object, or any embedded object is not a dict, list, str, float, bool or int
     recursive, so only meant for small dicts/lists!
    """
    if isinstance(orig, List):
        for i in orig:
            if not _is_json_compatible_type(i):
                return False
            elif isinstance(i, Dict) or isinstance(i, List):
                if not is_json_compatible(i):
                    return False
        return True
    elif isinstance(orig, Dict):
        for k, v in orig.items():
            if not _is_json_compatible_type(k):
                return False
            if not _is_json_compatible_type(v):
                return False
            elif isinstance(v, Dict) or isinstance(v, List):
                if not is_json_compatible(v):
                    return False
        return True
    else:
        return _is_json_compatible_type(orig)


def assert_json_compatible(orig: Union[Dict, List, str, float, int, bool]):
    """
     raises AssertionError if this object can not be converted to JSON.
     This happens if the object, or any embedded object is not a dict, list, str, float, bool or int

     recursive, so only meant for small dicts/lists!
    """
    if isinstance(orig, List):
        for i in orig:
            assert _is_json_compatible_type(i), f'Non JSON compatible List item: {i!r}'
            if isinstance(i, Dict) or isinstance(i, List):
                assert_json_compatible(i)
    elif isinstance(orig, Dict):
        for k, v in orig.items():
            assert _is_json_compatible_type(k), f'Non JSON compatible key: {k!r}'
            assert _is_json_compatible_type(v), f'Non JSON compatible value for key {k!r}: {v!r}'
            if isinstance(v, Dict) or isinstance(v, List):
                assert_json_compatible(v)
    else:
        assert _is_json_compatible_type(orig), f'Not JSON compatible: {orig!r}'


def extract_exception_message(e: Exception):
    """
    Try to extract the "message" of an exception.
    (usually str(e) is enough, but this is meant to handle some edge cases as well.)
    """
    if hasattr(e, 'message') and e.message:
        return e.message
    if hasattr(e, 'msg') and e.msg:
        return e.msg
    res = str(e)
    if res:
        return res
    else:
        return str(type(e))
