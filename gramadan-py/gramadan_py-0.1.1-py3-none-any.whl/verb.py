from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union, Sequence
from enum import Enum, auto
from lxml import etree as ET
from .features import Mutation, Form, AutoName

# Enumerations used to access verb phrase forms:
class VPTense(AutoName):
    Any = auto()
    Past = auto()
    PastCont = auto()
    Pres = auto()
    PresCont = auto()
    Fut = auto()
    Cond = auto()


class VPMood(AutoName):
    Imper = auto()
    Subj = auto()


class VPShape(AutoName):
    Any = auto()
    Declar = auto()
    Interrog = auto()
    # /*, RelDep, RelIndep, Report*/ }


class VPPerson(AutoName):
    Any = auto()
    Sg1 = auto()
    Sg2 = auto()
    Sg3Masc = auto()
    Sg3Fem = auto()
    Pl1 = auto()
    Pl2 = auto()
    Pl3 = auto()
    NoSubject = auto()
    Auto = auto()


class VPPolarity(AutoName):
    Any = auto()
    Pos = auto()
    Neg = auto()


# Enumerations used to access verb forms:
class VerbTense(AutoName):
    Past = auto()
    PastCont = auto()
    Pres = auto()
    PresCont = auto()
    Fut = auto()
    Cond = auto()


class VerbMood(AutoName):
    Imper = auto()
    Subj = auto()


class VerbDependency(AutoName):
    Indep = auto()
    Dep = auto()


class VerbPerson(AutoName):
    Base = auto()
    Sg1 = auto()
    Sg2 = auto()
    Sg3 = auto()
    Pl1 = auto()
    Pl2 = auto()
    Pl3 = auto()
    Auto = auto()


M = Mutation
VT = VerbTense
VD = VerbDependency
VPN = VerbPerson

# A rule for building a tensed form of a verbal phrase from a verb:
@dataclass
class VerbTenseRule:
    # Which particle to put in front of the verb form (empty string if none):
    particle: str  # =""; PTW: cannot have a default at the front

    # Which mutation to cause on the verb form:
    mutation: Mutation  # =Mutation.Nil; PTW: cannot have a default at the front

    # Which verb form to use:
    verbTense: VerbTense
    verbDependency: VerbDependency
    verbPerson: VerbPerson

    pronoun: str = ""


TenseDictionary = dict[VerbTense, dict[VerbDependency, dict[VerbPerson, list[Form]]]]
MoodDictionary = dict[VerbMood, dict[VerbPerson, list[Form]]]
TenseRuleDictionary = dict[
    VPTense, dict[VPPerson, dict[VPShape, dict[VPPolarity, list[VerbTenseRule]]]]
]

# A verb:
class Verb:
    disambig: str = ""

    def getNickname(self) -> str:
        ret: str = self.getLemma() + " verb"
        if self.disambig != "":
            ret += " " + self.disambig
        ret = ret.replace(" ", "_")
        return ret

    # Forms of the verb:
    def __init__(
        self,
        verbalNoun: Optional[list[Form]],
        verbalAdjective: Optional[list[Form]],
        tenses: Optional[TenseDictionary] = None,
        moods: Optional[MoodDictionary] = None,
        tenseRules: Optional[TenseRuleDictionary] = None,
        disambig: str = "",
    ):
        self.verbalNoun: list[Form] = [] if verbalNoun is None else verbalNoun
        self.verbalAdjective: list[Form] = (
            [] if verbalAdjective is None else verbalAdjective
        )

        # Rules for building verbal phrases:
        if tenseRules is not None:
            self.tenseRules = tenseRules
        else:
            self._populate_tense_rules()

        # region prepare-structure-for-data
        ts: Sequence[VerbTense] = (
            VerbTense.Past,
            VerbTense.PastCont,
            VerbTense.Pres,
            VerbTense.PresCont,
            VerbTense.Fut,
            VerbTense.Cond,
        )
        ms: Sequence[VerbMood] = (VerbMood.Imper, VerbMood.Subj)
        ds: Sequence[VerbDependency] = (VerbDependency.Indep, VerbDependency.Dep)
        ps: Sequence[VerbPerson] = (
            VerbPerson.Base,
            VerbPerson.Sg1,
            VerbPerson.Sg2,
            VerbPerson.Sg3,
            VerbPerson.Pl1,
            VerbPerson.Pl2,
            VerbPerson.Pl3,
            VerbPerson.Auto,
        )

        t: VerbTense
        d: VerbDependency
        p: VerbPerson
        m: VerbMood

        if tenses is None:
            tenses = {}
            for t in ts:
                tenses[t] = {}
                for d in ds:
                    tenses[t][d] = {}
                    for p in ps:
                        tenses[t][d][p] = []
        self.tenses = tenses

        if moods is None:
            moods = {}
            for m in ms:
                moods[m] = {}
                for p in ps:
                    moods[m][p] = []
        self.moods = moods
        # endregion

        self.disambig = disambig

    # Returns tense rules that match the parameters. In each paramer, '.Any' means 'any'.
    def getTenseRules(
        self, tense: VPTense, person: VPPerson, shape: VPShape, polarity: VPPolarity
    ) -> list[VerbTenseRule]:
        ret: list[VerbTenseRule] = []
        ts: Sequence[VPTense] = (
            VPTense.Past,
            VPTense.PastCont,
            VPTense.Pres,
            VPTense.PresCont,
            VPTense.Fut,
            VPTense.Cond,
        )
        ss: Sequence[VPShape] = (
            VPShape.Declar,
            VPShape.Interrog,
        )  # /*, VPShape.RelDep, VPShape.RelIndep, VPShape.Report*/)
        pers: Sequence[VPPerson] = (
            VPPerson.Sg1,
            VPPerson.Sg2,
            VPPerson.Sg3Masc,
            VPPerson.Sg3Fem,
            VPPerson.Pl1,
            VPPerson.Pl2,
            VPPerson.Pl3,
            VPPerson.NoSubject,
            VPPerson.Auto,
        )
        pols: Sequence[VPPolarity] = (VPPolarity.Pos, VPPolarity.Neg)

        t: VPTense
        for t in ts:
            per: VPPerson
            for per in pers:
                s: VPShape
                for s in ss:
                    pol: VPPolarity
                    for pol in pols:
                        if (
                            (tense == VPTense.Any or t == tense)
                            and (person == VPPerson.Any or per == person)
                            and (shape == VPShape.Any or s == shape)
                            and (polarity == VPPolarity.Any or pol == polarity)
                        ):
                            rule: VerbTenseRule
                            for rule in self.tenseRules[t][per][s][pol]:
                                ret.append(rule)
        return ret

    # Constructor:
    def _populate_tense_rules(self) -> None:
        tenseRules: TenseRuleDictionary = {}

        # region prepare-structure-for-rules
        ts: Sequence[VPTense] = (
            VPTense.Past,
            VPTense.PastCont,
            VPTense.Pres,
            VPTense.PresCont,
            VPTense.Fut,
            VPTense.Cond,
        )
        ss: Sequence[VPShape] = (
            VPShape.Declar,
            VPShape.Interrog,
        )  # /*, VPShape.RelDep, VPShape.RelIndep, VPShape.Report*/ )
        pers: Sequence[VPPerson] = (
            VPPerson.Sg1,
            VPPerson.Sg2,
            VPPerson.Sg3Masc,
            VPPerson.Sg3Fem,
            VPPerson.Pl1,
            VPPerson.Pl2,
            VPPerson.Pl3,
            VPPerson.NoSubject,
            VPPerson.Auto,
        )
        pols: Sequence[VPPolarity] = (VPPolarity.Pos, VPPolarity.Neg)
        t: VPTense
        p: VPPerson
        per: VPPerson
        s: VPShape
        pol: VPPolarity
        for t in ts:
            tenseRules[t] = {}
            for per in pers:
                tenseRules[t][per] = {}
                for s in ss:
                    tenseRules[t][per][s] = {}
                    for pol in pols:
                        tenseRules[t][per][s][pol] = []

        # endregion
        # region default-rules
        pron: str
        dec: VPShape = VPShape.Declar
        rog: VPShape = VPShape.Interrog
        pos: VPPolarity = VPPolarity.Pos
        neg: VPPolarity = VPPolarity.Neg

        # region past
        t = VPTense.Past
        p = VPPerson.NoSubject
        # cheap, d'oscail
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.Past, VD.Indep, VPN.Base, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("níor", M.Len1, VT.Past, VD.Dep, VPN.Base, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("ar", M.Len1, VT.Past, VD.Dep, VPN.Base, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nár", M.Len1, VT.Past, VD.Dep, VPN.Base, "")
        )

        p = VPPerson.Sg1
        pron = "mé"
        # cheap mé, d'oscail mé
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.Past, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("níor", M.Len1, VT.Past, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("ar", M.Len1, VT.Past, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nár", M.Len1, VT.Past, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Sg2
        pron = "tú"
        # cheap tú, d'oscail tú
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.Past, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("níor", M.Len1, VT.Past, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("ar", M.Len1, VT.Past, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nár", M.Len1, VT.Past, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Sg3Masc
        pron = "sé"
        # cheap sé, d'oscail sé
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.Past, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("níor", M.Len1, VT.Past, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("ar", M.Len1, VT.Past, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nár", M.Len1, VT.Past, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Sg3Fem
        pron = "sí"
        # cheap sí, d'oscail sí
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.Past, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("níor", M.Len1, VT.Past, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("ar", M.Len1, VT.Past, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nár", M.Len1, VT.Past, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Pl1
        # cheapamar, d'osclaíomar
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.Past, VD.Indep, VPN.Pl1, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("níor", M.Len1, VT.Past, VD.Dep, VPN.Pl1, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("ar", M.Len1, VT.Past, VD.Dep, VPN.Pl1, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nár", M.Len1, VT.Past, VD.Dep, VPN.Pl1, "")
        )

        p = VPPerson.Pl1
        pron = "muid"
        # cheap muid, d'oscail muid
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.Past, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("níor", M.Len1, VT.Past, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("ar", M.Len1, VT.Past, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nár", M.Len1, VT.Past, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Pl2
        pron = "sibh"
        # cheap sibh, d'oscail sibh
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.Past, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("níor", M.Len1, VT.Past, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("ar", M.Len1, VT.Past, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nár", M.Len1, VT.Past, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Pl3
        pron = "siad"
        # cheap siad, d'oscail siad
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.Past, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("níor", M.Len1, VT.Past, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("ar", M.Len1, VT.Past, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nár", M.Len1, VT.Past, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Pl3
        # cheapadar, d'osclaíodar
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.Past, VD.Indep, VPN.Pl3, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("níor", M.Len1, VT.Past, VD.Dep, VPN.Pl3, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("ar", M.Len1, VT.Past, VD.Dep, VPN.Pl3, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nár", M.Len1, VT.Past, VD.Dep, VPN.Pl3, "")
        )

        p = VPPerson.Auto
        # ceapadh, osclaíodh
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.Past, VD.Indep, VPN.Auto, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("níor", M.Nil, VT.Past, VD.Dep, VPN.Auto, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("ar", M.Nil, VT.Past, VD.Dep, VPN.Auto, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nár", M.Nil, VT.Past, VD.Dep, VPN.Auto, "")
        )
        # endregion
        # region pres
        t = VPTense.Pres
        # Only 'bí' has forms in tense.
        p = VPPerson.NoSubject
        # tá
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.Pres, VD.Indep, VPN.Base, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Pres, VD.Dep, VPN.Base, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Pres, VD.Dep, VPN.Base, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Pres, VD.Dep, VPN.Base, "")
        )

        p = VPPerson.Sg1
        # táim
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.Pres, VD.Indep, VPN.Sg1, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Pres, VD.Dep, VPN.Sg1, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Pres, VD.Dep, VPN.Sg1, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Pres, VD.Dep, VPN.Sg1, "")
        )

        p = VPPerson.Sg1
        pron = "mé"
        # tá mé
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.Pres, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Pres, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Pres, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Pres, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Sg2
        pron = "tú"
        # tá tú
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.Pres, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Pres, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Pres, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Pres, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Sg3Masc
        pron = "sé"
        # tá sé
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.Pres, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Pres, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Pres, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Pres, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Sg3Fem
        pron = "sí"
        # tá sí
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.Pres, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Pres, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Pres, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Pres, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Pl1
        # táimid
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.Pres, VD.Indep, VPN.Pl1, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Pres, VD.Dep, VPN.Pl1, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Pres, VD.Dep, VPN.Pl1, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Pres, VD.Dep, VPN.Pl1, "")
        )

        p = VPPerson.Pl1
        pron = "muid"
        # tá muid
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.Pres, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Pres, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Pres, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Pres, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Pl2
        pron = "sibh"
        # tá sibh
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.Pres, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Pres, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Pres, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Pres, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Pl3
        pron = "siad"
        # tá siad
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.Pres, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Pres, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Pres, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Pres, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Auto
        # táthar
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.Pres, VD.Indep, VPN.Auto, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Pres, VD.Dep, VPN.Auto, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Pres, VD.Dep, VPN.Auto, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Pres, VD.Dep, VPN.Auto, "")
        )
        # endregion
        # region presCont
        t = VPTense.PresCont
        p = VPPerson.NoSubject
        # ceapann, osclaíonn
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.PresCont, VD.Indep, VPN.Base, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.PresCont, VD.Dep, VPN.Base, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.PresCont, VD.Dep, VPN.Base, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.PresCont, VD.Dep, VPN.Base, "")
        )

        p = VPPerson.Sg1
        # ceapaim, osclaím
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.PresCont, VD.Indep, VPN.Sg1, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.PresCont, VD.Dep, VPN.Sg1, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.PresCont, VD.Dep, VPN.Sg1, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.PresCont, VD.Dep, VPN.Sg1, "")
        )

        p = VPPerson.Sg2
        pron = "tú"
        # ceapann tú, osclaíonn tú
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.PresCont, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.PresCont, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.PresCont, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.PresCont, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Sg3Masc
        pron = "sé"
        # ceapann sé, osclaíonn sé
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.PresCont, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.PresCont, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.PresCont, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.PresCont, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Sg3Fem
        pron = "sí"
        # ceapann sí, osclaíonn sí
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.PresCont, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.PresCont, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.PresCont, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.PresCont, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Pl1
        # ceapaimid, osclaímid
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.PresCont, VD.Indep, VPN.Pl1, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.PresCont, VD.Dep, VPN.Pl1, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.PresCont, VD.Dep, VPN.Pl1, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.PresCont, VD.Dep, VPN.Pl1, "")
        )

        p = VPPerson.Pl1
        pron = "muid"
        # ceapann muid, osclaíonn muid
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.PresCont, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.PresCont, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.PresCont, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.PresCont, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Pl2
        pron = "sibh"
        # ceapann sibh, osclaíonn sibh
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.PresCont, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.PresCont, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.PresCont, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.PresCont, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Pl3
        pron = "siad"
        # ceapann siad, osclaíonn siad
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.PresCont, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.PresCont, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.PresCont, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.PresCont, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Auto
        # ceaptar, osclaítear
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.PresCont, VD.Indep, VPN.Auto, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.PresCont, VD.Dep, VPN.Auto, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.PresCont, VD.Dep, VPN.Auto, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.PresCont, VD.Dep, VPN.Auto, "")
        )
        # endregion
        # region fut
        t = VPTense.Fut
        p = VPPerson.NoSubject
        # ceapfaidh, osclóidh
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.Fut, VD.Indep, VPN.Base, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Fut, VD.Dep, VPN.Base, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Fut, VD.Dep, VPN.Base, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Fut, VD.Dep, VPN.Base, "")
        )

        p = VPPerson.Sg1
        pron = "mé"
        # ceapfaidh mé, osclóidh mé
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.Fut, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Fut, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Fut, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Fut, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Sg2
        pron = "tú"
        # ceapfaidh tú, osclóidh tú
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.Fut, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Fut, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Fut, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Fut, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Sg3Masc
        pron = "sé"
        # ceapfaidh sé, osclóidh sé
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.Fut, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Fut, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Fut, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Fut, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Sg3Fem
        pron = "sí"
        # ceapfaidh sí, osclóidh sí
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.Fut, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Fut, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Fut, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Fut, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Pl1
        # ceapfaimid, osclóimid
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.Fut, VD.Indep, VPN.Pl1, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Fut, VD.Dep, VPN.Pl1, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Fut, VD.Dep, VPN.Pl1, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Fut, VD.Dep, VPN.Pl1, "")
        )

        p = VPPerson.Pl1
        pron = "muid"
        # ceapfaidh muid, osclóidh muid
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.Fut, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Fut, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Fut, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Fut, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Pl2
        pron = "sibh"
        # ceapfaidh sibh, osclóidh sibh
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.Fut, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Fut, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Fut, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Fut, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Pl3
        pron = "siad"
        # ceapfaidh siad, osclóidh siad
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.Fut, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Fut, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Fut, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Fut, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Auto
        # ceapfar, osclófar
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Nil, VT.Fut, VD.Indep, VPN.Auto, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Fut, VD.Dep, VPN.Auto, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Fut, VD.Dep, VPN.Auto, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Fut, VD.Dep, VPN.Auto, "")
        )
        # endregion
        # region cond
        t = VPTense.Cond
        p = VPPerson.NoSubject
        # cheapfadh, d'osclódh
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.Cond, VD.Indep, VPN.Base, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Cond, VD.Dep, VPN.Base, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Cond, VD.Dep, VPN.Base, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Cond, VD.Dep, VPN.Base, "")
        )

        p = VPPerson.Sg1
        # cheapfainn, d'osclóinn
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.Cond, VD.Indep, VPN.Sg1, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Cond, VD.Dep, VPN.Sg1, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Cond, VD.Dep, VPN.Sg1, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Cond, VD.Dep, VPN.Sg1, "")
        )

        p = VPPerson.Sg2
        # cheapfá, d'osclófá
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.Cond, VD.Indep, VPN.Sg2, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Cond, VD.Dep, VPN.Sg2, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Cond, VD.Dep, VPN.Sg2, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Cond, VD.Dep, VPN.Sg2, "")
        )

        p = VPPerson.Sg3Masc
        pron = "sé"
        # cheapfadh sé, d'osclódh sé
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.Cond, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Cond, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Cond, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Cond, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Sg3Fem
        pron = "sí"
        # cheapfadh sí, d'osclódh sí
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.Cond, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Cond, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Cond, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Cond, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Pl1
        # cheapfaimis, d'osclóimis
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.Cond, VD.Indep, VPN.Pl1, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Cond, VD.Dep, VPN.Pl1, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Cond, VD.Dep, VPN.Pl1, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Cond, VD.Dep, VPN.Pl1, "")
        )

        p = VPPerson.Pl1
        pron = "muid"
        # cheapfadh muid, d'osclódh muid
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.Cond, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Cond, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Cond, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Cond, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Pl2
        pron = "sibh"
        # cheapfadh sibh, d'osclódh sibh
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.Cond, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Cond, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Cond, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Cond, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Pl3
        # cheapfaidís, d'osclóidís
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.Cond, VD.Indep, VPN.Pl3, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Cond, VD.Dep, VPN.Pl3, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Cond, VD.Dep, VPN.Pl3, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Cond, VD.Dep, VPN.Pl3, "")
        )

        p = VPPerson.Pl3
        pron = "siad"
        # cheapfadh siad, d'osclódh siad
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.Cond, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Cond, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Cond, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Cond, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Auto
        # cheapfaí, d'osclófaí
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.Cond, VD.Indep, VPN.Auto, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.Cond, VD.Dep, VPN.Auto, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.Cond, VD.Dep, VPN.Auto, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.Cond, VD.Dep, VPN.Auto, "")
        )
        # endregion
        # region pastCont
        t = VPTense.PastCont
        p = VPPerson.NoSubject
        # cheapadh, d'osclaíodh
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.PastCont, VD.Indep, VPN.Base, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.PastCont, VD.Dep, VPN.Base, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.PastCont, VD.Dep, VPN.Base, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.PastCont, VD.Dep, VPN.Base, "")
        )

        p = VPPerson.Sg1
        # cheapainn, d'osclaínn
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.PastCont, VD.Indep, VPN.Sg1, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.PastCont, VD.Dep, VPN.Sg1, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.PastCont, VD.Dep, VPN.Sg1, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.PastCont, VD.Dep, VPN.Sg1, "")
        )

        p = VPPerson.Sg2
        # cheaptá, d'osclaíteá
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.PastCont, VD.Indep, VPN.Sg2, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.PastCont, VD.Dep, VPN.Sg2, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.PastCont, VD.Dep, VPN.Sg2, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.PastCont, VD.Dep, VPN.Sg2, "")
        )

        p = VPPerson.Sg3Masc
        pron = "sé"
        # cheapadh sé, d'osclaíodh sé
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.PastCont, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.PastCont, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.PastCont, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.PastCont, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Sg3Fem
        pron = "sí"
        # cheapadh sí, d'osclaíodh sí
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.PastCont, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.PastCont, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.PastCont, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.PastCont, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Pl1
        # cheapaimis, d'osclaímis
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.PastCont, VD.Indep, VPN.Pl1, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.PastCont, VD.Dep, VPN.Pl1, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.PastCont, VD.Dep, VPN.Pl1, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.PastCont, VD.Dep, VPN.Pl1, "")
        )

        p = VPPerson.Pl1
        pron = "muid"
        # cheapadh muid, d'osclaíodh muid
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.PastCont, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.PastCont, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.PastCont, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.PastCont, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Pl2
        pron = "sibh"
        # cheapadh sibh, d'osclaíodh sibh
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.PastCont, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.PastCont, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.PastCont, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.PastCont, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Pl3
        # cheapaidís, d'osclaídís
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.PastCont, VD.Indep, VPN.Pl3, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.PastCont, VD.Dep, VPN.Pl3, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.PastCont, VD.Dep, VPN.Pl3, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.PastCont, VD.Dep, VPN.Pl3, "")
        )

        p = VPPerson.Pl3
        pron = "siad"
        # cheapadh siad, d'osclaíodh siad
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.PastCont, VD.Indep, VPN.Base, pron)
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.PastCont, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.PastCont, VD.Dep, VPN.Base, pron)
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.PastCont, VD.Dep, VPN.Base, pron)
        )

        p = VPPerson.Auto
        # cheaptaí, d'osclaítí
        tenseRules[t][p][dec][pos].append(
            VerbTenseRule("", M.Len1D, VT.PastCont, VD.Indep, VPN.Auto, "")
        )
        tenseRules[t][p][dec][neg].append(
            VerbTenseRule("ní", M.Len1, VT.PastCont, VD.Dep, VPN.Auto, "")
        )
        tenseRules[t][p][rog][pos].append(
            VerbTenseRule("an", M.Ecl1x, VT.PastCont, VD.Dep, VPN.Auto, "")
        )
        tenseRules[t][p][rog][neg].append(
            VerbTenseRule("nach", M.Ecl1, VT.PastCont, VD.Dep, VPN.Auto, "")
        )
        # endregion

        self.tenseRules = tenseRules

        # endregion

    @classmethod
    def create_from_xml(cls, doc: Union[str, ET._ElementTree]) -> Verb:
        if isinstance(doc, str):
            xml = ET.parse(doc)
            return cls.create_from_xml(xml)

        root = doc.getroot()
        disambig = root.get("disambig", "")
        verbalNoun: list[Form] = []
        verbalAdjective: list[Form] = []

        verb = cls(
            verbalNoun=verbalNoun,
            verbalAdjective=verbalAdjective,
            disambig=disambig,
        )
        tenses: TenseDictionary = verb.tenses
        moods: MoodDictionary = verb.moods

        # Helper methods to add forms quickly:
        def _addTenseDep(
            t: VerbTense, d: VerbDependency, p: VerbPerson, form: str
        ) -> None:
            tenses[t][d][p].append(Form(form))

        def _addTense(
            t: VerbTense, d: Optional[VerbDependency], p: VerbPerson, form: str
        ) -> None:
            if d:
                tenses[t][d][p].append(Form(form))
            else:
                tenses[t][VerbDependency.Indep][p].append(Form(form))
                tenses[t][VerbDependency.Dep][p].append(Form(form))

        def _addMood(m: VerbMood, p: VerbPerson, form: str) -> None:
            moods[m][p].append(Form(form))

        el: ET._Element
        value: str
        dependency: VerbDependency
        person: VerbPerson
        tense: VerbTense

        for el in root.findall("./verbalNoun"):
            verbalNoun.append(Form(el.get("default", "")))

        for el in root.findall("./verbalAdjective"):
            verbalAdjective.append(Form(el.get("default", "")))

        for el in root.findall("./tenseForm"):
            value = el.get("default", "")
            tense = VerbTense(el.get("tense"))
            dependency = VerbDependency(el.get("dependency"))
            person = VerbPerson(el.get("person"))
            _addTense(tense, dependency, person, value)

        for el in root.findall("./moodForm"):
            value = el.get("default", "")
            mood = VerbMood(el.get("mood"))
            person = VerbPerson(el.get("person"))
            _addMood(mood, person, value)

        # PTW: should the rest only happen with XML load?

        rule: VerbTenseRule
        # region change-rules-for-irregular-bí
        if verb.getLemma() == "bí":
            for rule in verb.getTenseRules(
                VPTense.Past, VPPerson.Any, VPShape.Declar, VPPolarity.Pos
            ):
                rule.mutation = Mutation.Len1

            for rule in verb.getTenseRules(
                VPTense.Past, VPPerson.Any, VPShape.Declar, VPPolarity.Neg
            ):
                rule.mutation = Mutation.Nil
                rule.particle = "ní"

            for rule in verb.getTenseRules(
                VPTense.Past, VPPerson.Any, VPShape.Interrog, VPPolarity.Pos
            ):
                rule.mutation = Mutation.Nil
                rule.particle = "an"

            for rule in verb.getTenseRules(
                VPTense.Past, VPPerson.Any, VPShape.Interrog, VPPolarity.Neg
            ):
                rule.mutation = Mutation.Nil
                rule.particle = "nach"
        # endregion
        # region change-rules-for-irregular-abair
        if verb.getLemma() == "abair":
            for rule in verb.getTenseRules(
                VPTense.Any, VPPerson.Any, VPShape.Declar, VPPolarity.Pos
            ):
                rule.mutation = Mutation.Nil

            for rule in verb.getTenseRules(
                VPTense.Any, VPPerson.Any, VPShape.Declar, VPPolarity.Neg
            ):
                rule.mutation = Mutation.Nil
                rule.particle = "ní"

            for rule in verb.getTenseRules(
                VPTense.Any, VPPerson.Any, VPShape.Interrog, VPPolarity.Pos
            ):
                rule.mutation = Mutation.Ecl1x
                rule.particle = "an"

            for rule in verb.getTenseRules(
                VPTense.Any, VPPerson.Any, VPShape.Interrog, VPPolarity.Neg
            ):
                rule.mutation = Mutation.Ecl1
                rule.particle = "nach"
        # endregion
        # region change-rules-for-irregular-déan
        if verb.getLemma() == "déan":
            for rule in verb.getTenseRules(
                VPTense.Past, VPPerson.Any, VPShape.Declar, VPPolarity.Neg
            ):
                rule.mutation = Mutation.Len1
                rule.particle = "ní"

            for rule in verb.getTenseRules(
                VPTense.Past, VPPerson.Any, VPShape.Interrog, VPPolarity.Pos
            ):
                rule.mutation = Mutation.Ecl1x
                rule.particle = "an"

            for rule in verb.getTenseRules(
                VPTense.Past, VPPerson.Any, VPShape.Interrog, VPPolarity.Neg
            ):
                rule.mutation = Mutation.Ecl1
                rule.particle = "nach"
        # endregion
        # region change-rules-for-irregular-faigh
        if verb.getLemma() == "faigh":
            for rule in verb.getTenseRules(
                VPTense.Past, VPPerson.Any, VPShape.Declar, VPPolarity.Pos
            ):
                rule.mutation = Mutation.Nil

            for rule in verb.getTenseRules(
                VPTense.Past, VPPerson.Any, VPShape.Declar, VPPolarity.Neg
            ):
                rule.mutation = Mutation.Ecl1
                rule.particle = "ní"

            for rule in verb.getTenseRules(
                VPTense.Past, VPPerson.Any, VPShape.Interrog, VPPolarity.Pos
            ):
                rule.mutation = Mutation.Ecl1x
                rule.particle = "an"

            for rule in verb.getTenseRules(
                VPTense.Past, VPPerson.Any, VPShape.Interrog, VPPolarity.Neg
            ):
                rule.mutation = Mutation.Ecl1
                rule.particle = "nach"

            for rule in verb.getTenseRules(
                VPTense.Fut, VPPerson.Any, VPShape.Declar, VPPolarity.Pos
            ):
                rule.mutation = Mutation.Len1

            for rule in verb.getTenseRules(
                VPTense.Fut, VPPerson.Any, VPShape.Declar, VPPolarity.Neg
            ):
                rule.mutation = Mutation.Ecl1
                rule.particle = "ní"

            for rule in verb.getTenseRules(
                VPTense.Fut, VPPerson.Any, VPShape.Interrog, VPPolarity.Pos
            ):
                rule.mutation = Mutation.Ecl1x
                rule.particle = "an"

            for rule in verb.getTenseRules(
                VPTense.Fut, VPPerson.Any, VPShape.Interrog, VPPolarity.Neg
            ):
                rule.mutation = Mutation.Ecl1
                rule.particle = "nach"

            for rule in verb.getTenseRules(
                VPTense.Cond, VPPerson.Any, VPShape.Declar, VPPolarity.Neg
            ):
                rule.mutation = Mutation.Ecl1
                rule.particle = "ní"
        # endregion
        # region change-rules-for-irregular-feic
        if verb.getLemma() == "feic":
            for rule in verb.getTenseRules(
                VPTense.Past, VPPerson.Any, VPShape.Declar, VPPolarity.Pos
            ):
                rule.mutation = Mutation.Len1

            for rule in verb.getTenseRules(
                VPTense.Past, VPPerson.Any, VPShape.Declar, VPPolarity.Neg
            ):
                rule.mutation = Mutation.Len1
                rule.particle = "ní"

            for rule in verb.getTenseRules(
                VPTense.Past, VPPerson.Any, VPShape.Interrog, VPPolarity.Pos
            ):
                rule.mutation = Mutation.Ecl1x
                rule.particle = "an"

            for rule in verb.getTenseRules(
                VPTense.Past, VPPerson.Any, VPShape.Interrog, VPPolarity.Neg
            ):
                rule.mutation = Mutation.Ecl1
                rule.particle = "nach"
        # endregion
        # region change-rules-for-irregular-téigh
        if verb.getLemma() == "téigh":
            for rule in verb.getTenseRules(
                VPTense.Past, VPPerson.Any, VPShape.Declar, VPPolarity.Pos
            ):
                rule.mutation = Mutation.Len1

            for rule in verb.getTenseRules(
                VPTense.Past, VPPerson.Any, VPShape.Declar, VPPolarity.Neg
            ):
                rule.mutation = Mutation.Len1
                rule.particle = "ní"

            for rule in verb.getTenseRules(
                VPTense.Past, VPPerson.Any, VPShape.Interrog, VPPolarity.Pos
            ):
                rule.mutation = Mutation.Ecl1x
                rule.particle = "an"

            for rule in verb.getTenseRules(
                VPTense.Past, VPPerson.Any, VPShape.Interrog, VPPolarity.Neg
            ):
                rule.mutation = Mutation.Ecl1
                rule.particle = "nach"
        # endregion
        # region change-rules-for-irregular-tar
        if verb.getLemma() == "tar":
            for rule in verb.getTenseRules(
                VPTense.Past, VPPerson.Auto, VPShape.Any, VPPolarity.Any
            ):
                rule.mutation = Mutation.Len1
        # endregion
        # region change-rules-for-irregular-clois
        if verb.getLemma() == "clois":
            for rule in verb.getTenseRules(
                VPTense.Past, VPPerson.Auto, VPShape.Any, VPPolarity.Any
            ):
                rule.mutation = Mutation.Len1
        # endregion
        # region change-rules-for-irregular-cluin
        if verb.getLemma() == "cluin":
            for rule in verb.getTenseRules(
                VPTense.Past, VPPerson.Auto, VPShape.Any, VPPolarity.Any
            ):
                rule.mutation = Mutation.Len1
        # endregion

        return verb

    # Extracts the verb's lemma:
    def getLemma(self) -> str:
        ret: str = ""
        # the imperative second-person singular is the lemma:
        if len(self.moods[VerbMood.Imper][VerbPerson.Sg2]) > 0:
            ret = self.moods[VerbMood.Imper][VerbPerson.Sg2][0].value
        if ret == "":
            # if not available, then the past tense base is the lemma:
            if (
                len(self.tenses[VerbTense.Past][VerbDependency.Indep][VerbPerson.Base])
                > 0
            ):
                ret = self.tenses[VerbTense.Past][VerbDependency.Indep][
                    VerbPerson.Base
                ][0].value

        return ret

    # Prints the verb in BuNaMo format:
    def printXml(self) -> ET._ElementTree:
        root: ET._Element = ET.Element("verb")
        doc: ET._ElementTree = ET.ElementTree(root)

        root.set("default", self.getLemma())
        root.set("disambig", self.disambig)

        f: Form
        for f in self.verbalNoun:
            el = ET.SubElement(root, "verbalNoun")
            el.set("default", f.value)

        for f in self.verbalAdjective:
            el = ET.SubElement(root, "verbalAdjective")
            el.set("default", f.value)

        tense: VerbTense
        dependency: VerbDependency
        person: VerbPerson

        for tense in self.tenses:
            for dependency in self.tenses[tense]:
                for person in self.tenses[tense][dependency]:
                    for f in self.tenses[tense][dependency][person]:
                        el = ET.SubElement(root, "tenseForm")
                        el.set("default", f.value)
                        el.set("tense", tense.value)
                        el.set("dependency", dependency.value)
                        el.set("person", person.value)

        mood: VerbMood
        for mood in self.moods:
            for person in self.moods[mood]:
                for f in self.moods[mood][person]:
                    el = ET.SubElement(root, "moodForm")
                    el.set("default", f.value)
                    el.set("mood", mood.value)
                    el.set("person", person.value)

        return doc
