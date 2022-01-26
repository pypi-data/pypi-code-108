import json
from collections.abc import Iterable
from typing import Any, Union

from cognite.client import CogniteClient


def valfilter(cond, dct):
    """Filters items in dictionary by cond(value)"""
    return {k: v for k, v in dct.items() if cond(v)}


def keyfilter(cond, dct):
    """Filters items in dictionary by cond(key)"""
    return {k: v for k, v in dct.items() if cond(k)}


def valmap(fn, dct):
    """Applies fn to all values in dictionary"""
    return {k: fn(v) for k, v in dct.items()}


def keymap(fn, dct):
    """Applies fn to all keys in dictionary"""
    return {fn(k): v for k, v in dct.items()}


def is_jsonable(data: Union[str, bytes, bytearray]) -> bool:
    try:
        json.loads(data)
        return True
    except Exception:
        return False


def parse_json_if_json(data: str) -> str:
    if is_jsonable(data):
        return json.loads(data)
    return data


def strip_patch_from_version(version: str) -> str:
    if not isinstance(version, str):
        raise TypeError(f"Expected input '{version}' to be of type {str}, not {type(version)}")

    if version.count(".") > 2:
        raise ValueError("Expected at most two dots in version string, e.g. '1.33.7'")

    return ".".join(version.split(".")[:2])


def is_string_truthy(bool_like: Any) -> bool:
    """
    This function tries to solve the annoying problem of checking whether a given
    string is thruthy or not. It also accepts booleans and None.

    String caPitaLizaTIon is ignored.
    """
    if bool_like is None:
        return False

    elif isinstance(bool_like, bool):
        return bool_like

    elif not isinstance(bool_like, str):
        raise TypeError(f"Expected one of {[bool, str, None]}, got {type(bool_like)}")

    return bool_like.capitalize() == "True"


def validate_arg_type(enforced_types):
    """
    Produces decorators that type check their input functions first argument
    to be one of the given expected and enforced types.
    """
    enforced_types = tuple(enforced_types if isinstance(enforced_types, Iterable) else [enforced_types])
    assert all(isinstance(exp_type, type) for exp_type in enforced_types)

    def decorator(fn):
        def wrapper(arg, **kwargs):
            if not isinstance(arg, enforced_types):
                raise TypeError(f"Expected input arg type to one of {enforced_types}, not {type(arg)}")
            return fn(arg, **kwargs)

        return wrapper

    return decorator


def air_data_set_id(client: CogniteClient, name: str) -> int:
    data_sets = client.data_sets.list(limit=-1).dump()
    for ds in data_sets:
        if "name" in ds:
            if ("archived" not in ds["metadata"] or ds["metadata"]["archived"] != "true") and ds["name"] == name:
                return ds["id"]
    raise LookupError(f"Not able to find dataset named {name}")
