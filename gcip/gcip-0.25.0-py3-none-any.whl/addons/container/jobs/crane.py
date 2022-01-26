import os
from typing import Any, Union, Optional
from dataclasses import dataclass

from gcip.core.job import Job, ScriptArgumentNotAllowedError
from gcip.core.image import Image
from gcip.core.variables import PredefinedVariables
from gcip.addons.container.config import DockerClientConfig
from gcip.addons.container.images import PredefinedImages
from gcip.addons.container.registries import Registry


@dataclass
class Copy(Job):
    def __init__(
        self,
        *,
        name: str = "crane-copy",
        stage: str = "deploy",
        src_registry: Union[Registry, str],
        dst_registry: Union[Registry, str],
        docker_client_config: Optional[DockerClientConfig] = None,
        crane_image: Optional[Union[Image, str]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Creates a job to copy container images with `crane`.
        See [`crane`](https://github.com/google/go-containerregistry/tree/main/cmd/crane)

        Copying an image is usfull, if you want to have container images as close as possible
        to your cluster or servers.

        Args:
            src_registry (str): Registry URL to copy container image from.
            dst_registry (str): Registry URL to copy container image to.
            docker_client_config (Optional[DockerClientConfig], optional): Creates the Docker configuration file base on objects settings,
                used by crane to authenticate against given registries. Defaults to None.
            crane_image (Optional[Union[Image, str]], optional): Container image which contains `crane` command.
                Defaults to PredefindedImages.CRANE.
            job_name (str): The jobs name used in pipeline. Defaults to `crane-copy`.
            job_stage (str): The jobs stage used in pipeline. Defaults to `deploy`.
        """
        if "script" in kwargs:
            raise ScriptArgumentNotAllowedError()

        super().__init__(
            script=[
                f"crane validate --remote {src_registry}",
                f"crane copy {src_registry} {dst_registry}",
            ],
            name=name,
            stage=stage,
            **kwargs,
        )
        self.set_image(crane_image if crane_image is not None else PredefinedImages.CRANE)

        if docker_client_config:
            self.prepend_scripts(*docker_client_config.get_shell_command())


@dataclass
class Push(Job):
    def __init__(
        self,
        *,
        name: str = "crane-push",
        stage: str = "deploy",
        dst_registry: Union[Registry, str],
        tar_path: Optional[str] = None,
        image_name: Optional[str] = None,
        image_tag: Optional[str] = None,
        docker_client_config: Optional[DockerClientConfig] = None,
        crane_image: Optional[Union[Image, str]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Creates a job to push container image to remote container registry with `crane`.

        The image to copy must be in a `tarball` format. It gets validated with crane
        and is pushed to `dst_registry` destination registry.

        Args:
            dst_registry (str): Registry URL to copy container image to.
            tar_path (Optional[str], optional): Path where to find the container image tarball.
                If `None` it defaults internally to `PredefinedVariables.CI_PROJECT_DIR`. Defaults to None.
            image_name (Optional[str], optional): Container image name, searched for in `image_path` and gets `.tar` appended.
                If `None` it defaults internally to `PredefinedVariables.CI_PROJECT_NAME`. Defaults to None.
            image_tag (Optional[str]): The tag the image will be tagged with.
                Defaults to `PredefinedVariables.CI_COMMIT_REF_NAME` or `PredefinedVariables.CI_COMMIT_TAG`.
            docker_client_config (Optional[DockerClientConfig], optional): Creates the Docker configuration file base on objects settings,
                to authenticate against given registries. Defaults to a `DockerClientConfig` with login to the official Docker Hub
                and expecting credentials given as environment variables `REGISTRY_USER` and `REGISTRY_LOGIN`.
            crane_image (Optional[Union[Image, str]], optional): Container image which contains `crane` command.
                Defaults to PredefindedImages.CRANE.
            job_name (str): The jobs name used in pipeline. Defaults to `crane-push`.
            job_stage (str): The jobs stage used in pipeline. Defaults to `deploy`.
        """
        if "script" in kwargs:
            raise ScriptArgumentNotAllowedError()

        if not tar_path:
            tar_path = PredefinedVariables.CI_PROJECT_DIR
        if not image_name:
            image_name = PredefinedVariables.CI_PROJECT_NAME
        image_path = image_name.replace("/", "_")

        if not image_tag:
            if PredefinedVariables.CI_COMMIT_TAG:
                image_tag = PredefinedVariables.CI_COMMIT_TAG
            else:
                image_tag = PredefinedVariables.CI_COMMIT_REF_NAME

        super().__init__(
            script=[
                f"crane validate --tarball {tar_path}/{image_path}.tar",
                f"crane push {tar_path}/{image_path}.tar {dst_registry}/{image_name}:{image_tag}",
            ],
            name=name,
            stage=stage,
            **kwargs,
        )
        self.set_image(crane_image if crane_image is not None else PredefinedImages.CRANE)

        if image_tag in ["main", "master"]:
            self.append_scripts(f"crane push {tar_path}/{image_path}.tar {dst_registry}/{image_name}:latest")

        if not docker_client_config:
            docker_client_config = DockerClientConfig().add_auth(registry=Registry.DOCKER)
        self.prepend_scripts(*docker_client_config.get_shell_command())


@dataclass
class Pull(Job):
    def __init__(
        self,
        *,
        name: str = "crane",
        stage: str = "pull",
        src_registry: Union[Registry, str],
        image_name: str,
        image_tag: str = "latest",
        tar_path: Optional[str] = None,
        docker_client_config: Optional[DockerClientConfig] = None,
        crane_image: Optional[Union[Image, str]] = None,
        **kwargs: Any,
    ) -> None:
        """
        Creates a job to pull container image from remote container registry with `crane`.

        Args:
            src_registry (str): Registry URL to pull container image from.
            image_name (str): Container image with namespace to pull from `src_registry`.
            image_tag (str): Tag of the image which will be pulled. Defaults to "latest".
            tar_path (Optional[str], optional): Path where to save the container image tarball.
                If `None` it defaults internally to `PredefinedVariables.CI_PROJECT_DIR`. Defaults to None.
            docker_client_config (Optional[DockerClientConfig], optional): Creates the Docker configuration file base on objects settings,
                to authenticate against given registries. Defaults to a `DockerClientConfig` with login to the official Docker Hub
                and expecting credentials given as environment variables `REGISTRY_USER` and `REGISTRY_LOGIN`.
            crane_image (Optional[Union[Image, str]], optional): Container image which contains `crane` command.
                Defaults to PredefindedImages.CRANE.
            job_name (str): The jobs name used in pipeline. Defaults to `crane-push`.
            job_stage (str): The jobs stage used in pipeline. Defaults to `deploy`.
        """
        if "script" in kwargs:
            raise ScriptArgumentNotAllowedError()

        if not tar_path:
            tar_path = PredefinedVariables.CI_PROJECT_DIR

        image_path = image_name.replace("/", "_")
        super().__init__(
            script=[
                f"mkdir -p {os.path.normpath(tar_path)}",
                f"crane pull {src_registry}/{image_name}:{image_tag} {tar_path}/{image_path}.tar",
            ],
            name=name,
            stage=stage,
            **kwargs,
        )
        self.set_image(crane_image if crane_image is not None else PredefinedImages.CRANE)

        if not docker_client_config:
            docker_client_config = DockerClientConfig().add_auth(registry=Registry.DOCKER)
        self.prepend_scripts(*docker_client_config.get_shell_command())
