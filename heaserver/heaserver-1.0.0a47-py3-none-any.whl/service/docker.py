"""
Utility functions and classes for working with docker images and containers.
"""
import os
from contextlib import ExitStack

from testcontainers.general import DockerContainer
from testcontainers.core.waiting_utils import wait_container_is_ready
import requests
from testcontainers.mongodb import MongoDbContainer
from yarl import URL
from typing import Dict, List
from copy import deepcopy
from typing import Optional


class DockerImage:
    """
    Docker image specification.
    """

    def __init__(self, image: str, port: int, check_path: Optional[str] = None,
                 resources: Optional[List[Dict[str, str]]] = None):
        """
        Constructor.

        :param image: the image tag (required).
        :param port: the exposed port (required).
        :param check_path: the URL path to check if the microservice is running.
        :param resources: a list of heaobject.registry.Resource dicts indicating what content types this image is designed for.
        """
        if image is None:
            raise ValueError('image cannot be None')
        if port is None:
            raise ValueError('port cannot be None')
        self.__image = str(image)
        self.__port = int(port)
        self.__check_path = str(check_path)
        self.__resources = deepcopy(resources)

    @property
    def image(self) -> Optional[str]:
        """
        The image tag (read-only).
        """
        return self.__image

    @property
    def port(self) -> Optional[int]:
        """
        The exposed port (read-only).
        """
        return self.__port

    @property
    def check_path(self) -> Optional[str]:
        """
        The URL path to check for whether the microservice is running (read-only).
        """
        return self.__check_path

    @property
    def resources(self) -> Optional[List[Dict[str, str]]]:
        """
        A list of heaobject.registry.Resource dicts indicating what content types this image is designed for (read-only).
        """
        return deepcopy(self.__resources)


@wait_container_is_ready()
def get_exposed_port(container: DockerContainer, port: int):
    """
    Returns the actual port that the docker container is listening to. It tries getting the port repeatedly until the
    container has sufficiently started to assign the port number.

    :param container: the docker container (required).
    :param port: the port that the container's application is listening to internally.
    :return:
    """
    return container.get_exposed_port(port)


@wait_container_is_ready()
def wait_for_status_code(url, status):
    """
    Makes a HTTP GET call to the provided URL repeatedly until the returned status code is equal to the provided code.

    :param url: the URL to call.
    :param status: the status code to check for.
    """
    return requests.get(url).status_code == status


def get_bridge_ip(container: DockerContainer) -> str:
    """
    Returns the IP address of the container on the default bridge network.
    :param container: a docker container.
    :return: an IP address.
    """
    return container.get_docker_client().bridge_ip(container.get_wrapped_container().id)


def start_microservice_container(docker_image: DockerImage, mongo_: MongoDbContainer, stack: ExitStack, registry_url: str = None) -> str:
    """
    Starts a Docker container with the provided image, Mongo database container, and exit stack for cleaning up
    resources. If the docker_image object has a check_path, the function will wait until the microservice returns a 200
    status code from a GET call to the path before returning.

    :param docker_image: the Docker image to start (required).
    :param mongo_: the MongoDBContainer (required)
    :param stack: the ExitStack (required).
    :param registry_url: optional base URL for the heaserver-registry microservice.
    :return: the base URL of the container as a string.
    """
    container = DockerContainer(docker_image.image)
    container.with_env('MONGO_HOSTNAME', get_bridge_ip(mongo_))
    container.with_env('MONGO_HEA_USERNAME', 'test')
    container.with_env('MONGO_HEA_PASSWORD', 'test')
    container.with_env('MONGO_HEA_DATABASE', os.environ['MONGO_DB'])
    if registry_url is not None:
        container.with_env('HEASERVER_REGISTRY_URL', registry_url)
    container.with_exposed_ports(docker_image.port)
    microservice = stack.enter_context(container)
    base_url = f'http://{microservice.get_container_host_ip()}:{get_exposed_port(microservice, docker_image.port)}'
    if docker_image.check_path is not None:
        wait_for_status_code(str(URL(base_url).with_path(docker_image.check_path)), 200)
    return base_url
