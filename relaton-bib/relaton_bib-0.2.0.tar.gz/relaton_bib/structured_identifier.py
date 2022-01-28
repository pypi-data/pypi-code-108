from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

import re
import xml.etree.ElementTree as ET

from .relaton_bib import delegate
from .document_identifier import DocumentIdType


@dataclass
@delegate("collection", "__getitem__", "__len__", "__iter__",
          "__reversed__", "__contains__")
class StructuredIdentifierCollection:
    collection: List[StructuredIdentifier]

    def to_xml(self, parent):
        for si in self.collection:
            si.to_xml(parent)

    def to_asciibib(self, prefix=""):
        pref = f"{prefix}." if prefix else prefix
        pref += "structured_identifier"
        out = []
        for si in self.collection:
            if len(self.collection) > 1:
                out.append(f"{pref}::")
            out.append(si.to_asciibib(pref))
        return "\n".join(out)

    def remove_date(self):
        for si in self.collection:
            si.remove_date()

    def remove_part(self):
        for si in self.collection:
            si.remove_part()

    def all_parts(self):
        for si in self.collection:
            si.all_parts()


@dataclass
class StructuredIdentifier:
    docnumber: str

    agency: List[str] = field(default_factory=list)

    type: str = None
    class_: str = None
    partnumber: str = None
    edition: str = None
    version: str = None
    supplementtype: str = None
    supplementnumber: str = None
    language: str = None
    year: str = None

    def to_xml(self, parent):
        name = "structuredidentifier"
        result = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)

        for a in self.agency:
            ET.SubElement(result, "agency").text = a

        if self.class_:
            ET.SubElement(result, "class").text = self.class_

        ET.SubElement(result, "docnumber").text = self.docnumber

        for opt_attr in ["partnumber", "edition", "version", "supplementtype",
                         "supplementnumber", "language", "year"]:
            value = getattr(self, opt_attr)
            if value:
                ET.SubElement(result, opt_attr).text = value
        if self.type:
            result.attrib["type"] = self.type

        return result

    def to_asciibib(self, prefix="", count=1):
        pref = f"{prefix}." if prefix else prefix
        out = [f"{pref}docnumber:: {self.docnumber}"]
        for a in self.agency:
            out.append(f"{pref}agency:: {a}")

        for opt_attr in ["type", "class", "partnumber", "edition", "version",
                         "supplementtype", "supplementnumber", "language",
                         "year"]:
            attr = opt_attr if opt_attr != "class" else "class_"
            value = getattr(self, attr)
            if value:
                out.append(f"{pref}{opt_attr}:: {value}")

        return "\n".join(out)

    def remove_date(self):
        if self.type == DocumentIdType.CN_STD:
            self.docnumber = re.sub(r"-[12]\d\d\d", "", self.docnumber)
        else:
            self.docnumber = re.sub(r":[12]\d\d\d", "", self.docnumber)
        self.year = None

    # in docid manipulations, assume ISO as the default: id-part:year
    def remove_part(self):
        self.partnumber = None
        self.docnumber = re.sub(r"-\d+", "", self.docnumber)

    def all_parts(self):
        self.docnumber += " (all parts)"
