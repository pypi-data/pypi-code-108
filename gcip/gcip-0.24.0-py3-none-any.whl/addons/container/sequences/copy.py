import copy
from typing import Any, Dict, Union, Optional
from dataclasses import dataclass

from gcip.core.cache import Cache, CacheKey
from gcip.core.sequence import Sequence
from gcip.core.variables import PredefinedVariables
from gcip.addons.container.jobs import dive, crane, trivy
from gcip.addons.container.config import DockerClientConfig
from gcip.addons.container.registries import Registry


@dataclass
class CopyContainer(Sequence):
    def __init__(
        self,
        *,
        src_registry: Union[Registry, str] = Registry.DOCKER,
        dst_registry: Union[Registry, str],
        image_name: str,
        image_tag: str,
        dive_kwargs: Dict[str, Any] = {},
        trivy_kwargs: Dict[str, Any] = {},
        crane_kwargs: Dict[str, Any] = {},
        docker_client_config: Optional[DockerClientConfig] = None,
        do_dive_scan: bool = True,
        do_trivy_scan: bool = True,
    ) -> None:
        """
        Creates a `gcip.Sequence` to pull, scan and push a container image.

        The pull step is executed by `gcip.addons.container.jobs.crane.pull`, it will pull the container image an outputs it to a tarball.
        There are two scan's, optimization scan with `gcip.addons.container.jobs.dive.scan_local_image` to scan storage wasting in container image
        and a vulnerability scan with `gcip.addons.container.jobs.trivy.scan`. Both outputs are uploaded as an artifact to the GitLab instance.
        Built container image is uploaded with `gcip.addons.container.jobs.crane.push`.

        Args:
            src_registry (Union[Registry, str], optional): Container registry to pull the image from. If the container registry needs authentication,
                you have to provide a `gcip.addons.container.config.DockerClientConfig` object with credentials. Defaults to Registry.DOCKER.
            dst_registry (Union[Registry, str]): Container registry to push the image to. If the container registry needs authentication,
                you have to provide a `gcip.addons.container.config.DockerClientConfig` object with credentials. Defaults to Registry.DOCKER.
            image_name (str): Image name with stage in the registry. e.g. username/image_name.
            image_tag (str): Container image tag to pull from `src_registry` and push to `dst_registry`.
            dive_kwargs (Dict[str, Any], optional): Extra keyword arguaments passed to `gcip.addons.container.jobs.dive.scan`. Defaults to {}.
            trivy_kwargs (Dict[str, Any], optional): Extra keyword arguaments passed to `gcip.addons.container.jobs.trivy.scan_local_image`. Defaults to {}.
            crane_kwargs (Dict[str, Any], optional): Extra keyword arguaments passed to `gcip.addons.container.jobs.push`. Defaults to {}.
            docker_client_config (Optional[DockerClientConfig], optional): Creates the Docker configuration file base on objects settings,
                to authenticate against given registries. Defaults to a `DockerClientConfig` with login to the official Docker Hub
                and expecting credentials given as environment variables `REGISTRY_USER` and `REGISTRY_LOGIN`.
            do_dive_scan (Optional[bool]): Set to `False` to skip the Dive scan job. Defaults to True.
            do_trivy_scan (Optional[bool]): Set to `False` to skip the Trivy scan job. Defaults to True.

        Returns:
            Sequence: `gcip.Sequence` to pull, scan and push a container image.
        """
        super().__init__()

        """
        We decided to use caches instead of artifacts to pass the Docker image tar archive from one job to another.
        This is because those tar archives could become very large - especially larger then the maximum artifact size limit.
        This limit can just be adjusted by the admin of the gitlab instance, so your pipeline would never work, your Gitlab
        provider would not adjust this limit for you. For caches on the other hand you can define storage backends at the
        base of your Gitlab runners.

        Furthermore we set the cache key to the pipeline ID. This is because the name and tag of the image does not ensure that
        the downloaded tar is unique, as the image behind the image tag could be overridden. So we ensure uniqueness by downloading
        the image once per pipeline.
        """

        self.cache = Cache(paths=["image"], cache_key=CacheKey(PredefinedVariables.CI_PIPELINE_ID + image_name + image_tag))
        self.crane_pull_job = crane.Pull(
            src_registry=src_registry,
            image_name=image_name,
            image_tag=image_tag,
            tar_path=self.cache.paths[0],
            docker_client_config=copy.deepcopy(docker_client_config),
            **crane_kwargs,
        )
        self.crane_pull_job.set_cache(self.cache)
        self.add_children(self.crane_pull_job)

        if do_dive_scan:
            self.dive_scan_job = dive.Scan(
                image_path=self.cache.paths[0],
                image_name=image_name,
                **dive_kwargs,
            )
            self.dive_scan_job.set_cache(self.cache)
            self.dive_scan_job.add_needs(self.crane_pull_job)
            self.add_children(self.dive_scan_job)

        if do_trivy_scan:
            self.trivy_scan_job = trivy.ScanLocalImage(
                image_path=self.cache.paths[0],
                image_name=image_name,
                **trivy_kwargs,
            )
            self.trivy_scan_job.set_cache(self.cache)
            self.trivy_scan_job.add_needs(self.crane_pull_job)
            self.add_children(self.trivy_scan_job)

        self.crane_push_job = crane.Push(
            dst_registry=dst_registry,
            tar_path=self.cache.paths[0],
            image_name=image_name,
            image_tag=image_tag,
            docker_client_config=copy.deepcopy(docker_client_config),
            **crane_kwargs,
        )
        self.crane_push_job.set_cache(self.cache)
        self.crane_push_job.add_needs(self.crane_pull_job)
        if do_dive_scan:
            self.crane_push_job.add_needs(self.dive_scan_job)
        if do_trivy_scan:
            self.crane_push_job.add_needs(self.trivy_scan_job)
        self.add_children(self.crane_push_job)
