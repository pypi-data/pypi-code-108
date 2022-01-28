from __future__ import annotations
from dataclasses import dataclass
from typing import List

from .document_relation import DocumentRelation
from .relaton_bib import delegate


@dataclass
@delegate("array", "append", "__getitem__", "__len__", "__iter__",
          "__reversed__", "__contains__")
class DocRelationCollection:
    array: List[DocumentRelation]

    def __post_init__(self):
        self.array = list(map(
            lambda r: DocumentRelation(**r) if isinstance(r, dict) else r,
            self.array))

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
        # NOTE original gem missing to_xml
        for r in self.array:
            r.to_xml(parent, opts)
        return parent

    def replaces(self):
        return DocRelationCollection(filter(
            lambda r: r.type == DocumentRelation.Type.replace, self.array))

    def to_asciibib(self, prefix=""):
        pref = f"{prefix}.relation" if prefix else "relation"
        out = []
        for r in self.array:
            if len(self) > 1:
                out.append(f"{pref}::")
            out.append(r.to_asciibib(pref))
        return "\n".join(out)
