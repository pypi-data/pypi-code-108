from __future__ import annotations

import dataclasses
import datetime
import os
from typing import TYPE_CHECKING, Any, Generic, Iterable, TypeVar, Union
from urllib.parse import urlparse

from typing_extensions import TypeAlias
from werkzeug.utils import import_string

if TYPE_CHECKING:
    from ..types import *

DataClass: TypeAlias = Any
T = TypeVar("T")


def _id(v: Any):
    return v


def _get(el) -> Any:
    return import_string(".".join([__package__, el]))


@dataclasses.dataclass
class Atomic:
    value: Any

    def as_jml(self):
        ns = self.__module__.split(".")[-1]
        data = JmlRecord(f"{ns}:{self.__class__.__name__}")
        v = getattr(self, "format", _id)(self.value)
        data.append(v)
        return data


@dataclasses.dataclass
class Codelist(Generic[T]):
    value: str

    def as_jml(self):
        from ..utils import CodeListValue, codelist_options

        ns = self.__module__.split(".")[-1]
        name = type(self).__name__
        data = JmlRecord(f"{ns}:{name}")

        options = codelist_options(name)
        if options:

            for option in options:
                if option.name == self.value:
                    break
            else:
                raise ValueError(
                    f"Codelist [name] does not contain value {self.value}:"
                    f" {[o.name for o in options]}"
                )
        else:
            option = CodeListValue(self.value, "")

        data.attrs.update(
            {
                "codeList": option.location,
                "codeListValue": option.name,
            }
        )
        data.append(option.name)

        return data


class JmlRecord(list):
    def __init__(self, name: str, initial_attrs: Iterable[Any] = ()):
        attrs = dict(initial_attrs)
        super().__init__([name, attrs])

    @property
    def name(self):
        return self[0]

    @property
    def attrs(self):
        return self[1]

    @property
    def children(self):
        return self[2:]

    def refine_attributes(self):
        if not self.attrs:
            self.pop(1)


def make(el, *args, **kwargs):
    return _get(el)(*args, **kwargs)


def _default_as_jml(el: DataClass, ns: str):
    data = JmlRecord(f"{ns}:{el.__class__.__name__}")

    for field in dataclasses.fields(el):
        k = field.name
        v = getattr(el, k)

        optional = is_optional(field)
        # not sure if it's safe to simplify it ignoring any falsy value
        if optional and (v is None or v == []):
            continue

        if not isinstance(v, list) or v == []:
            v = [v]

        for element in v:
            child = JmlRecord(f"{ns}:{k}")
            data.append(child)

            if not dataclasses.is_dataclass(element):
                if is_cs(field):
                    element = cs(element)
                elif is_codelist(field):
                    element = codelist(field, element)

            content = (
                jml(element) if dataclasses.is_dataclass(element) else element
            )
            if content != []:
                child.append(content)
            child.refine_attributes()

    data.refine_attributes()
    return data


def jml(el: DataClass):
    ns = el.__module__.split(".")[-1]

    if hasattr(el, "as_jml"):
        data = el.as_jml()
    else:
        data = _default_as_jml(el, ns)
    data.refine_attributes

    return data


def is_codelist(field: dataclasses.Field) -> bool:
    return "Codelist[" in field.type


def is_cs(field: dataclasses.Field) -> bool:
    return "gco.CharacterString" in field.type


def is_optional(field: dataclasses.Field) -> bool:
    return "Optional[" in field.type


def codelist(field: dataclasses.Field, value: Any) -> dict[str, str]:
    t: str = field.type
    prefix = "Codelist["
    start = t.find(prefix) + len(prefix)
    end = t.find("]", start)
    dc = ":".join(t[start:end].split(".", 1))
    return make(dc, value)


def cs(v: Any):
    return make("gco:CharacterString", v)


def image(url: str) -> mcc.MD_BrowseGraphic:
    name, ext = os.path.splitext(os.path.basename(url))
    links = [link(url)]
    return make(
        "mcc:MD_BrowseGraphic", name, fileType=ext or None, linkage=links
    )


def link(url: str) -> cit.CI_OnlineResource:
    details = urlparse(url)
    return make("cit:CI_OnlineResource", url, details.scheme)


def date(dt: Union[str, datetime.date], type: str) -> cit.CI_Date:
    if isinstance(dt, str):
        dt = datetime.datetime.fromisoformat(dt)
    return make("cit:CI_Date", dt, type)


def responsibility(role, name, logo=None, **kwargs) -> cit.CI_Responsibility:
    p = make(f"cit:CI_Individual", name, **kwargs)
    if logo:
        p = make(f"cit:CI_Organisation", logo, p)

    return make("cit:CI_Responsibility", role, p)


def citation(title, **kwargs):
    return make("cit:CI_Citation", title, **kwargs)


def keyword(tag: str) -> mri.MD_Keywords:
    return make("mri:MD_Keywords", tag)


def locale(lang: str) -> lan.PT_Locale:
    return make("lan:PT_Locale", lang)
