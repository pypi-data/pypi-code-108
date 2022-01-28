from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

import logging
import re
import xml.etree.ElementTree as ET


class DocumentIdType(str, Enum):
    CN_STD = "Chinese Standard"
    ISO = "ISO"
    IEC = "IEC"
    URN = "URN"


@dataclass
class DocumentIdentifier:
    id: str
    type: str = None
    scope: str = None

    def remove_part(self):
        if self.type == DocumentIdType.CN_STD:
            self.id = re.sub(r"\.\d+", "", self.id)
        elif self.type in (DocumentIdType.ISO, DocumentIdType.IEC):
            self.id = re.sub(r"-[^:]+", "", self.id)
        elif self.type == DocumentIdType.URN:
            self._remove_urn_part()
        else:
            # sanity check
            logging.warning(f"[relaton-bib] unknown doc type: {self.type}")

    def remove_date(self):
        if self.type == DocumentIdType.CN_STD:
            self.id = re.sub(r"-[12]\d\d\d", "", self.id)
        elif self.type in (DocumentIdType.ISO, DocumentIdType.IEC):
            self.id = re.sub(r":[12]\d\d\d", "", self.id)
        elif self.type == DocumentIdType.URN:
            self.id = re.sub(
                r"^(urn:iec:std:[^:]+:[^:]+:)[^:]*", r"\1", self.id)

        # sanity check
        logging.warning(f"[relaton-bib] unknown doc type: {self.type}")

    def all_parts(self):
        if self.type == DocumentIdType.URN:
            return re.sub(r"^(urn:iec:std(?::[^:]*){4}).*", r"\1:ser", self.id)
        else:
            self.id += " (all parts)"

    def to_xml(self, parent, opts={}):
        lang = opts.get("lang")
        lid_re = fr"(?<=:)(?:\w\w,)*?({lang})(?:,\w\w)*"
        lid = re.sub(lid_re, r"\1", self.id) \
            if self.type == DocumentIdType.URN and lang else self.id

        result = ET.SubElement(parent, "docidentifier")
        result.text = lid
        if self.type:
            result.attrib["type"] = self.type
        if self.scope:
            result.attrib["scope"] = self.scope

        return result

    def to_asciibib(self, prefix="", count=1) -> str:
        pref = f"{prefix}." if prefix else prefix

        if not self.type and not self.scope:
            return f"{pref}docid:: {self.id}"

        out = [f"{pref}docid::"] if count > 1 else []
        if self.type:
            out.append(f"{pref}docid.type:: {self.type}")
        if self.scope:
            out.append(f"{pref}docid.scope:: {self.scope}")
        out.append(f"{pref}docid.id:: {self.id}")

        return "\n".join(out)

    def _remove_urn_part(self):
        self.id = re.sub(
            r"^(urn:iso:std:[^:]+"  # ISO prefix and originator
            r"  (?::(?:data|guide|isp|iwa|pas|r|tr|ts|tta))"  # type
            r"  ?:\d+)"  # docnumber
            r"(?::-[^:]+)?"  # partnumber
            r"(?::(draft|cancelled|stage-[^:]+))?"  # status
            r"(?::ed-\d+)?(?::v[^:]+)?"  # edition and version
            r"(?::\w{2}(?:,\w{2})*)?",  # langauge
            r"\1",
            self.id)
        self.id = re.sub(
            r"^(urn:iec:std:[^:]+"  # IEC prefix and originator
            r"  :\d+)"  # docnumber
            r"(?:-[^:]+)?",  # partnumber
            r"\1",
            self.id)
