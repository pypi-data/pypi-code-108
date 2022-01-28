from dataclasses import dataclass

import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class Medium:
    form: str = None
    size: str = None
    scale: str = None

    def to_xml(self, parent):
        name = "medium"
        node = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)
        if self.form:
            ET.SubElement(node, "form").text = self.form
        if self.size:
            ET.SubElement(node, "size").text = self.size
        if self.scale:
            ET.SubElement(node, "scale").text = self.scale
        return node

    def to_asciibib(self, prefix=""):
        pref = f"{prefix}.medium." if prefix else "medium."
        out = []
        if self.form:
            out.append(f"{pref}form:: {self.form}")
        if self.size:
            out.append(f"{pref}size:: {self.size}")
        if self.scale:
            out.append(f"{pref}scale:: {self.scale}")
        return "\n".join(out)
