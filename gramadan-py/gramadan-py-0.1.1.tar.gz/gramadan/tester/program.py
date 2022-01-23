from lxml import etree as ET
import sys
import os
from io import StringIO
from typing import Optional
import shutil

# This is an awful way to import Python, but it keeps us equivalent
# to the C# workflow for the moment (exception for the tester only).
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
from gramadan import *

from .testpossessives import TestPossessives
from .consistency import Consistency
from .quality_control import QualityControl


class Program:
    @classmethod
    def run(cls) -> None:
        Consistency.Nouns()
        Consistency.VerbalNouns()
        Consistency.Adjectives()
        Consistency.Similarity()
        QualityControl.AinmfhocailBearnai()
        QualityControl.AidiachtaiBearnai()
        QualityControl.BriathraInfinideachaBearnai()
        QualityControl.BriathraFinideachaBearnai()
        # #  QualityControl.AinmfhocailRegex();
        # #  QualityControl.AidiachtaiRegex();
        # #  Gadaíocht <-- no input available
        TestPossessives.PossNP()
        TestPossessives.PrepPossNP()

        if os.path.exists("NeidOutputPy"):
            shutil.rmtree("NeidOutputPy")
        os.makedirs("NeidOutputPy")

        cls.ShortTest()
        cls.FindAll()
        cls.Go()
        print("Déanta.")
        input()

    # Just quickly test something:
    @staticmethod
    def ShortTest() -> None:
        n: Noun = Noun.create_from_xml("data/noun/Gael_masc1.xml")
        adj: Adjective = Adjective.create_from_xml("data/adjective/Gaelach_adj1.xml")
        np: NP = NP.create_from_noun_adjective(n, adj)
        print(np.print())

    # Find all words that have some property:
    @staticmethod
    def FindAll() -> None:
        for fn in os.listdir("data/noun"):
            doc = ET.parse(f"data/noun/{fn}")
            noun: Noun = Noun.create_from_xml(doc)
            form: FormPlGen
            for form in noun.plGen:
                if form.strength == Strength.Weak and Opers.IsSlender(form.value):
                    print(form.value)

    # / <summary>
    # / Resaves BuNaMo entries (for example to update their file names).
    # / </summary>
    @classmethod
    def Resave(cls) -> None:
        for fn in os.listdir("data/noun"):
            doc = ET.parse(f"data/noun/{fn}")
            noun: Noun = Noun.create_from_xml(doc)
            with open("data/noun/" + noun.getNickname() + ".xml", "w") as f:
                f.write(cls.PrettyPrintXml(noun.printXml()))

        for fn in os.listdir("data/adjective"):
            doc = ET.parse(f"data/adjective/{fn}")
            adjective: Adjective = Adjective.create_from_xml(doc)
            with open("data/adjective/" + adjective.getNickname() + ".xml", "w") as f:
                f.write(cls.PrettyPrintXml(adjective.printXml()))

        for fn in os.listdir("data/nounPhrase"):
            doc = ET.parse(f"data/nounPhrase/{fn}")
            np: NP = NP.create_from_xml(doc)
            with open("data/nounPhrase/" + np.getNickname() + ".xml", "w") as f:
                f.write(cls.PrettyPrintXml(np.printXml()))

        for fn in os.listdir("data/preposition"):
            doc = ET.parse(f"data/preposition/{fn}")
            preposition: Preposition = Preposition.create_from_xml(doc)
            with open(
                "data/preposition/" + preposition.getNickname() + ".xml", "w"
            ) as f:
                f.write(cls.PrettyPrintXml(preposition.printXml()))

        for fn in os.listdir("data/verb"):
            doc = ET.parse(f"data/verb/{fn}")
            verb: Verb = Verb.create_from_xml(doc)
            with open("data/verb/" + verb.getNickname() + ".xml", "w") as f:
                f.write(cls.PrettyPrintXml(verb.printXml()))

    # / <summary>
    # / Bulk-converts BuNaMo entries from minimal format into expanded format.
    # / Outputs each entry into an individual file.
    # / </summary>
    @classmethod
    def Go(cls):
        doFilter: bool = False
        filterNicknames: list[str] = []
        # if(doFilter) filterNicknames=FilterFromNeidTrGrams();
        # if(doFilter) filterNicknames=FilterFromFile(filterNicknames);
        # NB: the nicknames returned by these have been lower-cased

        printer: PrinterNeid = PrinterNeid()
        for fn in os.listdir("data/noun"):
            doc = ET.parse(f"data/noun/{fn}")
            noun: Noun = Noun.create_from_xml(doc)
            if not doFilter or filterNicknames.Contains(noun.getNickname().ToLower()):
                with open("NeidOutputPy/" + noun.getNickname() + ".xml", "w") as f:
                    f.write(cls.PrettyPrintString(printer.printNounXml(noun)))

        for fn in os.listdir("data/adjective"):
            doc = ET.parse(f"data/adjective/{fn}")
            adjective: Adjective = Adjective.create_from_xml(doc)
            if not doFilter or filterNicknames.Contains(
                adjective.getNickname().ToLower()
            ):
                with open("NeidOutputPy/" + adjective.getNickname() + ".xml", "w") as f:
                    f.write(cls.PrettyPrintString(printer.printAdjectiveXml(adjective)))

        for fn in os.listdir("data/nounPhrase"):
            doc = ET.parse(f"data/nounPhrase/{fn}")
            np: NP = NP.create_from_xml(doc)
            if not doFilter or filterNicknames.Contains(np.getNickname().ToLower()):
                with open("NeidOutputPy/" + np.getNickname() + ".xml", "w") as f:
                    f.write(cls.PrettyPrintString(printer.printNPXml(np)))

        for fn in os.listdir("data/preposition"):
            doc = ET.parse(f"data/preposition/{fn}")
            preposition: Preposition = Preposition.create_from_xml(doc)
            if not doFilter or filterNicknames.Contains(
                preposition.getNickname().ToLower()
            ):
                with open(
                    "NeidOutputPy/" + preposition.getNickname() + ".xml", "w"
                ) as f:
                    f.write(
                        cls.PrettyPrintString(printer.printPrepositionXml(preposition))
                    )

        for fn in os.listdir("data/verb"):
            doc = ET.parse(f"data/verb/{fn}")
            verb: Verb = Verb.create_from_xml(doc)
            if not doFilter or filterNicknames.Contains(verb.getNickname().ToLower()):
                with open("NeidOutputPy/" + verb.getNickname() + ".xml", "w") as f:
                    f.write(cls.PrettyPrintString(printer.printVerbXml(verb)))

    @classmethod
    def _FilterFromFile(cls, nicknames: Optional[list[str]]) -> list[str]:
        if nicknames is None:
            nicknames = []

        with open("filter.txt", "r") as f:
            for line in f.readlines():
                line = line.strip().lower()
                if line != "" and not line in nicknames:
                    nicknames.append(line)

        return nicknames

    # PTW: TODO
    # @classmethod
    # def _FilterFromNeidTrGrams(cls) -> list[str]:
    # 	nicknames: list[str]=[]
    # 	# xmlReader.Namespaces=false;
    # 	tree = ET.parse("2D.xml"):
    # 	while(xmlReader.Read()) {
    # 		if(xmlReader.NodeType==XmlNodeType.Element && xmlReader.Name=="Entry") {
    # 			XmlDocument entry=new XmlDocument(); entry.Load(xmlReader.ReadSubtree());
    # 			foreach(XmlElement xmlTrGram in entry.SelectNodes("# TRGRAM[text()!='']")) {
    # 				string trGram=xmlTrGram.InnerText.Trim().ToLower();
    # 				if(!nicknames.Contains(trGram)) nicknames.Add(trGram);
    # 			}
    # 		}
    # 	}
    # 	return nicknames;
    # }

    # / <summary>
    # / Bulk-converts BuNaMo entries from minimal format into expanded format.
    # / Combines all entries into a single large file.
    # / </summary>
    # PTW: TODO
    # public static void GoBulk()
    # {
    # 	PrinterNeid printer=new PrinterNeid(false);
    # 	StreamWriter writer;

    # 	writer = new StreamWriter(@"../NeidOutputBulk/nouns.xml");
    # 	writer.WriteLine("<?xml version='1.0' encoding='utf-8'?>");
    # 	writer.WriteLine("<?xml-stylesheet type='text/xsl' href='!lemmas.xsl'?>");
    # 	writer.WriteLine("<lemmas>");
    # 	foreach(string file in Directory.GetFiles(@"data/noun")) {
    # 		XmlDocument doc = new XmlDocument(); doc.Load(file);
    # 		Noun noun = new Noun(doc);
    # 		writer.WriteLine(printer.printNounXml(noun));
    # 	}
    # 	writer.WriteLine("</lemmas>");
    # 	writer.Close();

    # 	writer = new StreamWriter(@"../NeidOutputBulk/nounPhrases.xml");
    # 	writer.WriteLine("<?xml version='1.0' encoding='utf-8'?>");
    # 	writer.WriteLine("<?xml-stylesheet type='text/xsl' href='!lemmas.xsl'?>");
    # 	writer.WriteLine("<lemmas>");
    # 	foreach(string file in Directory.GetFiles(@"data/nounPhrase")) {
    # 		XmlDocument doc = new XmlDocument(); doc.Load(file);
    # 		NP np = new NP(doc);
    # 		writer.WriteLine(printer.printNPXml(np));
    # 	}
    # 	writer.WriteLine("</lemmas>");
    # 	writer.Close();

    # 	writer = new StreamWriter(@"../NeidOutputBulk/adjectives.xml");
    # 	writer.WriteLine("<?xml version='1.0' encoding='utf-8'?>");
    # 	writer.WriteLine("<?xml-stylesheet type='text/xsl' href='!lemmas.xsl'?>");
    # 	writer.WriteLine("<lemmas>");
    # 	foreach(string file in Directory.GetFiles(@"data/adjective")) {
    # 		XmlDocument doc = new XmlDocument(); doc.Load(file);
    # 		Adjective a = new Adjective(doc);
    # 		writer.WriteLine(printer.printAdjectiveXml(a));
    # 	}
    # 	writer.WriteLine("</lemmas>");
    # 	writer.Close();

    # 	writer = new StreamWriter(@"../NeidOutputBulk/prepositions.xml");
    # 	writer.WriteLine("<?xml version='1.0' encoding='utf-8'?>");
    # 	writer.WriteLine("<?xml-stylesheet type='text/xsl' href='!lemmas.xsl'?>");
    # 	writer.WriteLine("<lemmas>");
    # 	foreach(string file in Directory.GetFiles(@"data/preposition")) {
    # 		XmlDocument doc = new XmlDocument(); doc.Load(file);
    # 		Preposition p = new Preposition(doc);
    # 		writer.WriteLine(printer.printPrepositionXml(p));
    # 	}
    # 	writer.WriteLine("</lemmas>");
    # 	writer.Close();

    # 	writer = new StreamWriter(@"../NeidOutputBulk/verbs.xml");
    # 	writer.WriteLine("<?xml version='1.0' encoding='utf-8'?>");
    # 	writer.WriteLine("<?xml-stylesheet type='text/xsl' href='!lemmas.xsl'?>");
    # 	writer.WriteLine("<lemmas>");
    # 	foreach(string file in Directory.GetFiles(@"data/verb")) {
    # 		XmlDocument doc=new XmlDocument(); doc.Load(file);
    # 		Verb v=new Verb(doc);
    # 		writer.WriteLine(printer.printVerbXml(v));
    # 	}
    # 	writer.WriteLine("</lemmas>");
    # 	writer.Close();
    # }

    # / <summary>
    # / Lists all entries in BuNaMo.
    # / </summary>
    # PTW: TODO
    # public static void ListAll()
    # {
    # 	StreamWriter writer=new StreamWriter(@"../listAll.txt");
    # 	foreach(string file in Directory.GetFiles(@"data/noun")) {
    # 		XmlDocument doc=new XmlDocument(); doc.Load(file);
    # 		Noun item=new Noun(doc);
    # 		writer.WriteLine("ainmfhocal\t"+item.getLemma()+"\t"+item.getNickname());
    # 	}
    # 	foreach(string file in Directory.GetFiles(@"data/nounPhrase")) {
    # 		XmlDocument doc=new XmlDocument(); doc.Load(file);
    # 		NP item=new NP(doc);
    # 		writer.WriteLine("frása ainmfhoclach\t"+item.getLemma()+"\t"+item.getNickname());
    # 	}
    # 	foreach(string file in Directory.GetFiles(@"data/adjective")) {
    # 		XmlDocument doc=new XmlDocument(); doc.Load(file);
    # 		Adjective item=new Adjective(doc);
    # 		writer.WriteLine("aidiacht\t"+item.getLemma()+"\t"+item.getNickname());
    # 	}
    # 	foreach(string file in Directory.GetFiles(@"data/verb")) {
    # 		XmlDocument doc=new XmlDocument(); doc.Load(file);
    # 		Verb item=new Verb(doc);
    # 		writer.WriteLine("briathar\t"+item.getLemma()+"\t"+item.getNickname());
    # 	}
    # 	foreach(string file in Directory.GetFiles(@"data/preposition")) {
    # 		XmlDocument doc=new XmlDocument(); doc.Load(file);
    # 		Preposition item=new Preposition(doc);
    # 		writer.WriteLine("réamhfhocal\t"+item.getLemma()+"\t"+item.getNickname());
    # 	}
    # 	writer.Close();
    # }

    @staticmethod
    def PrettyPrintXml(tree: ET._ElementTree) -> str:
        ET.indent(tree, space="  ", level=0)
        return ET.tostring(tree, xml_declaration=True).decode("utf-8")

    @staticmethod
    def PrettyPrintString(doc: str) -> str:
        return doc

    @staticmethod
    def _clean4xml(text: str) -> str:
        ret: str = text
        ret = ret.replace("&", "&amp;")
        ret = ret.replace('"', "&quot;")
        ret = ret.replace("'", "&apos;")
        ret = ret.replace("<", "&lt;")
        ret = ret.replace(">", "&gt;")
        return ret


if __name__ == "__main__":
    Program.run()
