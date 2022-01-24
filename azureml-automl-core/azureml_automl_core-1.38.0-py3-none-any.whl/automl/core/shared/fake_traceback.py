# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module to serialize and deserialize traceback-like objects."""
from typing import Any, Dict, Optional, Type
import types

"""
Implementation note:
We must use the objects below during serialization and deserialization. It is not possible to manually instantiate
frame objects in CPython without some interpreter hackery (you will get "TypeError: cannot create 'frame' instances")
and traceback objects can only be instantiated in Python code starting from Python 3.7.

Luckily the traceback library doesn't care if they're real objects or if we're using duck typing.
"""


class FakeCode:
    """Fake code object that implements enough to make traceback logging work."""

    def __init__(self, f_code: types.CodeType):
        """Create a new FakeCode."""
        # Here we just copy everything over except things like local variables that do nothing for us except
        # waste space and stub them out instead.
        self.co_filename = f_code.co_filename
        self.co_name = f_code.co_name
        self.co_argcount = f_code.co_argcount
        self.co_kwonlyargcount = f_code.co_kwonlyargcount
        self.co_varnames = f_code.co_varnames
        self.co_cellvars = ()
        self.co_freevars = ()
        self.co_nlocals = f_code.co_nlocals
        self.co_stacksize = f_code.co_stacksize
        self.co_flags = f_code.co_flags
        self.co_consts = ()
        self.co_code = b''
        self.co_lnotab = b''

    def serialize(self) -> Dict[str, Any]:
        """Serialize this object to a dict."""
        return self.__dict__

    @classmethod
    def deserialize(cls: 'Type[FakeCode]', d: Optional[Dict[str, Any]]) -> Optional['FakeCode']:
        """Deserialize this object from a dict."""
        if d is None:
            return None
        # We do NOT call the constructor here because we need to set attributes on it directly.
        # __init__() calls __new__() under the hood, then runs the rest of the code inside itself.
        obj = cls.__new__(cls)  # type: FakeCode
        obj.__dict__ = d
        return obj


class FakeFrame:
    """Fake frame object that implements enough to make traceback logging work."""

    def __init__(self, frame: types.FrameType):
        """Create a new FakeFrame."""
        # There is no point in storing locals or globals, except for __file__ and __name__ because those are
        # needed to render a stacktrace properly.
        self.f_locals = {}  # type: Dict[str, Any]
        self.f_globals = {
            k: v for k, v in frame.f_globals.items() if k in {'__file__', '__name__'}
        }
        self.f_code = FakeCode(frame.f_code)    # type: Optional[FakeCode]
        self.f_lineno = frame.f_lineno

    def serialize(self) -> Dict[str, Any]:
        """Serialize this object to a dict."""
        return {
            'f_locals': self.f_locals,
            'f_globals': self.f_globals,
            'f_code': self.f_code.serialize() if self.f_code else None,
            'f_lineno': self.f_lineno
        }

    @classmethod
    def deserialize(cls: 'Type[FakeFrame]', d: Optional[Dict[str, Any]]) -> Optional['FakeFrame']:
        """Deserialize this object from a dict."""
        if d is None:
            return None
        # We do NOT call the constructor here because we need to set attributes on it directly.
        # __init__() calls __new__() under the hood, then runs the rest of the code inside itself.
        obj = cls.__new__(cls)  # type: FakeFrame
        obj.f_locals = d['f_locals']
        obj.f_globals = d['f_globals']
        obj.f_code = FakeCode.deserialize(d['f_code'])
        obj.f_lineno = d['f_lineno']
        return obj


class FakeTraceback:
    """Fake traceback object that implements enough to make traceback logging work."""

    def __init__(self, tb: types.TracebackType):
        """Create a new FakeTraceback."""
        self.tb_next = FakeTraceback(tb.tb_next) if tb.tb_next else None
        self.tb_frame = FakeFrame(tb.tb_frame)  # type: Optional[FakeFrame]
        self.tb_lineno = tb.tb_lineno
        self.tb_lasti = tb.tb_lasti

    def serialize(self) -> Dict[str, Any]:
        """Serialize this object to a dict."""
        return {
            'tb_next': self.tb_next.serialize() if self.tb_next else None,
            'tb_frame': self.tb_frame.serialize() if self.tb_frame else None,
            'tb_lineno': self.tb_lineno,
            'tb_lasti': self.tb_lasti
        }

    @classmethod
    def serialize_exception_tb(cls: 'Type[FakeTraceback]',
                               ex: Optional[BaseException]) -> Optional[Dict[str, Any]]:
        if ex is None:
            return None
        return cls.serialize_traceback(ex.__traceback__)

    @classmethod
    def serialize_traceback(cls: 'Type[FakeTraceback]',
                            tb: Optional[types.TracebackType]) -> Optional[Dict[str, Any]]:
        if tb is None:
            return None
        return cls(tb).serialize()

    @classmethod
    def deserialize(cls: 'Type[FakeTraceback]', d: Optional[Dict[str, Any]]) -> Optional['FakeTraceback']:
        """Deserialize this object from a dict."""
        if d is None:
            return None
        # We do NOT call the constructor here because we need to set attributes on it directly.
        # __init__() calls __new__() under the hood, then runs the rest of the code inside itself.
        obj = cls.__new__(cls)  # type: FakeTraceback
        obj.tb_next = cls.deserialize(d['tb_next'])
        obj.tb_frame = FakeFrame.deserialize(d['tb_frame'])
        obj.tb_lineno = d['tb_lineno']
        obj.tb_lasti = d['tb_lasti']
        return obj
