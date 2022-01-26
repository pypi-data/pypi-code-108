from os import path
from typing import Any, List, Union, Optional
from dataclasses import dataclass

from gcip.core.job import Job, ScriptArgumentNotAllowedError
from gcip.core.image import Image
from gcip.core.variables import PredefinedVariables
from gcip.addons.container.images import PredefinedImages


@dataclass
class ScanLocalImage(Job):
    def __init__(
        self,
        *,
        name: str = "trivy",
        stage: str = "check",
        image_path: Optional[str] = None,
        image_name: Optional[str] = None,
        output_format: Optional[str] = None,
        severity: Optional[str] = None,
        vulnerability_types: Optional[str] = None,
        exit_if_vulnerable: bool = True,
        trivy_config: Optional[str] = None,
        trivy_image: Optional[Union[Image, str]] = None,
        **kwargs: Any,
    ) -> None:
        """This job scanns container images to find vulnerabilities.

        This job fails with exit code 1 if severities are found.
        The scan output is printed to stdout and uploaded to the artifacts of GitLab.

        Args:
            image_path (Optional[str]): Path where to find the container image.
                If `None` it defaults internally to `PredefinedVariables.CI_PROJECT_DIR`. Defaults to None.
            image_name (Optional[str]): Container image name, searched for in `image_path` and gets `.tar` appended.
                If `None` it defaults internally to `PredefinedVariables.CI_PROJECT_NAME`. Defaults to None.
            output_format (Optional[str]): Scan output format, possible values (table, json). Internal default `table`.
                Defaults to None.
            severity (Optional[str]): Severities of vulnerabilities to be displayed (comma separated).
                Defaults internally to "UNKNOWN,LOW,MEDIUM,HIGH,CRITICAL". Defaults to None.
            vulnerability_types (Optional[str]): List of vulnerability types (comma separated).
                Defaults internally to "os,library". Defaults to None.
            exit_if_vulnerable (bool): Exit code when vulnerabilities were found. If true exit code is 1 else 0. Defaults to True.
            trivy_config (Optional[str]): Additional options to pass to `trivy` binary. Defaults to None.
            trivy_image (Optional[Union[Image, str]]): Container image which contains `trivy` command.
                Defaults to PredefindedImages.TRIVY.
            name (str): The jobs name used in pipeline. Defaults to `trivy`.
            stage (str): The jobs stage used in pipeline. Defaults to `check`.

            Raises:
            ScriptArgumentNotAllowedError: It is not allowed to use the `script` argument in **kwargs,
                `script` is already initialized.
        """
        if "script" in kwargs:
            raise ScriptArgumentNotAllowedError()

        super().__init__(
            name=name,
            stage=stage,
            script="set -eo pipefail",
            **kwargs,
        )
        self.set_image(trivy_image if trivy_image is not None else PredefinedImages.TRIVY)

        if not image_path:
            image_path = PredefinedVariables.CI_PROJECT_DIR
        if not image_name:
            image_name = PredefinedVariables.CI_PROJECT_NAME
        image_name = image_name.replace("/", "_")

        trivy_cmd = ["trivy image"]
        trivy_cmd.append(f"--input {image_path}/{image_name}.tar")
        trivy_cmd.append("--no-progress")

        if output_format:
            trivy_cmd.append(f"--format {output_format}")

        if severity:
            trivy_cmd.append(f"--severity {severity}")

        if vulnerability_types:
            trivy_cmd.append(f"--vuln-type {vulnerability_types}")

        if exit_if_vulnerable:
            trivy_cmd.append("--exit-code 1")

        if trivy_config:
            trivy_cmd.append(trivy_config)

        trivy_cmd.append("|tee " + path.join(PredefinedVariables.CI_PROJECT_DIR, "trivi.txt"))
        self.append_scripts(" ".join(trivy_cmd))
        self.artifacts.add_paths("trivi.txt")


class TrivyIgnoreFileCheck(Job):
    def __init__(
        self,
        *,
        name: str = "trivyignore",
        stage: str = "check",
        allow_failure: Union[bool, int, List[int]] = 1,
        image: Optional[Union[Image, str]] = None,
        trivyignore_path: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """
        This job checks if a .trivyignore file exists and is not empty and fails if so.

        If a .trivyignore file is found and not empty, by default the job fails with `exit 1`,
        the job is configured to allow failures so that the pipeline keeps running.
        This ensures the visibility of acknowledged CVE's in the .trivyignore file inside the pipline.

        Args:
            name (str, optional): The jobs name used in pipeline. Defaults to "trivyignore".
            stage (str, optional): The jobs stage used in pipeline. Defaults to "check".
            allow_failure (bool, optional): Configure the job to allow failing or not.
                If `False` the job fails and the pipeline aborts, this job is not intendet to do that,
                but the possibilities are there. Defaults to True.
            image (Optional[Union[Image, str]], optional): Container image used, the image must have `stat` installed. Defaults to `busybox`.
            trivyignore_path (Optional[str], optional): Path to the `.trivyignore` file. Defaults to `$CI_PROJECT_DIR/.trivyignore`.

        Raises:
            ScriptArgumentNotAllowedError: It is not allowed to use the `script` argument in **kwargs,
                `script` is already initialized.
        """
        if "script" in kwargs:
            raise ScriptArgumentNotAllowedError()

        self._trivyignore_path = trivyignore_path if trivyignore_path else f"{PredefinedVariables.CI_PROJECT_DIR}/.trivyignore"

        super().__init__(
            name=name,
            stage=stage,
            script=[
                "set -eo pipefail",
                f'test -f {self._trivyignore_path} || {{ echo "{self._trivyignore_path} does not exists."; exit 0; }}',
                f'test "$(stat -c %b {self._trivyignore_path})" = "0" && {{ echo "{self._trivyignore_path} found but empty."; exit 0; }}',
                f'echo "{self._trivyignore_path} not empty. Please check your vulnerabilities!"; exit 1;',
            ],
            image=image if image is not None else PredefinedImages.BUSYBOX,
            allow_failure=allow_failure,
            **kwargs,
        )
