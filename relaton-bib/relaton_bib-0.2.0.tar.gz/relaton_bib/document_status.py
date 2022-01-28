from __future__ import annotations
from dataclasses import dataclass

import xml.etree.ElementTree as ET

from .relaton_bib import to_ds_instance


@dataclass
class DocumentStatus:

    @dataclass
    class Stage:
        value: str
        abbreviation: str = None

        def to_xml(self, parent):
            if self.abbreviation:
                parent.attrib["abbreviation"] = self.abbreviation
            parent.text = self.value
            return parent

        # NOTE missing to_asciibib in original

    stage: Stage
    substage: Stage = None
    iteration: str = None

    def __post_init__(self):
        self.stage = to_ds_instance(DocumentStatus.Stage)(self.stage)
        self.substage = to_ds_instance(DocumentStatus.Stage)(self.substage)

    def to_xml(self, parent):
        name = "status"
        result = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)
        self.stage.to_xml(ET.SubElement(result, "stage"))
        if self.substage:
            self.substage.to_xml(ET.SubElement(result, "substage"))
        if self.iteration:
            ET.SubElement(result, "iteration").text = self.iteration

        return result

    def to_asciibib(self, prefix=""):
        pref = f"{prefix}." if prefix else prefix
        out = [f"{pref}docstatus.stage:: {self.stage.value}"]
        if self.substage:
            out.append(f"{pref}docstatus.substage:: {self.substage.value}")
        if self.iteration:
            out.append(f"{pref}docstatus.iteration:: {self.iteration}")
        return "\n".join(out)
