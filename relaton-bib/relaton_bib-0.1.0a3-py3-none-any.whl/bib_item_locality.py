import re
import logging
import xml.etree.ElementTree as ET

from dataclasses import dataclass
from enum import Enum
from typing import List

from .localized_string import LocalizedString


class BibItemLocalityType(str, Enum):
    SECTION = "section"
    CLAUSE = "clause"
    PART = "part"
    PARAGRAPH = "paragraph"
    CHAPTER = "chapter"
    PAGE = "page"
    WHOLE = "whole"
    TABLE = "table"
    ANNEX = "annex"
    FIGURE = "figure"
    NOTE = "note"
    LIST = "list"
    EXAMPLE = "example"
    VOLUME = "volume"
    ISSUE = "issue"
    TIME = "time"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


@dataclass(frozen=True)
class BibItemLocality:
    """Bibliographic item locality."""

    type: str
    reference_from: LocalizedString
    reference_to: LocalizedString = None

    def __post_init__(self):
        if not (BibItemLocalityType.has_value(self.type)
                or re.match(r"locality:[a-zA-Z0-9_]+", self.type)):
            logging.warning(
                f"[relaton-bib] invalid locality type: {self.type}")

        if isinstance(self.type, BibItemLocalityType):
            object.__setattr__(self, "type", self.type.value)

        if isinstance(self.reference_from, str):
            object.__setattr__(self, "reference_from",
                               LocalizedString(self.reference_from))

        if isinstance(self.reference_to, str):
            object.__setattr__(self, "reference_to",
                               LocalizedString(self.reference_to))

    def to_xml(self, parent):
        parent.attrib["type"] = self.type
        ET.SubElement(parent, "referenceFrom").text = str(self.reference_from)
        if self.reference_to:
            ET.SubElement(parent, "referenceTo").text = str(self.reference_to)
        return parent

    def to_asciibib(self, prefix="", count=1):
        pref = prefix + "." if prefix else prefix
        out = [f"{prefix}::"] if count > 1 else []
        out.append(f"{pref}type:: {self.type}")
        out.append(f"{pref}reference_from:: {self.reference_from}")
        if self.reference_to:
            out.append(f"{pref}reference_to:: {self.reference_to}")
        return "\n".join(out)


@dataclass(frozen=True)
class Locality(BibItemLocality):

    def to_xml(self, parent):
        node = ET.SubElement(parent, "locality")
        node.attrib["type"] = self.type
        ET.SubElement(node, "referenceFrom").text = str(self.reference_from)
        if self.reference_to:
            ET.SubElement(node, "referenceTo").text = str(self.reference_to)
        return node


@dataclass(frozen=True)
class LocalityStack:
    locality: List[Locality]

    def to_xml(self, parent):
        node = ET.SubElement(parent, "localityStack")
        for loc in self.locality:
            loc.to_xml(node)
        return node

    # TODO REVISIT and for other classes too
    # def to_hash
    #   { "locality_stack" => single_element_array(locality) }
    # end


@dataclass(frozen=True)
class SourceLocality(BibItemLocality):
    def to_xml(self, parent):
        node = ET.SubElement(parent, "sourceLocality")
        super().to_xml(node)
        return node


class SourceLocalityStack(LocalityStack):
    def to_xml(self, parent):
        node = ET.SubElement(parent, "sourceLocalityStack")
        for loc in self.locality:
            loc.to_xml(node)
        return node

#     # TODO REVISIT
#     def to_hash
#       { "source_locality_stack" => single_element_array(locality) }
#     end

