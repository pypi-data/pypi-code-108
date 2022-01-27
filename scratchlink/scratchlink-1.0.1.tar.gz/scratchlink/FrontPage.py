"""
The Front Page Code
"""

import requests

_website = "scratch.mit.edu"
_api = f"api.{_website}"


class FrontPage:
    def __init__(self):
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
        }

    def health(self):
        """
        Returns the health of the Scratch Website.
        """
        return requests.get(f"https://{_api}/health", headers=self.headers).json()

    def news(self):
        """
        Returns the news of the Scratch Website.
        """
        return requests.get(f"https://{_api}/news", headers=self.headers).json()

    def front_page_projects(self):
        """
        Returns the front page projects of the Scratch Website.
        """
        return requests.get(f"https://{_api}/proxy/featured", headers=self.headers).json()

    def explore_projects(self, mode="trending", query="*"):
        """
        Explore the projects
        :param mode: The mode such as 'popular' or 'trending'
        :param query: The query
        """
        return requests.get(f"https://{_api}/explore/projects/?mode={mode}&q={query}").json()

    def explore_studios(self, mode="trending", query="*"):
        """
        Explore the studios
        :param mode: The mode such as 'popular' or 'trending'
        :param query: The query
        """
        return requests.get(f"https://{_api}/explore/studios/?mode={mode}&q={query}").json()

    def search_projects(self, mode="trending", search="*"):
        """
        Search the projects
        :param mode: The mode such as 'popular' or 'trending'
        :param query: The query
        """
        return requests.get(f"https://{_api}/search/projects/?mode={mode}&q={search}").json()

    def search_studios(self, mode="trending", search="*"):
        """
        Search the studios
        :param mode: The mode such as 'popular' or 'trending'
        :param query: The query
        """
        return requests.get(f"https://{_api}/search/studios/?mode={mode}&q={search}").json()
