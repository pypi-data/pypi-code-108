from __future__ import annotations

from lxml import etree as ET
from typing import Optional, Union
from .utils import Utils
from .features import Mutation, Form

# A possessive pronoun:
class Possessive:
    disambig: str = ""

    def getNickname(self) -> str:
        ret: str = self.getLemma()
        if self.disambig != "":
            ret += " " + self.disambig
        ret += " poss"
        ret = ret.replace(" ", "_")
        return ret

    def getFriendlyNickname(self) -> str:
        ret: str = self.getLemma()
        if self.disambig != "":
            ret += " (" + self.disambig + ")"
        return ret

    def __init__(
        self,
        full: Optional[list[Form]],
        apos: Optional[list[Form]],
        mutation: Mutation = Mutation.Nil,
        disambig: str = "",
    ):
        # Its forms:
        self.full: list[Form] = []
        if full:
            self.full = full
        self.apos: list[Form] = []
        if apos:
            self.apos = apos

        # The mutation it causes:
        self.mutation = mutation

        self.disambig = disambig

    # Returns the noun's lemma:
    def getLemma(self) -> str:
        ret: str = ""
        lemmaForm: Form = self.full[0]
        # PTW: is this possible? surely it'd be an empty list
        if lemmaForm != None:
            ret = lemmaForm.value
        return ret

    # Constructors:
    @classmethod
    def create_from_string_and_mutation(cls, s: str, mutation: Mutation) -> Possessive:
        return cls(full=[Form(s)], apos=[Form(s)], mutation=mutation)

    @classmethod
    def create_from_strings_and_mutation(
        cls, full: str, apos: str, mutation: Mutation
    ) -> Possessive:
        return cls(full=[Form(full)], apos=[Form(apos)], mutation=mutation)

    @classmethod
    def create_from_xml(cls, doc: Union[str, ET._ElementTree]) -> Possessive:
        if isinstance(doc, str):
            xml = ET.parse(doc)
            return cls.create_from_xml(xml)

        root = doc.getroot()
        disambig = root.get("disambig", "")
        mutation = Mutation(Utils.UpperInit(root.get("mutation", "")))
        full: list[Form] = []
        apos: list[Form] = []

        el: ET._Element
        for el in root.findall("./full"):
            full.append(Form(el.get("default", "")))

        for el in root.findall("./apos"):
            apos.append(Form(el.get("default", "")))

        return cls(full=full, apos=apos, mutation=mutation, disambig=disambig)

    # Prints the possessive pronoun in BuNaMo format:
    def printXml(self) -> ET._ElementTree:
        root: ET._Element = ET.Element("possessive")
        doc: ET._ElementTree = ET.ElementTree(root)
        root.set("default", self.getLemma())
        root.set("disambig", self.disambig)
        root.set("mutation", Utils.LowerInit(self.mutation.value))

        f: Form

        for f in self.full:
            el = ET.SubElement(root, "full")
            el.set("default", f.value)

        for f in self.apos:
            el = ET.SubElement(root, "apos")
            el.set("default", f.value)
        return doc
