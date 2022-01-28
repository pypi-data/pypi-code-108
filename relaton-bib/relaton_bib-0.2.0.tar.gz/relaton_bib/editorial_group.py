from __future__ import annotations
from dataclasses import dataclass
from typing import List

import xml.etree.ElementTree as ET

from .technical_committee import TechnicalCommittee


@dataclass
class EditorialGroup:
    technical_committee: List[TechnicalCommittee]

    def to_xml(self, parent):
        name = "editorialgroup"
        result = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)
        for tc in self.technical_committee:
            tc.to_xml(result)
        return result

    def to_asciibib(self, prefix=""):
        pref = f"{prefix}.editorialgroup" if prefix else "editorialgroup"
        return "\n".join([tc.to_asciibib(pref, len(self.technical_committee))
                          for tc in self.technical_committee])

    @property
    def presence(self):
        return True
