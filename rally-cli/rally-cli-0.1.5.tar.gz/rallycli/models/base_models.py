from __future__ import annotations

import json
import re
from collections.abc import KeysView
from logging import getLogger
from typing import List, Optional, TypeVar, Type, Union

from box import Box
from pydantic import BaseModel, AnyHttpUrl, Field

from rallycli.models.memento import RallyPydanticMemento, Memento

logger = getLogger(__name__)

BOX_PARAMS = {"default_box": True, "default_box_attr": Box, "box_dots": True}

T = TypeVar('T')


class RallyType(Box):
    # Class atts: Compiled regex
    oid_re = re.compile(r".*Original ObjectID: (\d+)", re.DOTALL)
    formattedid_re = re.compile(r".*Original FormattedID: (\D{1,2}\d+)", re.DOTALL)
    oid_from_ref = re.compile(r".*/(\d+)$")

    def __init__(self, *args, **kwargs):
        kwargs.update(BOX_PARAMS)
        super().__init__(*args, **kwargs)

    def get_as_entry(self, method, keys: List[str]) -> RallyEntry:
        rally_entry = RallyEntry()
        rally_entry.set_method(method)
        rally_entry.set_element(self, method, keys)
        return rally_entry

    def clean_for_creation(self):
        # remove content from model not allowed for creation
        # keys to mantain & keys to delete:
        dkeys: List[str] = list(filter(lambda k: re.match(r"^(?:_.*)", k), self.keys()))
        for key in dkeys:
            self.pop(key, None)

    def clean_for_update(self):
        # remove content from model not allowed for creation
        # keys to mantain & keys to delete:
        dkeys: List[str] = list(filter(lambda k: re.match(r"^(?!_ref$|_type$)(?:_.*)", k), self.keys()))
        for key in dkeys:
            self.pop(key, None)

    def clean_custom_fields(self):
        # remove content from model not allowed for creation
        dkeys: List[str] = list(filter(lambda k: re.match(r"^(?:c_\w*)", k), self.keys()))
        for key in dkeys:
            self.pop(key, None)

    @classmethod
    def get_typed_list_from_results(cls: Type[T], results: list) -> List[T]:
        lst: List[T] = list()
        for result in results:
            obj = cls.__new__(cls)
            obj.__init__(result)
            lst.append(obj)
        return lst

    @classmethod
    def get_oid_from_ref(cls, ref: str) -> str:
        if match := RallyType.oid_from_ref.match(ref):
            return match.group(1)
        return ""


class RallyPydanticBase(BaseModel):
    __slots__ = ('caretaker',)
    # ? _ref: Optional[AnyHttpUrl] = Field(alias='ref')
    # ? _type: Optional[str] = Field(alias='type')

    def __init__(self, *args, **kwargs):
        super().__init__(**RallyType(*args, **kwargs))
        object.__setattr__(self, 'caretaker', CareTaker(self))
        # ? Initial snapshot & performance issues for masive instantiation?
        # self.caretaker.take_snapshot()

    class Config:
        arbitrary_types_allowed = True
        anystr_strip_whitespace = True
        underscore_attrs_are_private = False
        extra = "allow"
        validate_assignment = True

    def get(self, key, restval=None):
        return self.dict().get(key, restval)

    def __setitem__(self, key, myvalue):
        """ field.subfield = x should be the same that field['subfield'] """
        self.__setattr__(key, myvalue)

    def __getattr__(self, item):
        logger.warning(f"Returning None (avoiding exception) for inexistent att: {item}")
        return None

    def items(self):
        return self._iter()

    def dict(self, *, include: Union['AbstractSetIntStr', 'MappingIntStrAny'] = None,
             exclude: Union['AbstractSetIntStr', 'MappingIntStrAny'] = None, by_alias: bool = False,
             skip_defaults: bool = None, exclude_unset: bool = True, exclude_defaults: bool = False,
             exclude_none: bool = True) -> 'DictStrAny':
        return super().dict(include=include, exclude=exclude, by_alias=by_alias, skip_defaults=skip_defaults,
                            exclude_unset=exclude_unset, exclude_defaults=exclude_defaults, exclude_none=exclude_none)

    def dict_for_create(self) -> dict:
        exclude = set(filter(lambda k: re.match(r"^(?:_.*)", k), self.dict().keys()))
        return self.dict(exclude=exclude)

    def copy_for_create(self) -> 'Model':
        exclude = set(filter(lambda k: re.match(r"^(?:_.*)", k), self.dict().keys()))
        return super().copy(exclude=exclude, include=None, update=None, deep=False)

    def dict_for_udpate(self, ) -> dict:
        exclude = set(filter(lambda k: re.match(r"^(?!_ref$|_type$)(?:_.*)", k), self.keys()))
        return self.dict(exclude=exclude)

    def copy_for_update(self, body_keys: set = None) -> 'Model':
        exclude = None
        include = None
        if body_keys:
            body_keys.update({"_ref", "_type"})
            include = body_keys
        else:
            # Excludes all _* keys except _ref and _type
            exclude = set(filter(lambda k: re.match(r"^(?!_ref$|_type$)(?:_.*)", k), self.keys()))
        return super().copy(exclude=exclude, include=include, update=None, deep=False)

    def dict_no_customs(self) -> dict:
        exclude = set(filter(lambda k: re.match(r"^(?:c_\w*)", k), self.keys()))
        return self.dict(exclude=exclude)

    def keys(self) -> KeysView[str]:
        return self.dict().keys()

    def save(self) -> RallyPydanticMemento:
        return RallyPydanticMemento(self.dict())


class RallyEntry(RallyType):
    def set_method(self, method: str):
        self["Entry"] = {"Method": method}

    def set_element(self, rallytype: RallyType, method: str, keys: List[str]):
        ref = rallytype.get("_ref", "")
        path = ref
        if method == "PUT" and not ref:
            path = f"/{rallytype['_type']}/create"
        elif (method == "POST" or method == "DELETE") and ref:
            if match := re.match(r".*/v2.0(.+)$", str(ref)):
                path = match.group(1)
        else:
            raise ValueError(f"Incompatible batch method: '{method}' with _ref content: {ref}")

        if path:
            self.get("Entry")["Path"] = path
        truncate_rallytype = {key: rallytype[key] for key in keys}
        if keys:
            body = {str(rallytype["_type"]): truncate_rallytype}
            self.get("Entry")["Body"] = body


class CareTaker:
    def __init__(self, model: RallyPydanticBase):
        self._model = model
        self._mementos: List[Memento] = []

    @staticmethod
    def __serialize_dict(d: dict) -> dict:
        s_dict = {}
        for k, v in d.items():
            sv: str = ""
            if isinstance(v, str):
                sv = v
            else:
                sv = json.dumps(v, sort_keys=True, default=str)
            s_dict[k] = sv
        return s_dict

    def take_snapshot(self) -> 'CareTaker':
        self._mementos.append(self._model.save())
        return self

    def get_diff_keys(self) -> List[str]:
        """Diff last snapshot and actual state"""
        s_last_snapshot_state: dict = self.__serialize_dict(self._mementos[-1].get_state())
        s_actual: dict = self.__serialize_dict(self._model.save().get_state())
        s1 = set(s_last_snapshot_state.items())
        s2 = set(s_actual.items())
        diff_keys: List[str] = [k for k, _ in s2 - s1]
        return diff_keys
