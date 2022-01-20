"""Docker container backend
"""
import io
from hashlib import md5
from typing import Generator

import docker
import pexpect
from logzero import setup_logger

from ..factories import DevContainerFactory
from ..interfaces import Configuration, ContainerBuilder, ContainerRunner, ContainerTech
from ..utils import stream_load

# pylint: disable=too-few-public-methods


def parse_docker_builder_stream(streamed_builder: Generator) -> Generator:
    """Parse Docker's builder streamed JSON"""

    for builder_step in streamed_builder:
        data = io.BytesIO(builder_step)
        yield from stream_load(data)


def docker_client():
    """Provide the docker client object"""

    return docker.client.from_env()


class Builder(ContainerBuilder):
    """Container builder"""

    type = ContainerTech.DOCKER

    def __init__(self, config: Configuration) -> None:
        super().__init__()
        self.__client = docker_client().api
        self.__logger = setup_logger(name=self.__class__.__name__)
        self.__location = config.location

    def _get_image_labels(self) -> dict:
        return {
            "devcontainers4all.definition.path": str(self.__location.resolve()),
        }

    def build(self, buildargs: dict, tag: str = None) -> str:
        """Build the container"""
        # An image is built according to the information of the manifest+dockerfile, which normally are within
        # location. So far this should be strong enough to uniquely identify the image
        tag = (
            f"devcontainers4all-{md5(bytes(self.__location.resolve())).hexdigest()}"
            if tag is None
            else tag
        )

        self.__logger.debug(
            "Building %s image, from %s", tag, self.__location.resolve()
        )

        builder = self.__client.build(
            str(self.__location),
            buildargs=buildargs,
            labels=self._get_image_labels(),
            tag=tag,
            rm=False,
            nocache=False,
        )

        # consume the builder's steps and send its output to the logger
        # the builder is a generator of streamed-json data, which needs to be parsed in a non-common way

        for step in parse_docker_builder_stream(builder):
            if "stream" not in step:
                continue

            for line in step["stream"].splitlines():
                if line:
                    self.__logger.debug(line)

        #        # consume the builder's steps and send its output to the logger
        #        for build_out in builder:
        #            # builder yields streamed json, which needs to be parsed before splitting in steps
        #            steps = stream_load(io.BytesIO(build_out))
        #
        #            for step in steps:
        #                if "stream" not in step:
        #                    continue
        #
        #                for line in step["stream"].splitlines():
        #                    if line:
        #                        self.__logger.debug(line)

        return tag


class Runner(ContainerRunner):
    """Docker Runner"""

    def __init__(self, config: Configuration) -> None:
        super().__init__()
        self.__client = docker_client()
        self.__config = config
        self.__logger = setup_logger(name="Runner")

    def run(self, image_id: str = None) -> int:
        """Start container"""
        manifest = DevContainerFactory(self.__config)
        post_create_command = manifest.get("build").get("postCreateCommand")

        volumes = {
            str(self.__config.repository.resolve()): {
                "bind": "/workspace",
                "mode": "rw",
            }
        }
        self.__logger.debug("Using volumes %s", volumes)
        self.__logger.debug(image_id)

        container = self.__client.containers.create(
            image_id,
            tty=True,
            detach=True,
            command="/bin/bash",
            labels={
                "devcontainers4all.repository.path": str(
                    self.__config.repository.resolve()
                )
            },
            stdin_open=True,
            volumes=volumes,
        )

        container.start()
        try:
            # attach via CLI: managing the terminal is too complex for now
            attached_container = pexpect.spawn(f"docker attach {container.id}")
        except:
            container.stop()
            container.remove()
            raise

        try:
            if isinstance(post_create_command, str):
                attached_container.sendline(post_create_command)
            elif isinstance(post_create_command, list):
                for line in post_create_command:
                    attached_container.sendline(line)

            attached_container.interact()
        finally:
            attached_container.close()
            exit_code = attached_container.exitstatus

            container.stop()
            container.remove()

        return exit_code
