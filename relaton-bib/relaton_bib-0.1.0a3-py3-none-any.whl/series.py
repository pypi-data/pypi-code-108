from dataclasses import dataclass
from enum import Enum

import logging
import xml.etree.ElementTree as ET

from .formatted_ref import FormattedRef
from .localized_string import LocalizedString
from .typed_title_string import TypedTitleString


class SeriesType(str, Enum):
    MAIN = "main"
    ALT = "alt"
    JOURNAL = "journal"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


@dataclass(frozen=True)
class Series:
    type: str = None
    formattedref: FormattedRef = None
    title: TypedTitleString = None
    place: str = None
    organization: str = None
    abbreviation: LocalizedString = None
    from_: str = None
    to: str = None
    number: str = None
    partnumber: str = None

    def __post_init__(self):
        if not(type(self.title) is TypedTitleString or self.formattedref):
            raise ValueError("arg `title` or `formattedref` should present")

        if self.type and not SeriesType.has_value(self.type):
            logging.warning(
                f"[relaton-bib] Series type is invalid: {self.type}")

    # to_hash -> dataclasses.asdict

    def to_xml(self, parent, opts={}):
        name = "series"
        node = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)

        if self.formattedref:
            self.formattedref.to_xml(node)
        else:
            if self.title:
                self.title.to_xml(ET.SubElement(node, "title"))
            if self.place:
                ET.SubElement(node, "place").text = self.place
            if self.organization:
                ET.SubElement(node, "organization").text = self.organization
            if self.abbreviation:
                self.abbreviation.to_xml(ET.SubElement(node, "abbreviation"))
            if self.from_:
                ET.SubElement(node, "from").text = self.from_
            if self.to:
                ET.SubElement(node, "to").text = self.to
            if self.number:
                ET.SubElement(node, "number").text = self.number
            if self.partnumber:
                ET.SubElement(node, "partnumber").text = self.partnumber

        if self.type:
            node.attrib["type"] = self.type

        return node

    def to_asciibib(self, prefix="", count=1):
        pref = f"{prefix}.series" if prefix else "series"

        lines = [f"{pref}::"] if count > 1 else []
        if self.type:
            lines.append(f"{pref}.type:: {self.type}")
        if self.formattedref:
            lines.append(self.formattedref.to_asciibib(pref))
        if self.title:
            lines.append(self.title.to_asciibib(pref))
        if self.place:
            lines.append(f"{pref}.place:: {self.place}")
        if self.organization:
            lines.append(f"{pref}.organization:: {self.organization}")
        if self.abbreviation:
            lines.append(self.abbreviation.to_asciibib(f"{pref}.abbreviation"))
        if self.from_:
            lines.append(f"{pref}.from:: {self.from_}")
        if self.to:
            lines.append(f"{pref}.to:: {self.to}")
        if self.number:
            lines.append(f"{pref}.number:: {self.number}")
        if self.partnumber:
            lines.append(f"{pref}.partnumber:: {self.partnumber}")

        return "\n".join(lines)
