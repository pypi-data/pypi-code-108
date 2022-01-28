import xml.etree.ElementTree as ET

from dataclasses import dataclass, InitVar
from typing import List

from .formatted_string import FormattedString
from .relaton_bib import delegate


@dataclass(frozen=True)
class BiblioNote(FormattedString):
    type: str = None
    format: str = None

    def to_xml(self, parent=None):
        name = "note"
        node = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)
        super().to_xml(node)
        if self.type:
            node.attrib["type"] = self.type
        return node

    def to_asciibib(self, prefix="", count=1):
        pref = f"{prefix}." if prefix else prefix
        has_attrs = self.type
        out = [f"{pref}biblionote::"] if count > 1 and has_attrs else []
        if self.type:
            out.append(f"{pref}biblionote.type:: {self.type}")
        out.append(super().to_asciibib(f"{pref}biblionote", 1, has_attrs))
        return "\n".join(out)


@dataclass
@delegate("array", "append", "__getitem__", "__len__", "__iter__",
          "__reversed__", "__contains__")
class BiblioNoteCollection:
    array: List[BiblioNote]

    @property
    def first(self):
        return self.array[0] if len(self.array) > 0 else None

    @property
    def last(self):
        return self.array[-1] if len(self.array) > 0 else None

    @property
    def empty(self):
        return len(self.array) == 0

    def any(self):
        # https://stackoverflow.com/a/2323165/902217
        return any(x for x in self.array)

    def to_xml(self, parent, opts={}):
        lang = opts.get("lang")
        bnc = list(filter(lambda bn: lang in bn.language, self.array))
        if not bnc:
            bnc = self.array
        [bn.to_xml(parent) for bn in bnc]
        return parent

    # TODO missing to_asciibib?
    # def to_asciibib(self, prefix="", count=1):
    #   return "\n".join(map(lambda bn: bn.to_asciibib(prefix, count), self.array))
