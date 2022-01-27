"""
The Project Code
"""

import requests

from scratchlink import Exceptions
from scratchlink.Cloud import Cloud

_website = "scratch.mit.edu"
_api = f"api.{_website}"


class Project:
    def __init__(self, id):
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
        }
        self.project_id = str(id)
        self.update_data()

    def update_data(self):
        self.project_author = None
        self.project_title = None
        self.project_notes = None
        self.project_instructions = None
        self.project_are_comments_allowed = None
        self.project_stats = None
        self.project_history = None
        self.project_remix_data = None
        self.project_visibility = None
        self.project_is_public = None
        self.project_is_published = None
        self.project_thubmnail_url = None

        data = requests.get(f"https://api.scratch.mit.edu/projects/{self.project_id}/", headers=self.headers).json()
        try:
            self.project_id = data["id"]
        except KeyError:
            raise Exceptions.InvalidProject(f"The project with ID - '{self.project_id}' doesn't exist!")

        self.project_author = data["author"]
        self.project_title = data["title"]
        self.project_notes = data["description"]
        self.project_instructions = data["instructions"]
        self.project_are_comments_allowed = data["comments_allowed"] == True
        self.project_stats = data["stats"]
        self.project_history = data["history"]
        self.project_remix_data = data["remix"]
        self.project_visibility = data["visibility"]
        self.project_is_public = data["public"] == True
        self.project_is_published = data["is_published"] == True
        self.project_thubmnail_url = data["images"]

    def id(self):
        """
        Returns the project ID
        """
        return self.project_id

    def author(self):
        """
        Returns the author of the project
        """
        if self.project_author is None:
            self.update_data()
        return self.project_author

    def title(self):
        """
        Returns the title of the project
        """
        if self.title is None:
            self.update_data()
        return self.project_title

    def notes(self):
        """
        Returns the notes(Notes or Credits) of the project
        """
        if self.project_notes is None:
            self.update_data()
        return self.project_notes

    def instructions(self):
        """
        Returns the instructions of the project
        """
        if self.project_instructions is None:
            self.update_data()
        return self.project_instructions

    def are_comments_allowed(self):
        """
        Returns whether the comments are allowed in a project
        """
        if self.project_are_comments_allowed is None:
            self.update_data()
        return self.project_are_comments_allowed

    def stats(self):
        """
        Returns the stats of a project
        """
        if self.project_stats is None:
            self.update_data()
        return self.project_stats

    def history(self):
        """
        Returns the history of a project
        """
        if self.project_history is None:
            self.update_data()
        return self.project_history

    def remix_data(self):
        """
        Returns the remix data of a project
        """
        if self.project_remix_data is None:
            self.update_data()
        return self.project_remix_data

    def visibility(self):
        """
        Returns whether the project is visible
        """
        if self.project_visibility is None:
            self.update_data()
        return self.project_visibility

    def is_public(self):
        """
        Returns whether the project is public
        """
        if self.project_is_public is None:
            self.update_data()
        return self.project_is_public

    def is_published(self):
        """
        Returns whether the project is published
        """
        if self.project_is_published is None:
            self.update_data()
        return self.project_is_public

    def thumbnail_url(self):
        """
        Returns the thumbnail url of a project
        """
        if self.project_thubmnail_url is None:
            self.update_data()
        return self.project_thubmnail_url

    def assets_info(self):
        """
        Returns the Assets info of a project
        """
        return \
            requests.get(f"https://scratchdb.lefty.one/v3/project/info/{self.project_id}", headers=self.headers).json()[
                "metadata"]

    def scripts(self):
        """
        Returns the scripts of a project
        """
        return requests.get(f"https://projects.scratch.mit.edu/{self.project_id}/", headers=self.headers).json()

    def comments(self, all=False, limit=20, offset=0, comment_id=None):
        """
        Returns the list of comments of a project
        :param all: True if you want all
        :param limit: The limit
        :param offset: The offset or the data which you want after the beginning
        :param comment_id: If you want a comment from its ID then use this
        """
        if self.project_author is None:
            self.update_data()
        comments = []
        if all:
            offset = 40
            limit = 40
            while True:
                response = requests.get(
                    f"https://api.scratch.mit.edu/users/{self.project_author['username']}/projects/{str(self.project_id)}/comments/?limit={limit}&offset={offset}",
                    headers=self.headers
                ).json()
                if len(response) != 40:
                    break
                offset += 40
            comments.append(response)
        if not all:
            comments.append(requests.get(
                f"https://api.scratch.mit.edu/users/{self.project_author['username']}/projects/{str(self.project_id)}/comments/?limit={limit}&offset={offset}",
                headers=self.headers
            ).json())
        if comment_id is not None:
            comments = []
            comments.append(requests.get(
                f"https://api.scratch.mit.edu/users/{self.project_author['username']}/projects/{str(self.project_id)}/comments/{comment_id}",
                headers=self.headers
            ).json())
        return comments

    def remixes(self, all=False, limit=20, offset=0):
        """
        Returns the list of remixes of a project
        :param all: True if you want all
        :param limit: The limit
        :param offset: The offset or the data which you want after the beginning
        """
        projects = []
        if all:
            offset = 0
            while True:
                response = requests.get(
                    f"https://api.scratch.mit.edu/projects/{self.project_id}/remixes/?limit=40&offset={offset}",
                    headers=self.headers).json()
                projects += response
                if len(response) != 40:
                    break
                offset += 40
        else:
            projects.append(requests.get(
                f"https://api.scratch.mit.edu/projects/{self.project_id}/remixes/?limit={limit}&offset={offset}",
                headers=self.headers).json())
        return projects

    def _all_data(self):
        """
        DON'T USE THIS
        """
        data = {
            'Project ID': self.id(),
            'Project Name': self.title(),
            'Author': self.author()['username'],
            'Are Comments Allowed?': self.are_comments_allowed(),
            'Views': self.stats()['views'],
            'Loves': self.stats()['loves'],
            'Favourites': self.stats()['favorites'],
            'Remixes': self.stats()['remixes'],
            'Visibility': self.visibility(),
            'Is public?': self.is_public(),
            'Is published?': self.is_published(),
            'Version': self.assets_info()['version'],
            'Costumes': self.assets_info()['costumes'],
            'Blocks': self.assets_info()['blocks'],
            'Variables': self.assets_info()['variables'],
            'Assets': self.assets_info()['assets']
        }
        return data

    def pretty_print_project_data(self):
        """
        Pretty Print the Project Data
        """
        data = self._all_data()
        length = self._find_max_length(data) + 10
        print("\033[1;33;40m" + "-" * length)
        print("\033[1;35;40m" + "Data of Project with ID", str(self.project_id) + ":")
        for i in data:
            print("\t\033[1;32;40m" + i + ":", "\033[1;34;40m" + str(data[i]).replace("\n", " "))
        print("\033[1;33;40m" + "-" * length)
        print("\033[0m")

    def _find_max_length(self, d):
        """
        DON'T USE THIS
        """
        length = 0
        for i in d.values():
            if len(str(i)) > length:
                length = len(str(i))
        return length

    def link_cloud(self):
        return Cloud(project_id=self.project_id)
