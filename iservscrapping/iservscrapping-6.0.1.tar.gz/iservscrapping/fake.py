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

import random
import time

import requests


# pylint: disable=no-self-use
# pylint: disable=duplicate-code
# pylint: disable=too-few-public-methods


class FakeBaseIserv:
    """
    Exactly the same members as BaseIserv, but no queries are made, everything is static.
    useful for development
    when you don't want to spam the server.
    """

    # pylint: disable=too-few-public-methods

    def __init__(self, url, username, password, cache=False):
        self.username = username
        self.password = password
        self.time_to_next_substitution_request = 0
        self.url = url
        self.session = requests.Session()
        if cache:
            pass

    def login(self):
        """
        Raises:
            LoginError: The login failed.
        Sends a login request and stores the tokens in the session
        """
        time.sleep(1)


class FakeTask(FakeBaseIserv):
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

       Same as Task, but loads only fake data, no requests made. Useful for development
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
            path (:obj:`str`, optional): The path where the tests box is located.
                Defaults to /iserv/exercise/show/
        Returns:
            Task: The task filled with details
        Loads details for the task. For this, the page for that task needs to be loaded which
        is the reason that there
        is an extra function for it.
        """
        # Do something with it
        path.split("x")
        self.author = random.choice(["Mr X.", "Mrs. Y"])
        self.description = random.choice(
            ["Do this task.", "This is a fake task!", "hi pls do your task"])

        provided_files_list = []
        for _ in range(1, random.randint(2, 8)):
            filename = random.choice(
                ["coolfile.pdf", "filename with spaces", "I am a file lolä.png"])
            provided_files_dict = \
                {
                    "filename": filename,
                    "size": f"{random.randint(1, 50)}kb",
                    "link": "/path/to/the/file",
                    "description": "file description"
                }

            provided_files_list.append(provided_files_dict)
        self.provided_files = provided_files_list
        return self


class FakeIserv(FakeBaseIserv):
    """
    Exactly the same members as Iserv, but no queries are made, everything is static.
    useful for development
    when you don't want to spam the server.
    """

    def get_home(self):
        """
        Returns:
            requests.Response: The response for the main page
        Gets the main page of iserv
        """
        return "<html>This is not implemented correctly due to copyright.</html>"

    def get_untis_substitution_plan(self, path):
        """
        Args:
            path str: The path where the plan is located. Defaults to /iserv
        Returns:
            tuple: (plan dict, date str, week str) Returns the parsed plan, date and a or b week.
        Note: Make sure you have the raw plan, not a page with the plan in an iframe
        """
        path.split("x")
        return {
            "-----": [
                {
                    "course": "",
                    "room": "",
                    "subject": "BER",
                    "teacher": "XXX→XXX",
                    "text": "",
                    "time": "1",
                },
                {
                    "course": "",
                    "room": "H-1",
                    "subject": "",
                    "teacher": "XXX→XXX",
                    "text": "",
                    "time": "2/3",
                },
                {
                    "course": "",
                    "room": "A2",
                    "subject": "",
                    "teacher": "XXX→XXX",
                    "text": "",
                    "time": "4/5",
                },
            ],
            "10a": [
                {
                    "course": "10af",
                    "room": "---",
                    "subject": "RE",
                    "teacher": "XXX",
                    "text": "",
                    "time": "1 - 2",
                }
            ],
            "10b": [
                {
                    "course": "10b",
                    "room": "---",
                    "subject": "DE",
                    "teacher": "XXX",
                    "text": "",
                    "time": "5",
                },
                {
                    "course": "10b",
                    "room": "---",
                    "subject": "DE",
                    "teacher": "XXX",
                    "text": "",
                    "time": "6",
                },
            ],
            "10f": [
                {
                    "course": "10af",
                    "room": "---",
                    "subject": "RE",
                    "teacher": "XXX",
                    "text": "",
                    "time": "1 - 2",
                }
            ],
            "5c": [
                {
                    "course": "5c",
                    "room": "B1.04",
                    "subject": "PH",
                    "teacher": "XXX",
                    "text": "KA",
                    "time": "3 - 4",
                }
            ],
            "6d": [
                {
                    "course": "6d",
                    "room": "B2.04",
                    "subject": "VFG→EK",
                    "teacher": "HST→XXX",
                    "text": "",
                    "time": "2",
                }
            ],
            "8f": [
                {
                    "course": "8f",
                    "room": "PO2",
                    "subject": "CH→SN",
                    "teacher": "XXX",
                    "text": "",
                    "time": "3 - 4",
                }
            ],
            "9c": [
                {
                    "course": "9c",
                    "room": "DE2",
                    "subject": "CH→BI",
                    "teacher": "XXX→XXX",
                    "text": "",
                    "time": "1",
                },
                {
                    "course": "9c",
                    "room": "DE2",
                    "subject": "CH→BI",
                    "teacher": "XXX→XXX",
                    "text": "",
                    "time": "2",
                },
            ],
            "Q1-L2-MA-XXX": [
                {
                    "course": "Q1-L2-MA-XXX",
                    "room": "---",
                    "subject": "MA",
                    "teacher": "XXX",
                    "text": "",
                    "time": "3 - 4",
                }
            ],
            "Q1-L4-de-XXX": [
                {
                    "course": "Q1-L4-de-XXX",
                    "room": "---",
                    "subject": "DE",
                    "teacher": "XXX",
                    "text": "",
                    "time": "5 - 6",
                }
            ],
            "Q2-L2-BI-XXX": [
                {
                    "course": "Q2-L2-BI-XXX",
                    "room": "NW1→HÖ",
                    "subject": "BI",
                    "teacher": "XXX",
                    "text": "",
                    "time": "3 - 4",
                }
            ],
            "Q2-L2-MU-XXX": [
                {
                    "course": "Q2-L2-MU-XXX",
                    "room": "---",
                    "subject": "MU",
                    "teacher": "XXX",
                    "text": "",
                    "time": "3 - 4",
                }
            ],
            "Q2-L4-bi-XXX": [
                {
                    "course": "Q2-L4-bi-XXX",
                    "room": "---",
                    "subject": "BI",
                    "teacher": "XXX",
                    "text": "",
                    "time": "5 - 6",
                }
            ],
            "Q2-L4-ma-XXX": [
                {
                    "course": "Q2-L4-ma-XXX",
                    "room": "---",
                    "subject": "MA",
                    "teacher": "XXX",
                    "text": "",
                    "time": "5 - 6",
                }
            ],
        }, "3.11.2020", "A"

    def get_next_tests_formatted(self, path="/iserv"):
        """
        Args:
            path (:obj:`str`, optional): The path where the tests box is located. Defaults to /iserv
        Returns:
            list: Next tests from the box on mainpage.

        This does NOT parse the tasks into fields, it keeps the formatting and just splits
            into tests
        """
        path.split("x")
        return ['Mi, 4.11. - 11:30 - Klasse 9F\n                        - 9f Erdkunde XXX',
                'Mi, 11.11. - 09:40 - Klasse 9F\n                        - 9f Sn XXX',
                'Fr, 13.11. - 09:40 - Klasse 9F\n                        - Biologie XXX',
                'Mo, 16.11. - 09:40 - Klasse 9F\n                        - 9F GE XXX',
                'Do, 26.11. - 09:40 - Klasse 9F\n                        - 9f Ku XXX',
                'Fr, 4.12. - 11:30 - Klasse 9F\n                        - 9f PW XXX',
                'Do, 10.12. - 11:30 - Klasse 9F\n                        - 9F Mathematik 2 XXX',
                'Di, 15.12. - 11:30 - Klasse 9F\n                        - 9F Chemie XXX',
                'Fr, 18.12. - 07:50 - Klasse 9F\n                        - 9f Sn XXX']

    def get_next_tests(self, path="/iserv"):
        """
        Args:
            path (:obj:`str`, optional): The path where the tests box is located. Defaults to /iserv
        Returns:
            list: Next tests from the box on mainpage.
        """
        path.split("x")
        tests = []
        for _ in range(1, random.randint(1, 10)):
            tests.append(
                {
                    'date': random.choice(['Mi, 4.11.', 'Do, 5.11.', 'Fr, 6.11.']),
                    'time': random.choice(['11:30', '9:20', '7:50']),
                    'class': random.choice(['Klasse 9F', 'Klasse 10A', 'Klasse 5D']),
                    'subject': random.choice(['9f Erdkunde XXX', '10a Mathe XXX']) + str(
                        random.randint(1, 100))
                }
            )
        return tests

    def get_tasks(self, path="/iserv/exercise?filter[status]=current"):
        """
        Args:
            path (:obj:`str`, optional): The path where the tasks are located.
                Defaults to /iserv/exercise?filter[status]=current
        Returns:
            list: List of Task objects for current user
        """

        path.split("x")
        tasks = []

        for _ in range(0, random.randint(0, 15)):
            task = FakeTask(self.url, self.username, self.password)
            task.title = random.choice(
                ["Tasks for next week", "Hey i made a task", "Home-work tasks"])
            task.id = random.randint(1, 5000)
            task.start_date = "22.03.2020"
            task.end_date = "26.03.2020 18:00"
            task.done = random.choice([True, False])
            task.corrections = "not implemented"
            tasks.append(task)
        return tasks
