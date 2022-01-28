from dataclasses import dataclass
from urllib.parse import urlparse

import xml.etree.ElementTree as ET


@dataclass()
class TypedUri:
    content: str
    type: str = None

    def __post_init__(self):
        if not self._valid_uri:
            raise ValueError(f"Invalid content: {self.content}")

    # to_hash -> dataclasses.asdict

    def to_xml(self, parent=None, opts={}):
        name = "uri"
        node = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)
        node.text = self.content

        if self.type:
            node.attrib["type"] = self.type

        return node

    def to_asciibib(self, prefix="", count=1):
        pref = f"{prefix}.link" if prefix else "link"
        out = [f"{pref}::"] if count > 1 else []
        if self.type:
            out.append(f"{pref}.type:: {self.type}")
        out.append(f"{pref}.content:: {self.content}")
        return "\n".join(out)

    @property
    def _valid_uri(self):
        if self.content is None:
            return True
        try:
            result = urlparse(self.content)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
