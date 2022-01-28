from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List

import re
import xml.etree.ElementTree as ET

from .relaton_bib import lang_filter, to_ds_instance
from .localized_string import LocalizedString
from .affiliation import Affiliation
from .contributor import Contributor


def localized_string():
    return to_ds_instance(LocalizedString)


@dataclass
class FullName:
    surname: LocalizedString = None
    completename: LocalizedString = None
    forename: List[LocalizedString] = field(default_factory=list)
    initial: List[LocalizedString] = field(default_factory=list)
    addition: List[LocalizedString] = field(default_factory=list)
    prefix: List[LocalizedString] = field(default_factory=list)

    def __post_init__(self):
        if not self.surname and not self.completename:
            raise ValueError("Should be given surname or completename")

        if isinstance(self.surname, str):
            self.surname = LocalizedString(self.surname)

        if isinstance(self.completename, str):
            self.completename = LocalizedString(self.completename)

        if isinstance(self.forename, str):
            self.forename = [LocalizedString(self.forename)]
        elif isinstance(self.forename, List):
            self.forename = list(map(localized_string(), self.forename))

        if isinstance(self.initial, str):
            self.initial = [LocalizedString(self.initial)]
        elif isinstance(self.initial, List):
            self.initial = list(map(localized_string(), self.initial))

        if isinstance(self.addition, str):
            self.addition = [LocalizedString(self.addition)]
        elif isinstance(self.addition, List):
            self.addition = list(map(localized_string(), self.addition))

        if isinstance(self.prefix, str):
            self.prefix = [LocalizedString(self.prefix)]
        elif isinstance(self.prefix, List):
            self.prefix = list(map(localized_string(), self.prefix))

    def to_xml(self, parent, opts={}):
        name = "name"
        result = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)

        if self.completename:
            self.completename.to_xml(ET.SubElement(result, "completename"))
        else:
            for p in lang_filter(self.prefix, opts):
                p.to_xml(ET.SubElement(result, "prefix"))
            for f in lang_filter(self.forename, opts):
                f.to_xml(ET.SubElement(result, "forename"))
            for i in lang_filter(self.initial, opts):
                i.to_xml(ET.SubElement(result, "initial"))
            self.surname.to_xml(ET.SubElement(result, "surname"))
            for a in lang_filter(self.addition, opts):
                a.to_xml(ET.SubElement(result, "addition"))

        return result

    def to_asciibib(self, prefix):
        prf = f"{prefix}.name." if prefix else "name."
        out = [fn.to_asciibib(f"{prf}forename", len(self.forename))
               for fn in self.forename]
        out += [i.to_asciibib(f"{prf}initial", len(self.initial))
                for i in self.initial]
        if self.surname:
            out.append(self.surname.to_asciibib(f"{prf}surname"))
        out += [ad.to_asciibib(f"{prf}addition", len(self.addition))
                for ad in self.addition]
        out += [pr.to_asciibib(f"{prf}prefix", len(self.prefix))
                for pr in self.prefix]
        if self.completename:
            out.append(self.completename.to_asciibib(f"{prf}completename"))
        return "\n".join(out)


class PersonIdentifierType(Enum):
    ISNI = "isni"
    URI = "uri"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


@dataclass
class PersonIdentifier:
    type: str
    value: str

    def __post_init__(self):
        if not PersonIdentifierType.has_value(self.type):
            raise ValueError('Invalid type. It should be "isni" or "uri".')

        if isinstance(self.type, PersonIdentifierType):
            self.type = self.type.value

    def to_xml(self, parent):
        name = "identifier"
        result = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)
        result.text = self.value
        result.attrib["type"] = self.type

    def to_asciibib(self, prefix="", count=1):
        pref = prefix + "." if prefix else prefix
        out = [f"{prefix}::"] if count > 1 else []
        out.append(f"{pref}type:: {self.type}")
        out.append(f"{pref}value:: {self.value}")
        return "\n".join(out)


@dataclass
class Person(Contributor):
    name: FullName = None
    affiliation: List[Affiliation] = field(default_factory=list)
    identifier: List[PersonIdentifier] = field(default_factory=list)

    def __post_init__(self):
        # WORKAROUND for https://bugs.python.org/issue36077
        if not self.name:
            raise ValueError("missing name")

    def to_xml(self, parent, opts={}):
        name = "person"
        result = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)
        self.name.to_xml(result, opts)
        for a in self.affiliation:
            a.to_xml(result, opts)
        for i in self.identifier:
            i.to_xml(result)
        for c in self.contact:
            c.to_xml(result)
        return result

    def to_asciibib(self, prefix="", count=1):
        pref = re.sub(r"\*$", "person", prefix)
        out = [f"{pref}::"] if count > 1 else []
        out.append(self.name.to_asciibib(pref))
        for a in self.affiliation:
            out.append(a.to_asciibib(pref, len(self.affiliation)))
        for i in self.identifier:
            out.append(i.to_asciibib(pref, len(self.identifier)))
        out.append(super().to_asciibib(pref))
        return "\n".join([l for l in out if l])

    def bib_name(self) -> str:
        return str(self.name.completename)