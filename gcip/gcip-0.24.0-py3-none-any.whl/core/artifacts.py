"""This module represents the Gitlab CI [artifacts](https://docs.gitlab.com/ee/ci/yaml/#artifacts) keyword

Simple example:

```
from gcip import Artifact, ArtifactReport

files = ["file1.txt", "file2.txt", "path/to/file3.txt"]

job1 = Job(stage="buildit", script="build my app")
job1.artifacts.add_paths(files)
```
"""
from __future__ import annotations

import os
from enum import Enum
from typing import Dict, List, Union, Optional

from gcip.core import OrderedSetType
from gcip.core.rule import WhenStatement
from gcip.core.variables import PredefinedVariables

__author__ = "Thomas Steinbach"
__copyright__ = "Copyright 2020 DB Systel GmbH"
__credits__ = ["Daniel von Eßen"]
# SPDX-License-Identifier: Apache-2.0
__license__ = "Apache-2.0"
__maintainer__ = "Daniel von Eßen"
__email__ = "daniel.von-essen@deutschebahn.com"


class ArtifactsReport(Enum):
    """This class represents the [artifacts:reports](https://docs.gitlab.com/ee/ci/yaml/#artifactsreports) types."""

    API_FUZZING = "api_fuzzing"
    """The api_fuzzing report collects API Fuzzing bugs as artifacts."""

    COBERTURA = "cobertura"
    """The cobertura report collects Cobertura coverage XML files."""

    CODEQUALITY = "codequality"
    """The codequality report collects Code Quality issues as artifacts."""

    CONTAINER_SCANNING = "container_scanning"
    """The container_scanning report collects Container Scanning vulnerabilities as artifacts."""

    COVERAGE_FUZZING = "coverage_fuzzing"
    """The coverage_fuzzing report collects coverage fuzzing bugs as artifacts."""

    DAST = "dast"
    """The dast report collects DAST vulnerabilities as artifacts."""

    DEPENDENCY_SCANNING = "dependency_scanning"
    """The dependency_scanning report collects Dependency Scanning vulnerabilities as artifacts."""

    DOTENV = "dotenv"
    """The dotenv report collects a set of environment variables as artifacts."""

    JUNIT = "junit"
    """The junit report collects JUnit report format XML files as artifacts."""

    LICENSE_SCANNING = "license_scanning"
    """The license_scanning report collects Licenses as artifacts."""

    LOAD_PERFORMANCE = "load_performance"
    """The load_performance report collects Load Performance Testing metrics as artifacts."""

    METRICS = "metrics"
    """The metrics report collects Metrics as artifacts."""

    PERFORMANCE = "performance"
    """The performance report collects Browser Performance Testing metrics as artifacts."""

    REQUIREMENTS = "requirements"
    """The requirements report collects requirements.json files as artifacts."""

    SAST = "sast"
    """The sast report collects SAST vulnerabilities as artifacts."""

    SECRET_DETECTION = "secret_detection"
    """The secret-detection report collects detected secrets as artifacts."""

    TERRAFORM = "terraform"
    """The terraform report obtains a Terraform tfplan.json file."""


class Artifacts:
    def __init__(
        self,
        *paths: str,
        excludes: List[str] = [],
        expire_in: Optional[str] = None,
        expose_as: Optional[str] = None,
        name: Optional[str] = None,
        public: Optional[bool] = None,
        reports: Dict[ArtifactsReport, str] = {},
        untracked: Optional[bool] = None,
        when: Optional[WhenStatement] = None,
    ) -> None:
        """
        This class represents the [artifacts](https://docs.gitlab.com/ee/ci/yaml/#artifacts) keyword.

        Gitlab CI documentation: _"Use artifacts to specify a list of files and directories that are
            attached to the `gcip.core.job.Job` when it succeeds, fails, or always.
        [...] by default, `gcip.core.job.Job`s in later stages automatically download all the artifacts created
            by jobs in earlier stages. You can control artifact download behavior in jobs with dependencies.


        Args:
            paths (str): Paths relative to project directory `$CI_PROJECT_DIR`,
                found files will be used to create the artifacts.
            excludes (List[str], optional): Paths that prevent files from being added to an artifacts archive. Defaults to [].
            expire_in (Optional[str], optional): How long the artifacts will be saved before it gets deleted. Defaults to None.
            expose_as (Optional[str], optional): Used to expose artifacts in merge requests. Defaults to None.
            name (Optional[str], optional): Name of the artifacts archive.
                Internally defaults to {PredefinedVariables.CI_JOB_NAME}-{PredefinedVariables.CI_COMMIT_REF_SLUG}.
            public (Optional[bool], optional): True makes artifacts public. Defaults to None.
            reports (Dict[ArtifactsReport, str]): Reports must be a valid dictionary, the key represents a ArtifactsReport and the
                value must be a valid relativ file path to the reports file. Defaults to {}.
            untracked (Optional[bool], optional): If true adds all untracked file to artifacts archive. Defaults to None.
            when (Optional[WhenStatement], optional): When to upload artifacts, Only `on_success`, `on_failure` or `always` is allowed. Defaults to None.

        Raises:
            ValueError: If `when` not one of `WhenStatement.ALWAYS`, `WhenStatement.ON_FAILURE` or `WhenStatement.ON_SUCCESS`.
        """
        self._paths: OrderedSetType = dict.fromkeys([self._sanitize_path(path) for path in paths])
        self._excludes: OrderedSetType = dict.fromkeys([self._sanitize_path(exclude) for exclude in excludes])
        self._expire_in = expire_in
        self._expose_as = expose_as
        self._name = name if name else f"{PredefinedVariables.CI_JOB_NAME}-{PredefinedVariables.CI_COMMIT_REF_SLUG}"
        self._public = public
        self._reports = {k.value: self._sanitize_path(v) for k, v in reports.items()}
        self._untracked = untracked
        self._when = when

        if self._when and self._when not in [WhenStatement.ALWAYS, WhenStatement.ON_FAILURE, WhenStatement.ON_SUCCESS]:
            raise ValueError(f"{self._when} not allowed. Only possible values are `on_success`, `on_failure` or `always`")

    @staticmethod
    def _sanitize_path(path: str) -> str:
        """Sanitizes the given path.

        Uses `os.path.normpath()` to normalize path.
        Shorten `PredefinedVariables.CI_PROJECT_DIR` at the very beginning of the path to just '.'.

        Args:
            path (str): Path to get sanitized.

        Raises:
            ValueError: If path begins with `/` and is not `PredefinedVariables.CI_PROJECT_DIR`.

        Returns:
            str: Sanitized path.
        """
        _path = os.path.normpath(path)
        if _path.startswith(PredefinedVariables.CI_PROJECT_DIR):
            _path = _path.replace(PredefinedVariables.CI_PROJECT_DIR, ".")

        if _path.startswith("/"):
            raise ValueError(f"Path {_path} not relative to {PredefinedVariables.CI_PROJECT_DIR}.")
        return _path

    @property
    def paths(self) -> List[str]:
        """Equals the identical Class argument."""
        return list(self._paths.keys())

    def add_paths(self, *paths: str) -> Artifacts:
        self._paths.update(dict.fromkeys([self._sanitize_path(path) for path in paths]))
        return self

    @property
    def excludes(self) -> List[str]:
        """Equals the identical Class argument."""
        return list(self._excludes)

    def add_excludes(self, *excludes: str) -> Artifacts:
        self._excludes.update(dict.fromkeys([self._sanitize_path(exclude) for exclude in excludes]))
        return self

    @property
    def expire_in(self) -> Optional[str]:
        """Equals the identical Class argument."""
        return self._expire_in

    @expire_in.setter
    def expire_in(self, expire_in: str) -> Artifacts:
        self._expire_in = expire_in
        return self

    @property
    def expose_as(self) -> Optional[str]:
        """Equals the identical Class argument."""
        return self._expose_as

    @expose_as.setter
    def expose_as(self, expose_as: str) -> Artifacts:
        self._expose_as = expose_as
        return self

    @property
    def name(self) -> str:
        """Equals the identical Class argument."""
        return self._name

    @name.setter
    def name(self, name: str) -> Artifacts:
        self._name = name
        return self

    @property
    def public(self) -> Optional[bool]:
        """Equals the identical Class argument."""
        return self._public

    @public.setter
    def public(self, public: bool) -> Artifacts:
        self._public = public
        return self

    @property
    def reports(self) -> Dict[str, str]:
        """Equals the identical Class argument."""
        return self._reports

    @reports.setter
    def reports(self, reports: Dict[str, str]) -> Artifacts:
        self._reports = reports
        return self

    def add_reports(self, reports: Dict[ArtifactsReport, str]) -> Artifacts:
        self._reports.update({k.value: v for k, v in reports.items()})
        return self

    @property
    def untracked(self) -> Optional[bool]:
        """Equals the identical Class argument."""
        return self._untracked

    @untracked.setter
    def untracked(self, untracked: bool) -> Artifacts:
        self._untracked = untracked
        return self

    @property
    def when(self) -> Optional[WhenStatement]:
        """Equals the identical Class argument."""
        return self._when

    @when.setter
    def when(self, when: WhenStatement) -> Artifacts:
        self._when = when
        return self

    def render(self) -> Optional[Dict[str, Union[str, bool, List[str], Dict[str, str], Dict[ArtifactsReport, str]]]]:
        """Return a representation of this Artifacts object as dictionary with static values.

        The rendered representation is used by the gcip to dump it
        in YAML format as part of the .gitlab-ci.yml pipeline.

        Returns:
            Dict[str, Union[str, bool, List[str], Dict[str, str], Dict[ArtifactReport, str]]]: A dictionary representing the
                artifacts object in Gitlab CI.
        """
        if not self._paths and not self._reports:
            return None

        rendered: Dict[str, Union[str, bool, List[str], Dict[str, str], Dict[ArtifactsReport, str]]]
        rendered = {
            "name": self.name,
        }
        if self.paths:
            rendered["paths"] = list(self.paths)
        if self.excludes:
            rendered["excludes"] = list(self.excludes)
        if self.expire_in:
            rendered["expire_in"] = self.expire_in
        if self.expose_as:
            rendered["expose_as"] = self.expose_as
        if self.public is not None:
            rendered["public"] = self.public
        if self.reports:
            rendered["reports"] = self.reports
        if self.untracked is not None:
            rendered["untracked"] = self.untracked
        if self.when:
            rendered["when"] = self.when.value
        return rendered

    def _equals(self, artifact: Optional[Artifacts]) -> bool:
        """
        Returns:
            bool: True if self equals to `artifact`.
        """
        if not artifact:
            return False

        return self.render() == artifact.render()
