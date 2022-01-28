from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict

from .hit_collection import HitCollection


@dataclass
class Hit:
    hit: List[Dict] = field(default_factory=list)
    hit_collection: HitCollection = None

    def fetch():
        raise NotImplementedError()

    # @param opts [Hash]
    # @option opts [Nokogiri::XML::Builder] :builder XML builder
    # @option opts [Boolean] :bibdata
    # @option opts [String, Symbol] :lang language
    # @return [String] XML
    def to_xml(self, parent, opts={}):
        self.fetch().to_xml(parent, opts)
