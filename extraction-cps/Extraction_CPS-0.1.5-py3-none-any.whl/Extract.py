import os
import re
import pandas as pd
import numpy as np
import sys


class Extraction:
    """
        Extract the information in the text or latex files in a directory. No matter how many files the directory
        contains. The code will go through each folder and find the files whose format (i.e., txt or tex) defined by
        the user.
        The information can be: -Abstract -Authors -Title -Date -Thesis type -Supervisor -Advisor -Directory.

        :param directory: The directory that you want to extract information from it.
        :param format: txt or tex
        :type directory: str
    """

    def __init__(self, directory, format):
        self.directory = directory
        self.format = format
    def Extract_all_together(self):
        format = self.format.replace(".", "")
        format = f'.{format}'
        path = re.sub(r"/", r"\\", self.directory)
        Patterns_Abstract = [r"(\\begin{abstract})(?P<Abstract>.+)(\\end{abstract})",
                             r"(\\chapter{\\abstractname})(?P<Abstract>.+)(\\tableofcontents)",
                             r"(\\chapter{\\abstractname})(?P<Abstract>.+)(\\microtypesetup{protrusion=false})",
                             r"(\\chapter{Abstract})(?P<Abstract>.+)(\\tableofcontents)",
                             r"(\\section{Abstract})(?P<Abstract>.+)(\\tableofcontents)",
                             r"(\\RAIstudentthesisAbstract)({.*})(\\RAI)",
                             r"(\\section{Goal})(?P<Abstract>.+)(\\renewcommand)",
                             r"(\\addcontentsline{toc}{chapter}{Abstract})(?P<Abstract>.+)(\\cleardoublepage)",
                             r"(\\addcontentsline{toc}{chapter}{Abstract})(?P<Abstract>.+)(\\clearemptydoublepage)",
                             r"(\\RAIstudentthesisAbstract)(.*)(\\RAI)"]
        Patterns_Authors = [r"(\\author)({)(?P<Authors>.+)(})",
                            r"(\\author)({)(?P<Authors>[\w\s\n\:\-\'\{\}\"\\]*)(})",
                            r"(\\newcommand{\\getAuthor})({)(?P<Authors>.+)(})",
                            r"({.+Author.+)({)(.+)(})",
                            r"(\\RAIlangFieldOfStudyInformatics)(})(.+)({\\RAInamesProfAlthoff)",
                            r"(\\author)({)(.+)(})",
                            r"(\\author)({)(?P<Authors>.+)",
                            r"(\\authorblockN)({)(.+)(})"]
        Patterns_Title_en = [r"(\\title)({)(?P<Title_en>[\w\s\n\:\-\[\]\.\\\(\)\,]*)(})",
                             r"(\\newcommand{\\getTitle})({)(?P<Title_en>.+)(})",
                             r"(\\RAIstudentthesisTitlePageCustomBachelorsThesis)({.+}{)(?P<Title_en>.*)(}{\\RAIlangFieldOfStudyInformatics)",
                             r"(\\titleEng)({)(.+)(})"]
        Patterns_Title_de = [r"(\\titleGer)({)(?P<Title_de>.+)(})",
                             r"(\\newcommand{\\getTitleGer})({)(?P<Title_de>.+)(})",
                             r"(\\RAIstudentthesisTitlePageCustomBachelorsThesis{)(?P<Title_de>.+)(}{.*})({\\RAIlangFieldOfStudyInformatics)",
                             r"(\\title)({)(.+)(})",
                             r"(\\title)({)([\w\s\n\:\-\[\]\.\\\(\)\,\{\}]*)(\\author{)"]
        Patterns_Date = [r"(\\date)({)(?P<Date>.+)(})",
                         r"(\\newcommand{\\getSubmissionDate})({)(?P<Date>.+)(})",
                         r"({.+Submission.+)({)(.+)(})",
                         r"(\\date)({)(.+)(})"]
        # ,r"(\\RAIutilsDate)({)(.+)(})"
        Patterns_Supervisor = [r"(\\supervisor)({)(?P<supervisor>.+)(})",
                               r"(\\newcommand{\\getSupervisor})({)(?P<Supervisor>.+)(})",
                               r"({.+Supervisor.+)({)(.+)(})",
                               r"(.+Betreuer)(:)(.+)"]
        # ,r"(\\RAInamesProfAlthoff})({)(.+)(}{\\RAIutilsDate)"
        Patterns_Advisor = [r"(\\advisor)({)(?P<advisor>.+)(})",
                            r"(\\newcommand{\\getAdvisor})({)(?P<Advisor>.+)(})",
                            r"({.+Advisor.+)({)(.+)(})"]
        Patterns_ThesisType = [r"(\\doctype)({)(?P<ThesisType>.+)(})",
                               r"(\\newcommand{\\getDoctype})({)(?P<ThesisType>.+)(})",
                               r"(\\doctype)({)(.+)(})"]

        df_all = pd.DataFrame([], columns=["Directory",
                                       "Authors",
                                       "Supervisor",
                                       "Advisor",
                                       "Date",
                                       "Title_en",
                                       "Title_de",
                                       "Abstract_en",
                                       "Abstract_de"])

        number_of_students = 1
        for subdir, dirs, files in os.walk(path):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(format.lower()) or filepath.endswith(format.upper()):
                    Text = open(filepath, "r", encoding="utf-8")
                    text = Text.read()
                    text = text.replace('\\%', " percent ")
                    text = re.sub(r"(?:%.+)", '', text)
                    text = re.sub(r"\n+", '\n', text)
                    text = re.sub(r"\\Large", '', text)
                    text = text.replace('*', '')
                    for pattern in Patterns_Authors:
                        Authors = re.findall(pattern, text)
                        if Authors != []:
                            filename = filepath
                            df_all.loc[number_of_students, "Directory"] = filepath
                            break
                    for pattern in Patterns_Abstract:
                        Abstract = re.findall(pattern, text.replace("\n", " "))
                        if Abstract != []:
                            df_all.loc[number_of_students, "Abstract_en"] = \
                            Abstract[0][1].split("\chapter{Zusammenfassung}")[0].strip()
                            if np.size(Abstract[0][1].split("\chapter{Zusammenfassung}")) == 2:
                                df_all.loc[number_of_students, "Abstract_de"] = \
                                Abstract[0][1].split("\chapter{Zusammenfassung}")[1].strip()
                            if np.size(Abstract[0][1].split("\section{Inhaltsangabe}")) == 2:
                                df_all.loc[number_of_students, "Abstract_en"] = \
                                Abstract[0][1].split("\section{Inhaltsangabe}")[0].strip()
                                df_all.loc[number_of_students, "Abstract_de"] = \
                                Abstract[0][1].split("\section{Inhaltsangabe}")[1].strip()
                            if np.size(Abstract[0][1].split("\chapter{Inhaltsangabe}")) == 2:
                                df_all.loc[number_of_students, "Abstract_en"] = \
                                Abstract[0][1].split("\chapter{Inhaltsangabe}")[0].strip()
                                df_all.loc[number_of_students, "Abstract_de"] = \
                                Abstract[0][1].split("\chapter{Inhaltsangabe}")[1].strip()
                            break
                    for pattern in Patterns_Title_en:
                        Title_en = re.findall(pattern, text)
                        if Title_en != [] and filename == filepath:
                            df_all.loc[number_of_students, "Title_en"] = Title_en[0][2].strip()
                            break
                    for pattern in Patterns_Title_de:
                        Title_de = re.findall(pattern, text)
                        if Title_de != [] and filename == filepath:
                            df_all.loc[number_of_students, "Title_de"] = Title_de[0][2].strip()
                            break
                    for pattern in Patterns_Date:
                        Date = re.findall(pattern, text)
                        if Date != [] and filename == filepath:
                            df_all.loc[number_of_students, "Date"] = Date[0][2].strip()
                            break
                    for pattern in Patterns_Supervisor:
                        Supervisor = re.findall(pattern, text)
                        if Supervisor != [] and filename == filepath:
                            df_all.loc[number_of_students, "Supervisor"] = Supervisor[0][2].strip()
                            break
                    for pattern in Patterns_Advisor:
                        Advisor = re.findall(pattern, text)
                        if Advisor != [] and filename == filepath:
                            df_all.loc[number_of_students, "Advisor"] = Advisor[0][2].strip()
                            break
                    for pattern in Patterns_ThesisType:
                        ThesisType = re.findall(pattern, text)
                        if ThesisType != [] and filename == filepath:
                            df_all.loc[number_of_students, "ThesisType"] = ThesisType[0][2].strip()
                            break
                    if Abstract != [] or Authors != [] or Title_en != [] or Title_de != [] or Date != [] or Supervisor != [] or Advisor != [] or ThesisType != []:
                        if Authors != [] and Abstract == []:
                            df_all.drop(index=number_of_students, inplace=True)
                            continue
                        elif Authors == [] and Abstract != []:
                            df_all.loc[number_of_students, "Directory"] = filepath
                            df_all.loc[number_of_students, "Type"] = filepath.split("\\")[7]
                            df_all.loc[number_of_students, "Year"] = filepath.split("\\")[8]
                        number_of_students += 1
        return df_all

    def Extract_Authors(self):
        format = self.format.replace(".", "")
        format = f'.{format}'
        path = re.sub(r"/", r"\\", self.directory)
        Patterns_Authors = [r"(\\author)({)(?P<Authors>.+)(})",
                            r"(\\author)({)(?P<Authors>[\w\s\n\:\-\'\{\}\"\\]*)(})",
                            r"(\\newcommand{\\getAuthor})({)(?P<Authors>.+)(})",
                            r"({.+Author.+)({)(.+)(})",
                            r"(\\RAIlangFieldOfStudyInformatics)(})(.+)({\\RAInamesProfAlthoff)",
                            r"(\\author)({)(.+)(})",
                            r"(\\author)({)(?P<Authors>.+)",
                            r"(\\authorblockN)({)(.+)(})"]

        df_authors = pd.DataFrame([], columns=["Directory", "Authors"])

        number_of_students = 1
        for subdir, dirs, files in os.walk(path):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(format.lower()) or filepath.endswith(format.upper()):
                    Text = open(filepath, "r", encoding="utf-8")
                    text = Text.read()
                    text = text.replace('\\%', " percent ")
                    text = re.sub(r"(?:%.+)", '', text)
                    text = re.sub(r"\n+", '\n', text)
                    text = re.sub(r"\\Large", '', text)
                    text = text.replace('*', '')
                    for pattern in Patterns_Authors:
                        Authors = re.findall(pattern, text)
                        if Authors != []:
                            df_authors.loc[number_of_students, "Directory"] = filepath
                            df_authors.loc[number_of_students, "Authors"] = Authors[0][2].strip()
                            number_of_students += 1
                            break
        return df_authors

    def Extract_Abstract(self):
        format = self.format.replace(".", "")
        format = f'.{format}'
        path = re.sub(r"/", r"\\", self.directory)
        Patterns_Abstract = [r"(\\begin{abstract})(?P<Abstract>.+)(\\end{abstract})",
                             r"(\\chapter{\\abstractname})(?P<Abstract>.+)(\\microtypesetup)",
                             r"(\\chapter{Abstract})(?P<Abstract>.+)(\\tableofcontents)",
                             r"(\\section{Abstract})(?P<Abstract>.+)(\\tableofcontents)",
                             r"(\\RAIstudentthesisAbstract)({.*})(\\RAI)",
                             r"(\\section{Goal})(?P<Abstract>.+)(\\renewcommand)",
                             r"(\\addcontentsline{toc}{chapter}{Abstract})(?P<Abstract>.+)(\\cleardoublepage)",
                             r"(\\addcontentsline{toc}{chapter}{Abstract})(?P<Abstract>.+)(\\clearemptydoublepage)",
                             r"(\\RAIstudentthesisAbstract)(.*)(\\RAI)"]
        df_Abstract = pd.DataFrame([], columns=["Directory", "Abstract_en", "Abstract_de"])
        number_of_students = 1
        for subdir, dirs, files in os.walk(path):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(format.lower()) or filepath.endswith(format.upper()):
                    Text = open(filepath, "r", encoding="utf-8")
                    text = Text.read()
                    text = text.strip()
                    text = text.replace('\\%', " percent ")
                    text = text.replace('\\&', " percent ")
                    #text = re.sub(r".\\+", "", text)
                    text = re.sub(r"(?:%.+)", '', text)
                    text = re.sub(r"\n+", '\n', text)
                    text = re.sub(r"\\Large", '', text)
                    text = text.replace('*', '')
                    for pattern in Patterns_Abstract:
                        Abstract = re.findall(pattern, text.replace("\n", " "))
                        if Abstract != []:
                            df_Abstract.loc[number_of_students, "Directory"] = filepath
                            df_Abstract.loc[number_of_students, "Abstract_en"] = Abstract[0][1].split("\chapter{Zusammenfassung}")[0].strip()
                            if np.size(Abstract[0][1].split("\chapter{Zusammenfassung}")) == 2:
                                df_Abstract.loc[number_of_students, "Abstract_de"] = Abstract[0][1].split("\chapter{Zusammenfassung}")[1].strip()
                            elif np.size(Abstract[0][1].split("\section{Inhaltsangabe}")) == 2:
                                df_Abstract.loc[number_of_students, "Abstract_en"] = Abstract[0][1].split("\section{Inhaltsangabe}")[0].strip()
                                df_Abstract.loc[number_of_students, "Abstract_de"] = Abstract[0][1].split("\section{Inhaltsangabe}")[1].strip()
                            elif np.size(Abstract[0][1].split("\chapter{Inhaltsangabe}")) == 2:
                                df_Abstract.loc[number_of_students, "Abstract_en"] = Abstract[0][1].split("\chapter{Inhaltsangabe}")[0].strip()
                                df_Abstract.loc[number_of_students, "Abstract_de"] = Abstract[0][1].split("\chapter{Inhaltsangabe}")[1].strip()
                            number_of_students += 1
        return df_Abstract

    def Extract_Title_en(self):
        format = self.format.replace(".", "")
        format = f'.{format}'
        path = re.sub(r"/", r"\\", self.directory)
        Patterns_Title_en = [r"(\\title)({)(?P<Title_en>[\w\s\n\:\-\[\]\.\\\(\)\,]*)(})",
                             r"(\\newcommand{\\getTitle})({)(?P<Title_en>.+)(})",
                             r"(\\RAIstudentthesisTitlePageCustomBachelorsThesis)({.+}{)(?P<Title_en>.*)(}{\\RAIlangFieldOfStudyInformatics)",
                             r"(\\titleEng)({)(.+)(})"]

        df_title_en = pd.DataFrame([], columns=["Directory", "Title_en"])

        number_of_students = 1
        for subdir, dirs, files in os.walk(path):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(format.lower()) or filepath.endswith(format.upper()):
                    Text = open(filepath, "r", encoding="utf-8")
                    text = Text.read()
                    text = text.replace('\\%', " percent ")
                    text = re.sub(r"(?:%.+)", '', text)
                    text = re.sub(r"\n+", '\n', text)
                    text = re.sub(r"\\Large", '', text)
                    text = text.replace('*', '')
                    for pattern in Patterns_Title_en:
                        Title_en = re.findall(pattern, text)
                        if Title_en != []:
                            df_title_en.loc[number_of_students, "Title_en"] = Title_en[0][2].strip()
                            number_of_students += 1
                            break
        return df_title_en

    def Extract_Title_de(self):
        format = self.format.replace(".", "")
        format = f'.{format}'
        path = re.sub(r"/", r"\\", self.directory)
        Patterns_Title_de = [r"(\\titleGer)({)(?P<Title_de>.+)(})",
                             r"(\\newcommand{\\getTitleGer})({)(?P<Title_de>.+)(})",
                             r"(\\RAIstudentthesisTitlePageCustomBachelorsThesis{)(?P<Title_de>.+)(}{.*})({\\RAIlangFieldOfStudyInformatics)",
                             r"(\\title)({)(.+)(})",
                             r"(\\title)({)([\w\s\n\:\-\[\]\.\\\(\)\,\{\}]*)(\\author{)"]

        df_title_de = pd.DataFrame([], columns=["Directory", "Title_de"])

        number_of_students = 1
        for subdir, dirs, files in os.walk(path):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(format.lower()) or filepath.endswith(format.upper()):
                    Text = open(filepath, "r", encoding="utf-8")
                    text = Text.read()
                    text = text.replace('\\%', " percent ")
                    text = re.sub(r"(?:%.+)", '', text)
                    text = re.sub(r"\n+", '\n', text)
                    text = re.sub(r"\\Large", '', text)
                    text = text.replace('*', '')
                    for pattern in Patterns_Title_de:
                        Title_de = re.findall(pattern, text)
                        if Title_de != []:
                            df_title_de.loc[number_of_students, "Title_de"] = Title_de[0][2].strip()
                            number_of_students += 1
                            break
        return df_title_de

    def Extract_Date(self):
        format = self.format.replace(".", "")
        format = f'.{format}'
        path = re.sub(r"/", r"\\", self.directory)
        Patterns_Date = [r"(\\date)({)(?P<Date>.+)(})",
                         r"(\\newcommand{\\getSubmissionDate})({)(?P<Date>.+)(})",
                         r"({.+Submission.+)({)(.+)(})",
                         r"(\\date)({)(.+)(})"]

        df_date = pd.DataFrame([], columns=["Directory", "Date"])

        number_of_students = 1
        for subdir, dirs, files in os.walk(path):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(format.lower()) or filepath.endswith(format.upper()):
                    Text = open(filepath, "r", encoding="utf-8")
                    text = Text.read()
                    text = text.replace('\\%', " percent ")
                    text = re.sub(r"(?:%.+)", '', text)
                    text = re.sub(r"\n+", '\n', text)
                    text = re.sub(r"\\Large", '', text)
                    text = text.replace('*', '')
                    for pattern in Patterns_Date:
                        Date = re.findall(pattern, text)
                        if Date != []:
                            df_date.loc[number_of_students, "Date"] = Date[0][2].strip()
                            number_of_students += 1
                            break
        return df_date

    def Extract_Supervisor(self):
        format = self.format.replace(".", "")
        format = f'.{format}'
        path = re.sub(r"/", r"\\", self.directory)
        Patterns_Supervisor = [r"(\\supervisor)({)(?P<supervisor>.+)(})",
                               r"(\\newcommand{\\getSupervisor})({)(?P<Supervisor>.+)(})",
                               r"({.+Supervisor.+)({)(.+)(})",
                               r"(.+Betreuer)(:)(.+)"]

        df_supervisor = pd.DataFrame([], columns=["Directory", "Supervisor"])

        number_of_students = 1
        for subdir, dirs, files in os.walk(path):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(format.lower()) or filepath.endswith(format.upper()):
                    Text = open(filepath, "r", encoding="utf-8")
                    text = Text.read()
                    text = text.replace('\\%', " percent ")
                    text = re.sub(r"(?:%.+)", '', text)
                    text = re.sub(r"\n+", '\n', text)
                    text = re.sub(r"\\Large", '', text)
                    text = text.replace('*', '')
                    for pattern in Patterns_Supervisor:
                        Supervisor = re.findall(pattern, text)
                        if Supervisor != []:
                            df_supervisor.loc[number_of_students, "Supervisor"] = Supervisor[0][2].strip()
                            number_of_students += 1
                            break
        return df_supervisor

    def Extract_Advisor(self):
        format = self.format.replace(".", "")
        format = f'.{format}'
        path = re.sub(r"/", r"\\", self.directory)
        Patterns_Advisor = [r"(\\advisor)({)(?P<advisor>.+)(})",
                            r"(\\newcommand{\\getAdvisor})({)(?P<Advisor>.+)(})",
                            r"({.+Advisor.+)({)(.+)(})"]

        df_advisor = pd.DataFrame([], columns=["Directory", "Advisor"])

        number_of_students = 1
        for subdir, dirs, files in os.walk(path):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(format.lower()) or filepath.endswith(format.upper()):
                    Text = open(filepath, "r", encoding="utf-8")
                    text = Text.read()
                    text = text.replace('\\%', " percent ")
                    text = re.sub(r"(?:%.+)", '', text)
                    text = re.sub(r"\n+", '\n', text)
                    text = re.sub(r"\\Large", '', text)
                    text = text.replace('*', '')
                    for pattern in Patterns_Advisor:
                        Advisor = re.findall(pattern, text)
                        if Advisor != []:
                            df_advisor.loc[number_of_students, "Advisor"] = Advisor[0][2].strip()
                            number_of_students += 1
                            break
        return df_advisor

    def Extract_ThesisType(self):
        format = self.format.replace(".", "")
        format = f'.{format}'
        path = re.sub(r"/", r"\\", self.directory)
        Patterns_ThesisType = [r"(\\doctype)({)(?P<ThesisType>.+)(})",
                               r"(\\newcommand{\\getDoctype})({)(?P<ThesisType>.+)(})",
                               r"(\\doctype)({)(.+)(})"]

        df_ThesisType = pd.DataFrame([], columns=["Directory", "ThesisType"])

        number_of_students = 1
        for subdir, dirs, files in os.walk(path):
            for file in files:
                filepath = subdir + os.sep + file
                if filepath.endswith(format.lower()) or filepath.endswith(format.upper()):
                    Text = open(filepath, "r", encoding="utf-8")
                    text = Text.read()
                    text = text.replace('\\%', " percent ")
                    text = re.sub(r"(?:%.+)", '', text)
                    text = re.sub(r"\n+", '\n', text)
                    text = re.sub(r"\\Large", '', text)
                    text = text.replace('*', '')
                    for pattern in Patterns_ThesisType:
                        ThesisType = re.findall(pattern, text)
                        if ThesisType != []:
                            df_ThesisType.loc[number_of_students, "ThesisType"] = ThesisType[0][2].strip()
                            number_of_students += 1
                            break
        return df_ThesisType