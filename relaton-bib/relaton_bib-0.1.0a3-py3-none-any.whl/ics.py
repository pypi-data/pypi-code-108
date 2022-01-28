from dataclasses import dataclass

import xml.etree.ElementTree as ET


@dataclass
class ICS:
    code: str
    text: str

    def to_xml(self, parent):
        name = "ics"
        node = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)
        ET.SubElement(node, "code").text = self.code
        ET.SubElement(node, "text").text = self.text
        return node

    def to_asciibib(self, prefix="", count=1):
        suffix = "ics"
        pref = f"{prefix}.{suffix}" if prefix else suffix
        out = [f"{pref}::"] if count > 1 else []
        out.append(f"{pref}.code:: {self.code}")
        out.append(f"{pref}.text:: {self.text}")
        return "\n".join(out)
