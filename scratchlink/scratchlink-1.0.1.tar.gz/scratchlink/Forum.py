"""
The Forum Post Code
"""

import requests

from scratchlink import Exceptions

_website = "scratch.mit.edu"
_api = f"api.{_website}"


class Forum:
    def __init__(self, id):
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
        }
        self.f_id = str(id)
        self.update_data()

    def update_data(self):
        """
        Update the data
        """
        try:
            data = requests.get(f"https://scratchdb.lefty.one/v3/forum/topic/info/{self.f_id}",
                                headers=self.headers).json()
        except KeyError:
            raise Exceptions.InvalidForumTopic(f"Forum with ID - '{self.f_id}' doesn't exist!")
        self.f_title = data['title']
        self.f_category = data['category']
        self.f_is_closed = data['closed'] == 1
        self.f_is_deleted = data['deleted'] == 1
        self.f_time = data['time']
        self.f_post_count = data["post_count"]

    def id(self):
        """
        Returns the id of the forum
        """
        return self.f_id

    def title(self):
        """
        Returns the title of the forum
        """
        return self.f_title

    def category(self):
        """
        Returns the category of the forum
        """
        return self.f_category

    def is_closed(self):
        """
        Returns whether the forum is closed or not
        """
        return self.f_is_closed

    def is_deleted(self):
        """
        Returns whether the forum is deleted or not
        """
        return self.f_is_deleted

    def time(self):
        """
        Returns the activity of the forum
        """
        return self.f_time

    def post_count(self):
        """
        Returns the total post count of the forum
        """
        return self.f_post_count

    def posts(self, page=1):
        """
        Get the post in Forum Topic of a specified page. Images and some other stuff will not appear!
        :param page: The page
        """
        return requests.get(f"https://scratch-forum.sid72020123.repl.co/forum/?topic={self.f_id}&page={page}",
                            headers=self.headers).json()

    def _all_data(self):
        """
        DON'T USE THIS
        """
        data = {
            'Forum ID': self.id(),
            'Title': self.title(),
            'Category': self.category(),
            'Is Closed?': self.is_closed(),
            'Is Deleted?': self.is_deleted(),
            'Post Count': self.post_count()
        }
        return data

    def pretty_print_topic_data(self):
        """
        Pretty Print the Forum Topic Data
        """
        data = self._all_data()
        length = self._find_max_length(data) + 10
        print("\033[1;33;40m" + "-" * length)
        print("\033[1;35;40m" + "Data of Forum with ID", str(self.f_id) + ":")
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
