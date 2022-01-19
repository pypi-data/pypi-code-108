"""
The MIT License (MIT)
Copyright (c) Alwin Lohrie (Niwla23)
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from typing import List, Tuple
from dataclasses import dataclass
import re
from bs4 import BeautifulSoup, element, Tag
from iservscrapping.errors import WrongContentError
import markdownify


@dataclass
class SubstitutionEntry:
    """Represents one row in the substitution plan"""
    time: str
    subject: str
    teacher: str
    room: str
    courses: List[str]
    text: str | None


@dataclass
class CourseHeading:
    """Represents one Course in the substitution plan and contains the rows."""
    name: str
    entrys: List[SubstitutionEntry]

@dataclass
class SubstitutionPlanMetaTable:
    """Represents information from the table at the top of the plan"""
    teachers_absent: List[str]
    courses_absent: List[str]
    blocked_rooms: List[Tuple[str, str]]
    affected_teachers: List[str]
    affected_courses: List[str]
    affected_rooms: List[str]


@dataclass
class SubstitutionPlan:
    """Represents a parsed substitution plan document"""
    # pylint: disable=too-many-instance-attributes
    courses: List[CourseHeading]
    meta_table: SubstitutionPlanMetaTable
    date: str
    week: str


class UntisScrapper:
    """
    Args:
        html (str): The HTML to parse
    Attributes:
        html (str): The HTML to parse
        soup (str): The Soup of the HTML
        content_header_list (str): Ordered list of headers to match the fields from the table
    A scrapper to parse Untis substitution plans. you will most of the time want to use
    :exc:`Iserv.get_untis_substitution_plan`
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, html: str):
        """Initializes the scraper

        Args:
            html (str): the html to parse
        """
        self.html = html
        self.soup = BeautifulSoup(html, 'lxml')
        self.content_header_list = [
            "time",
            "subject",
            "teacher",
            "text",
            "course",
            "room",
        ]

    def parse_content(self) -> List[CourseHeading]:
        """Parses the main content of the plan

        Returns:
            List[CourseHeading]: A list of CourseHeadings containing the actual data per course
        """
        current_class = "0b118b33-d1e4-4579-8055-fa5230d0c34b"
        parsed_plan = {}
        content_table: List[Tag] = list(self.soup.select_one(".mon_list"))
        for row in content_table:
            if len(row) == 6:
                parsed_row = SubstitutionEntry(
                    time="", subject="", teacher="", courses=[], room="", text=None)
                if current_class not in parsed_plan.keys():
                    parsed_plan[current_class] = CourseHeading(current_class, [])
                for i, column in enumerate(row):
                    if i == 0:
                        parsed_row.time = column.text.strip()
                    elif i == 1:
                        parsed_row.subject = markdownify.markdownify(column.decode_contents()).strip()
                    elif i == 2:
                        parsed_row.teacher = markdownify.markdownify(column.decode_contents()).strip()
                    elif i == 3:
                        parsed_row.text = markdownify.markdownify(column.decode_contents()).strip()
                    elif i == 4:
                        parsed_row.courses = column.text.strip()
                    elif i == 5:
                        parsed_row.room = markdownify.markdownify(column.decode_contents()).strip()
                parsed_plan[current_class].entrys.append(parsed_row)
            elif len(row) == 1:
                first_element = list(row)[0]
                if isinstance(first_element, element.Tag):
                    current_class = list(row)[0].text.split(" ")[0]
        try:
            del parsed_plan['0b118b33-d1e4-4579-8055-fa5230d0c34b']
        except KeyError:
            pass

        return parsed_plan

    def parse_meta_table(self) -> SubstitutionPlanMetaTable:
        """parses the meta table at the top of the plan

        Returns:
            SubstitutionPlanMetaTable: The metadata
        """
        meta_table = list(self.soup.select_one("table.info"))
        meta_table_parsed = SubstitutionPlanMetaTable(
            teachers_absent=[],
            courses_absent=[],
            blocked_rooms=[],
            affected_teachers=[],
            affected_courses=[],
            affected_rooms=[]
        )

        for row in meta_table:
            try:
                key_name = list(row)[0].text.strip()
                value_raw = list(row)[1].text.strip()
            except IndexError:
                continue
            except AttributeError:
                continue
            if key_name == "Abwesende Lehrer":
                meta_table_parsed.teachers_absent = re.findall(
                    r"(..\. \S*)[,( \()]", value_raw)
            elif key_name == "Abwesende Klassen":
                meta_table_parsed.courses_absent = re.findall(
                    r"(\S*)\s\(", value_raw)
            elif key_name == "Blockierte Räume":
                meta_table_parsed.blocked_rooms = re.findall(
                    r"(\S*)\s\((\S*)\)", value_raw)
            elif key_name == "Betroffene Lehrer":
                meta_table_parsed.affected_teachers = [
                    i.strip() for i in value_raw.split(",")]
            elif key_name == "Betroffene Klassen":
                meta_table_parsed.affected_courses = [
                    i.strip() for i in value_raw.split(",")]
            elif key_name == "Betroffene Räume":
                meta_table_parsed.affected_rooms = [
                    i.strip() for i in value_raw.split(",")]

        return meta_table_parsed

    def scrape(self) -> SubstitutionPlan:
        """Parses the whole plan with all sections.

        Raises:
            WrongContentError: The HTML passed was not in the form expected.

        Returns:
            SubstitutionPlan: The whole substitution plan
        """
        try:
            header = self.soup.select_one(".mon_title").get_text().split(" ")
            date = header[0]
            week = header[-1]

        except AttributeError as error:
            raise WrongContentError(
                "Content was not parsable."
                "Since Iserv is to dumb to throw a 404, we can only guess about this.") from error

        parsed_content = self.parse_content()
        parsed_meta_table = self.parse_meta_table()

        result = SubstitutionPlan(
            courses=parsed_content, date=date, week=week, meta_table=parsed_meta_table)

        return result
