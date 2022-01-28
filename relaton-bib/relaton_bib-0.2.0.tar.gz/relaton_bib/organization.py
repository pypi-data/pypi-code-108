from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List
import re
import logging
import xml.etree.ElementTree as ET

from .localized_string import LocalizedString
from .relaton_bib import lang_filter, to_ds_instance
from .contributor import Contributor


class OrgIdentifierType(Enum):
    ORCID = "orcid"
    URI = "uri"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


@dataclass(frozen=True)
class OrgIdentifier:
    type: str
    value: str

    def __post_init__(self):
        if not (OrgIdentifierType.has_value(self.type)):
            logging.warning(
                f"[relaton-bib] invalid locality type: {self.type}")

    def to_xml(self, parent):
        name = "identifier"
        node = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)
        node.text = self.value
        node.attrib["type"] = self.type
        return node

    def to_asciibib(self, prefix="", count=1):
        pref = f"{prefix}." if prefix else prefix
        out = [f"{pref}identifier::"] if count > 1 else []
        out.append(f"{pref}identifier.type:: {self.type}")
        out.append(f"{pref}identifier.value:: {self.value}")
        return "\n".join(out)


@dataclass
class Organization(Contributor):
    name: List[LocalizedString] = field(default_factory=list)
    abbreviation: LocalizedString = None
    subdivision: List[LocalizedString] = field(default_factory=list)
    identifier: List[OrgIdentifier] = field(default_factory=list)

    def __post_init__(self):
        if not self.name:
            # WORKAROUND for https://bugs.python.org/issue36077
            raise ValueError("missing name")

        if isinstance(self.name, str):
            self.name = [LocalizedString(self.name)]
        elif isinstance(self.name, List):
            self.name = list(map(to_ds_instance(LocalizedString), self.name))

        if isinstance(self.abbreviation, str):
            self.abbreviation = LocalizedString(self.abbreviation)

        if isinstance(self.subdivision, List):
            self.subdivision = list(map(to_ds_instance(LocalizedString),
                                        self.subdivision))

    def to_xml(self, parent, opts={}):
        name = "organization"
        result = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)
        for n in lang_filter(self.name, opts):
            n.to_xml(ET.SubElement(result, "name"))
        for s in lang_filter(self.subdivision, opts):
            s.to_xml(ET.SubElement(result, "subdivision"))
        if self.abbreviation:
            self.abbreviation.to_xml(ET.SubElement(result, "abbreviation"))
        if self.uri:
            ET.SubElement(result, "uri").text = self.uri
        for idntfr in self.identifier:
            idntfr.to_xml(result)
        super().to_xml(result)
        return result

    def to_asciibib(self, prefix="", count=1):
        prefix = re.sub(r"\*$", "organization", prefix)
        out = [f"{prefix}::"] if count > 1 else []
        pref = f"{prefix}." if prefix else prefix
        for n in self.name:
            out.append(n.to_asciibib(f"{pref}name", len(self.name)))
        if self.abbreviation:
            out.append(self.abbreviation.to_asciibib(f"{pref}abbreviation"))
        for sd in self.subdivision:
            if len(self.subdivision) > 1:
                # NOTE originally it was without \n
                out.append(f"{pref}subdivision::")
            out.append(sd.to_asciibib(f"{pref}subdivision"))
        for idtfr in self.identifier:
            out.append(idtfr.to_asciibib(prefix, len(self.identifier)))
        parent = super().to_asciibib(prefix)
        if parent:
            out.append(parent)
        return "\n".join(out)

    def bib_name(self) -> str:
        return str(self.name[0]) if len(self.name) > 0 else None
