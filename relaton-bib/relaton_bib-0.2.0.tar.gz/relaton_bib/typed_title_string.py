from __future__ import annotations
from dataclasses import dataclass, field, InitVar
from enum import Enum
from typing import List, Union, Tuple

import re
import xml.etree.ElementTree as ET

from .formatted_string import FormattedString, FormattedStringFormat
from .localized_string import LocalizedString
from .relaton_bib import delegate, to_ds_instance


@dataclass
class TypedTitleString:
    class Type(str, Enum):
        MAIN = "main"
        TINTRO = "title-intro"
        TMAIN = "title-main"
        TPART = "title-part"

    type: str = None
    title: FormattedString = None
    content: InitVar[Union[str, List[LocalizedString]]] = field(default=None)
    language: InitVar[List[str]] = field(default=[])
    script: InitVar[List[str]] = field(default=list())
    format: InitVar[str] = field(
        default=FormattedStringFormat.TEXT_PLAIN.value)

    def __post_init__(self, content, language, script, format):
        if self.title is None and content is None:
            raise ValueError("Argument title or content should be passed")

        if not self.title:
            self.title = FormattedString(
                content=content,
                language=language,
                script=script,
                format=format)

    def __str__(self):
        return str(self.title)

    @classmethod
    def from_string(cls, title, lang=[], script=[]) \
            -> TypedTitleStringCollection:
        types = [cls.Type.TINTRO, cls.Type.TMAIN, cls.Type.TPART]
        ttls = cls.split_title(title)
        tts = [None if p is None else
               cls(type=types[i].value,
                   content=p,
                   language=lang,
                   script=script)
               for i, p in enumerate(ttls)]
        tts = list(filter(None, tts))
        ttls = list(filter(None, ttls))
        tts.append(TypedTitleString(type=cls.Type.MAIN,
                                    content=" - ".join(ttls),
                                    language=lang,
                                    script=script))
        return TypedTitleStringCollection(tts)

    @classmethod
    def split_title(cls, title) -> Tuple[str, str, str]:
        ttls = re.sub(r"\w\.Imp\s?\d+\u00A0:\u00A0", "", title).split(" - ")
        if len(ttls) < 2:
            return [None, str(ttls[0]), None]
        else:
            return cls.intro_or_part(ttls)

    @classmethod
    def intro_or_part(cls, ttls) -> Tuple[str, str, str]:
        if re.match(r"^(Part|Partie) \d+:", ttls[1]):
            return (None, ttls[0], " -- ".join(ttls[1:]))
        else:
            parts = ttls[2:]
            part = None
            if any(parts):
                part = " -- ".join(parts)
            return (ttls[0], ttls[1], part)

    def to_xml(self, parent) -> ET.Element:
        if self.type:
            parent.attrib["type"] = self.type
        self.title.to_xml(parent)
        return parent

    def to_asciibib(self, prefix="", count=1) -> str:
        pref = f"{prefix}." if prefix else prefix
        out = [f"{pref}title::"] if count > 1 else []
        if self.type:
            out.append(f"{pref}title.type:: {self.type}")
        out.append(self.title.to_asciibib(f"{pref}title", 1, bool(self.type)))
        return "\n".join(out)


@dataclass
@delegate("titles", "append", "extend", "insert", "remove", "pop", "clear",
          "__getitem__", "__len__", "__iter__", "__reversed__",
          "__contains__")
class TypedTitleStringCollection():
    titles: List[TypedTitleString]

    def __post_init__(self):
        self.titles = list(map(to_ds_instance(TypedTitleString), self.titles))

    def lang(self, lang=None):
        return self.__class__(filter(
            lambda t: lang in t.title.language, self.titles)) \
            if lang else self

    def delete_title_part(self):
        self.titles = list(
            filter(lambda t: t.type != TypedTitleString.Type.TPART,
                   self.titles))

    # @param init [Array, Hash]
    # @return [RelatonBib::TypedTitleStringCollection]
    # def reduce(init)
    #   self.class.new @array.reduce(init) { |m, t| yield m, t }
    # end

    # @param title [RelatonBib::TypedTitleString]
    # # @return [self]
    # def <<(title)
    #   titles << title
    #   self
    # end

    # # @param tcoll [RelatonBib::TypedTitleStringCollection]
    # # @return [RelatonBib::TypedTitleStringCollection]
    # def +(tcoll)
    #   TypedTitleStringCollection.new titles + tcoll.titles
    # end

    # @param opts [Hash]
    # @option opts [Nokogiri::XML::Builder] XML builder
    # @option opts [String, Symbol] :lang language
    def to_xml(self, parent, opts={}):
        lang = opts.get("lang")
        filtered = list(filter(
            lambda t: t.title.language and lang in t.title.language,
            self.titles))
        titles = filtered if any(filtered) else self.titles
        for t in titles:
            t.to_xml(ET.SubElement(parent, "title"))

        return parent
