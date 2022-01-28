from dataclasses import dataclass, field
from typing import List

import xml.etree.ElementTree as ET


@dataclass
class Address:
    city: str
    country: str
    street: List[str] = field(default_factory=list)
    state: str = None
    postcode: str = None

    def to_xml(self, parent):
        name = "address"
        result = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)
        for st in self.street:
            ET.SubElement(result, "street").text = st
        ET.SubElement(result, "city").text = self.city
        if self.state:
            ET.SubElement(result, "state").text = self.state
        ET.SubElement(result, "country").text = self.country
        if self.postcode:
            ET.SubElement(result, "postcode").text = self.postcode
        return result

    def to_asciibib(self, prefix="", count=1):
        pref = f"{prefix}.address" if prefix else "address"
        out = [f"{pref}::"] if count > 1 else []
        for st in self.street:
            out.append(f"{pref}.street:: {st}")
        out.append(f"{pref}.city:: {self.city}")
        if self.state:
            out.append(f"{pref}.state:: {self.state}")
        out.append(f"{pref}.country:: {self.country}")
        if self.postcode:
            out.append(f"{pref}.postcode:: {self.postcode}")
        return "\n".join(out)
