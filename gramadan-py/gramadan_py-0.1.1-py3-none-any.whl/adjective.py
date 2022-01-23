from __future__ import annotations

from lxml import etree as ET
import re
from typing import List, Optional, Union
from .singular_info import SingularInfo
from .features import Form, Mutation
from .opers import Opers
from .utils import to_bool


class Adjective:
    disambig: str = ""
    declension: int = 0
    isPre: bool = False

    @classmethod
    def create_from_xml(cls, doc: Union[str, ET._ElementTree]) -> Adjective:
        if isinstance(doc, str):
            xml = ET.parse(doc)
            return cls.create_from_xml(xml)

        root = doc.getroot()
        disambig = root.get("disambig")

        try:
            declension = int(root.get("declension", 0))
        except:
            declension = 0

        try:
            isPre = to_bool(root.get("isPre", False))
        except:
            isPre = False

        sgNom: list[Form] = []
        el: ET._Element

        for el in root.findall("./sgNom"):
            sgNom.append(Form(el.get("default", "")))

        sgGenMasc: list[Form] = []
        for el in root.findall("./sgGenMasc"):
            sgGenMasc.append(Form(el.get("default", "")))

        sgGenFem: list[Form] = []
        for el in root.findall("./sgGenFem"):
            sgGenFem.append(Form(el.get("default", "")))

        sgVocMasc: list[Form] = []
        for el in root.findall("./sgVocMasc"):
            sgVocMasc.append(Form(el.get("default", "")))

        sgVocFem: list[Form] = []
        for el in root.findall("./sgVocFem"):
            sgVocFem.append(Form(el.get("default", "")))

        plNom: list[Form] = []
        for el in root.findall("./plNom"):
            plNom.append(Form(el.get("default", "")))

        graded: list[Form] = []
        for el in root.findall("./graded"):
            graded.append(Form(el.get("default", "")))

        abstractNoun: list[Form] = []
        for el in root.findall("./abstractNoun"):
            abstractNoun.append(Form(el.get("default", "")))

        return cls(
            sgNom=sgNom,
            sgGenMasc=sgGenMasc,
            sgGenFem=sgGenFem,
            sgVocMasc=sgVocMasc,
            sgVocFem=sgVocFem,
            plNom=plNom,
            graded=graded,
            abstractNoun=abstractNoun,
            disambig=disambig,
            declension=declension,
            isPre=isPre,
        )

    @classmethod
    def create_from_singular_info(
        cls,
        sgMasc: SingularInfo,
        sgFem: SingularInfo,
        plural_or_graded: Optional[str],
        graded: Optional[str],
    ) -> Adjective:
        graded_: str = ""
        if graded is None:
            plural = None
            if plural_or_graded is not None:
                graded_ = plural_or_graded
        else:
            plural = plural_or_graded
            graded_ = graded

        return cls(
            sgNom=sgMasc.nominative,
            sgGenMasc=sgMasc.genitive,
            sgGenFem=sgFem.genitive,
            sgVocMasc=sgMasc.vocative,
            sgVocFem=sgFem.vocative,
            plNom=None if plural is None else [Form(plural)],
            graded=[Form(graded_)],
        )

    def __init__(
        self,
        sgNom: Optional[list[Form]] = None,
        sgGenMasc: Optional[list[Form]] = None,
        sgGenFem: Optional[list[Form]] = None,
        sgVocMasc: Optional[list[Form]] = None,
        sgVocFem: Optional[list[Form]] = None,
        plNom: Optional[list[Form]] = None,
        graded: Optional[list[Form]] = None,
        abstractNoun: Optional[list[Form]] = None,
        disambig="",
        declension: int = 0,
        isPre: bool = False,
    ):
        # The adjective's traditional declension class (not actually used for anything); default is 0 meaning none or unknown:

        # Forms of the adjective:
        self.sgNom: list[Form] = [] if sgNom is None else sgNom
        self.sgGenMasc: list[Form] = [] if sgGenMasc is None else sgGenMasc
        self.sgGenFem: list[Form] = [] if sgGenFem is None else sgGenFem
        self.sgVocMasc: list[Form] = [] if sgVocMasc is None else sgVocMasc
        self.sgVocFem: list[Form] = [] if sgVocFem is None else sgVocFem

        self.disambig = disambig
        self.declension = declension
        self.isPre = isPre

        # Adjective forms in the plural:
        self.plNom: list[Form] = [] if plNom is None else plNom

        # Form for grading:
        self.graded: list[Form] = [] if graded is None else graded

        # Related abstract noun:
        self.abstractNoun: list[Form] = [] if abstractNoun is None else abstractNoun

        # Whether the adjective is a prefix (like "sean"):

    # Returns the adjective's lemma:
    def getLemma(self) -> str:
        ret: str = ""
        lemmaForm: Form = self.sgNom[0]
        if lemmaForm is not None:
            ret = lemmaForm.value

        return ret

    # These return graded forms of the adjective:
    def getComparPres(self) -> list[Form]:  # comparative present, eg. "níos mó"
        ret: list[Form] = []
        gradedForm: Form
        for gradedForm in self.graded:
            ret.append(Form("níos " + gradedForm.value))
        return ret

    def getSuperPres(self) -> list[Form]:  # superlative present, eg. "is mó"
        ret: list[Form] = []
        gradedForm: Form
        for gradedForm in self.graded:
            ret.append(Form("is " + gradedForm.value))
        return ret

    def getComparPast(
        self,
    ) -> list[Form]:  # comparative past/conditional, eg. "ní ba mhó"
        ret: list[Form] = []
        gradedForm: Form
        for gradedForm in self.graded:
            form: str = ""
            if re.search("^[aeiouáéíóúAEIOUÁÉÍÓÚ]", gradedForm.value):
                form = "ní b'" + gradedForm.value
            elif re.search("^f[aeiouáéíóúAEIOUÁÉÍÓÚ]", gradedForm.value):
                form = "ní b'" + Opers.Mutate(Mutation.Len1, gradedForm.value)
            else:
                form = "ní ba " + Opers.Mutate(Mutation.Len1, gradedForm.value)
            ret.append(Form(form))
        return ret

    def getSuperPast(self) -> list[Form]:  # superlative past/conditional, eg. "ba mhó"
        ret: list[Form] = []
        gradedForm: Form
        for gradedForm in self.graded:
            form: str = ""
            if re.search("^[aeiouáéíóúAEIOUÁÉÍÓÚ]", gradedForm.value):
                form = "ab " + gradedForm.value
            elif re.search("^f", gradedForm.value):
                form = "ab " + Opers.Mutate(Mutation.Len1, gradedForm.value)
            else:
                form = "ba " + Opers.Mutate(Mutation.Len1, gradedForm.value)
            ret.append(Form(form))
        return ret

    def getNickname(self) -> str:
        ret: str = self.getLemma()
        ret += " adj"
        ret += str(self.declension) if self.declension > 0 else ""
        if self.disambig != "":
            ret += " " + self.disambig
        ret = ret.replace(" ", "_")
        return ret

    def getFriendlyNickname(self) -> str:
        ret: str = self.getLemma()
        ret += " (adj"
        ret += str(self.declension) if self.declension > 0 else ""
        if self.disambig != "":
            ret += " " + self.disambig
        ret += ")"
        return ret

    # Prints the adjective in BuNaMo format:
    def printXml(self) -> ET._ElementTree:
        root: ET._Element = ET.Element("adjective")
        doc: ET._ElementTree = ET.ElementTree(root)
        root.set("default", self.getLemma())
        root.set("declension", str(self.declension))
        root.set("disambig", self.disambig)
        root.set("isPre", str(self.isPre))

        f: Form
        e: ET._Element
        for f in self.sgNom:
            el = ET.SubElement(root, "sgNom")
            el.set("default", f.value)

        for f in self.sgGenMasc:
            el = ET.SubElement(root, "sgGenMasc")
            el.set("default", f.value)

        for f in self.sgGenFem:
            el = ET.SubElement(root, "sgGenFem")
            el.set("default", f.value)

        for f in self.sgVocMasc:
            el = ET.SubElement(root, "sgVocMasc")
            el.set("default", f.value)

        for f in self.sgVocFem:
            el = ET.SubElement(root, "sgVocFem")
            el.set("default", f.value)

        for f in self.plNom:
            el = ET.SubElement(root, "plNom")
            el.set("default", f.value)

        for f in self.graded:
            el = ET.SubElement(root, "graded")
            el.set("default", f.value)

        for f in self.abstractNoun:
            el = ET.SubElement(root, "abstractNoun")
            el.set("default", f.value)

        return doc
