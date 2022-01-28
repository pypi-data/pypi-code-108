from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Union

import logging
import xml.etree.ElementTree as ET

from .formatted_string import FormattedString
from .relaton_bib import lang_filter, to_ds_instance
from .person import Person
from .organization import Organization


class ContributorRoleType(str, Enum):
    AUTHOR = "author"
    PERFORMER = "performer"
    PUBLISHER = "publisher"
    EDITOR = "editor"
    ADAPTER = "adapter"
    TRANSLATOR = "translator"
    DISTRIBUTOR = "distributor"
    INSTITUTION = "institution"
    ORGANIZATION = "organization"
    SCHOOL = "school"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


@dataclass
class ContributorRole:
    type: str
    description: list[FormattedString] = field(default_factory=list)

    def __post_init__(self):
        if not (ContributorRoleType.has_value(self.type)):
            logging.warning(
                f"[relaton-bib] Contributor's type {self.type} is invalid")

        def str_to_formatted(s):
            return FormattedString(content=s, format=None) if s is str else s

        self.description = list(map(str_to_formatted, self.description))

    def to_xml(self, parent, opts={}):
        name = "role"
        result = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)
        result.attrib["type"] = self.type

        for d in lang_filter(self.description, opts):
            d.to_xml(ET.SubElement(result, "description"))

        return result

    def to_asciibib(self, prefix="", count=1):
        pref = f"{prefix}." if prefix else prefix
        out = [f"{prefix}::"] if count > 1 else []
        for desc in self.description:
            out.append(desc.to_asciibib(f"{pref}role.description",
                                        len(self.description)))
        if self.type:
            out.append(f"{pref}role.type:: {self.type}")
        return "\n".join(out)


@dataclass
class ContributionInfo:
    entity: Union[Person, Organization]
    role: List[ContributorRole] = field(default_factory=list)

    def __post_init__(self):
        if self.role:
            self.role = list(map(to_ds_instance(ContributorRole), self.role))
        else:
            role_type = ContributorRoleType.AUTHOR \
                if isinstance(self.entity, Person) \
                else ContributorRoleType.PUBLISHER
            self.role.append(ContributorRole(type=role_type.value))

    def to_xml(self, parent, opts={}):
        return self.entity.to_xml(parent, opts)

    def to_asciibib(self, prefix="", count=1):
        # V ported from original code but looks strange
        pref = (prefix.split(".") + [None])[0]
        out = [f"{pref}::"] if count > 1 else []
        out.append(self.entity.to_asciibib(prefix))
        for r in self.role:
            out.append(r.to_asciibib(pref, len(self.role)))
        return "\n".join(out)
