from dataclasses import dataclass
from enum import Enum

import logging
import xml.etree.ElementTree as ET


class ContactType(str, Enum):
    PHONE = "phone"
    EMAIL = "email"
    URI = "uri"
    ADDRESS = "address"

    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_


@dataclass
class Contact:
    type: str
    value: str

    def __post_init__(self):
        if not ContactType.has_value(self.type):
            logging.warning(
                f"[relaton-bib] invalid contact type: {self.type}")

    def to_xml(self, parent):
        result = ET.Element(self.type) if parent is None \
            else ET.SubElement(parent, self.type)
        result.text = self.value
        return result

    def to_asciibib(self, prefix="", count=1):
        pref = f"{prefix}." if prefix else prefix
        out = [f"{pref}contact::"] if count > 1 else []
        out.append(f"{pref}contact.type:: {self.type}")
        out.append(f"{pref}contact.value:: {self.value}")
        return "\n".join(out)