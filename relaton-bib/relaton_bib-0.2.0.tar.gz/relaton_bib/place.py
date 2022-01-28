from dataclasses import dataclass

import xml.etree.ElementTree as ET


@dataclass
class Place:
    name: str
    uri: str = None
    region: str = None

    def to_xml(self, parent):
        name = "place"
        node = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)
        node.text = self.name
        if self.uri:
            node.attrib["uri"] = self.uri
        if self.region:
            node.attrib["region"] = self.region
        return node

    def to_asciibib(self, prefix="", count=1):
        pref = f"{prefix}.place" if prefix else "place"
        out = [f"{pref}::"] if count > 1 else []
        out.append(f"{pref}.name:: {self.name}")
        if self.uri:
            out.append(f"{pref}.uri:: {self.uri}")
        if self.region:
            out.append(f"{pref}.region:: {self.region}")
        return "\n".join(out)
