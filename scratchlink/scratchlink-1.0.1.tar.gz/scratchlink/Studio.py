"""
The Studio Code
"""

import requests

from scratchlink import Exceptions

_website = "scratch.mit.edu"
_api = f"api.{_website}"


class Studio:
    def __init__(self, id):
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
        }
        self.studio_id = str(id)
        self.update_data()

    def update_data(self):
        """
        Update the studio data
        """
        self.studio_title = None
        self.studio_owner = None
        self.studio_description = None
        self.studio_visibility = None
        self.studio_are_comments_allowed = None
        self.studio_history = None
        self.studio_stats = None
        self.studio_thumbnail_url = None
        self.studio_projects = None
        self.studio_comments = None
        self.studio_curators = None
        self.studio_managers = None
        self.studio_activity = None

        data = requests.get(f"https://{_api}/studios/{self.studio_id}/", headers=self.headers).json()
        try:
            self.studio_id = data["id"]
        except KeyError:
            raise Exceptions.InvalidStudio(f"Studio with ID - '{self.studio_id}' doesn't exist!")
        self.studio_title = data["title"]
        self.studio_owner = data["host"]
        self.studio_description = data["description"]
        self.studio_visibility = data["visibility"]
        self.studio_is_public = data["public"] == True
        self.studio_is_open_to_all = data["open_to_all"] == True
        self.studio_are_comments_allowed = data["comments_allowed"] == True
        self.studio_history = data["history"]
        self.studio_stats = data["stats"]
        self.studio_thumbnail_url = data["image"]

    def id(self):
        """
        Returns the studio ID
        """
        if self.studio_id is None:
            self.update_data()
        return self.studio_id

    def title(self):
        """
        Returns the studio title
        """
        if self.studio_title is None:
            self.update_data()
        return self.studio_title

    def host_id(self):
        """
        Returns the studio owner/host ID
        """
        if self.studio_owner is None:
            self.update_data()
        return self.studio_owner

    def description(self):
        """
        Returns the studio description
        """
        if self.studio_description is None:
            self.update_data()
        return self.studio_description

    def visibility(self):
        """
        Returns the studio visibility
        """
        if self.studio_visibility is None:
            self.update_data()
        return self.studio_visibility

    def is_public(self):
        """
        Returns whether a studio is public
        """
        if self.studio_is_public is None:
            self.update_data()
        return self.studio_is_public

    def is_open_to_all(self):
        """
        Returns whether a studio is open to all
        """
        if self.studio_is_open_to_all is None:
            self.update_data()
        return self.studio_is_open_to_all

    def are_comments_allowed(self):
        """
        Returns whether a studio has comments allowed
        """
        if self.studio_are_comments_allowed is None:
            self.update_data()
        return self.studio_are_comments_allowed

    def history(self):
        """
        Returns the history of the studio
        """
        if self.studio_history is None:
            self.update_data()
        return self.studio_history

    def stats(self):
        """
        Returns the stats of the studio
        """
        if self.studio_stats is None:
            self.update_data()
        return self.studio_stats

    def thumbnail_url(self):
        """
        Returns the thumbnail URL of the studio
        """
        if self.studio_thumbnail_url is None:
            self.update_data()
        return self.studio_thumbnail_url

    def projects(self, all=False, limit=20, offset=0):
        """
        Get the projects of the studio
        :param all: If you want all the projects then set it to True
        :param limit: The limit
        :param offset: The offset or the number of data you want from the beginning
        """
        if self.studio_projects is None:
            projects = []
            if all:
                limit = 40
                offset = 0
                while True:
                    response = requests.get(
                        f"https://api.scratch.mit.edu/studios/{self.studio_id}/projects/?limit={limit}&offset={offset}",
                        headers=self.headers).json()
                    projects.append(response)
                    offset += 40
                    if len(response) != 40:
                        break
            if not all:
                projects.append(requests.get(
                    f"https://api.scratch.mit.edu/studios/{self.studio_id}/projects/?limit={limit}&offset={offset}",
                    headers=self.headers).json())
            self.studio_projects = projects
        return self.studio_projects

    def comments(self, all=False, limit=20, offset=0):
        """
        Get the comments of the studio
        :param all: If you want all the comments then set it to True
        :param limit: The limit
        :param offset: The offset or the number of data you want from the beginning
        """
        if self.studio_comments is None:
            comments = []
            if all:
                limit = 40
                offset = 0
                while True:
                    response = requests.get(
                        f"https://api.scratch.mit.edu/studios/{self.studio_id}/comments/?limit={limit}&offset={offset}",
                        headers=self.headers).json()
                    comments.append(response)
                    offset += 40
                    if len(response) != 40:
                        break
            if not all:
                comments.append(requests.get(
                    f"https://api.scratch.mit.edu/studios/{self.studio_id}/comments/?limit={limit}&offset={offset}",
                    headers=self.headers).json())
            self.studio_comments = comments
        return self.studio_comments

    def curators(self, all=False, limit=20, offset=0):
        """
        Get the curators of the studio
        :param all: If you want all the curators then set it to True
        :param limit: The limit
        :param offset: The offset or the number of data you want from the beginning
        """
        if self.studio_curators is None:
            curators = []
            if all:
                limit = 40
                offset = 0
                while True:
                    response = requests.get(
                        f"https://api.scratch.mit.edu/studios/{self.studio_id}/curators/?limit={limit}&offset={offset}",
                        headers=self.headers).json()
                    curators.append(response)
                    offset += 40
                    if len(response) != 40:
                        break
            if not all:
                curators.append(requests.get(
                    f"https://api.scratch.mit.edu/studios/{self.studio_id}/curators/?limit={limit}&offset={offset}",
                    headers=self.headers).json())
            self.studio_curators = curators
        return self.studio_curators

    def managers(self, all=False, limit=20, offset=0):
        """
        Get the managers of the studio
        :param all: If you want all the managers then set it to True
        :param limit: The limit
        :param offset: The offset or the number of data you want from the beginning
        """
        if self.studio_managers is None:
            managers = []
            if all:
                limit = 40
                offset = 0
                while True:
                    response = requests.get(
                        f"https://api.scratch.mit.edu/studios/{self.studio_id}/managers/?limit={limit}&offset={offset}",
                        headers=self.headers).json()
                    managers.append(response)
                    offset += 40
                    if len(response) != 40:
                        break
            if not all:
                managers.append(requests.get(
                    f"https://api.scratch.mit.edu/studios/{self.studio_id}/managers/?limit={limit}&offset={offset}",
                    headers=self.headers).json())
            self.studio_managers = managers
        return self.studio_managers

    def activity(self, all=False, limit=20, offset=0):
        """
        Get the activity of the studio
        :param all: If you want all the activity then set it to True
        :param limit: The limit
        :param offset: The offset or the number of data you want from the beginning
        """
        if self.studio_activity is None:
            activity = []
            if all:
                limit = 40
                offset = 0
                while True:
                    response = requests.get(
                        f"https://api.scratch.mit.edu/studios/{self.studio_id}/activity/?limit={limit}&offset={offset}",
                        headers=self.headers).json()
                    activity.append(response)
                    offset += 40
                    if len(response) != 40:
                        break
            if not all:
                activity.append(requests.get(
                    f"https://api.scratch.mit.edu/studios/{self.studio_id}/activity/?limit={limit}&offset={offset}",
                    headers=self.headers).json())
            self.studio_activity = activity
        return activity

    def _all_data(self):
        """
        DON'T USE THIS
        """
        data = {
            'Studio ID': self.id(),
            'Title': self.title(),
            'Host ID': self.host_id(),
            'Description': self.description(),
            'Comments Count': self.stats()['comments'],
            'Followers Count': self.stats()['followers'],
            'Managers Count': self.stats()['managers'],
            'Projects Count': self.stats()['projects'],
            'Visibility': self.visibility(),
            'Is Public?': self.is_public(),
            'Is Open To All?': self.is_open_to_all(),
            'Are Comments Allowed?': self.are_comments_allowed(),
        }
        return data

    def pretty_print_studio_data(self):
        """
        Pretty Print the Studio Data
        """
        data = self._all_data()
        length = self._find_max_length(data) + 10
        print("\033[1;33;40m" + "-" * length)
        print("\033[1;35;40m" + "Data of Studio with ID", str(self.studio_id) + ":")
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
