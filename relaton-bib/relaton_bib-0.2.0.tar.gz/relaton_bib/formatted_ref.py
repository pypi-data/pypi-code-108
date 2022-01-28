from dataclasses import dataclass

import xml.etree.ElementTree as ET

from .formatted_string import FormattedString


@dataclass(frozen=True)
class FormattedRef(FormattedString):
    def to_xml(self, parent):
        name = "formattedref"
        node = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)
        return super().to_xml(node)

    def to_asciibib(self, prefix=""):
        pref = f"{prefix}.formattedref" if prefix else "formattedref"
        return super().to_asciibib(pref)
