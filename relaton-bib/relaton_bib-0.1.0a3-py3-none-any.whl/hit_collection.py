from __future__ import annotations
from dataclasses import dataclass, field
from multiprocessing import Pool
from typing import List

import xml.etree.ElementTree as ET

from .relaton_bib import delegate


def hit_fetch(hit):
    return hit.fetch()


@dataclass
@delegate("array", "append", "__getitem__", "__len__", "__iter__",
          "__reversed__", "__contains__")
class HitCollection:
    text: str
    year: str = None
    fetched: bool = False
    array: List = field(default_factory=list)

    def fetch(self):
        workers = Pool(4)
        result = workers.map(hit_fetch, self.array)
        # TODO looks incomplete
        self.fetched = True
        return self

    # @param opts [Hash]
    # @option opts [Nokogiri::XML::Builder] :builder XML builder
    # @option opts [Boolean] :bibdata
    # @option opts [String, Symbol] :lang language
    # @return [String] XML
    def to_xml(self, parent=None, opts={}):
        name = "documents"
        result = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)

        for hit in self.array:
            hit.fetch()
            hit.to_xml(result, opts)

        return result
