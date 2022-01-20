"""Interfaces
"""
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Protocol

# pylint: disable=too-few-public-methods


class ContainerTech(Enum):
    """Available Container Technologies"""

    DOCKER = auto()
    PODMAN = auto()


class ContainerProvider(Enum):
    """Available DevContainers providers"""

    VSC = auto()


@dataclass
class Configuration:
    """Configuration data"""

    location: Path
    repository: Path

    devcontainer_provider: ContainerProvider = ContainerProvider.VSC
    container_tech: ContainerTech = ContainerTech.DOCKER
    manifest_file: str = "devcontainer.json"


class DevContainer(Protocol):
    """DevContainer manifest definition"""

    def get(self, key: str):
        """Get a key from the devcontainer definition"""
        ...


class ContainerRunner(Protocol):
    """definition for classes whose responsibility is to executes containers having a image"""

    def run(self, image_id: str = None) -> int:
        """Run a container"""
        ...


class ContainerBuilder(Protocol):
    """Build a container against a specific container technology"""

    def build(self, buildargs: dict, tag: str) -> str:
        """Build"""
        ...
