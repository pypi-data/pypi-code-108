from __future__ import annotations

from lxml import etree as ET
import re
from typing import Optional, Union
from .preposition import Preposition
from .np import NP
from .features import FormSg, Form, Gender, Mutation
from .opers import Opers

# A class for a prepositional phrase:
class PP:
    def __init__(
        self,
        sg: Optional[list[FormSg]],
        sgArtN: Optional[list[FormSg]],
        sgArtS: Optional[list[FormSg]],
        pl: Optional[list[Form]],
        plArt: Optional[list[Form]],
        prepNick: str = "",
    ):
        # Forms:
        self.sg: list[FormSg] = []  # singular, no article
        if sg is not None:
            self.sg = sg

        self.sgArtN: list[FormSg] = []  # singular, with article, northern system
        if sgArtN is not None:
            self.sgArtN = sgArtN

        self.sgArtS: list[FormSg] = []  # singular, with article, southern system
        if sgArtS is not None:
            self.sgArtS = sgArtS

        self.pl: list[Form] = []  # plural, no article
        if pl is not None:
            self.pl = pl

        self.plArt: list[Form] = []  # plural, with article
        if plArt is not None:
            self.plArt = plArt

        # The nickname of the preposition from which this prepositional phrase was created:
        self.prepNick: str = prepNick

    # Returns the prepositional phrase's lemma:
    def getLemma(self) -> str:
        ret: str = ""
        if len(self.sg) != 0:
            ret = self.sg[0].value
        if ret == "" and len(self.sgArtS) != 0:
            ret = self.sgArtS[0].value
        if ret == "" and len(self.sgArtN) != 0:
            ret = self.sgArtN[0].value
        if ret == "" and len(self.pl) != 0:
            ret = self.pl[0].value
        if ret == "" and len(self.plArt) != 0:
            ret = self.plArt[0].value
        return ret

    def getNickname(self) -> str:
        ret: str = self.getLemma() + " PP"
        ret = ret.replace(" ", "_")
        return ret

    # Returns the prepositional phrase's gender:
    def getGender(self) -> Gender:
        ret: Gender = Gender.Masc
        if len(self.sg) != 0:
            ret = self.sg[0].gender
        elif len(self.sgArtS) != 0:
            ret = self.sgArtS[0].gender
        elif len(self.sgArtN) != 0:
            ret = self.sgArtN[0].gender
        return ret

    def hasGender(self) -> bool:
        ret: bool = False

        if len(self.sg) != 0 or len(self.sgArtS) != 0 or len(self.sgArtN) != 0:
            ret = True
        return ret

    # Is the prepositional phrase invalid? This can happen if it has been constructed from an unsupported preposition:
    def isInvalid(self) -> bool:
        ret: bool = True
        if len(self.sg) != 0:
            ret = False
        if ret and len(self.sgArtS) != 0:
            ret = False
        if ret and len(self.sgArtN) != 0:
            ret = False
        if ret and len(self.pl) != 0:
            ret = False
        if ret and len(self.plArt) != 0:
            ret = False
        return ret

    # Prints a user-friendly summary of the prepositional phrase's forms
    def print(self) -> str:
        ret: str = ""
        ret += "uatha, gan alt:                  "
        f: Form
        for f in self.sg:
            ret += "[" + f.value + "] "
        ret += "\n"

        ret += "uatha, alt, córas lárnach:       "
        for f in self.sgArtS:
            ret += "[" + f.value + "] "
        ret += "\n"
        ret += "uatha, alt, córas an tséimhithe: "
        for f in self.sgArtN:
            ret += "[" + f.value + "] "
        ret += "\n"

        ret += "iolra, gan alt:                  "
        for f in self.pl:
            ret += "[" + f.value + "] "
        ret += "\n"

        ret += "iolra, alt:                      "
        for f in self.plArt:
            ret += "[" + f.value + "] "
        ret += "\n"
        ret = ret.replace("] [", ", ").replace("[", "").replace("] ", "")
        return ret

    def printXml(self) -> ET._ElementTree:
        root: ET._Element = ET.Element("prepositionalPhrase")
        doc: ET._ElementTree = ET.ElementTree(root)

        root.set("default", self.getLemma())
        root.set("prepNick", self.prepNick)
        f: Form
        fSg: FormSg
        for fSg in self.sg:
            el = ET.SubElement(root, "sg")
            el.set("default", fSg.value)
            el.set("gender", ("masc" if fSg.gender == Gender.Masc else "fem"))

        for fSg in self.sgArtS:
            el = ET.SubElement(root, "sgArtS")
            el.set("default", fSg.value)
            el.set("gender", ("masc" if fSg.gender == Gender.Masc else "fem"))

        for fSg in self.sgArtN:
            el = ET.SubElement(root, "sgArtN")
            el.set("default", fSg.value)
            el.set("gender", ("masc" if fSg.gender == Gender.Masc else "fem"))

        for f in self.pl:
            el = ET.SubElement(root, "pl")
            el.set("default", f.value)

        for f in self.plArt:
            el = ET.SubElement(root, "plArt")
            el.set("default", f.value)

        return doc

    # Creates a prepositional phrase from a preposition and a noun phrase:
    @classmethod
    def create(cls, prep: Preposition, np: NP) -> PP:
        if not np.isPossessed:
            pp = cls._populateFromUnpossNP(prep, np)
        else:
            pp = cls._populateFromPossNP(prep, np)
        return pp

    # Populates "this" as a prepositional phrase composed from a preposition and an unpossessed noun phrase:
    @classmethod
    def _populateFromUnpossNP(cls, prep: Preposition, np: NP) -> PP:
        prepNick = prep.getNickname()
        sg: list[FormSg] = []  # singular, no article
        sgArtN: list[FormSg] = []  # singular, with article, northern system
        sgArtS: list[FormSg] = []  # singular, with article, southern system
        pl: list[Form] = []  # plural, no article
        plArt: list[Form] = []  # plural, with article
        f: Form
        txt: str

        if prepNick == "ag_prep":
            for f in np.sgDat:
                sg.append(FormSg("ag " + f.value, f.gender))
            for f in np.plDat:
                pl.append(Form("ag " + f.value))
            for f in np.sgDatArtN:
                sgArtN.append(
                    FormSg("ag an " + Opers.Mutate(Mutation.Len3, f.value), f.gender)
                )
            for f in np.sgDatArtS:
                sgArtS.append(
                    FormSg(
                        "ag an "
                        + Opers.Mutate(
                            (
                                Mutation.Ecl3
                                if f.gender == Gender.Fem
                                else Mutation.Ecl2
                            ),
                            f.value,
                        ),
                        f.gender,
                    )
                )
            for f in np.plDatArt:
                plArt.append(Form("ag na " + Opers.Mutate(Mutation.PrefH, f.value)))

        if prepNick == "ar_prep":
            for f in np.sgDat:
                sg.append(
                    FormSg("ar " + Opers.Mutate(Mutation.Len1, f.value), f.gender)
                )
            for f in np.plDat:
                pl.append(Form("ar " + Opers.Mutate(Mutation.Len1, f.value)))
            for f in np.sgDatArtN:
                sgArtN.append(
                    FormSg("ar an " + Opers.Mutate(Mutation.Len3, f.value), f.gender)
                )
            for f in np.sgDatArtS:
                sgArtS.append(
                    FormSg(
                        "ar an "
                        + Opers.Mutate(
                            (
                                Mutation.Ecl3
                                if f.gender == Gender.Fem
                                else Mutation.Ecl2
                            ),
                            f.value,
                        ),
                        f.gender,
                    )
                )
            for f in np.plDatArt:
                plArt.append(Form("ar na " + Opers.Mutate(Mutation.PrefH, f.value)))

        if prepNick == "thar_prep":
            for f in np.sgDat:
                sg.append(
                    FormSg("thar " + Opers.Mutate(Mutation.Len1, f.value), f.gender)
                )
            for f in np.plDat:
                pl.append(Form("thar " + Opers.Mutate(Mutation.Len1, f.value)))
            for f in np.sgDatArtN:
                sgArtN.append(
                    FormSg("thar an " + Opers.Mutate(Mutation.Len3, f.value), f.gender)
                )
            for f in np.sgDatArtS:
                sgArtS.append(
                    FormSg(
                        "thar an "
                        + Opers.Mutate(
                            (
                                Mutation.Ecl3
                                if f.gender == Gender.Fem
                                else Mutation.Ecl2
                            ),
                            f.value,
                        ),
                        f.gender,
                    )
                )
            for f in np.plDatArt:
                plArt.append(Form("thar na " + Opers.Mutate(Mutation.PrefH, f.value)))

        if prepNick == "as_prep":
            for f in np.sgDat:
                sg.append(FormSg("as " + f.value, f.gender))
            for f in np.plDat:
                pl.append(Form("as " + f.value))
            for f in np.sgDatArtN:
                sgArtN.append(
                    FormSg("as an " + Opers.Mutate(Mutation.Len3, f.value), f.gender)
                )
            for f in np.sgDatArtS:
                sgArtS.append(
                    FormSg(
                        "as an "
                        + Opers.Mutate(
                            (
                                Mutation.Ecl3
                                if f.gender == Gender.Fem
                                else Mutation.Ecl2
                            ),
                            f.value,
                        ),
                        f.gender,
                    )
                )
            for f in np.plDatArt:
                plArt.append(Form("as na " + Opers.Mutate(Mutation.PrefH, f.value)))

        if prepNick == "chuig_prep":
            for f in np.sgDat:
                sg.append(FormSg("chuig " + f.value, f.gender))
            for f in np.plDat:
                pl.append(Form("chuig " + f.value))
            for f in np.sgDatArtN:
                sgArtN.append(
                    FormSg("chuig an " + Opers.Mutate(Mutation.Len3, f.value), f.gender)
                )
            for f in np.sgDatArtS:
                sgArtS.append(
                    FormSg(
                        "chuig an "
                        + Opers.Mutate(
                            (
                                Mutation.Ecl3
                                if f.gender == Gender.Fem
                                else Mutation.Ecl2
                            ),
                            f.value,
                        ),
                        f.gender,
                    )
                )
            for f in np.plDatArt:
                plArt.append(Form("chuig na " + Opers.Mutate(Mutation.PrefH, f.value)))

        if prepNick == "de_prep":
            for f in np.sgDat:
                txt = Opers.Mutate(Mutation.Len1, f.value)
                if Opers.StartsVowelFhx(txt):
                    txt = "d'" + txt
                else:
                    txt = "de " + txt
                sg.append(FormSg(txt, f.gender))
            for f in np.plDat:
                txt = Opers.Mutate(Mutation.Len1, f.value)
                if Opers.StartsVowelFhx(txt):
                    txt = "d'" + txt
                else:
                    txt = "de " + txt
                pl.append(Form(txt))
            for f in np.sgDatArtN:
                sgArtN.append(
                    FormSg("den " + Opers.Mutate(Mutation.Len3, f.value), f.gender)
                )
            for f in np.sgDatArtS:
                sgArtS.append(
                    FormSg(
                        "den "
                        + Opers.Mutate(
                            (
                                Mutation.Len3
                                if f.gender == Gender.Fem
                                else Mutation.Len2
                            ),
                            f.value,
                        ),
                        f.gender,
                    )
                )
            for f in np.plDatArt:
                plArt.append(Form("de na " + Opers.Mutate(Mutation.PrefH, f.value)))

        if prepNick == "do_prep":
            for f in np.sgDat:
                txt = Opers.Mutate(Mutation.Len1, f.value)
                if Opers.StartsVowelFhx(txt):
                    txt = "d'" + txt
                else:
                    txt = "do " + txt
                sg.append(FormSg(txt, f.gender))

            for f in np.plDat:
                txt = Opers.Mutate(Mutation.Len1, f.value)
                if Opers.StartsVowelFhx(txt):
                    txt = "d'" + txt
                else:
                    txt = "do " + txt
                pl.append(Form(txt))

            for f in np.sgDatArtN:
                sgArtN.append(
                    FormSg("don " + Opers.Mutate(Mutation.Len3, f.value), f.gender)
                )
            for f in np.sgDatArtS:
                sgArtS.append(
                    FormSg(
                        "don "
                        + Opers.Mutate(
                            (
                                Mutation.Len3
                                if f.gender == Gender.Fem
                                else Mutation.Len2
                            ),
                            f.value,
                        ),
                        f.gender,
                    )
                )
            for f in np.plDatArt:
                plArt.append(Form("do na " + Opers.Mutate(Mutation.PrefH, f.value)))

        if prepNick == "faoi_prep":
            for f in np.sgDat:
                sg.append(
                    FormSg("faoi " + Opers.Mutate(Mutation.Len1, f.value), f.gender)
                )
            for f in np.plDat:
                pl.append(Form("faoi " + Opers.Mutate(Mutation.Len1, f.value)))
            for f in np.sgDatArtN:
                sgArtN.append(
                    FormSg("faoin " + Opers.Mutate(Mutation.Len3, f.value), f.gender)
                )
            for f in np.sgDatArtS:
                sgArtS.append(
                    FormSg(
                        "faoin "
                        + Opers.Mutate(
                            (
                                Mutation.Ecl3
                                if f.gender == Gender.Fem
                                else Mutation.Ecl2
                            ),
                            f.value,
                        ),
                        f.gender,
                    )
                )
            for f in np.plDatArt:
                plArt.append(Form("faoi na " + Opers.Mutate(Mutation.PrefH, f.value)))

        if prepNick == "i_prep":
            for f in np.sgDat:
                if Opers.StartsVowel(f.value):
                    sg.append(FormSg("in " + f.value, f.gender))
                else:
                    sg.append(
                        FormSg("i " + Opers.Mutate(Mutation.Ecl1x, f.value), f.gender)
                    )

            for f in np.plDat:
                if Opers.StartsVowel(f.value):
                    pl.append(Form("in " + f.value))
                else:
                    pl.append(Form("i " + Opers.Mutate(Mutation.Ecl1x, f.value)))

            for f in np.sgDatArtN:
                txt = Opers.Mutate(Mutation.Len3, f.value)
                if Opers.StartsVowelFhx(txt):
                    txt = "san " + txt
                else:
                    txt = "sa " + txt
                sgArtN.append(FormSg(txt, f.gender))

            for f in np.sgDatArtS:
                txt = Opers.Mutate(
                    (Mutation.Len3 if f.gender == Gender.Fem else Mutation.Len2),
                    f.value,
                )
                if Opers.StartsVowelFhx(txt):
                    txt = "san " + txt
                else:
                    txt = "sa " + txt
                sgArtS.append(FormSg(txt, f.gender))

            for f in np.plDatArt:
                plArt.append(Form("sna " + Opers.Mutate(Mutation.PrefH, f.value)))

        if prepNick == "le_prep":
            for f in np.sgDat:
                sg.append(
                    FormSg("le " + Opers.Mutate(Mutation.PrefH, f.value), f.gender)
                )
            for f in np.plDat:
                pl.append(Form("le " + Opers.Mutate(Mutation.PrefH, f.value)))
            for f in np.sgDatArtN:
                sgArtN.append(
                    FormSg("leis an " + Opers.Mutate(Mutation.Len3, f.value), f.gender)
                )
            for f in np.sgDatArtS:
                sgArtS.append(
                    FormSg(
                        "leis an "
                        + Opers.Mutate(
                            (
                                Mutation.Ecl3
                                if f.gender == Gender.Fem
                                else Mutation.Ecl2
                            ),
                            f.value,
                        ),
                        f.gender,
                    )
                )
            for f in np.plDatArt:
                plArt.append(Form("leis na " + Opers.Mutate(Mutation.PrefH, f.value)))

        if prepNick == "ó_prep":
            for f in np.sgDat:
                sg.append(FormSg("ó " + Opers.Mutate(Mutation.Len1, f.value), f.gender))
            for f in np.plDat:
                pl.append(Form("ó " + Opers.Mutate(Mutation.Len1, f.value)))
            for f in np.sgDatArtN:
                sgArtN.append(
                    FormSg("ón " + Opers.Mutate(Mutation.Len3, f.value), f.gender)
                )
            for f in np.sgDatArtS:
                sgArtS.append(
                    FormSg(
                        "ón "
                        + Opers.Mutate(
                            (
                                Mutation.Ecl3
                                if f.gender == Gender.Fem
                                else Mutation.Ecl2
                            ),
                            f.value,
                        ),
                        f.gender,
                    )
                )
            for f in np.plDatArt:
                plArt.append(Form("ó na " + Opers.Mutate(Mutation.PrefH, f.value)))

        if prepNick == "roimh_prep":
            for f in np.sgDat:
                sg.append(
                    FormSg("roimh " + Opers.Mutate(Mutation.Len1, f.value), f.gender)
                )
            for f in np.plDat:
                pl.append(Form("roimh " + Opers.Mutate(Mutation.Len1, f.value)))
            for f in np.sgDatArtN:
                sgArtN.append(
                    FormSg("roimh an " + Opers.Mutate(Mutation.Len3, f.value), f.gender)
                )
            for f in np.sgDatArtS:
                sgArtS.append(
                    FormSg(
                        "roimh an "
                        + Opers.Mutate(
                            (
                                Mutation.Ecl3
                                if f.gender == Gender.Fem
                                else Mutation.Ecl2
                            ),
                            f.value,
                        ),
                        f.gender,
                    )
                )
            for f in np.plDatArt:
                plArt.append(Form("roimh na " + Opers.Mutate(Mutation.PrefH, f.value)))

        if prepNick == "trí_prep":
            for f in np.sgDat:
                sg.append(
                    FormSg("trí " + Opers.Mutate(Mutation.Len1, f.value), f.gender)
                )
            for f in np.plDat:
                pl.append(Form("trí " + Opers.Mutate(Mutation.Len1, f.value)))
            for f in np.sgDatArtN:
                sgArtN.append(
                    FormSg("tríd an " + Opers.Mutate(Mutation.Len3, f.value), f.gender)
                )
            for f in np.sgDatArtS:
                sgArtS.append(
                    FormSg(
                        "tríd an "
                        + Opers.Mutate(
                            (
                                Mutation.Ecl3
                                if f.gender == Gender.Fem
                                else Mutation.Ecl2
                            ),
                            f.value,
                        ),
                        f.gender,
                    )
                )
            for f in np.plDatArt:
                plArt.append(Form("trí na " + Opers.Mutate(Mutation.PrefH, f.value)))

        if prepNick == "um_prep":
            for f in np.sgDat:
                txt = f.value
                if not Opers.StartsBilabial(txt):
                    txt = Opers.Mutate(Mutation.Len1, txt)
                sg.append(FormSg("um " + txt, f.gender))

            for f in np.plDat:
                txt = f.value
                if not Opers.StartsBilabial(txt):
                    txt = Opers.Mutate(Mutation.Len1, txt)
                pl.append(Form("um " + txt))

            for f in np.sgDatArtN:
                sgArtN.append(
                    FormSg("um an " + Opers.Mutate(Mutation.Len3, f.value), f.gender)
                )
            for f in np.sgDatArtS:
                sgArtS.append(
                    FormSg(
                        "um an "
                        + Opers.Mutate(
                            (
                                Mutation.Ecl3
                                if f.gender == Gender.Fem
                                else Mutation.Ecl2
                            ),
                            f.value,
                        ),
                        f.gender,
                    )
                )
            for f in np.plDatArt:
                plArt.append(Form("um na " + Opers.Mutate(Mutation.PrefH, f.value)))

        return cls(
            sg=sg, sgArtN=sgArtN, sgArtS=sgArtS, pl=pl, plArt=plArt, prepNick=prepNick
        )

    # Populates "this" as a prepositional phrase composed from a preposition and a possessed noun phrase:
    @classmethod
    def _populateFromPossNP(cls, prep: Preposition, np: NP) -> PP:
        prepNick = prep.getNickname()
        sg: list[FormSg] = []  # singular, no article
        sgArtN: list[FormSg] = []  # singular, with article, northern system
        sgArtS: list[FormSg] = []  # singular, with article, southern system
        pl: list[Form] = []  # plural, no article
        plArt: list[Form] = []  # plural, with article
        f: Form
        if prepNick == "de_prep" or prepNick == "do_prep":
            for f in np.sgDat:
                if f.value.startswith("a "):
                    sg.append(FormSg(re.sub("^a ", "dá ", f.value), f.gender))
                elif f.value.startswith("ár "):
                    sg.append(FormSg(re.sub("^ár ", "dár ", f.value), f.gender))
                else:
                    sg.append(FormSg(prep.getLemma() + " " + f.value, f.gender))

            for f in np.plDat:
                if f.value.startswith("a "):
                    pl.append(Form(re.sub("^a ", "dá ", f.value)))
                elif f.value.startswith("ár "):
                    pl.append(Form(re.sub("^ár ", "dár ", f.value)))
                else:
                    pl.append(Form(prep.getLemma() + " " + f.value))
        elif prepNick == "faoi_prep":
            for f in np.sgDat:
                if f.value.startswith("a "):
                    sg.append(FormSg(re.sub("^a ", "faoina ", f.value), f.gender))
                elif f.value.startswith("ár "):
                    sg.append(FormSg(re.sub("^ár ", "faoinár ", f.value), f.gender))
                else:
                    sg.append(FormSg(prep.getLemma() + " " + f.value, f.gender))

            for f in np.plDat:
                if f.value.startswith("a "):
                    pl.append(Form(re.sub("^a ", "faoina ", f.value)))
                elif f.value.startswith("ár "):
                    pl.append(Form(re.sub("^ár ", "faoinár ", f.value)))
                else:
                    pl.append(Form(prep.getLemma() + " " + f.value))
        elif prepNick == "i_prep":
            for f in np.sgDat:
                if f.value.startswith("a "):
                    sg.append(FormSg(re.sub("^a ", "ina ", f.value), f.gender))
                elif f.value.startswith("ár "):
                    sg.append(FormSg(re.sub("^ár ", "inár ", f.value), f.gender))
                elif f.value.startswith("bhur "):
                    sg.append(FormSg(re.sub("^bhur ", "in bhur ", f.value), f.gender))
                else:
                    sg.append(FormSg(prep.getLemma() + " " + f.value, f.gender))
            for f in np.plDat:
                if f.value.startswith("a "):
                    pl.append(Form(re.sub("^a ", "ina ", f.value)))
                elif f.value.startswith("ár "):
                    pl.append(Form(re.sub("^ár ", "inár ", f.value)))
                elif f.value.startswith("bhur "):
                    pl.append(Form(re.sub("^bhur ", "in bhur ", f.value)))
                else:
                    pl.append(Form(prep.getLemma() + " " + f.value))
        elif prepNick == "le_prep":
            for f in np.sgDat:
                if f.value.startswith("a "):
                    sg.append(FormSg(re.sub("^a ", "lena ", f.value), f.gender))
                elif f.value.startswith("ár "):
                    sg.append(FormSg(re.sub("^ár ", "lenár ", f.value), f.gender))
                else:
                    sg.append(FormSg(prep.getLemma() + " " + f.value, f.gender))
            for f in np.plDat:
                if f.value.startswith("a "):
                    pl.append(Form(re.sub("^a ", "lena ", f.value)))
                elif f.value.startswith("ár "):
                    pl.append(Form(re.sub("^ár ", "lenár ", f.value)))
                else:
                    pl.append(Form(prep.getLemma() + " " + f.value))
        elif prepNick == "ó_prep":
            for f in np.sgDat:
                if f.value.startswith("a "):
                    sg.append(FormSg(re.sub("^a ", "óna ", f.value), f.gender))
                elif f.value.startswith("ár "):
                    sg.append(FormSg(re.sub("^ár ", "ónár ", f.value), f.gender))
                else:
                    sg.append(FormSg(prep.getLemma() + " " + f.value, f.gender))

            for f in np.plDat:
                if f.value.startswith("a "):
                    pl.append(Form(re.sub("^a ", "óna ", f.value)))
                elif f.value.startswith("ár "):
                    pl.append(Form(re.sub("^ár ", "ónár ", f.value)))
                else:
                    pl.append(Form(prep.getLemma() + " " + f.value))
        elif prepNick == "trí_prep":
            for f in np.sgDat:
                if f.value.startswith("a "):
                    sg.append(FormSg(re.sub("^a ", "trína ", f.value), f.gender))
                elif f.value.startswith("ár "):
                    sg.append(FormSg(re.sub("^ár ", "trínár ", f.value), f.gender))
                else:
                    sg.append(FormSg(prep.getLemma() + " " + f.value, f.gender))
            for f in np.plDat:
                if f.value.startswith("a "):
                    pl.append(Form(re.sub("^a ", "trína ", f.value)))
                elif f.value.startswith("ár "):
                    pl.append(Form(re.sub("^ár ", "trínár ", f.value)))
                else:
                    pl.append(Form(prep.getLemma() + " " + f.value))
        else:
            for f in np.sgDat:
                sg.append(FormSg(prep.getLemma() + " " + f.value, f.gender))
            for f in np.plDat:
                pl.append(Form(prep.getLemma() + " " + f.value))

        return cls(
            sg=sg, sgArtN=sgArtN, sgArtS=sgArtS, pl=pl, plArt=plArt, prepNick=prepNick
        )

    # Constructs a prepositional phrase from an XML file in BuNaMo format:
    @classmethod
    def create_from_xml(cls, doc: Union[str, ET._ElementTree]) -> PP:
        if isinstance(doc, str):
            xml = ET.parse(doc)
            return cls.create_from_xml(xml)

        root = doc.getroot()
        prepNick = root.get("prepNick", "")
        sg: list[FormSg] = []  # singular, no article
        sgArtN: list[FormSg] = []  # singular, with article, northern system
        sgArtS: list[FormSg] = []  # singular, with article, southern system
        pl: list[Form] = []  # plural, no article
        plArt: list[Form] = []  # plural, with article

        for el in root.findall("./sg"):
            sg.append(
                FormSg(
                    el.get("default", ""),
                    (Gender.Fem if el.get("gender") == "fem" else Gender.Masc),
                )
            )

        for el in root.findall("./sgArtN"):
            sgArtN.append(
                FormSg(
                    el.get("default", ""),
                    (Gender.Fem if el.get("gender") == "fem" else Gender.Masc),
                )
            )

        for el in root.findall("./sgArtS"):
            sgArtS.append(
                FormSg(
                    el.get("default", ""),
                    (Gender.Fem if el.get("gender") == "fem" else Gender.Masc),
                )
            )

        for el in root.findall("./pl"):
            pl.append(Form(el.get("default", "")))

        for el in root.findall("./plArt"):
            plArt.append(Form(el.get("default", "")))

        return cls(
            sg=sg, sgArtN=sgArtN, sgArtS=sgArtS, pl=pl, plArt=plArt, prepNick=prepNick
        )
