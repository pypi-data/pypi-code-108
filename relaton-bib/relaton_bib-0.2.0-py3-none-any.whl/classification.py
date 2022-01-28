from dataclasses import dataclass
from typing import Optional

import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class Classification:
    value: str
    type: str = None

    def to_xml(self, parent):
        name = "classification"
        node = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)
        node.text = self.value

        if self.type:
            node.attrib["type"] = self.type

        return node

    def to_asciibib(self, prefix="", count=1):
        pref = f"{prefix}.classification" if prefix else "classification"
        out = [f"{pref}::"] if count > 1 else []
        if self.type:
            out.append(f"{pref}.type:: {self.type}")
        out.append(f"{pref}.value:: {self.value}")
        return "\n".join(out)
