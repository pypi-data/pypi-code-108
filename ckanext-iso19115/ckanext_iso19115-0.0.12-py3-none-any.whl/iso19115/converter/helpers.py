from __future__ import annotations
import dataclasses

import datetime
import os
from typing import Any, Literal, Optional, Union, overload
from urllib.parse import urlparse
from werkzeug.utils import import_string


from ..types import *
from ..types.base import Codelist


def make(el: str, *args, **kwargs):
    return _get(el)(*args, **kwargs)


def _get(el) -> Any:
    return import_string(".".join(["ckanext.iso19115.types", el]))


def cs(v: Any) -> gco.CharacterString:
    return gco.CharacterString(v)


def image(url: str) -> mcc.MD_BrowseGraphic:
    name, ext = os.path.splitext(os.path.basename(url))
    links = [link(url)]
    return mcc.MD_BrowseGraphic(
        cs(name), fileType=cs(ext) if ext else None, linkage=links
    )


def link(url: str) -> cit.CI_OnlineResource:
    details = urlparse(url)
    return cit.CI_OnlineResource(cs(url), cs(details.scheme))


@overload
def date(dt: Any, force_datetime: Literal[True]) -> gco.DateTime:
    ...


@overload
def date(
    dt: Union[str, datetime.date], force_datetime: bool = False
) -> Union[gco.Date, gco.DateTime]:
    ...


def date(dt, force_datetime=False):
    if isinstance(dt, str):
        dt = datetime.datetime.fromisoformat(dt)
    assert isinstance(dt, datetime.date)

    if (
        isinstance(dt, datetime.datetime)
        and not force_datetime
        and (
            dt.hour,
            dt.minute,
            dt.second,
        )
        == (0, 0, 0)
    ):
        dt = dt.date()

    if isinstance(dt, datetime.datetime):
        v = gco.DateTime(dt)
    elif isinstance(dt, datetime.date):
        v = gco.Date(dt)
    return v


def codelist(field: dataclasses.Field, value: Any) -> Codelist:
    t: str = field.type
    prefix = "Codelist["
    start = t.find(prefix) + len(prefix)
    end = t.find("]", start)
    dc = ":".join(t[start:end].split(".", 1))
    return make(dc, value)


def individual(name: str, **kwargs) -> cit.CI_Individual:
    return cit.CI_Individual(cs(name), **kwargs)


def org(name: str, **kwargs) -> cit.CI_Organisation:
    return cit.CI_Organisation(cs(name), **kwargs)


def responsibility(
    role: str, party: cit.AbstractCI_Party
) -> cit.CI_Responsibility:
    return cit.CI_Responsibility(cit.CI_RoleCode(role), party=[party])


def citation(title: str, **kwargs):
    return cit.CI_Citation(cs(title), **kwargs)


def keyword(tag: str) -> mri.MD_Keywords:
    return mri.MD_Keywords([cs(tag)])


def locale(lang: str) -> lan.PT_Locale:
    return lan.PT_Locale(lan.LanguageCode(lang))


def id(id_: str, **kwargs) -> mcc.MD_Identifier:
    return mcc.MD_Identifier(code=cs(id_), **kwargs)


def contact(**kwargs) -> cit.CI_Contact:
    return cit.CI_Contact(**kwargs)


def phone(number: str, type_: Optional[str] = None) -> cit.CI_Telephone:
    return cit.CI_Telephone(
        cs(number), cit.CI_TelephoneTypeCode(type_) if type_ else None
    )


def address(
    deliveryPoint=None,
    city=None,
    administrativeArea=None,
    postalCode=None,
    country=None,
    email=None,
) -> cit.CI_Address:
    return cit.CI_Address(
        deliveryPoint, city, administrativeArea, postalCode, country, email
    )
