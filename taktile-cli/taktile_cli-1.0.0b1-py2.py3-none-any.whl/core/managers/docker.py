import os
import time
from typing import Dict

import docker  # type: ignore
import requests
from requests.exceptions import RequestException

from tktl.commands.health import GetGrpcHealthCommand, GetRestHealthCommand
from tktl.core.config import settings
from tktl.core.exceptions import APIClientException, MissingDocker
from tktl.core.loggers import LOG, MUTE_LOG

TESTING_DOCKERFILE = "Dockerfile.taktile-cli-testing"
MULTI_STAGE_BUILD_STEP_NAME = "build_step"


class DockerManager:
    def __init__(self, path):
        try:
            self._client = docker.from_env()
            self._path = path
        except docker.errors.DockerException as err:
            raise MissingDocker from err

    def get_docker_file(self) -> str:
        with open(os.path.join(self._path, ".buildfile")) as fp:
            return fp.read()

    def stream_logs(self, container) -> None:
        for line in container.logs(stream=True):
            LOG.log(f"> {line.decode()}".strip())

    def remove_image(self, image):
        self._client.images.remove(image, force=True)

    def build_image(
        self, dockerfile: str, cache: bool, prune: bool, buildargs: Dict = None
    ) -> str:

        if prune:
            try:
                image = self._client.images.get("taktile-cli-test:latest")
                self._client.images.remove(image.id)
            except docker.errors.ImageNotFound:
                pass

        if not cache:
            LOG.log("Building without Docker cache. This may take some time...")

        LOG.log(
            f"Multistage dockerfile, building target {MULTI_STAGE_BUILD_STEP_NAME}..."
        )
        image, stream = self._client.images.build(
            path=self._path,
            dockerfile=dockerfile,
            tag="taktile-cli-test",
            nocache=not cache,
            target=MULTI_STAGE_BUILD_STEP_NAME,
            buildargs=buildargs,
            forcerm=True,
        )

        for chunk in stream:
            if "stream" in chunk:
                for line in chunk["stream"].splitlines():
                    LOG.trace("> " + line)

        return image.id

    def test_import(self, image_id: str):
        client_name = "tktl" if not settings.FUTURE_ENDPOINTS else "client"
        command = f"python -c 'from src.endpoints import {client_name}'"
        try:
            container = self._client.containers.run(image_id, command, detach=True,)
            self.stream_logs(container)

            status = container.wait()
            return status, container
        finally:
            container.remove()

    def test_endpoint_sample(self, image_id: str):
        try:
            command = f"python /app/scripts/endpoint_sample_test{'_future' if settings.FUTURE_ENDPOINTS else ''}.py"
            container = self._client.containers.run(image_id, command, detach=True)
            self.stream_logs(container)

            status = container.wait()
            return status, container
        finally:
            container.remove()

    def test_unittest(self, image_id: str):
        try:
            container = self._client.containers.run(
                image_id, "python -m pytest ./user_tests/", detach=True
            )
            self.stream_logs(container)

            status = container.wait()
            return status, container
        finally:
            container.remove()

    def run_rest_container(
        self, image_id: str, detach: bool = True, auth_enabled: bool = True
    ):
        return self._client.containers.run(
            image_id,
            detach=detach,
            entrypoint="/start-rest.sh",
            environment={
                "AUTH_ENABLED": auth_enabled,
                "TAKTILE_GIT_SHA": "local-run",
                "TAKTILE_GIT_REF": "local-run",
            },
            ports={"80/tcp": 8080},
            remove=True,
            stderr=True,
            stdout=True,
        )

    def run_arrow_container(
        self, image_id: str, detach: bool = True, auth_enabled: bool = True
    ):
        return self._client.containers.run(
            image_id,
            detach=detach,
            entrypoint="/start-flight.sh",
            environment={
                "AUTH_ENABLED": auth_enabled,
                "TAKTILE_GIT_SHA": "local-run",
                "TAKTILE_GIT_REF": "local-run",
            },
            ports={"5005/tcp": 5005},
            remove=True,
            stderr=True,
            stdout=True,
        )

    def run_containers(
        self, image_id: str, detach: bool = True, auth_enabled: bool = True
    ):
        arrow_container = self.run_arrow_container(
            image_id=image_id, detach=detach, auth_enabled=auth_enabled
        )
        rest_container = self.run_rest_container(
            image_id=image_id, detach=detach, auth_enabled=auth_enabled
        )
        return arrow_container, rest_container

    def run_profiling_container(self):
        try:
            image_name = f"taktile/taktile-profiler:{_get_profiling_version()}"
            LOG.debug(f"Using Profiling Image {image_name}")
            container = self._client.containers.run(
                image_name,
                entrypoint="profiler profile -l",
                network_mode="host",
                detach=True,
            )
            self.stream_logs(container)
            status = container.wait()
            return status, container
        finally:
            container.remove()

    def run_and_check_health(
        self,
        image_id: str,
        kill_on_success: bool = False,
        auth_enabled: bool = True,
        timeout: int = 7,
        retries: int = 7,
    ):
        arrow_container, rest_container = self.run_containers(
            image_id=image_id, detach=True, auth_enabled=auth_enabled
        )
        grpc_health_cmd = GetGrpcHealthCommand(
            branch_name="",
            repository="",
            local=True,
            logger=MUTE_LOG if not LOG.VERBOSE else LOG,
            skip_auth=True,
        )
        rest_health_cmd = GetRestHealthCommand(
            branch_name="",
            repository="",
            local=True,
            logger=MUTE_LOG if not LOG.VERBOSE else LOG,
            skip_auth=True,
        )

        try:
            for _ in range(retries):
                try:
                    time.sleep(timeout)
                    rest_response = rest_health_cmd.execute()
                    grpc_response = grpc_health_cmd.execute()
                    return rest_response, grpc_response, arrow_container, rest_container
                except (APIClientException, Exception):
                    pass

            return None, None, arrow_container, rest_container
        finally:
            if kill_on_success:
                arrow_container.kill()
                rest_container.kill()


def _get_profiling_version() -> str:
    if settings.TAKTILE_PROFILING_VERSION:
        return settings.TAKTILE_PROFILING_VERSION
    else:
        try:
            res = requests.get(f"{settings.LOCAL_REST_ENDPOINT}/info").json()
            if isinstance(res, list):  # Not Future
                profiling_version = "latest"
            else:  # Future
                profiling_version = res.get("profiling", "latest")
        except RequestException as e:
            LOG.debug(f"Failed to fetch profiling version from Info {e}")
            profiling_version = "latest"
        return profiling_version
