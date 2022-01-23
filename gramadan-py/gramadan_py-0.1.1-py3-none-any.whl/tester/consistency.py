import os
import re
from lxml import etree as ET

from ..noun import Noun
from ..verb import Verb
from ..adjective import Adjective


class Consistency:
    @staticmethod
    def Nouns() -> None:
        with open("consistency-report-nouns.txt", "w") as f:
            folderNames = ["noun"]

            count: int = 0
            countNoPl: int = 0

            for folderName in folderNames:
                for file in os.listdir("data/" + folderName):
                    noun: Noun = Noun.create_from_xml(f"data/{folderName}/{file}")

                    count += 1
                    if len(noun.sgNom) == 0:
                        f.write(
                            folderName
                            + "\t"
                            + noun.getNickname()
                            + "\tUatha in easnamh.\n"
                        )

                    if len(noun.sgNom) > 0 and len(noun.sgGen) == 0:
                        f.write(
                            folderName
                            + "\t"
                            + noun.getNickname()
                            + "\tGinideach uatha in easnamh.\n"
                        )

                    if len(noun.plNom) == 0:
                        countNoPl += 1

                    if len(noun.plNom) > 0 and len(noun.plGen) == 0:
                        f.write(
                            folderName
                            + "\t"
                            + noun.getNickname()
                            + "\tGinideach iolra in easnamh.\n"
                        )

            f.write("----\n")
            f.write("Iomlán:\t" + str(count) + "\n")
            f.write("Gan iolra:\t" + str(countNoPl) + "\n")

    @staticmethod
    def Adjectives() -> None:
        with open("consistency-report-adjectives.txt", "w") as f:
            folderNames = ["adjective"]

            count: int = 0

            for folderName in folderNames:
                for file in os.listdir("data/" + folderName):
                    adj: Adjective = Adjective.create_from_xml(
                        f"data/{folderName}/{file}"
                    )

                    count += 1
                    if len(adj.sgNom) == 0:
                        f.write(
                            folderName
                            + "\t"
                            + adj.getNickname()
                            + "\tUatha in easnamh.\n"
                        )

                    if len(adj.sgNom) > 0 and len(adj.sgGenMasc) == 0:
                        f.write(
                            folderName
                            + "\t"
                            + adj.getNickname()
                            + "\tGinideach uatha fir. in easnamh.\n"
                        )

                    if len(adj.sgNom) > 0 and len(adj.sgGenFem) == 0:
                        f.write(
                            folderName
                            + "\t"
                            + adj.getNickname()
                            + "\tGinideach uatha bain. in easnamh.\n"
                        )

                    if len(adj.plNom) == 0:
                        f.write(
                            folderName
                            + "\t"
                            + adj.getNickname()
                            + "\tIolra in easnamh.\n"
                        )

                    if len(adj.graded) == 0:
                        f.write(
                            folderName
                            + "\t"
                            + adj.getNickname()
                            + "\tFoirmeacha céimithe in easnamh.\n"
                        )
            f.write("----\n")
            f.write("Iomlán:\t" + str(count) + "\n")

    @staticmethod
    def Similarity() -> None:
        with open("consistency-report-similarity.txt", "w") as f:
            folderNames = ["noun", "adjective", "verb"]

            for folderName in folderNames:
                print(folderName)
                for file in os.listdir("data/" + folderName):
                    root = ET.parse(f"data/{folderName}/{file}").getroot()

                    nickname, _ = os.path.splitext(file)
                    lemma = root.xpath("./*/@default")
                    if lemma and isinstance(lemma, list) and isinstance(lemma[0], str):
                        lemmaStart = lemma[0][0:1]
                    else:
                        raise RuntimeError(
                            f"Could not find default attributes for {file}"
                        )

                    atts = root.xpath("./*/*/@default")
                    if not isinstance(atts, list):
                        raise RuntimeError(
                            f"Could not find default attributes for {file}"
                        )
                    for att in atts:
                        if not isinstance(att, str) or not att.text:
                            raise RuntimeError(f"Could not find elements for {file}")
                        if not att.startswith(lemmaStart):
                            f.write(
                                folderName
                                + "\t"
                                + nickname
                                + "\tFoirm éagosúil:\t"
                                + att
                                + "\n"
                            )

    @staticmethod
    def VerbalNouns() -> None:
        with open("consistency-vns.txt", "w") as f:
            folderNames = ["verb"]

            count: int = 0
            collector: dict[str, str] = {}

            for folderName in folderNames:
                for file in os.listdir("data/" + folderName):
                    v = Verb.create_from_xml(f"data/{folderName}/{file}")

                    if file != "féad_verb.xml" and file != "bí_verb.xml":
                        vn: str = v.verbalAdjective[0].value
                        if not vn in collector:
                            collector[vn] = v.getNickname()
                        else:
                            f.write(
                                folderName
                                + "\t"
                                + vn
                                + "\t"
                                + collector[vn]
                                + "\t"
                                + v.getNickname()
                                + "\n"
                            )
                            count += 1
            f.write("----\n")
            f.write("Iomlán:\t" + str(count) + "\n")

    @staticmethod
    def VerbalWhitespace() -> None:
        with open("consistency-whitespace.txt", "w") as f:
            folderNames = ["verb"]

            count: int = 0
            collector: dict[str, str] = {}

            for folderName in folderNames:
                for file in os.listdir("data/" + folderName):
                    root = ET.parse(f"data/{folderName}/{file}").getroot()
                    for attr in root.findall(".//*/@*"):
                        if re.search("ie", attr.text or ""):
                            f.write(f"{file}\n")

                    # writer.WriteLine(folderName+"\t"+vn+"\t"+collector[vn]+"\t"+v.getNickname());
            f.write("----\n")
            f.write("Iomlán:\t" + str(count) + "\n")
