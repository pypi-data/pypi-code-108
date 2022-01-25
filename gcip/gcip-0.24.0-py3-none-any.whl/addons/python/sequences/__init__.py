__author__ = "Thomas Steinbach"
__copyright__ = "Copyright 2020 DB Systel GmbH"
__credits__ = ["Thomas Steinbach"]
# SPDX-License-Identifier: Apache-2.0
__license__ = "Apache-2.0"
__maintainer__ = "Thomas Steinbach"
__email__ = "thomas.t.steinbach@deutschebahn.com"

from typing import Any, Dict, Optional

from gcip.lib import rules
from gcip.core.sequence import Sequence
from gcip.addons.gitlab.jobs import pages as gitlab_pages
from gcip.addons.python.jobs.test import (
    Pytest,
    EvaluateGitTagPepe440Conformity,
)
from gcip.addons.python.jobs.build import BdistWheel
from gcip.addons.python.jobs.deploy import TwineUpload
from gcip.addons.python.jobs.linter import (
    Mypy,
    Isort,
    Flake8,
)


class FullStack(Sequence):
    def __init__(
        self,
        dev_repository_url: str,
        dev_user: str,
        varname_dev_password: str,
        stable_repository_url: str,
        stable_user: str,
        varname_stable_password: str,
        mypy_package_dir: Optional[str] = None,
        evaluate_git_tag_pep440_conformity_args: Dict[str, Any] = {},
    ) -> None:
        """
        Returns a sequence containing following jobs:
            * isort
            * flake8
            * pytest
            * evaluating CI_COMMIT_TAG as valid PyPI version string (if exists)
            * bdist_wheel
            * Gitlab Pages sphinx
            * twine upload

        Optional jobs:
            * mypy

        The `varname_dev_password` and `varname_stable_password` arguments are **only** used to specify the variable name and **not**
        the actuall password. The variable name has to be set outside of the pipline itself, if you set it within the pipline,
        that would be a security risk.

        Args:
            dev_repository_url (str): Development PyPI url, this URL will be used for development python packages.
            dev_user (str): User which is used to authenticate against `dev_repository_url` PyPI repository.
            varname_dev_password (str): Environment variable name to use in conjunction with `dev_user` to get authenticated.
            stable_repository_url (str): Stable PyPI url, this URL will be used for stable python packages, only for tagged versions.
            stable_user (str): User which is used to authenticate against `stable_repository_url` PyPI repository.
            varname_stable_password (str):  Environment variable name to use in conjunction with `stable_user` to get authenticated.
            mypy_package_dir (Optional[str]): Name of the directory to check with `mypy` for typing issues. Defaults to None.
            evaluate_git_tag_pep440_conformity_args (Dict[str, Any]): Check if the git tag is conform with
                Python [PEP440](https://www.python.org/dev/peps/pep-0440/). Defaults to {}.
        """
        super().__init__()

        self.isort_job = Isort()
        self.flake8_job = Flake8()
        self.pytest_job = Pytest()
        self.evaluate_git_tag_pep404_conformity_job = EvaluateGitTagPepe440Conformity(**evaluate_git_tag_pep440_conformity_args)
        self.bdist_wheel = BdistWheel()

        self.add_children(
            self.isort_job,
            self.flake8_job,
            self.pytest_job,
            self.evaluate_git_tag_pep404_conformity_job,
            self.bdist_wheel,
        )

        if mypy_package_dir:
            self.mypy_job = Mypy(mypy_package_dir)
            self.add_children(self.mypy_job)

        self.pages_sphinx_job = gitlab_pages.Sphinx()
        self.pages_sphinx_job.append_rules(
            rules.on_main(),
            rules.on_master(),
            rules.on_tags(),
        )
        self.add_children(self.pages_sphinx_job)

        self.twine_upload_dev_job = TwineUpload(
            twine_repository_url=dev_repository_url,
            twine_username_env_var=dev_user,
            twine_password_env_var=varname_dev_password,
        )
        self.twine_upload_dev_job.append_rules(
            rules.on_tags().never(),
            rules.on_success(),
        )
        self.add_children(self.twine_upload_dev_job, name="dev")

        self.twine_upload_stable_job = TwineUpload(
            twine_repository_url=stable_repository_url,
            twine_username_env_var=stable_user,
            twine_password_env_var=varname_stable_password,
        )
        self.twine_upload_stable_job.append_rules(rules.on_tags())
        self.add_children(self.twine_upload_stable_job, name="stable")
