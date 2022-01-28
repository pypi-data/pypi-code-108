from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

import xml.etree.ElementTree as ET

from .organization import Organization
from .localized_string import LocalizedString
from .formatted_string import FormattedString
from .relaton_bib import lang_filter


@dataclass
class Affiliation:
    organization: Organization
    name: LocalizedString = None
    description: List[FormattedString] = field(default_factory=list)

    def to_xml(self, parent, opts={}):
        name = "affiliation"
        result = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)
        if self.name:
            self.name.to_xml(ET.SubElement(result, "name"))

        for d in lang_filter(self.description, opts):
            d.to_xml(ET.SubElement(result, "description"))

        self.organization.to_xml(result, opts)

        return result

    def to_asciibib(self, prefix="", count=1):
        pref = f"{prefix}." if prefix else prefix
        out = f"#{pref}affiliation::" if count > 1 else []
        if self.name:
            out.append(self.name.to_asciibib(f"{pref}affiliation.name"))
        for d in self.description:
            out.append(d.to_asciibib(f"{pref}affiliation.description",
                                     len(self.description)))
        out.append(self.organization.to_asciibib(f"{pref}affiliation.*"))
        return "\n".join(out)
