from __future__ import annotations

from lxml import etree as ET
from typing import Optional, Union

from .features import FormSg, Form, FormPlGen, Gender, Strength
from .singular_info import SingularInfo
from .plural_info import PluralInfo

# A noun
class Noun:
    disambig: str = ""

    def getNickname(self) -> str:
        ret: str = self.getLemma()
        ret += " masc" if self.getGender() == Gender.Masc else " fem"
        ret += str(self.declension) if self.declension > 0 else ""
        if self.disambig != "":
            ret += " " + self.disambig
        ret = ret.replace(" ", "_")
        return ret

    def getFriendlyNickname(self) -> str:
        ret: str = self.getLemma()
        ret += " ("
        ret += "masc" if self.getGender() == Gender.Masc else "fem"
        ret += str(self.declension) if self.declension > 0 else ""
        if self.disambig != "":
            ret += " " + self.disambig
        ret += ")"
        return ret

    # The noun's traditional declension class (not actually used for anything); default is 0 meaning "none":
    declension: int = 0

    isProper: bool = False
    # If true, then all article-less genitives are always lenited, no matter what.

    isImmutable: bool = False
    # Eg. "blitz", genitive singular "an blitz"

    # Whether this noun is already definite, even without an article:
    isDefinite: bool = False
    # If true, then no articled forms will be generated when this noun is converted into a noun phrase.

    # For definite noun (isDefinite==true), whether an articled genitive may be generated
    allowArticledGenitive: bool = False
    # Eg. "na hÉireann", "na Gaillimhe"

    def __init__(
        self,
        sgNom: Optional[list[FormSg]] = None,
        sgGen: Optional[list[FormSg]] = None,
        sgVoc: Optional[list[FormSg]] = None,
        sgDat: Optional[list[FormSg]] = None,
        plNom: Optional[list[Form]] = None,
        plGen: Optional[list[FormPlGen]] = None,
        plVoc: Optional[list[Form]] = None,
        count: Optional[list[Form]] = None,
        isProper: bool = False,
        isImmutable: bool = False,
        isDefinite: bool = False,
        allowArticledGenitive: bool = False,
        declension: int = 0,
        disambig: str = "",
    ):
        # Noun forms in the singular:
        self.sgNom: list[FormSg] = [] if sgNom is None else sgNom
        self.sgGen: list[FormSg] = [] if sgGen is None else sgGen
        self.sgVoc: list[FormSg] = [] if sgVoc is None else sgVoc
        self.sgDat: list[FormSg] = [] if sgDat is None else sgDat

        # Noun forms in the plural:
        self.plNom: list[Form] = [] if plNom is None else plNom
        self.plGen: list[FormPlGen] = [] if plGen is None else plGen
        self.plVoc: list[Form] = [] if plVoc is None else plVoc

        # Noun form for counting (if any):
        self.count: list[Form] = [] if count is None else count

        # Whether this is a proper name:
        self.isProper = isProper

        # Whether this noun cannot be mutated (overrides isProper):
        self.isImmutable = isImmutable
        # Eg. "blitz", genitive singular "an blitz"

        # Whether this noun is already definite, even without an article:
        self.isDefinite = isDefinite
        # If true, then no articled forms will be generated when this noun is converted into a noun phrase.

        # For definite noun (isDefinite==true), whether an articled genitive may be generated
        self.allowArticledGenitive = allowArticledGenitive
        # Eg. "na hÉireann", "na Gaillimhe"

        self.declension = declension
        self.disambig = disambig

        self._AddDative()

    # Returns the noun's lemma:
    def getLemma(self) -> str:
        ret: str = ""
        lemmaForm: Form = self.sgNom[0]
        if lemmaForm is not None:
            ret = lemmaForm.value
        return ret

    # Returns the noun's gender:
    def getGender(self) -> Gender:
        return self.sgNom[0].gender

    # Constructors:
    @classmethod
    def create_from_info(cls, si: SingularInfo, pi: Optional[PluralInfo] = None) -> Noun:
        sgNom: list[FormSg] = []
        wf: Form
        for wf in si.nominative:
            sgNom.append(FormSg(wf.value, si.gender))

        sgGen: list[FormSg] = []

        for wf in si.genitive:
            sgGen.append(FormSg(wf.value, si.gender))

        sgVoc: list[FormSg] = []

        for wf in si.vocative:
            sgVoc.append(FormSg(wf.value, si.gender))

        sgDat: list[FormSg] = []

        for wf in si.dative:
            sgDat.append(FormSg(wf.value, si.gender))

        plNom: list[Form] = []
        plGen: list[FormPlGen] = []
        plVoc: list[Form] = []
        if pi is not None:
            for wf in pi.nominative:
                plNom.append(Form(wf.value))

            for wf in pi.genitive:
                plGen.append(FormPlGen(wf.value, pi.strength))

            for wf in pi.vocative:
                plVoc.append(Form(wf.value))

        obj = cls(
            sgNom=sgNom,
            sgGen=sgGen,
            sgVoc=sgVoc,
            sgDat=sgDat,
            plNom=plNom,
            plGen=plGen,
            plVoc=plVoc,
        )
        return obj

    @classmethod
    def from_str(
        cls,
        gender: Gender,
        sgNom: str,
        sgGen: str,
        sgVoc: str,
        strength: Strength,
        plNom: str,
        plGen: str,
        plVoc: str,
    ) -> Noun:
        obj = cls(
            sgNom=[FormSg(sgNom, gender)],
            sgGen=[FormSg(sgGen, gender)],
            sgVoc=[FormSg(sgVoc, gender)],
            sgDat=[FormSg(sgNom, gender)],
            plNom=[Form(plNom)],
            plGen=[FormPlGen(plGen, strength)],
            plVoc=[Form(plVoc)],
        )
        return obj

    @classmethod
    def create_from_xml(cls, doc: Union[str, ET._ElementTree]) -> Noun:
        if isinstance(doc, str):
            xml = ET.parse(doc)
            return cls.create_from_xml(xml)

        root = doc.getroot()
        disambig = root.get("disambig", "")

        try:
            declension = int(root.get("declension", ""))
        except:
            declension = 0

        isProper = root.get("isProper") == "1"
        isImmutable = root.get("isImmutable") == "1"
        isDefinite = root.get("isDefinite") == "1"
        allowArticledGenitive = root.get("allowArticledGenitive") == "1"

        sgNom: list[FormSg] = []
        el: ET._Element
        for el in root.findall("./sgNom"):
            sgNom.append(
                FormSg(
                    el.get("default", ""),
                    Gender.Fem if el.get("gender") == "fem" else Gender.Masc,
                )
            )

        sgGen: list[FormSg] = []
        for el in root.findall("./sgGen"):
            sgGen.append(
                FormSg(
                    el.get("default", ""),
                    Gender.Fem if el.get("gender") == "fem" else Gender.Masc,
                )
            )

        sgVoc: list[FormSg] = []
        for el in root.findall("./sgVoc"):
            sgVoc.append(
                FormSg(
                    el.get("default", ""),
                    Gender.Fem if el.get("gender") == "fem" else Gender.Masc,
                )
            )

        sgDat: list[FormSg] = []
        for el in root.findall("./sgDat"):
            sgDat.append(
                FormSg(
                    el.get("default", ""),
                    Gender.Fem if el.get("gender") == "fem" else Gender.Masc,
                )
            )

        plNom: list[Form] = []
        for el in root.findall("./plNom"):
            plNom.append(Form(el.get("default", "")))

        plGen: list[FormPlGen] = []
        for el in root.findall("./plGen"):
            plGen.append(
                FormPlGen(
                    el.get("default", ""),
                    Strength.Weak if el.get("strength") == "weak" else Strength.Strong,
                )
            )

        plVoc: list[Form] = []
        for el in root.findall("./plVoc"):
            plVoc.append(Form(el.get("default", "")))

        count: list[Form] = []
        for el in root.findall("./count"):
            count.append(Form(el.get("default", "")))

        obj = cls(
            sgNom=sgNom,
            sgGen=sgGen,
            sgVoc=sgVoc,
            sgDat=sgNom,
            plNom=plNom,
            plGen=plGen,
            plVoc=plVoc,
            count=count,
            disambig=disambig,
            declension=declension,
            isProper=isProper,
            isImmutable=isImmutable,
            isDefinite=isDefinite,
            allowArticledGenitive=allowArticledGenitive,
        )
        return obj

    # Called from each constructor to make sure the noun has a dative singular:
    def _AddDative(self) -> None:
        if len(self.sgDat) == 0:
            f: FormSg
            for f in self.sgNom:
                self.sgDat.append(FormSg(f.value, f.gender))

    # Prints a user-friendly summary of the noun's forms:
    def print(self) -> str:
        f: Form
        ret: str = ""
        ret += "sgNom: "
        for f in self.sgNom:
            ret += "[" + f.value + "] "
        ret += "\n"
        ret += "sgGen: "
        for f in self.sgGen:
            ret += "[" + f.value + "] "
        ret += "\n"
        ret += "sgVoc: "
        for f in self.sgVoc:
            ret += "[" + f.value + "] "
        ret += "\n"
        ret += "sgDat: "
        for f in self.sgDat:
            ret += "[" + f.value + "] "
        ret += "\n"
        ret += "plNom: "
        for f in self.plNom:
            ret += "[" + f.value + "] "
        ret += "\n"
        ret += "plGen: "
        for f in self.plGen:
            ret += "[" + f.value + "] "
        ret += "\n"
        ret += "plVoc: "
        for f in self.plVoc:
            ret += "[" + f.value + "] "
        ret += "\n"
        return ret

    # Prints the noun in BuNaMo format:
    def printXml(self) -> ET._ElementTree:
        root: ET._Element = ET.Element("noun")
        doc: ET._ElementTree = ET.ElementTree(root)
        el: ET._Element
        f: Form

        root.set("default", self.getLemma())
        root.set("declension", str(self.declension))
        root.set("disambig", self.disambig)
        root.set("isProper", ("1" if self.isProper else "0"))
        root.set("isImmutable", ("1" if self.isImmutable else "0"))
        root.set("isDefinite", ("1" if self.isDefinite else "0"))
        root.set("allowArticledGenitive", ("1" if self.allowArticledGenitive else "0"))

        for f in self.sgNom:
            el = ET.SubElement(root, "sgNom")
            el.set("default", f.value)
            el.set("gender", ("masc" if f.gender == Gender.Masc else "fem"))

        for f in self.sgGen:
            el = ET.SubElement(root, "sgGen")
            el.set("default", f.value)
            el.set("gender", ("masc" if f.gender == Gender.Masc else "fem"))

        for f in self.sgVoc:
            el = ET.SubElement(root, "sgVoc")
            el.set("default", f.value)
            el.set("gender", ("masc" if f.gender == Gender.Masc else "fem"))

        for f in self.sgDat:
            el = ET.SubElement(root, "sgDat")
            el.set("default", f.value)
            el.set("gender", ("masc" if f.gender == Gender.Masc else "fem"))

        for f in self.plNom:
            el = ET.SubElement(root, "plNom")
            el.set("default", f.value)

        for f in self.plGen:
            el = ET.SubElement(root, "plGen")
            el.set("default", f.value)
            el.set("strength", ("strong" if f.strength == Strength.Strong else "weak"))

        for f in self.plVoc:
            el = ET.SubElement(root, "plVoc")
            el.set("default", f.value)

        for f in self.count:
            el = ET.SubElement(root, "count")
            el.set("default", f.value)

        return doc
