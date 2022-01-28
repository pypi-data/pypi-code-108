from __future__ import annotations
from dataclasses import dataclass
from typing import List

import datetime
import re
import xml.etree.ElementTree as ET

from .contribution_info import ContributionInfo
from .relaton_bib import to_ds_instance


@dataclass
class CopyrightAssociation:
    from_: datetime.date
    owner: List[ContributionInfo]

    to: datetime.date = None
    scope: str = None

    def __post_init__(self):
        if not self.owner:
            raise ValueError("at least one owner should exist.")

        self.owner = list(map(to_ds_instance(ContributionInfo), self.owner))

        if isinstance(self.from_, str) and re.match(r"\d{4}", self.from_):
            self.from_ = datetime.datetime.strptime(self.from_, "%Y")

        if isinstance(self.to, str) and self.to:
            self.to = datetime.datetime.strptime(self.to, "%Y")

    def _date_reset(self, d):
        return d.replace(month=1, day=1)

    def to_xml(self, parent, opts={}):
        name = "copyright"
        result = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)
        ET.SubElement(result, "from").text = str(self.from_.year) \
            if self.from_ else "unknown"
        if self.to:
            ET.SubElement(result, "to").text = str(self.to.year)
        for o in self.owner:
            o.to_xml(ET.SubElement(result, "owner"), opts)
        if self.scope:
            ET.SubElement(result, "scope").text = self.scope

        return result

    def to_asciibib(self, prefix="", count=1):
        pref = f"{prefix}.copyright" if prefix else "copyright"
        out = [f"{pref}::"] if count > 1 else []
        for ow in self.owner:
            out.append(ow.to_asciibib(f"{pref}.owner", len(self.owner)))
        if self.from_:
            out.append(f"{pref}.from:: {self.from_.year}")
        if self.to:
            out.append(f"{pref}.to:: {self.to.year}")
        if self.scope:
            out.append(f"{pref}.scope:: {self.scope}")
        return "\n".join(out)
