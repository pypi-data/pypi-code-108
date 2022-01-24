"""Module responsible for JSON serialization and deserialization.

The library orjson is used when available, else the standard library is used.
"""
from __future__ import annotations

from typing import Any, Callable, Optional, Protocol, Tuple, Union

from pydantic import BaseModel


class LoadJSONProtocol(Protocol):
    def __call__(
        self, v: Union[None, bytes, bytearray, memoryview, str], **kwargs: Any
    ) -> Any:  # pragma: no cover
        ...  # pragma: no cover


class DumpJSONProtocol(Protocol):
    def __call__(
        self,
        v: Any,
        *,
        default: Optional[Callable[..., Any]] = None,
        indent: bool = False,
        sort_keys: bool = False,
        **kwargs: Any,
    ) -> str:
        ...  # pragma: no cover


class DumpBytesJSONProtocol(Protocol):
    def __call__(
        self,
        v: Any,
        *,
        default: Optional[Callable[..., Any]] = None,
        indent: bool = False,
        sort_keys: bool = False,
        **kwargs: Any,
    ) -> bytes:
        ...  # pragma: no cover


def default() -> Tuple[
    LoadJSONProtocol,
    DumpJSONProtocol,
    DumpBytesJSONProtocol,
]:
    import json

    def loads(v: Union[None, bytes, bytearray, memoryview, str], **kwargs: Any) -> Any:
        if v is None:
            return None
        if v == b"":
            return None
        if v == "":
            return None
        return json.loads(v, **kwargs)

    def dumps(
        v: Any,
        *,
        default: Optional[Callable[..., Any]] = None,
        indent: bool = False,
        sort_keys: bool = False,
        **kwargs: Any,
    ) -> str:
        """Serialize Python objects to a JSON string using standard library."""
        if v is None:
            return ""
        if v == b"":
            return ""
        if isinstance(v, str):
            return v
        if isinstance(v, BaseModel):
            return v.json(indent=indent if indent else 0, sort_keys=sort_keys)
        return json.dumps(
            v,
            default=default,
            indent=2 if indent else 0,
            sort_keys=sort_keys,
            **kwargs,
        )

    def dump(
        v: Any,
        *,
        default: Optional[Callable[..., Any]] = None,
        indent: bool = False,
        sort_keys: bool = False,
        **kwargs: Any,
    ) -> bytes:
        """Serialize Python objects to JSON bytes using standard library."""
        if v is None:
            return b""
        if isinstance(v, BaseModel):
            return v.json(indent=indent if indent else 0, sort_keys=sort_keys).encode(
                "utf-8"
            )
        if isinstance(v, bytes):
            return v
        if isinstance(v, str):
            return v.encode("utf-8")

        return json.dumps(
            v,
            indent=2 if indent else 0,
            default=default,
            sort_keys=sort_keys,
            **kwargs,
        ).encode(encoding="utf-8")

    return loads, dumps, dump


def orjson() -> Tuple[
    LoadJSONProtocol,
    DumpJSONProtocol,
    DumpBytesJSONProtocol,
]:

    import orjson as _orjson

    def loads(v: Union[None, bytes, bytearray, memoryview, str], **_: Any) -> Any:
        """Deserialize JSON to Python objects using orjson."""
        return _orjson.loads(v) if v else None

    def dump(
        v: Any,
        *,
        default: Optional[Callable[..., Any]] = None,
        indent: bool = False,
        sort_keys: bool = False,
        **kwargs: Any,
    ) -> bytes:
        """Serialize Python objects to JSON bytes using orjson."""
        if v is None:
            return b""
        if isinstance(v, BaseModel):
            return v.json(indent=indent, sort_keys=sort_keys).encode("utf-8")
        if isinstance(v, bytes):
            return v
        if isinstance(v, str):
            return v.encode("utf-8")
        # We allow numpy serialization and str keys conversion by default
        opts = _orjson.OPT_SERIALIZE_NUMPY | _orjson.OPT_NON_STR_KEYS
        # Optionally indentation
        if indent:
            opts |= _orjson.OPT_INDENT_2
        # And optionally key sorting
        if sort_keys:
            opts |= _orjson.OPT_SORT_KEYS
        # orjson's dumps returns bytes instead of str
        return _orjson.dumps(v, default=default, option=opts)

    def dumps(
        v: Any,
        *,
        default: Optional[Callable[..., Any]] = None,
        indent: bool = False,
        sort_keys: bool = False,
        **kwargs: Any,
    ) -> str:
        """Serialize Python objects to a JSON string using orjson."""
        if isinstance(v, BaseModel):
            return v.json(indent=indent, sort_keys=sort_keys)
        return dump(
            v, default=default, indent=indent, sort_keys=sort_keys, **kwargs
        ).decode(encoding="utf-8")

    return loads, dumps, dump


try:
    loads, dumps, dump = orjson()
except ModuleNotFoundError:  # pragma: no cover
    loads, dumps, dump = default()  # pragma: no cover


__all__ = ["loads", "dumps", "dump"]
