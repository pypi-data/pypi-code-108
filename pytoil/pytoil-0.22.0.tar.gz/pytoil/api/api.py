"""
Module responsible for handling pytoil's interface with the
GitHub GraphQL v4 API.


Author: Tom Fleet
Created: 21/12/2021
"""


from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx
import humanize

from pytoil import __version__
from pytoil.api import queries

URL = "https://api.github.com/graphql"


GITHUB_TIME_FORMAT = r"%Y-%m-%dT%H:%M:%SZ"


class API:
    def __init__(self, username: str, token: str, url: str = URL) -> None:
        """
        Container for methods and data for hitting the GitHub v4
        GraphQL API

        Args:
            username (str): User's GitHub username.
            token (str): User's personal access token.
            url (str, optional): GraphQL URL
                defaults to https://api.github.com/graphql
        """
        self.username = username
        self.token = token
        self.url = url

    def __repr__(self) -> str:
        return (
            self.__class__.__qualname__
            + f"(username={self.username}, token={self.token}, url={self.url})"
        )

    __slots__ = ("username", "token", "url")

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"token {self.token}",
            "User-Agent": f"pytoil/{__version__}",
            "Accept": "application/vnd.github.v4+json",
        }

    async def get_repos(self, limit: int = 50) -> list[dict[str, Any]] | None:
        """
        Gets some summary info for all the users repos.

        Args:
            limit (int, optional): Maximum number of repos to return.
                Defaults to 50.

        Returns:
            list[dict[str, Any]]: The repos info.
        """
        async with httpx.AsyncClient(http2=True, headers=self.headers) as client:
            r = await client.post(
                self.url,
                json={
                    "query": queries.GET_REPOS,
                    "variables": {"username": self.username, "limit": limit},
                },
            )
            r.raise_for_status()

        raw: dict[str, Any] = r.json()

        if data := raw.get("data"):
            return [node for node in data["user"]["repositories"]["nodes"]]

        return None

    async def get_repo_names(self, limit: int = 50) -> set[str]:
        """
        Gets the names of all repos owned by the authenticated user.

        Args:
            limit (int, optional): Maximum number of repos to return.
                Defaults to 50.

        Raises:
            ValueError: If the GraphQL query is malformed.

        Returns:
            Set[str]: The names of the user's repos.
        """

        async with httpx.AsyncClient(http2=True, headers=self.headers) as client:
            r = await client.post(
                self.url,
                json={
                    "query": queries.GET_REPO_NAMES,
                    "variables": {"username": self.username, "limit": limit},
                },
            )
            r.raise_for_status()

        raw: dict[str, Any] = r.json()

        # TODO: I don't like the indexing here, must be a more type safe way of doing this
        # What happens when there are no nodes? e.g. user has no forks
        if data := raw.get("data"):
            return {node["name"] for node in data["user"]["repositories"]["nodes"]}

        else:
            raise ValueError(f"Bad GraphQL: {raw}")

    async def get_forks(self, limit: int = 50) -> list[dict[str, Any]] | None:
        """
        Gets info for all users forks.

        Args:
            limit: (int, optional): Maximum number of repos to return.
                Defaults to 50.

        Returns:
            list[dict[str, Any]]: The JSON info for all forks.
        """
        async with httpx.AsyncClient(http2=True, headers=self.headers) as client:
            r = await client.post(
                self.url,
                json={
                    "query": queries.GET_FORKS,
                    "variables": {"username": self.username, "limit": limit},
                },
            )
            r.raise_for_status()

        raw: dict[str, Any] = r.json()

        if data := raw.get("data"):
            return [node for node in data["user"]["repositories"]["nodes"]]

        return None

    async def check_repo_exists(self, name: str) -> bool:
        """
        Checks whether or not a repo given by `name` exists
        under the current user

        Args:
            name (str): Repo name to check for

        Returns:
            bool: True if repo exists on GitHub, else False.
        """
        async with httpx.AsyncClient(http2=True, headers=self.headers) as client:
            r = await client.post(
                self.url,
                json={
                    "query": queries.CHECK_REPO_EXISTS,
                    "variables": {"username": self.username, "name": name},
                },
            )
            r.raise_for_status()

        raw: dict[str, Any] = r.json()

        if data := raw.get("data"):
            if data["repository"] is None:
                return False
            else:
                return True
        else:
            raise ValueError(f"Bad GraphQL: {raw}")

    async def create_fork(self, owner: str, repo: str) -> None:
        """
        Use the v3 REST API to create a fork of the specified repository
        under the authenticated user.

        Args:
            owner (str): Owner of the original repo.
            repo (str): Name of the original repo.
        """
        rest_headers = self.headers.copy()
        rest_headers["Accept"] = "application/vnd.github.v3+json"
        fork_url = f"https://api.github.com/repos/{owner}/{repo}/forks"

        async with httpx.AsyncClient(http2=True, headers=rest_headers) as client:
            r = await client.post(fork_url)
            r.raise_for_status()

    @staticmethod
    def _humanize_datetime(dt: str) -> str:
        """
        Takes a string datetime of GITHUB_TIME_FORMAT
        and converts it to our STR_TIME_FORMAT.
        """
        s: str = humanize.naturaltime(datetime.strptime(dt, GITHUB_TIME_FORMAT))
        return s

    async def get_repo_info(self, name: str) -> dict[str, Any] | None:
        """
        Gets some descriptive info for the repo given by
        `name` under the current user.

        Args:
            name (str): Name of the repo to fetch info for.

        Returns:
            Dict[str, Any]: Repository info.
        """
        async with httpx.AsyncClient(http2=True, headers=self.headers) as client:
            r = await client.post(
                self.url,
                json={
                    "query": queries.GET_REPO_INFO,
                    "variables": {"username": self.username, "name": name},
                },
            )
            r.raise_for_status()

        raw: dict[str, Any] = r.json()

        if data := raw.get("data"):
            if repo := data.get("repository"):
                return {
                    "Name": repo["name"],
                    "Description": repo["description"],
                    "Created": self._humanize_datetime(repo["createdAt"]),
                    "Updated": self._humanize_datetime(repo["updatedAt"]),
                    "Size": humanize.naturalsize(
                        int(repo["diskUsage"]) * 1024
                    ),  # diskUsage is in kB
                    "License": repo["licenseInfo"]["name"]
                    if repo.get("licenseInfo")
                    else None,
                    "Remote": True,
                }
            return None
        return None
