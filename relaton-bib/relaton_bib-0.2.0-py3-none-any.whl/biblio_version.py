import xml.etree.ElementTree as ET

from dataclasses import dataclass, field
from typing import List


@dataclass
class BibliographicItemVersion:
    revision_date: str = None
    draft: List[str] = field(default_factory=list)

    def to_xml(self, parent=None):
        name = "version"
        node = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)
        if self.revision_date:
            ET.SubElement(node, "revision-date").text = self.revision_date
        for d in self.draft:
            ET.SubElement(node, "draft").text = d
        return node

    def to_asciibib(self, prefix=""):
        pref = f"{prefix}." if prefix else prefix
        out = []
        if self.revision_date:
            out.append(f"{pref}version.revision_date:: {self.revision_date}")
        for d in self.draft:
            out.append(f"{pref}version.draft:: {d}")
        return "\n".join(out)
