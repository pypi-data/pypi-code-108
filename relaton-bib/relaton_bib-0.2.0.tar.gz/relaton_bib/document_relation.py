from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Union

import logging
import xml.etree.ElementTree as ET

from .bibliographic_item import *
from .formatted_string import FormattedString
from .bib_item_locality import Locality, LocalityStack, SourceLocality, \
    SourceLocalityStack


@dataclass
class DocumentRelation:
    class Type(str, Enum):
        includes = "includes"
        includedIn = "includedIn"
        hasPart = "hasPart"
        partOf = "partOf"
        merges = "merges"
        mergedInto = "mergedInto"
        splits = "splits"
        splitInto = "splitInto"
        instance = "instance"
        hasInstance = "hasInstance"
        exemplarOf = "exemplarOf"
        hasExemplar = "hasExemplar"
        manifestationOf = "manifestationOf"
        hasManifestation = "hasManifestation"
        reproductionOf = "reproductionOf"
        hasReproduction = "hasReproduction"
        reprintOf = "reprintOf"
        hasReprint = "hasReprint"
        expressionOf = "expressionOf"
        hasExpression = "hasExpression"
        translatedFrom = "translatedFrom"
        hasTranslation = "hasTranslation"
        arrangementOf = "arrangementOf"
        hasArrangement = "hasArrangement"
        abridgementOf = "abridgementOf"
        hasAbridgement = "hasAbridgement"
        annotationOf = "annotationOf"
        hasAnnotation = "hasAnnotation"
        draftOf = "draftOf"
        hasDraft = "hasDraft"
        editionOf = "editionOf"
        hasEdition = "hasEdition"
        updates = "updates"
        updatedBy = "updatedBy"
        derivedFrom = "derivedFrom"
        derives = "derives"
        describes = "describes"
        describedBy = "describedBy"
        catalogues = "catalogues"
        cataloguedBy = "cataloguedBy"
        hasSuccessor = "hasSuccessor"
        successorOf = "successorOf"
        adaptedFrom = "adaptedFrom"
        hasAdaptation = "hasAdaptation"
        adoptedFrom = "adoptedFrom"
        adoptedAs = "adoptedAs"
        reviewOf = "reviewOf"
        hasReview = "hasReview"
        commentaryOf = "commentaryOf"
        hasCommentary = "hasCommentary"
        related = "related"
        complements = "complements"
        complementOf = "complementOf"
        obsoletes = "obsoletes"
        obsoletedBy = "obsoletedBy"
        cited = "cited"
        isCitedIn = "isCitedIn"
        replace = "replace"  # special type to be replaced

        @classmethod
        def has_value(cls, value):
            return value in cls._value2member_map_

    type: str
    bibitem: BibliographicItem
    description: FormattedString = None
    locality: Union[Locality, LocalityStack] = field(default_factory=list)
    source_locality: Union[SourceLocality, SourceLocalityStack] = field(
        default_factory=list)

    def __post_init__(self):
        if self.type == "Now withdrawn":
            self.type = DocumentRelation.Type.obsoletes

        if not DocumentRelation.Type.has_value(self.type):
            logging.warning(
                f"[relaton-bib] WARNING: invalid relation type: {self.type}")

        if isinstance(self.type, DocumentRelation.Type):
            self.type = self.type.value

    def to_xml(self, parent, opts={}) -> str:
        opts.pop("bibdata", None)
        opts.pop("note", None)

        name = "relation"
        result = ET.Element(name) if parent is None \
            else ET.SubElement(parent, name)
        result.attrib["type"] = self.type
        if self.description:
            self.description.to_xml(ET.SubElement(result, "description"))

        self.bibitem.to_xml(result, {"embedded": True, **opts})

        for loc in self.locality:
            loc.to_xml(result)

        for loc in self.source_locality:
            loc.to_xml(result)

        return result

    def to_asciibib(self, prefix="", count=1) -> str:
        pref = f"{prefix}." if prefix else prefix
        out = [f"{pref}type:: {self.type}"]
        if self.description:
            out.append(self.description.to_asciibib(f"{pref}desctiption"))
        if self.bibitem:
            out.append(self.bibitem.to_asciibib(f"{pref}bibitem"))
        return "\n".join(out)
