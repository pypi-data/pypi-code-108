from __future__ import annotations

from lxml import etree as ET
from typing import Optional, Union
from .features import Gender, Mutation, FormSg, Form, FormPlGen, Strength
from .noun import Noun
from .opers import Opers
from .possessive import Possessive
from .adjective import Adjective

# A class for a noun phrase:
class NP:
    disambig: str = ""

    isImmutable: bool = False

    forceNominative: bool = False

    # Returns the noun phrase's lemma:
    def getLemma(self) -> str:
        ret: str = ""
        if len(self.sgNom) != 0:
            ret = self.sgNom[0].value
        if ret == "" and len(self.sgNomArt) != 0:
            ret = self.sgNomArt[0].value
        if ret == "" and len(self.plNom) != 0:
            ret = self.plNom[0].value
        if ret == "" and len(self.plNomArt) != 0:
            ret = self.plNomArt[0].value
        return ret

    def getNickname(self) -> str:
        ret: str = self.getLemma() + " NP"
        if self.disambig != "":
            ret += " " + self.disambig
        ret = ret.replace(" ", "_")
        return ret

    def __init__(
        self,
        sgNom: Optional[list[FormSg]],
        sgGen: Optional[list[FormSg]],
        sgDat: Optional[list[FormSg]],
        sgNomArt: Optional[list[FormSg]],
        sgGenArt: Optional[list[FormSg]],
        sgDatArtN: Optional[list[FormSg]],
        sgDatArtS: Optional[list[FormSg]],
        plNom: Optional[list[Form]],
        plGen: Optional[list[Form]],
        plDat: Optional[list[Form]],
        plNomArt: Optional[list[Form]],
        plGenArt: Optional[list[Form]],
        plDatArt: Optional[list[Form]],
        isDefinite: bool = False,
        isPossessed: bool = False,
        isImmutable: bool = False,
        forceNominative: bool = False,
        disambig: str = "",
    ):
        # Noun phrase forms in the singular, without article:
        self.sgNom: list[FormSg] = []
        if sgNom is not None:
            self.sgNom = sgNom
        self.sgGen: list[FormSg] = []
        if sgGen is not None:
            self.sgGen = sgGen
        self.sgDat: list[FormSg] = []  # head noun left unmutated
        if sgDat is not None:
            self.sgDat = sgDat

        # Noun phrase forms in the singular, with article:
        self.sgNomArt: list[FormSg] = []
        if sgNomArt is not None:
            self.sgNomArt = sgNomArt
        self.sgGenArt: list[FormSg] = []
        if sgGenArt is not None:
            self.sgGenArt = sgGenArt
        # northern system, as if with article but the article is *not* included, head noun unmutated
        self.sgDatArtN: list[FormSg] = []
        if sgDatArtN is not None:
            self.sgDatArtN = sgDatArtN
        # southern system, as if with article but the article is *not* included, head noun unmutated
        self.sgDatArtS: list[FormSg] = []
        if sgDatArtS is not None:
            self.sgDatArtS = sgDatArtS

        # Noun phrase forms in the plural, without article:
        self.plNom: list[Form] = []
        if plNom is not None:
            self.plNom = plNom
        self.plGen: list[Form] = []
        if plGen is not None:
            self.plGen = plGen
        self.plDat: list[Form] = []  # head noun left unmutated
        if plDat is not None:
            self.plDat = plDat

        # Noun phrase forms in the plural, with article:
        self.plNomArt: list[Form] = []
        if plNomArt is not None:
            self.plNomArt = plNomArt
        self.plGenArt: list[Form] = []
        if plGenArt is not None:
            self.plGenArt = plGenArt
        self.plDatArt: list[Form] = []
        if (
            plDatArt is not None
        ):  # as if with article but the article is *not* included, head noun unmutated
            self.plDatArt = plDatArt

        # Whether self noun phrase is definite:
        self.isDefinite: bool = isDefinite  # If True, the articleless forms are definite and there are no articled forms.
        # If False, the articleless forms are indefinite and the articled forms are definite.
        # Whether self noun phrase is determined by a possessive pronoun:
        self.isPossessed: bool = isPossessed  # if True, only sgNom, sgDat, sgGen, plNom, plDat, plGen exist, the others are empty.

        # Whether self NP's head noun cannot be mutated by prepositions:
        self.isImmutable: bool = isImmutable  # Eg. "blitz", dative "leis an blitz mhór"

        # Should the unarticled nominative be used in place of the unarticled genitive?
        self.forceNominative: bool = forceNominative

        self.disambig = disambig

    # Returns the noun phrase's gender:
    def getGender(self) -> Gender:
        ret: Gender = Gender.Masc
        if len(self.sgNom) != 0:
            ret = self.sgNom[0].gender
        elif len(self.sgNomArt) != 0:
            ret = self.sgNomArt[0].gender
        return ret

    def hasGender(self) -> bool:
        ret: bool = False
        if len(self.sgNom) != 0 or len(self.sgNomArt) != 0:
            ret = True
        return ret

    # Prints a user-friendly summary of the noun phrase's forms:
    def print(self) -> str:
        ret: str = ""
        ret += "sgNom: "
        f: Form
        for f in self.sgNom:
            ret += "[" + f.value + "] "
        ret += "\n"
        ret += "sgGen: "

        for f in self.sgGen:
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
        ret += "sgNomArt: "

        for f in self.sgNomArt:
            ret += "[" + f.value + "] "
        ret += "\n"
        ret += "sgGenArt: "

        for f in self.sgGenArt:
            ret += "[" + f.value + "] "
        ret += "\n"
        ret += "plNomArt: "

        for f in self.plNomArt:
            ret += "[" + f.value + "] "
        ret += "\n"
        ret += "plGenArt: "

        for f in self.plGenArt:
            ret += "[" + f.value + "] "

        ret += "\n\n"
        # ---

        ret += "sgDat: "

        for f in self.sgDat:
            ret += "[" + f.value + "] "
        ret += "\n"
        ret += "sgDatArtN: "

        for f in self.sgDatArtN:
            ret += "[" + f.value + "] "
        ret += "\n"
        ret += "sgDatArtS: "

        for f in self.sgDatArtS:
            ret += "[" + f.value + "] "
        ret += "\n"
        ret += "plDat: "

        for f in self.plDat:
            ret += "[" + f.value + "] "
        ret += "\n"
        ret += "plDatArt: "

        for f in self.plDatArt:
            ret += "[" + f.value + "] "
        ret += "\n"
        return ret

    # Creates a noun phrase from an explicit listing of all the basic forms:
    @classmethod
    def create(
        cls,
        gender: Gender,
        sgNomStr: str,
        sgGenStr: str,
        plNomStr: str,
        plGenStr: str,
        sgDatArtNStr: str,
    ):
        # region singular-nominative
        # without article:
        sgNom: list[FormSg] = [FormSg(sgNomStr, gender)]
        # { # with article:
        value: str
        mut: Mutation

        mut = Mutation.PrefT if gender == Gender.Masc else Mutation.Len3
        value = "an " + Opers.Mutate(mut, sgNomStr)
        sgNomArt: list[FormSg] = [FormSg(value, gender)]
        # }
        # endregion
        # region singular-genitive
        # { # without article:
        sgGen: list[FormSg] = [FormSg(sgNomStr, gender)]
        # }
        # { # with article:
        mut = Mutation.Len3 if gender == Gender.Masc else Mutation.PrefH
        article: str = "an" if gender == Gender.Masc else "na"
        value = article + " " + Opers.Mutate(mut, sgGenStr)
        sgGenArt: list[FormSg] = [FormSg(value, gender)]
        # }
        # endregion
        # region plural-nominative
        # { # without article:
        plNom: list[Form] = [Form(plNomStr)]
        # }
        # { # with article:
        value = "na " + Opers.Mutate(Mutation.PrefH, plNomStr)
        plNomArt: list[Form] = [Form(value)]
        # }
        # endregion
        # region plural-genitive
        # { # without article:
        plGen: list[Form] = [Form(plNomStr)]
        # }
        # { # with article:
        value = "na " + Opers.Mutate(Mutation.Ecl1, plGenStr)
        plGenArt: list[Form] = [Form(value)]
        # }
        # endregion
        # region singular-dative
        # { # without article:
        sgDat: list[FormSg] = [FormSg(sgNomStr, gender)]
        # }
        # { # with article:
        sgDatArtN: list[FormSg] = [FormSg(sgDatArtNStr, gender)]
        sgDatArtS: list[FormSg] = [FormSg(sgNomStr, gender)]  # PTW: yes, nominative

        mut = Mutation.PrefT if gender == Gender.Masc else Mutation.Len3
        value = "an " + Opers.Mutate(mut, sgNomStr)
        # PTW: TODO - not entirely clear why sgNomArt is being appended to here... (but true in CS also l152)
        sgNomArt.append(FormSg(value, gender))
        # }
        # endregion
        # region plural-dative
        # { # without article:
        plDat = [Form(plNomStr)]
        # }
        # { # with article:
        plDatArt = [Form(plNomStr)]
        # }
        # endregion
        return cls(
            sgNom=sgNom,
            sgGen=sgGen,
            sgDat=sgDat,
            sgNomArt=sgNomArt,
            sgGenArt=sgGenArt,
            sgDatArtN=sgDatArtN,
            sgDatArtS=sgDatArtS,
            plNom=plNom,
            plGen=plGen,
            plDat=plDat,
            plNomArt=plNomArt,
            plGenArt=plGenArt,
            plDatArt=plDatArt,
            # PTW: TODO - are the below always default here?
            # isDefinite=isDefinite,
            # isPossessed=isPossessed,
            # isImmutable=isImmutable,
            # forceNominative=forceNominative,
        )

    # Creates a noun phrase from a noun determined by a possessive pronoun:
    @classmethod
    def create_from_possessive(cls, head: Noun, poss: Possessive) -> NP:
        np = cls.create_from_noun(head)
        np._makePossessive(poss)
        return np

    # Creates a noun phrase from a noun modified by an adjective determined by a possessive pronoun:
    @classmethod
    def create_from_noun_adjective_possessive(
        cls, head: Noun, mod: Adjective, poss: Possessive
    ) -> NP:
        np = cls.create_from_noun_adjective(head, mod)
        np._makePossessive(poss)
        return np

    # Creates a noun phrase from a noun:
    @classmethod
    def create_from_noun(cls, head: Noun) -> NP:
        isDefinite = head.isDefinite
        isImmutable = head.isImmutable
        # region singular-nominative
        headFormSg: FormSg  # naturally, these could be together, but
        headForm: Form  # this is very helpful for checking
        headFormPlGen: FormPlGen
        sgNom: list[FormSg] = []
        sgGen: list[FormSg] = []
        sgDat: list[FormSg] = []
        sgNomArt: list[FormSg] = []
        sgGenArt: list[FormSg] = []
        sgDatArtN: list[FormSg] = []
        sgDatArtS: list[FormSg] = []
        plNom: list[Form] = []
        plGen: list[Form] = []
        plDat: list[Form] = []
        plNomArt: list[Form] = []
        plGenArt: list[Form] = []
        plDatArt: list[Form] = []

        article: str
        value: str
        mut: Mutation

        for headFormSg in head.sgNom:
            # without article:
            sgNom.append(FormSg(headFormSg.value, headFormSg.gender))

            if not head.isDefinite:  # with article:
                mut = (
                    Mutation.PrefT
                    if headFormSg.gender == Gender.Masc
                    else Mutation.Len3
                )
                if head.isImmutable:
                    mut = Mutation.Nil
                value = "an " + Opers.Mutate(mut, headFormSg.value)
                sgNomArt.append(FormSg(value, headFormSg.gender))

        # endregion
        # region singular-genitive
        for headFormSg in head.sgGen:
            # without article:
            mut = Mutation.Len1 if head.isProper else Mutation.Nil
            # proper nouns are always lenited in the genitive
            if head.isImmutable:
                mut = Mutation.Nil
            value = Opers.Mutate(mut, headFormSg.value)
            sgGen.append(FormSg(value, headFormSg.gender))

            # with article:
            if not head.isDefinite or head.allowArticledGenitive:
                mut = (
                    Mutation.Len3
                    if headFormSg.gender == Gender.Masc
                    else Mutation.PrefH
                )
                if head.isImmutable:
                    mut = Mutation.Nil
                article = "an" if headFormSg.gender == Gender.Masc else "na"
                value = article + " " + Opers.Mutate(mut, headFormSg.value)
                sgGenArt.append(FormSg(value, headFormSg.gender))

        # endregion
        # region plural-nominative
        for headForm in head.plNom:
            # without article:
            plNom.append(Form(headForm.value))

            if not head.isDefinite:  # with article:
                mut = Mutation.PrefH
                if head.isImmutable:
                    mut = Mutation.Nil
                value = "na " + Opers.Mutate(mut, headForm.value)
                plNomArt.append(Form(value))

        # endregion
        # region plural-genitive
        for headFormPlGen in head.plGen:
            # without article:
            mut = Mutation.Len1 if head.isProper else Mutation.Nil
            # proper nouns are always lenited in the articleless genitive
            if head.isImmutable:
                mut = Mutation.Nil
            value = Opers.Mutate(mut, headFormPlGen.value)
            plGen.append(Form(value))

            if not head.isDefinite or head.allowArticledGenitive:  # with article:
                mut = Mutation.Ecl1
                if head.isImmutable:
                    mut = Mutation.Nil
                value = "na " + Opers.Mutate(mut, headFormPlGen.value)
                plGenArt.append(Form(value))

        # endregion
        # region singular-dative
        for headFormSg in head.sgDat:
            # without article:
            sgDat.append(FormSg(headFormSg.value, headFormSg.gender))

            if not head.isDefinite:  # with article:
                sgDatArtN.append(FormSg(headFormSg.value, headFormSg.gender))
                sgDatArtS.append(FormSg(headFormSg.value, headFormSg.gender))

        # endregion
        # region plural-dative
        for headForm in head.plNom:
            # without article:
            plDat.append(Form(headForm.value))
            if not head.isDefinite:  # with article:
                plDatArt.append(Form(headForm.value))

        # endregion
        return cls(
            sgNom=sgNom,
            sgGen=sgGen,
            sgDat=sgDat,
            sgNomArt=sgNomArt,
            sgGenArt=sgGenArt,
            sgDatArtN=sgDatArtN,
            sgDatArtS=sgDatArtS,
            plNom=plNom,
            plGen=plGen,
            plDat=plDat,
            plNomArt=plNomArt,
            plGenArt=plGenArt,
            plDatArt=plDatArt,
            isDefinite=isDefinite,
            isImmutable=isImmutable,
            # isPossessed=isPossessed,   # PTW: sure these are default?
            # forceNominative=forceNominative,
        )

    # Creates a noun phrase from a noun modified by an adjective:
    @classmethod
    def create_from_noun_adjective(cls, head: Noun, mod: Adjective) -> NP:
        if mod.isPre:
            prefixedHead: Noun = Noun.create_from_xml(head.printXml())
            # create a copy of the head noun
            prefix: str = mod.getLemma()
            f: Form
            for f in prefixedHead.sgNom:
                f.value = Opers.Prefix(prefix, f.value)

            for f in prefixedHead.sgGen:
                f.value = Opers.Prefix(prefix, f.value)

            for f in prefixedHead.sgDat:
                f.value = Opers.Prefix(prefix, f.value)

            for f in prefixedHead.sgVoc:
                f.value = Opers.Prefix(prefix, f.value)

            for f in prefixedHead.plNom:
                f.value = Opers.Prefix(prefix, f.value)

            for f in prefixedHead.plGen:
                f.value = Opers.Prefix(prefix, f.value)

            for f in prefixedHead.plVoc:
                f.value = Opers.Prefix(prefix, f.value)

            for f in prefixedHead.count:
                f.value = Opers.Prefix(prefix, f.value)
            np: NP = cls.create_from_noun(prefixedHead)
            isDefinite: bool = np.isDefinite
            isImmutable: bool = cls.isImmutable  # PTW: use the default
            forceNominative: bool = cls.forceNominative
            sgNom = np.sgNom
            sgNomArt = np.sgNomArt
            sgGen = np.sgGen
            sgGenArt = np.sgGenArt
            sgDat = np.sgDat
            sgDatArtN = np.sgDatArtN
            sgDatArtS = np.sgDatArtS
            plNom = np.plNom
            plNomArt = np.plNomArt
            plGen = np.plGen
            plGenArt = np.plGenArt
            plDat = np.plDat
            plDatArt = np.plDatArt
        else:
            isDefinite = head.isDefinite
            isImmutable = head.isImmutable
            forceNominative = True
            sgNom = []
            sgNomArt = []
            sgGen = []
            sgGenArt = []
            sgDat = []
            sgDatArtN = []
            sgDatArtS = []
            plNom = []
            plNomArt = []
            plGen = []
            plGenArt = []
            plDat = []
            plDatArt = []
            # region singular-nominative
            headFormSg: FormSg
            modForm: Form
            modForms: list[Form]
            mutA: Mutation
            mutN: Mutation
            value: str
            article: str

            for headFormSg in head.sgNom:
                # without article:
                for modForm in mod.sgNom:
                    mutA = (
                        Mutation.Nil
                        if headFormSg.gender == Gender.Masc
                        else Mutation.Len1
                    )
                    value = headFormSg.value + " " + Opers.Mutate(mutA, modForm.value)
                    sgNom.append(FormSg(value, headFormSg.gender))

                if not head.isDefinite:  # with article:
                    for modForm in mod.sgNom:
                        mutN = (
                            Mutation.PrefT
                            if headFormSg.gender == Gender.Masc
                            else Mutation.Len3
                        )
                        if head.isImmutable:
                            mutN = Mutation.Nil
                        mutA = (
                            Mutation.Nil
                            if headFormSg.gender == Gender.Masc
                            else Mutation.Len1
                        )
                        value = (
                            "an "
                            + Opers.Mutate(mutN, headFormSg.value)
                            + " "
                            + Opers.Mutate(mutA, modForm.value)
                        )
                        sgNomArt.append(FormSg(value, headFormSg.gender))

            # endregion
            # region singular-genitive
            for headFormSg in head.sgGen:
                # without article:
                modForms = (
                    mod.sgGenMasc if headFormSg.gender == Gender.Masc else mod.sgGenFem
                )
                for modForm in modForms:
                    mutN = Mutation.Len1 if head.isProper else Mutation.Nil
                    # proper nouns are always lenited in the genitive
                    if head.isImmutable:
                        mutN = Mutation.Nil
                    mutA = (
                        Mutation.Len1
                        if headFormSg.gender == Gender.Masc
                        else Mutation.Nil
                    )
                    value = (
                        Opers.Mutate(mutN, headFormSg.value)
                        + " "
                        + Opers.Mutate(mutA, modForm.value)
                    )
                    sgGen.append(FormSg(value, headFormSg.gender))

            for headFormSg in head.sgGen:
                # with article:
                if not head.isDefinite or head.allowArticledGenitive:
                    modForms = (
                        mod.sgGenMasc
                        if headFormSg.gender == Gender.Masc
                        else mod.sgGenFem
                    )
                    for modForm in modForms:
                        mutN = (
                            Mutation.Len3
                            if headFormSg.gender == Gender.Masc
                            else Mutation.PrefH
                        )
                        if head.isImmutable:
                            mutN = Mutation.Nil
                        mutA = (
                            Mutation.Len1
                            if headFormSg.gender == Gender.Masc
                            else Mutation.Nil
                        )
                        article = "an" if headFormSg.gender == Gender.Masc else "na"
                        value = (
                            article
                            + " "
                            + Opers.Mutate(mutN, headFormSg.value)
                            + " "
                            + Opers.Mutate(mutA, modForm.value)
                        )
                        sgGenArt.append(FormSg(value, headFormSg.gender))

            # endregion
            # region plural-nominative
            headForm: Form
            for headForm in head.plNom:
                # without article:
                for modForm in mod.plNom:
                    mutA = (
                        Mutation.Len1
                        if Opers.IsSlender(headForm.value)
                        else Mutation.Nil
                    )
                    value = headForm.value + " " + Opers.Mutate(mutA, modForm.value)
                    plNom.append(Form(value))

                if not head.isDefinite:  # with article:
                    for modForm in mod.plNom:
                        mutN = Mutation.PrefH
                        if head.isImmutable:
                            mutN = Mutation.Nil
                        mutA = (
                            Mutation.Len1
                            if Opers.IsSlender(headForm.value)
                            else Mutation.Nil
                        )
                        value = (
                            "na "
                            + Opers.Mutate(mutN, headForm.value)
                            + " "
                            + Opers.Mutate(mutA, modForm.value)
                        )
                        plNomArt.append(Form(value))

            # endregion
            # region plural-genitive
            headFormPlGen: FormPlGen
            for headFormPlGen in head.plGen:
                # without article:
                modForms = (
                    mod.plNom
                    if headFormPlGen.strength == Strength.Strong
                    else mod.sgNom
                )
                for modForm in modForms:
                    mutA = (
                        Mutation.Len1
                        if Opers.IsSlender(headFormPlGen.value)
                        else Mutation.Nil
                    )
                    if headFormPlGen.strength == Strength.Weak:
                        mutA = (
                            Mutation.Len1
                            if Opers.IsSlenderI(headFormPlGen.value)
                            else Mutation.Nil
                        )
                        # "Gael", "captaen" are not slender
                    value = (
                        headFormPlGen.value + " " + Opers.Mutate(mutA, modForm.value)
                    )
                    plGen.append(Form(value))

            for headFormPlGen in head.plGen:
                # with article:
                if not head.isDefinite or head.allowArticledGenitive:
                    modForms = (
                        mod.plNom
                        if headFormPlGen.strength == Strength.Strong
                        else mod.sgNom
                    )
                    for modForm in modForms:
                        mutN = Mutation.Ecl1
                        if head.isImmutable:
                            mutN = Mutation.Nil
                        mutA = (
                            Mutation.Len1
                            if Opers.IsSlender(headFormPlGen.value)
                            else Mutation.Nil
                        )
                        if headFormPlGen.strength == Strength.Weak:
                            mutA = (
                                Mutation.Len1
                                if Opers.IsSlenderI(headFormPlGen.value)
                                else Mutation.Nil
                            )
                            # "Gael", "captaen" are not slender
                        value = (
                            "na "
                            + Opers.Mutate(mutN, headFormPlGen.value)
                            + " "
                            + Opers.Mutate(mutA, modForm.value)
                        )
                        plGenArt.append(Form(value))

            # endregion
            # region singular-dative
            for headFormSg in head.sgDat:
                # without article:
                for modForm in mod.sgNom:
                    mutA = (
                        Mutation.Nil
                        if headFormSg.gender == Gender.Masc
                        else Mutation.Len1
                    )
                    value = headFormSg.value + " " + Opers.Mutate(mutA, modForm.value)
                    sgDat.append(FormSg(value, headFormSg.gender))

                if not head.isDefinite:  # with article:
                    for modForm in mod.sgNom:
                        mutA = (
                            Mutation.Nil
                            if headFormSg.gender == Gender.Masc
                            else Mutation.Len1
                        )
                        value = (
                            headFormSg.value + " " + Opers.Mutate(mutA, modForm.value)
                        )
                        sgDatArtS.append(FormSg(value, headFormSg.gender))

                    for modForm in mod.sgNom:
                        value = (
                            headFormSg.value
                            + " "
                            + Opers.Mutate(Mutation.Len1, modForm.value)
                        )
                        sgDatArtN.append(FormSg(value, headFormSg.gender))

            # endregion
            # region plural-dative
            for headForm in head.plNom:
                # without article:
                for modForm in mod.plNom:
                    mutA = (
                        Mutation.Len1
                        if Opers.IsSlender(headForm.value)
                        else Mutation.Nil
                    )
                    value = headForm.value + " " + Opers.Mutate(mutA, modForm.value)
                    plDat.append(Form(value))

                if not head.isDefinite:  # with article:
                    for modForm in mod.plNom:
                        mutA = (
                            Mutation.Len1
                            if Opers.IsSlender(headForm.value)
                            else Mutation.Nil
                        )
                        value = headForm.value + " " + Opers.Mutate(mutA, modForm.value)
                        plDatArt.append(Form(value))

                # endregion
        return cls(
            sgNom=sgNom,
            sgGen=sgGen,
            sgDat=sgDat,
            sgNomArt=sgNomArt,
            sgGenArt=sgGenArt,
            sgDatArtN=sgDatArtN,
            sgDatArtS=sgDatArtS,
            plNom=plNom,
            plGen=plGen,
            plDat=plDat,
            plNomArt=plNomArt,
            plGenArt=plGenArt,
            plDatArt=plDatArt,
            isDefinite=isDefinite,
            isImmutable=isImmutable,
            forceNominative=forceNominative,
            # isPossessed=isPossessed,
        )

    # Constructor helper: Adds a possessive pronoun to sgNom, sgDat, sgGen, plNom, plDat, plGen of itself, empties all other forms:
    def _makePossessive(self, poss: Possessive) -> None:
        self.isDefinite = True
        self.isPossessed = True
        # region singular-nominative
        headFormSg: FormSg
        possForm: Form
        value: str

        for headFormSg in self.sgNom:
            # & vs && ?
            if len(poss.apos) > 0 and (
                Opers.StartsVowel(headFormSg.value)
                or Opers.StartsFVowel(headFormSg.value)
            ):
                for possForm in poss.apos:
                    value = possForm.value + Opers.Mutate(
                        poss.mutation, headFormSg.value
                    )
                    headFormSg.value = value

            else:
                for possForm in poss.full:
                    value = (
                        possForm.value
                        + " "
                        + Opers.Mutate(poss.mutation, headFormSg.value)
                    )
                    headFormSg.value = value

        # endregion
        # region singular-dative
        for headFormSg in self.sgDat:
            if len(poss.apos) > 0 and (
                Opers.StartsVowel(headFormSg.value)
                or Opers.StartsFVowel(headFormSg.value)
            ):
                for possForm in poss.apos:
                    value = possForm.value + Opers.Mutate(
                        poss.mutation, headFormSg.value
                    )
                    headFormSg.value = value

            else:
                for possForm in poss.full:
                    value = (
                        possForm.value
                        + " "
                        + Opers.Mutate(poss.mutation, headFormSg.value)
                    )
                    headFormSg.value = value

        # endregion
        # region singular-genitive
        for headFormSg in self.sgGen:
            if len(poss.apos) > 0 and (
                Opers.StartsVowel(headFormSg.value)
                or Opers.StartsFVowel(headFormSg.value)
            ):
                for possForm in poss.apos:
                    value = possForm.value + Opers.Mutate(
                        poss.mutation, headFormSg.value
                    )
                    headFormSg.value = value

            else:
                for possForm in poss.full:
                    value = (
                        possForm.value
                        + " "
                        + Opers.Mutate(poss.mutation, headFormSg.value)
                    )
                    headFormSg.value = value

        # endregion
        # region plural-nominative
        headForm: Form
        for headForm in self.plNom:
            if len(poss.apos) > 0 and (
                Opers.StartsVowel(headForm.value) or Opers.StartsFVowel(headForm.value)
            ):
                for possForm in poss.apos:
                    value = possForm.value + Opers.Mutate(poss.mutation, headForm.value)
                    headForm.value = value

            else:
                for possForm in poss.full:
                    value = (
                        possForm.value
                        + " "
                        + Opers.Mutate(poss.mutation, headForm.value)
                    )
                    headForm.value = value

        # endregion
        # region plural-dative
        for headForm in self.plDat:
            if len(poss.apos) > 0 and (
                Opers.StartsVowel(headForm.value) or Opers.StartsFVowel(headForm.value)
            ):
                for possForm in poss.apos:
                    value = possForm.value + Opers.Mutate(poss.mutation, headForm.value)
                    headForm.value = value

            else:
                for possForm in poss.full:
                    value = (
                        possForm.value
                        + " "
                        + Opers.Mutate(poss.mutation, headForm.value)
                    )
                    headForm.value = value

        # endregion
        # region plural-genitive
        headFormPlGen: Form
        for headFormPlGen in self.plGen:
            if len(poss.apos) > 0 and (
                Opers.StartsVowel(headFormPlGen.value)
                or Opers.StartsFVowel(headFormPlGen.value)
            ):
                for possForm in poss.apos:
                    value = possForm.value + Opers.Mutate(
                        poss.mutation, headFormPlGen.value
                    )
                    headFormPlGen.value = value

            else:
                for possForm in poss.full:
                    value = (
                        possForm.value
                        + " "
                        + Opers.Mutate(poss.mutation, headFormPlGen.value)
                    )
                    headFormPlGen.value = value

        # endregion
        # region empty-all-others
        self.sgDatArtN = []
        self.sgDatArtS = []
        self.sgGenArt = []
        self.sgNomArt = []
        self.plDatArt = []
        self.plGenArt = []
        self.plNomArt = []
        # endregion

    # Prints the noun phrase in BuNaMo format:
    def printXml(self) -> ET._ElementTree:
        root: ET._Element = ET.Element("nounPhrase")
        doc: ET._ElementTree = ET.ElementTree(root)
        root.set("default", self.getLemma())
        root.set("disambig", self.disambig)
        root.set("isImmutable", ("1" if self.isImmutable else "0"))
        root.set("isDefinite", ("1" if self.isDefinite else "0"))
        root.set("isPossessed", ("1" if self.isPossessed else "0"))
        root.set("forceNominative", ("1" if self.forceNominative else "0"))
        fSg: FormSg
        f: Form
        fPlGen: FormPlGen
        for fSg in self.sgNom:
            el = ET.SubElement(root, "sgNom")
            el.set("default", fSg.value)
            el.set("gender", ("masc" if fSg.gender == Gender.Masc else "fem"))

        for fSg in self.sgGen:
            el = ET.SubElement(root, "sgGen")
            el.set("default", fSg.value)
            el.set("gender", ("masc" if fSg.gender == Gender.Masc else "fem"))

        for fSg in self.sgNomArt:
            el = ET.SubElement(root, "sgNomArt")
            el.set("default", fSg.value)
            el.set("gender", ("masc" if fSg.gender == Gender.Masc else "fem"))

        for fSg in self.sgGenArt:
            el = ET.SubElement(root, "sgGenArt")
            el.set("default", fSg.value)
            el.set("gender", ("masc" if fSg.gender == Gender.Masc else "fem"))

        for f in self.plNom:
            el = ET.SubElement(root, "plNom")
            el.set("default", f.value)

        for f in self.plGen:
            el = ET.SubElement(root, "plGen")
            el.set("default", fPlGen.value)

        for f in self.plNomArt:
            el = ET.SubElement(root, "plNomArt")
            el.set("default", f.value)

        for f in self.plGenArt:
            el = ET.SubElement(root, "plGenArt")
            el.set("default", f.value)

        for fSg in self.sgDat:
            el = ET.SubElement(root, "sgDat")
            el.set("default", fSg.value)
            el.set("gender", ("masc" if fSg.gender == Gender.Masc else "fem"))

        for fSg in self.sgDatArtN:
            el = ET.SubElement(root, "sgDatArtN")
            el.set("default", fSg.value)
            el.set("gender", ("masc" if fSg.gender == Gender.Masc else "fem"))

        for fSg in self.sgDatArtS:
            el = ET.SubElement(root, "sgDatArtS")
            el.set("default", fSg.value)
            el.set("gender", ("masc" if fSg.gender == Gender.Masc else "fem"))

        for f in self.plDat:
            el = ET.SubElement(root, "plDat")
            el.set("default", f.value)

        for f in self.plDatArt:
            el = ET.SubElement(root, "plDatArt")
            el.set("default", f.value)

        return doc

    @classmethod
    def create_from_xml(cls, doc: Union[str, ET._ElementTree]) -> NP:
        if isinstance(doc, str):
            xml = ET.parse(doc)
            return cls.create_from_xml(xml)

        root = doc.getroot()
        disambig = root.get("disambig", "")
        isDefinite: bool = root.get("isDefinite") == "1"
        isPossessed: bool = root.get("isPossessed") == "1"
        isImmutable: bool = root.get("isImmutable") == "1"
        forceNominative: bool = root.get("forceNominative") == "1"
        sgNom: list[FormSg] = []
        sgNomArt: list[FormSg] = []
        sgGen: list[FormSg] = []
        sgGenArt: list[FormSg] = []
        sgDat: list[FormSg] = []
        sgDatArtN: list[FormSg] = []
        sgDatArtS: list[FormSg] = []
        plNom: list[Form] = []
        plNomArt: list[Form] = []
        plGen: list[Form] = []
        plGenArt: list[Form] = []
        plDat: list[Form] = []
        plDatArt: list[Form] = []
        el: ET._Element

        for el in root.findall("./sgNom"):
            sgNom.append(
                FormSg(
                    el.get("default", ""),
                    (Gender.Fem if el.get("gender") == "fem" else Gender.Masc),
                )
            )

        for el in root.findall("./sgGen"):
            sgGen.append(
                FormSg(
                    el.get("default", ""),
                    (Gender.Fem if el.get("gender") == "fem" else Gender.Masc),
                )
            )

        for el in root.findall("./sgNomArt"):
            sgNomArt.append(
                FormSg(
                    el.get("default", ""),
                    (Gender.Fem if el.get("gender") == "fem" else Gender.Masc),
                )
            )

        for el in root.findall("./sgGenArt"):
            sgGenArt.append(
                FormSg(
                    el.get("default", ""),
                    (Gender.Fem if el.get("gender") == "fem" else Gender.Masc),
                )
            )

        for el in root.findall("./plNom"):
            plNom.append(Form(el.get("default", "")))

        for el in root.findall("./plGen"):
            plGen.append(Form(el.get("default", "")))

        for el in root.findall("./plNomArt"):
            plNomArt.append(Form(el.get("default", "")))

        for el in root.findall("./plGenArt"):
            plGenArt.append(Form(el.get("default", "")))

        for el in root.findall("./sgDat"):
            sgDat.append(
                FormSg(
                    el.get("default", ""),
                    (Gender.Fem if el.get("gender") == "fem" else Gender.Masc),
                )
            )

        for el in root.findall("./sgDatArtN"):
            sgDatArtN.append(
                FormSg(
                    el.get("default", ""),
                    (Gender.Fem if el.get("gender") == "fem" else Gender.Masc),
                )
            )

        for el in root.findall("./sgDatArtS"):
            sgDatArtS.append(
                FormSg(
                    el.get("default", ""),
                    (Gender.Fem if el.get("gender") == "fem" else Gender.Masc),
                )
            )

        for el in root.findall("./plDat"):
            plDat.append(Form(el.get("default", "")))

        for el in root.findall("./plDatArt"):
            plDatArt.append(Form(el.get("default", "")))

        return cls(
            sgNom=sgNom,
            sgGen=sgGen,
            sgDat=sgDat,
            sgNomArt=sgNomArt,
            sgGenArt=sgGenArt,
            sgDatArtN=sgDatArtN,
            sgDatArtS=sgDatArtS,
            plNom=plNom,
            plGen=plGen,
            plDat=plDat,
            plNomArt=plNomArt,
            plGenArt=plGenArt,
            plDatArt=plDatArt,
            isDefinite=isDefinite,
            isPossessed=isPossessed,
            isImmutable=isImmutable,
            forceNominative=forceNominative,
            disambig=disambig,
        )
