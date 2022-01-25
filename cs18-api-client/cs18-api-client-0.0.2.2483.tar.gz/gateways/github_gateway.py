import json
import urllib.parse
from typing import List

from time import sleep

import requests

from requests import Response

from common.test_utils import TestUtils
from gateways.common.cs18_api_classes import Commit


class GithubGateway:
    def __init__(self, user: str = "QualiNext", repo: str = "cs18-space-testing"):
        token = TestUtils.get_test_github_access_token()
        self.session = requests.Session()
        self.session.headers.update({"Authorization": "token " + token})
        self.session.headers.update({"Accept": "application/vnd.github.v3.raw"})
        self.base_api_url = "https://api.github.com/repos/{user}/{repo}".format(
            user=user, repo=repo
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def close(self):
        self.session.close()

    def get_file(self, file_path, branch=None, tag=None, commit_id=None) -> str:
        url = "{github_api_url}/contents/{file_path}?ref={v}".format(
            github_api_url=self.base_api_url,
            file_path=file_path,
            v=branch or tag or commit_id,
        )
        return self.http_get(url=url).text

    def get_commit_history(self, file_path, branch="master") -> List[Commit]:
        url = "{github_api_url}/commits?sha={branch}&path={path}".format(
            github_api_url=self.base_api_url,
            branch=branch,
            path=urllib.parse.quote(file_path, safe=""),
        )
        response = self.http_get(url=url)
        items = json.loads(response.text)
        commits = [Commit(x) for x in items]
        sorted(commits, key=lambda x: x.date)
        return commits

    def http_get(self, url: str) -> Response:
        response = None
        attempt = 0
        while attempt < 5:
            response = self.session.get(url=url)
            if response.ok:
                return response
            attempt += 1
            print("Response from '{0}' returned {1}".format(url, response.status_code))
            sleep(1)
        response.raise_for_status()
