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

from typing import List
from dataclasses import dataclass
from bs4 import BeautifulSoup


from iservscrapping.base import BaseIserv
from iservscrapping.task import Task
from iservscrapping.untis_scrapper import UntisScrapper

numbers = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]


@dataclass
class Classtest:
    """Contains data about a classtest or event
    """
    date: str
    time: str
    name: str
    course: str
    kind: str


class Iserv(BaseIserv):
    """
    The main class you will want to use most of the time. Provides all the scrapping functions.

    This inherits from :exc:`base.BaseIserv`.
    """

    def get_home(self):
        """
        Returns:
            requests.Response: The response for the main page
        Gets the main page of iserv
        """
        return self.session.get(f"{self.url}/iserv")

    def get_untis_substitution_plan(self, path):
        """
        Args:
            path str: The path where the plan is located. Defaults to /iserv
        Returns:
            tuple: (plan dict, date str, week str) Returns the parsed plan, date and a or b week.
        Note: Make sure you have the raw plan, not a page with the plan in an iframe
        """
        res = self.session.get(self.url + path)
        res.raise_for_status()
        scrapper = UntisScrapper(res.text)
        return scrapper.scrape()

    def get_next_tests_formatted(self, path="/iserv"):
        """
        Args:
            path (:obj:`str`, optional): The path where the tests box is located. Defaults to /iserv
        Returns:
            list: Next tests from the box on mainpage.

        This does NOT parse the tasks into fields, it keeps the formatting and just splits into tests
        """

        test_list = []

        res = self.session.get(self.url + path)
        soup = BeautifulSoup(res.text, 'lxml')

        tests = soup.find("ul", "pl mb0")

        for i in tests.find_all("li"):
            test_list.append(i.text)
        return test_list

    def get_next_tests(self, path="/iserv") -> List[Classtest]:
        """
        Args:
            path (:obj:`str`, optional): The path where the tests box is located. Defaults to /iserv
        Returns:
            list: Next tests from the box on mainpage.
        """
        test_list = []

        res = self.session.get(self.url + path)
        soup = BeautifulSoup(res.text, 'lxml')

        tests = soup.find("ul", "pl mb0")

        for i in tests.find_all("li"):
            parsed = i.text.split(" - ")

            title_and_kind: List[str] = parsed[3].strip().split("(")

            entry = Classtest(
                date=parsed[0].strip(),
                time=parsed[1].strip(),
                course=parsed[2].strip(),
                kind=title_and_kind.pop()[:-1],
                name="(".join(title_and_kind)
            )
            test_list.append(entry)
        return test_list

    def get_tasks(self, path="/iserv/exercise?filter[status]=current"):
        """
        Args:
            path (:obj:`str`, optional): The path where the tasks are located.
                Defaults to /iserv/exercise?filter[status]=current
        Returns:
            list: List of Task objects for current user
        """

        tasks = []

        res = self.session.get(self.url + path)
        soup = BeautifulSoup(res.text, 'lxml')
        task_table = soup.find("table", {"id": "crud-table"})
        rows = task_table.find_all("tr")
        for row in rows:
            columns = row.find_all("td")
            if len(columns) == 7:
                current_task = Task(self.url, self.username, self.password)
                current_task.title = columns[0].find("a").text
                current_task.id = int(columns[0].find("a")[
                                      "href"].split("/")[-1])
                current_task.start_date = columns[1].text
                current_task.end_date = columns[2].text
                if columns[4].find("span", {"class": "glyphicon-ok"}):
                    current_task.done = True
                else:
                    current_task.done = False
                current_task.corrections = columns[5].text
                tasks.append(current_task)
        return tasks
