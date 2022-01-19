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

from bs4 import BeautifulSoup
from iservscrapping.base import BaseIserv


class Task(BaseIserv):
    """
    Args:
        url (str): The URL to connect to without trailing slash
        username (str): The Username to login with
        password (str): The Password to login with
    Attributes:
        title (str): The title of the task
        start_date (str): The date and maybe time the task starts
        end_date (str): The date and maybe time the task ends
        done (str): Whether the task is done or not
        corrections (bool): If the task has been corrected by a teacher (broken)
        id (int): The internal ID of the task
        author (str): The user who created this task
        description (str): The description of the task
        provided_files (list): A list of files provided to solve the task

    Represents a task from the iserv task module.
    """

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=invalid-name

    def __init__(self, url, username, password):
        super().__init__(url, username, password)
        self.title = None
        self.start_date = None
        self.end_date = None
        self.done = None
        self.corrections = None
        self.id = None

        self.author = None
        self.description = None
        self.provided_files = []

    def get_details(self, path="/iserv/exercise/show/"):
        """
        Args:
            path (:obj:`str`, optional): The path where the tests box is located. Defaults to /iserv/exercise/show/
        Returns:
            Task: The task filled with details
        Loads details for the task. For this, the page for that task needs to be loaded which is the reason that there
        is an extra function for it.
        """
        res = self.session.get(self.url + path + str(self.id))
        soup = BeautifulSoup(res.text, 'lxml')
        task_rows = soup.find("table", {"class": "table"}).find_all("tr")
        task_details = []
        for row in task_rows:
            task_details.append(row.find_all("td"))
        self.author = task_details[0][0].find("a").text
        self.description = task_details[3][0].text
        try:
            provided_files = task_details[5][0].find("ul").find_all("li")
            provided_files_list = []
            for file in provided_files:
                provided_files_dict = {"filename": file.find("a").text.split("\n")[0].strip(),
                                       "size": file.find("a").text.split("\n")[1].strip(),
                                       "link": file.find("a")["href"],
                                       }
                try:
                    provided_files_dict["description"] = file.text.split("\n")[1].strip().split("-")[1].strip()
                except IndexError:
                    provided_files_dict["description"] = ""
                provided_files_list.append(provided_files_dict)
            self.provided_files = provided_files_list
        except IndexError:
            pass
        return self
