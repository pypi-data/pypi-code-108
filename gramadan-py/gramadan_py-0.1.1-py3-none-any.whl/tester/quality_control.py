import re
import os
from typing import Union
from ..noun import Noun
from ..verb import Verb, VerbTense, VerbMood, VerbPerson, VerbDependency
from ..features import Form, FormSg, FormPlGen
from ..adjective import Adjective


class QualityControl:
    @classmethod
    def AinmfhocailBearnai(cls) -> None:
        with open("ainmfhocail-bearnaí.txt", "w") as f:
            f.write(
                "fillteán" + "\t" + "leama" + "\t" + "inscne" + "\t" + "díochlaonadh"
            )
            f.write("\t" + "fadhb")
            f.write("\t" + "ginideach uatha")
            f.write("\t" + "ainmneach iolra")
            f.write("\t" + "ginideach iolra")
            f.write("\n")

            folders = ["noun"]
            for folder in folders:
                for file in (
                    file
                    for file in os.listdir("data/" + folder)
                    if file.endswith(".xml")
                ):
                    print(f"data/{folder}/{file}")
                    problem: str = ""

                    n: Noun = Noun.create_from_xml(f"data/{folder}/{file}")
                    if len(n.sgGen) == 0 and len(n.plNom) == 0 and len(n.plGen) == 0:
                        problem += ", gach foirm in easnamh"
                    else:
                        if len(n.sgNom) == 0 and len(n.sgGen) == 0:
                            problem += ", uatha in easnamh"
                        if len(n.sgNom) == 0 and len(n.sgGen) != 0:
                            problem += ", ainmneach uatha in easnamh"
                        if len(n.sgNom) != 0 and len(n.sgGen) == 0:
                            problem += ", ginideach uatha in easnamh"
                        if len(n.plNom) == 0 and len(n.plGen) == 0:
                            problem += ", iolra in easnamh"
                        if len(n.plNom) == 0 and len(n.plGen) != 0:
                            problem += ", ainmneach iolra in easnamh"
                        if len(n.plNom) != 0 and len(n.plGen) == 0:
                            problem += ", ginideach iolra in easnamh"

                    if len(problem) > 1:
                        problem = problem[2:]
                    if problem != "":
                        f.write(
                            folder
                            + "\t"
                            + n.getLemma()
                            + "\t"
                            + n.getGender().value.lower()
                            + "\t"
                            + str(n.declension)
                        )
                        f.write("\t" + problem)
                        f.write("\t" + cls._PrintForms(n.sgGen))
                        f.write("\t" + cls._PrintForms(n.plNom))
                        f.write("\t" + cls._PrintForms(n.plGen))
                        f.write("\n")

    @classmethod
    def AidiachtaiBearnai(cls) -> None:
        with open("aidiachtaí-bearnaí.txt", "w") as f:
            f.write("fillteán" + "\t" + "leama" + "\t" + "díochlaonadh")
            f.write("\t" + "fadhb")
            f.write("\t" + "ginideach firinsneach")
            f.write("\t" + "ginideach baininscneach")
            f.write("\t" + "iolra")
            f.write("\t" + "foirm chéimithe")
            f.write("\n")

            folders = ["adjective"]
            for folder in folders:
                for file in (
                    file
                    for file in os.listdir("data/" + folder)
                    if file.endswith(".xml")
                ):
                    print(f"data/{folder}/{file}")
                    problem: str = ""

                    a: Adjective = Adjective.create_from_xml(f"data/{folder}/{file}")
                    if len(a.sgGenMasc) == 0 and len(a.sgGenFem) == 0:
                        problem += ", ginideach in easnamh"
                    if len(a.sgGenMasc) != 0 and len(a.sgGenFem) == 0:
                        problem += ", ginideach baininscneach in easnamh"
                    if len(a.sgGenMasc) == 0 and len(a.sgGenFem) != 0:
                        problem += ", ginideach firinscneach in easnamh"
                    if len(a.plNom) == 0:
                        problem += ", iolra in easnamh"
                    if len(a.graded) == 0:
                        problem += ", foirm chéimithe in easnamh"

                    if len(problem) > 1:
                        problem = problem[2:]
                    if problem != "":
                        f.write(folder + "\t" + a.getLemma() + "\t" + str(a.declension))
                        f.write("\t" + problem)
                        f.write("\t" + cls._PrintForms(a.sgGenMasc))
                        f.write("\t" + cls._PrintForms(a.sgGenFem))
                        f.write("\t" + cls._PrintForms(a.plNom))
                        f.write("\t" + cls._PrintForms(a.graded))
                        f.write("\n")

    @classmethod
    def BriathraInfinideachaBearnai(cls) -> None:
        with open("briathra-infinideacha-bearnaí.txt", "w") as f:
            f.write("fillteán" + "\t" + "leama")
            f.write("\t" + "fadhb")
            f.write("\t" + "ainm briathartha")
            f.write("\t" + "aidiacht bhriathartha")
            f.write("\n")

            folders = ["verb"]
            for folder in folders:
                for file in (
                    file
                    for file in os.listdir("data/" + folder)
                    if file.endswith(".xml")
                ):
                    print(f"data/{folder}/{file}")
                    problem: str = ""

                    v: Verb = Verb.create_from_xml(f"data/{folder}/{file}")
                    if len(v.verbalNoun) == 0:
                        problem += ", ainm briathartha in easnamh"
                    if len(v.verbalAdjective) == 0:
                        problem += ", aidiacht bhriathartha in easnamh"

                    if len(problem) > 1:
                        problem = problem[2:]
                    if problem != "":
                        f.write(folder + "\t" + v.getLemma())
                        f.write("\t" + problem)
                        f.write("\t" + cls._PrintForms(v.verbalNoun))
                        f.write("\t" + cls._PrintForms(v.verbalAdjective))
                        f.write("\n")

    @classmethod
    def BriathraFinideachaBearnai(cls) -> None:
        tenses: dict[VerbTense, str] = {}
        moods: dict[VerbMood, str] = {}
        tenses[VerbTense.Past] = "aimsir chaite"
        tenses[VerbTense.PastCont] = "aimsir ghnáthchaite"
        tenses[VerbTense.PresCont] = "aimsir ghnáthláithreach"
        tenses[VerbTense.Fut] = "aimsir fháistineach"
        tenses[VerbTense.Cond] = "modh coinníollach"
        moods[VerbMood.Imper] = "modh ordaitheach"
        moods[VerbMood.Subj] = "modh foshuiteach"

        with open("briathra-finideacha-bearnaí.txt", "w") as f:
            f.write("fillteán" + "\t" + "leama" + "\t" + "aimsir/modh")
            f.write("\t" + "fadhb")
            f.write("\t" + "bunfhoirm scartha")
            f.write("\t" + "uatha 1 táite")
            f.write("\t" + "uatha 2 táite")
            f.write("\t" + "uatha 3 táite")
            f.write("\t" + "iolra 1 táite")
            f.write("\t" + "iolra 2 táite")
            f.write("\t" + "iolra 3 táite")
            f.write("\t" + "saorbhriathar")
            f.write("\n")

            folders = ["verb"]
            for folder in folders:
                for file in (
                    file
                    for file in os.listdir("data/" + folder)
                    if file.endswith(".xml")
                ):
                    print(f"data/{folder}/{file}")
                    v: Verb = Verb.create_from_xml(f"data/{folder}/{file}")

                    problem: str
                    for t in tenses:
                        problem = ""
                        if len(v.tenses[t][VerbDependency.Indep][VerbPerson.Base]) == 0:
                            problem += ", foirm scartha in easnamh"
                        if len(v.tenses[t][VerbDependency.Indep][VerbPerson.Auto]) == 0:
                            problem += ", saorbhriathar in easnamh"
                        if len(v.tenses[t][VerbDependency.Indep][VerbPerson.Pl1]) == 0:
                            problem += ", iolra 1 táite in easnamh"
                        if (
                            t == VerbTense.Past
                            or t == VerbTense.PastCont
                            or t == VerbTense.Cond
                        ):
                            if (
                                len(v.tenses[t][VerbDependency.Indep][VerbPerson.Pl3])
                                == 0
                            ):
                                problem += ", iolra 3 táite in easnamh"

                        if len(problem) > 1:
                            problem = problem[2:]
                        if problem != "":
                            f.write(folder + "\t" + v.getLemma() + "\t" + tenses[t])
                            f.write("\t" + problem)
                            f.write(
                                "\t"
                                + cls._PrintForms(
                                    v.tenses[t][VerbDependency.Indep][VerbPerson.Base]
                                )
                            )
                            f.write(
                                "\t"
                                + cls._PrintForms(
                                    v.tenses[t][VerbDependency.Indep][VerbPerson.Sg1]
                                )
                            )
                            f.write(
                                "\t"
                                + cls._PrintForms(
                                    v.tenses[t][VerbDependency.Indep][VerbPerson.Sg2]
                                )
                            )
                            f.write(
                                "\t"
                                + cls._PrintForms(
                                    v.tenses[t][VerbDependency.Indep][VerbPerson.Sg3]
                                )
                            )
                            f.write(
                                "\t"
                                + cls._PrintForms(
                                    v.tenses[t][VerbDependency.Indep][VerbPerson.Pl1]
                                )
                            )
                            f.write(
                                "\t"
                                + cls._PrintForms(
                                    v.tenses[t][VerbDependency.Indep][VerbPerson.Pl2]
                                )
                            )
                            f.write(
                                "\t"
                                + cls._PrintForms(
                                    v.tenses[t][VerbDependency.Indep][VerbPerson.Pl3]
                                )
                            )
                            f.write(
                                "\t"
                                + cls._PrintForms(
                                    v.tenses[t][VerbDependency.Indep][VerbPerson.Auto]
                                )
                            )
                            f.write("\n")

                    for m in moods:
                        problem = ""
                        if len(v.moods[m][VerbPerson.Base]) == 0:
                            problem += ", foirm scartha in easnamh"
                        if len(v.moods[m][VerbPerson.Auto]) == 0:
                            problem += ", saorbhriathar in easnamh"
                        if len(v.moods[m][VerbPerson.Pl1]) == 0:
                            problem += ", iolra 1 táite in easnamh"
                        if m == VerbMood.Imper:
                            if len(v.moods[m][VerbPerson.Pl3]) == 0:
                                problem += ", iolra 3 táite in easnamh"

                        if len(problem) > 1:
                            problem = problem[2:]
                        if problem != "":
                            f.write(folder + "\t" + v.getLemma() + "\t" + moods[m])
                            f.write("\t" + problem)
                            f.write("\t" + cls._PrintForms(v.moods[m][VerbPerson.Base]))
                            f.write("\t" + cls._PrintForms(v.moods[m][VerbPerson.Sg1]))
                            f.write("\t" + cls._PrintForms(v.moods[m][VerbPerson.Sg2]))
                            f.write("\t" + cls._PrintForms(v.moods[m][VerbPerson.Sg3]))
                            f.write("\t" + cls._PrintForms(v.moods[m][VerbPerson.Pl1]))
                            f.write("\t" + cls._PrintForms(v.moods[m][VerbPerson.Pl2]))
                            f.write("\t" + cls._PrintForms(v.moods[m][VerbPerson.Pl3]))
                            f.write("\t" + cls._PrintForms(v.moods[m][VerbPerson.Auto]))
                            f.write("\n")

    @staticmethod
    def AinmfhocailRegex(regex: str, filenameEnding: str) -> None:
        with open("ainmfhocail-" + filenameEnding + ".txt") as f:
            f.write(
                "fillteán"
                + "\t"
                + "leama"
                + "\t"
                + "inscne"
                + "\t"
                + "díochlaonadh mar atá"
                + "\t"
                + "díochlaonadh nua"
            )
            f.write("\n")

            folders = ["noun"]
            for folder in folders:
                for file in (
                    file
                    for file in os.listdir("data/" + folder)
                    if file.endswith(".xml")
                ):
                    print(f"data/{folder}/{file}")
                    n: Noun = Noun.create_from_xml(f"data/{folder}/{file}")
                    if re.search(regex, n.getLemma()):
                        f.write(
                            folder
                            + "\t"
                            + n.getLemma()
                            + "\t"
                            + n.getGender().value.lower()
                            + "\t"
                            + n.declension
                        )
                        f.write("\n")

    @staticmethod
    def AidiachtaiRegex(regex: str, filenameEnding: str) -> None:
        with open("aidiachtaí-" + filenameEnding + ".txt", "w") as f:
            f.write(
                "fillteán"
                + "\t"
                + "leama"
                + "\t"
                + "díochlaonadh"
                + "\t"
                + "díochlaonadh nua"
            )
            f.write("\n")

            folders = ["adjective"]
            for folder in folders:
                for file in (
                    file
                    for file in os.listdir("data/" + folder)
                    if file.endswith(".xml")
                ):
                    print(f"data/{folder}/{file}")
                    a: Adjective = Adjective.create_from_xml(f"data/{folder}/{file}")
                    if re.search(regex, a.getLemma()):
                        f.write(folder + "\t" + a.getLemma() + "\t" + str(a.declension))
                        f.write("\n")

    @staticmethod
    def _PrintForms(forms: Union[list[Form], list[FormSg], list[FormPlGen]]) -> str:
        ret: str = ""
        for f in forms:
            if ret != "":
                ret += " | "
            ret += f.value
        return ret
