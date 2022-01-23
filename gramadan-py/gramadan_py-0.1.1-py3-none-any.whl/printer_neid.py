import re

from .noun import Noun
from .verb import Verb
from .possessive import Possessive
from .np import NP
from .pp import PP
from .vp import VP, VPTense, VPPerson, VPPolarity, VPShape, VPMood
from .adjective import Adjective
from .preposition import Preposition
from .features import Gender, Form, Mutation
from .opers import Opers


class PrinterNeid:
    withXmlDeclarations: bool = True

    def __init__(self, withXmlDeclarations: bool = True):
        self.withXmlDeclarations = withXmlDeclarations

    def printNounXml(self, n: Noun) -> str:
        np: NP = NP.create_from_noun(n)

        ret: str = ""
        if self.withXmlDeclarations:
            ret += "<?xml version='1.0' encoding='utf-8'?>\n"
        if self.withXmlDeclarations:
            ret += "<?xml-stylesheet type='text/xsl' href='!gram.xsl'?>\n"
        ret += (
            "<Lemma lemma='"
            + self._clean4xml(n.getLemma())
            + "' uid='"
            + self._clean4xml(n.getNickname())
            + "'>\n"
        )
        ret += (
            "<noun gender='"
            + ("masc" if n.getGender() == Gender.Masc else "fem")
            + "' declension='"
            + str(n.declension)
            + "'>\n"
        )
        # Singular nominative:
        for i in range(max(len(np.sgNom), len(np.sgNomArt))):
            ret += "\t<sgNom>\n"
            if len(np.sgNom) > i:
                ret += (
                    "\t\t<articleNo>"
                    + self._clean4xml(np.sgNom[i].value)
                    + "</articleNo>\n"
                )
            if len(np.sgNomArt) > i:
                ret += (
                    "\t\t<articleYes>"
                    + self._clean4xml(np.sgNomArt[i].value)
                    + "</articleYes>\n"
                )
            ret += "\t</sgNom>\n"

        # Singular genitive:
        for i in range(max(len(np.sgGen), len(np.sgGenArt))):
            ret += "\t<sgGen>\n"
            if len(np.sgGen) > i:
                ret += (
                    "\t\t<articleNo>"
                    + self._clean4xml(np.sgGen[i].value)
                    + "</articleNo>\n"
                )
            if len(np.sgGenArt) > i:
                ret += (
                    "\t\t<articleYes>"
                    + self._clean4xml(np.sgGenArt[i].value)
                    + "</articleYes>\n"
                )
            ret += "\t</sgGen>\n"

        # Plural nominative:
        for i in range(max(len(np.plNom), len(np.plNomArt))):
            ret += "\t<plNom>\n"
            if len(np.plNom) > i:
                ret += (
                    "\t\t<articleNo>"
                    + self._clean4xml(np.plNom[i].value)
                    + "</articleNo>\n"
                )
            if len(np.plNomArt) > i:
                ret += (
                    "\t\t<articleYes>"
                    + self._clean4xml(np.plNomArt[i].value)
                    + "</articleYes>\n"
                )
            ret += "\t</plNom>\n"

        # Plural genitive:
        for i in range(max(len(np.plGen), len(np.plGenArt))):
            ret += "\t<plGen>\n"
            if len(np.plGen) > i:
                ret += (
                    "\t\t<articleNo>"
                    + self._clean4xml(np.plGen[i].value)
                    + "</articleNo>\n"
                )
            if len(np.plGenArt) > i:
                ret += (
                    "\t\t<articleYes>"
                    + self._clean4xml(np.plGenArt[i].value)
                    + "</articleYes>\n"
                )
            ret += "\t</plGen>\n"

        ret += "</noun>\n"
        ret += "</Lemma>"
        return ret

    def printAdjectiveXml(self, a: Adjective) -> str:
        ret: str = ""
        f: Form

        if self.withXmlDeclarations:
            ret += "<?xml version='1.0' encoding='utf-8'?>\n"
        if self.withXmlDeclarations:
            ret += "<?xml-stylesheet type='text/xsl' href='!gram.xsl'?>\n"
        ret += (
            "<Lemma lemma='"
            + self._clean4xml(a.getLemma())
            + "' uid='"
            + self._clean4xml(a.getNickname())
            + "'>\n"
        )
        ret += "<adjective declension='" + str(a.declension) + "'>\n"
        for f in a.sgNom:
            ret += "\t<sgNomMasc>" + self._clean4xml(f.value) + "</sgNomMasc>\n"

        for f in a.sgNom:
            ret += (
                "\t<sgNomFem>"
                + self._clean4xml(Opers.Mutate(Mutation.Len1, f.value))
                + "</sgNomFem>\n"
            )

        for f in a.sgGenMasc:
            ret += (
                "\t<sgGenMasc>"
                + self._clean4xml(Opers.Mutate(Mutation.Len1, f.value))
                + "</sgGenMasc>\n"
            )

        for f in a.sgGenFem:
            ret += "\t<sgGenFem>" + self._clean4xml(f.value) + "</sgGenFem>\n"

        for f in a.plNom:
            ret += "\t<plNom>" + self._clean4xml(f.value) + "</plNom>\n"

        for f in a.plNom:
            ret += (
                "\t<plNomSlen>"
                + self._clean4xml(Opers.Mutate(Mutation.Len1, f.value))
                + "</plNomSlen>\n"
            )

        for f in a.plNom:
            ret += "\t<plGenStrong>" + self._clean4xml(f.value) + "</plGenStrong>\n"

        for f in a.sgNom:
            ret += "\t<plGenWeak>" + self._clean4xml(f.value) + "</plGenWeak>\n"

        for f in a.getComparPres():
            ret += "\t<comparPres>" + self._clean4xml(f.value) + "</comparPres>\n"

        for f in a.getComparPast():
            ret += "\t<comparPast>" + self._clean4xml(f.value) + "</comparPast>\n"

        for f in a.getSuperPres():
            ret += "\t<superPres>" + self._clean4xml(f.value) + "</superPres>\n"

        for f in a.getSuperPast():
            ret += "\t<superPast>" + self._clean4xml(f.value) + "</superPast>\n"

        for f in a.abstractNoun:
            ret += "\t<abstractNoun>" + self._clean4xml(f.value) + "</abstractNoun>\n"

        for f in a.abstractNoun:
            ret += "\t<abstractNounExamples>\n"
            ret += (
                "\t\t<example>"
                + self._clean4xml("dá " + Opers.Mutate(Mutation.Len1, f.value))
                + "</example>\n"
            )
            if re.search("^[" + Opers.Vowels + "]", f.value):
                ret += (
                    "\t\t<example>"
                    + self._clean4xml(
                        "ag dul in " + Opers.Mutate(Mutation.Nil, f.value)
                    )
                    + "</example>\n"
                )
            else:
                ret += (
                    "\t\t<example>"
                    + self._clean4xml(
                        "ag dul i " + Opers.Mutate(Mutation.Ecl1, f.value)
                    )
                    + "</example>\n"
                )
            ret += "\t</abstractNounExamples>\n"

        ret += "</adjective>\n"
        ret += "</Lemma>"
        return ret

    def printNPXml(self, np: NP) -> str:
        ret: str = ""
        if self.withXmlDeclarations:
            ret += "<?xml version='1.0' encoding='utf-8'?>\n"
        if self.withXmlDeclarations:
            ret += "<?xml-stylesheet type='text/xsl' href='!gram.xsl'?>\n"
        ret += (
            "<Lemma lemma='"
            + self._clean4xml(np.getLemma())
            + "' uid='"
            + self._clean4xml(np.getNickname())
            + "'>\n"
        )
        ret += "<nounPhrase"
        if np.hasGender():
            ret += (
                " gender='" + ("masc" if np.getGender() == Gender.Masc else "fem") + "'"
            )
        ret += " forceNominative='" + ("1" if np.forceNominative else "0") + "'"
        ret += " isPossessed='" + ("1" if np.isPossessed else "0") + "'"
        ret += ">\n"
        # Singular nominative:
        for i in range(max(len(np.sgNom), len(np.sgNomArt))):
            ret += "\t<sgNom>\n"
            if len(np.sgNom) > i:
                ret += (
                    "\t\t<articleNo>"
                    + self._clean4xml(np.sgNom[i].value)
                    + "</articleNo>\n"
                )
            if len(np.sgNomArt) > i:
                ret += (
                    "\t\t<articleYes>"
                    + self._clean4xml(np.sgNomArt[i].value)
                    + "</articleYes>\n"
                )
            ret += "\t</sgNom>\n"

        # Singular genitive:
        for i in range(max(len(np.sgGen), len(np.sgGenArt))):
            ret += "\t<sgGen>\n"
            if len(np.sgGen) > i:
                ret += (
                    "\t\t<articleNo>"
                    + self._clean4xml(np.sgGen[i].value)
                    + "</articleNo>\n"
                )
            if len(np.sgGenArt) > i:
                ret += (
                    "\t\t<articleYes>"
                    + self._clean4xml(np.sgGenArt[i].value)
                    + "</articleYes>\n"
                )
            ret += "\t</sgGen>\n"

        # Plural nominative:
        for i in range(max(len(np.plNom), len(np.plNomArt))):
            ret += "\t<plNom>\n"
            if len(np.plNom) > i:
                ret += (
                    "\t\t<articleNo>"
                    + self._clean4xml(np.plNom[i].value)
                    + "</articleNo>\n"
                )
            if len(np.plNomArt) > i:
                ret += (
                    "\t\t<articleYes>"
                    + self._clean4xml(np.plNomArt[i].value)
                    + "</articleYes>\n"
                )
            ret += "\t</plNom>\n"

        # Plural genitive:
        for i in range(max(len(np.plGen), len(np.plGenArt))):
            ret += "\t<plGen>\n"
            if len(np.plGen) > i:
                ret += (
                    "\t\t<articleNo>"
                    + self._clean4xml(np.plGen[i].value)
                    + "</articleNo>\n"
                )
            if len(np.plGenArt) > i:
                ret += (
                    "\t\t<articleYes>"
                    + self._clean4xml(np.plGenArt[i].value)
                    + "</articleYes>\n"
                )
            ret += "\t</plGen>\n"

        ret += "</nounPhrase>\n"
        ret += "</Lemma>"
        return ret

    def printPPXml(self, pp: PP) -> str:
        ret: str = ""
        if self.withXmlDeclarations:
            ret += "<?xml version='1.0' encoding='utf-8'?>\n"
        if self.withXmlDeclarations:
            ret += "<?xml-stylesheet type='text/xsl' href='!gram.xsl'?>\n"
        ret += (
            "<Lemma lemma='"
            + self._clean4xml(pp.getLemma())
            + "' uid='"
            + self._clean4xml(pp.getNickname())
            + "'>\n"
        )
        ret += "<prepositionalPhrase>\n"
        # Singular nominative:
        for i in range(max(len(pp.sg), len(pp.sgArtS), len(pp.sgArtN))):
            ret += "\t<sg>\n"
            if len(pp.sg) > i:
                ret += (
                    "\t\t<articleNo>"
                    + self._clean4xml(pp.sg[i].value)
                    + "</articleNo>\n"
                )
            if len(pp.sgArtS) > i and len(pp.sgArtN) > i:
                if pp.sgArtS[i].value == pp.sgArtN[i].value:
                    ret += (
                        "\t\t<articleYes>"
                        + self._clean4xml(pp.sgArtS[i].value)
                        + "</articleYes>\n"
                    )
                else:
                    ret += (
                        "\t\t<articleYes var='south'>"
                        + self._clean4xml(pp.sgArtS[i].value)
                        + "</articleYes>\n"
                    )
                    ret += (
                        "\t\t<articleYes var='north'>"
                        + self._clean4xml(pp.sgArtN[i].value)
                        + "</articleYes>\n"
                    )
            else:
                if len(pp.sgArtS) > i:
                    ret += (
                        "\t\t<articleYes>"
                        + self._clean4xml(pp.sgArtS[i].value)
                        + "</articleYes>\n"
                    )
                if len(pp.sgArtN) > i:
                    ret += (
                        "\t\t<articleYes>"
                        + self._clean4xml(pp.sgArtN[i].value)
                        + "</articleYes>\n"
                    )
            ret += "\t</sg>\n"

        # Plural nominative:
        for i in range(max(len(pp.pl), len(pp.plArt))):
            ret += "\t<pl>\n"
            if len(pp.pl) > i:
                ret += (
                    "\t\t<articleNo>"
                    + self._clean4xml(pp.pl[i].value)
                    + "</articleNo>\n"
                )
            if len(pp.plArt) > i:
                ret += (
                    "\t\t<articleYes>"
                    + self._clean4xml(pp.plArt[i].value)
                    + "</articleYes>\n"
                )
            ret += "\t</pl>\n"

        ret += "</prepositionalPhrase>\n"
        ret += "</Lemma>"
        return ret

    def printPrepositionXml(self, p: Preposition) -> str:

        ret: str = ""
        if self.withXmlDeclarations:
            ret += "<?xml version='1.0' encoding='utf-8'?>\n"
        if self.withXmlDeclarations:
            ret += "<?xml-stylesheet type='text/xsl' href='!gram.xsl'?>\n"
        ret += (
            "<Lemma lemma='"
            + self._clean4xml(p.lemma)
            + "' uid='"
            + self._clean4xml(p.getNickname())
            + "'>\n"
        )
        ret += "<preposition>\n"
        # Inflected forms:
        f: Form
        for f in p.sg1:
            ret += "\t<persSg1>" + f.value + "</persSg1>\n"

        for f in p.sg2:
            ret += "\t<persSg2>" + f.value + "</persSg2>\n"

        for f in p.sg3Masc:
            ret += "\t<persSg3Masc>" + f.value + "</persSg3Masc>\n"

        for f in p.sg3Fem:
            ret += "\t<persSg3Fem>" + f.value + "</persSg3Fem>\n"

        for f in p.pl1:
            ret += "\t<persPl1>" + f.value + "</persPl1>\n"

        for f in p.pl2:
            ret += "\t<persPl2>" + f.value + "</persPl2>\n"

        for f in p.pl3:
            ret += "\t<persPl3>" + f.value + "</persPl3>\n"
        ret += "</preposition>\n"
        ret += "</Lemma>"
        return ret

    def printVerbXml(self, v: Verb) -> str:

        ret: str = ""
        if self.withXmlDeclarations:
            ret += "<?xml version='1.0' encoding='utf-8'?>\n"
        if self.withXmlDeclarations:
            ret += "<?xml-stylesheet type='text/xsl' href='!gram.xsl'?>\n"
        ret += (
            "<Lemma lemma='"
            + self._clean4xml(v.getLemma())
            + "' uid='"
            + self._clean4xml(v.getNickname())
            + "'>\n"
        )
        ret += "<verb>\n"
        f: Form
        for f in v.verbalNoun:
            ret += "\t<vn>" + self._clean4xml(f.value) + "</vn>\n"

        for f in v.verbalAdjective:
            ret += "\t<va>" + self._clean4xml(f.value) + "</va>\n"

        mapTense: dict[str, VPTense] = {}
        mapTense["past"] = VPTense.Past
        if v.getLemma() == "bí":
            mapTense["present"] = VPTense.Pres
            mapTense["presentConti"] = VPTense.PresCont
        else:
            mapTense["present"] = VPTense.PresCont
        mapTense["future"] = VPTense.Fut
        mapTense["condi"] = VPTense.Cond
        mapTense["pastConti"] = VPTense.PastCont

        mapPerson: dict[str, VPPerson] = {}
        mapPerson["sg1"] = VPPerson.Sg1
        mapPerson["sg2"] = VPPerson.Sg2
        mapPerson["sg3Masc"] = VPPerson.Sg3Masc
        mapPerson["sg3Fem"] = VPPerson.Sg3Fem
        mapPerson["pl1"] = VPPerson.Pl1
        mapPerson["pl2"] = VPPerson.Pl2
        mapPerson["pl3"] = VPPerson.Pl3
        mapPerson["auto"] = VPPerson.Auto

        vp: VP = VP.from_verb(v)

        tense: str
        mood: str
        pers: str
        for tense in mapTense:
            ret += "\t<" + tense + ">\n"
            for pers in mapPerson:
                ret += "\t\t<" + pers + ">\n"
                form: Form
                for form in vp.tenses[mapTense[tense]][VPShape.Declar][mapPerson[pers]][
                    VPPolarity.Pos
                ]:
                    ret += "\t\t\t<pos>" + self._clean4xml(form.value) + "</pos>\n"
                for form in vp.tenses[mapTense[tense]][VPShape.Interrog][
                    mapPerson[pers]
                ][VPPolarity.Pos]:
                    ret += "\t\t\t<quest>" + self._clean4xml(form.value) + "?</quest>\n"
                for form in vp.tenses[mapTense[tense]][VPShape.Declar][mapPerson[pers]][
                    VPPolarity.Neg
                ]:
                    ret += "\t\t\t<neg>" + self._clean4xml(form.value) + "</neg>\n"
                ret += "\t\t</" + pers + ">\n"
            ret += "\t</" + tense + ">\n"

        mapMood: dict[str, VPMood] = {}
        mapMood["imper"] = VPMood.Imper
        mapMood["subj"] = VPMood.Subj

        for mood in mapMood:
            ret += "\t<" + mood + ">\n"
            for pers in mapPerson:
                ret += "\t\t<" + pers + ">\n"
                for form in vp.moods[mapMood[mood]][mapPerson[pers]][VPPolarity.Pos]:
                    ret += (
                        "\t\t\t<pos>"
                        + self._clean4xml(form.value)
                        + ("!" if mapMood[mood] == VPMood.Imper else "")
                        + "</pos>\n"
                    )

                for form in vp.moods[mapMood[mood]][mapPerson[pers]][VPPolarity.Neg]:
                    ret += (
                        "\t\t\t<neg>"
                        + self._clean4xml(form.value)
                        + ("!" if mapMood[mood] == VPMood.Imper else "")
                        + "</neg>\n"
                    )
                ret += "\t\t</" + pers + ">\n"
            ret += "\t</" + mood + ">\n"

        ret += "</verb>\n"
        ret += "</Lemma>"
        return ret

    def printPossessiveXml(self, p: Possessive) -> str:
        ret: str = ""
        if self.withXmlDeclarations:
            ret += "<?xml version='1.0' encoding='utf-8'?>\n"
        if self.withXmlDeclarations:
            ret += "<?xml-stylesheet type='text/xsl' href='!gram.xsl'?>\n"
        ret += (
            "<Lemma lemma='"
            + self._clean4xml(p.getLemma())
            + "' uid='"
            + self._clean4xml(p.getNickname())
            + "'>\n"
        )
        ret += "<possessive disambig='" + p.disambig + "'>\n"
        # Forms:
        f: Form
        for f in p.full:
            ret += "\t<full>" + f.value + "</full>\n"

        for f in p.apos:
            ret += "\t<apos>" + f.value + "</apos>\n"
        ret += "</possessive>\n"
        ret += "</Lemma>"
        return ret

    def _clean4xml(self, text: str) -> str:
        ret: str = text
        ret = ret.replace("&", "&amp;")
        ret = ret.replace('"', "&quot;")
        ret = ret.replace("'", "&apos;")
        ret = ret.replace("<", "&lt;")
        ret = ret.replace(">", "&gt;")
        return ret
