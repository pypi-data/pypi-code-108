from typing import List

from .Constants import (
    CUSTOMER_GIT_REPO,
    CUSTOMER_GIT_REPO_DIRECTORY,
    USERNAME,
    CUSTOMER_NAME,
    EMAIL,
)


class RequestInfo:
    def __init__(self, param_dict):
        self._customer_name = param_dict.get(CUSTOMER_NAME)
        self._username = param_dict.get(USERNAME)
        self._email = param_dict.get(EMAIL)
        self._git_repo = param_dict.get(CUSTOMER_GIT_REPO)
        self._git_repo_dir = param_dict.get(CUSTOMER_GIT_REPO_DIRECTORY)
        self.param_dict = param_dict

    @staticmethod
    def from_variables(customer, customer_repo, repo_dir, username=None, email=None):
        return RequestInfo(
            {
                CUSTOMER_NAME: customer,
                CUSTOMER_GIT_REPO: customer_repo,
                CUSTOMER_GIT_REPO_DIRECTORY: repo_dir,
                USERNAME: username,
                EMAIL: email,
            }
        )

    def missing_data(self) -> List[str]:
        """Returns a list of any fields that are 'None'"""
        fields = {
            CUSTOMER_NAME: self._customer_name,
            USERNAME: self._username,
            EMAIL: self._email,
            CUSTOMER_GIT_REPO: self._git_repo,
            CUSTOMER_GIT_REPO_DIRECTORY: self._git_repo_dir,
        }
        results = []
        for k, v in fields.items():
            if not v:
                results.append(k)
        return results

    @property
    def customer_name(self):
        return self._customer_name

    @property
    def username(self):
        return self._username

    @property
    def email(self):
        return self._email

    @property
    def git_repo(self):
        return self._git_repo

    @property
    def git_repo_dir(self):
        return self._git_repo_dir

    def get(self, parameter, default=None):
        return self.param_dict.get(parameter, default)
