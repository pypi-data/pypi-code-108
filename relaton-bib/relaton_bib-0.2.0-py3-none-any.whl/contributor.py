from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Union

from .address import Address
from .contact import Contact


@dataclass
class Contributor:
    uri: str = None
    contact: List[Union[Address, Contact]] = field(default_factory=list)

    @property
    def url(self):
        return self.uri

    def to_xml(self, parent):
        for c in self.contact:
            c.to_xml(parent)
        return parent

    def to_asciibib(self, prefix=""):
        pref = f"{prefix}." if prefix else prefix
        out = []
        if self.uri:
            out.append(f"{pref}url:: {self.uri}")
        addr = [x for x in self.contact if isinstance(x, Address)]
        for a in addr:
            out.append(a.to_asciibib(prefix, len(addr)))
        cont = [x for x in self.contact if isinstance(x, Contact)]
        for c in cont:
            out.append(c.to_asciibib(prefix, len(cont)))
        return "\n".join(out)

    def bib_name(self) -> str:
        raise NotImplementedError()
