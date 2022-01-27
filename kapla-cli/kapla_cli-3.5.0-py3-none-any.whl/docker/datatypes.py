from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from kapla.cli.utils import current_directory
from loguru import logger
from pydantic import BaseModel, DirectoryPath, FilePath, ValidationError
from yaml import SafeLoader, load


class Architecture(str, Enum):
    arm64 = "linux/arm64"
    amd64 = "linux/amd64"
    armv7 = "linux/arm/v7"
    ppc64le = "linux/ppc64le"


class Argument(BaseModel):
    name: str
    type: Any
    default: Optional[str] = None
    description: Optional[str] = None


class BuildConfig(BaseModel):
    context: DirectoryPath = Path(".")
    file: FilePath = Path("Dockerfile")
    build_args: List[Argument] = []
    add_hosts: Dict[str, str] = {}


class BuildContext(BaseModel):
    context_path: DirectoryPath
    add_hosts: Dict[str, str] = {}
    allow: List[str] = []
    build_args: Dict[str, str] = {}
    cache: bool = True
    cache_from: Union[str, Dict[str, str], None] = None
    cache_to: Union[str, Dict[str, str], None] = None
    file: Optional[FilePath] = None
    labels: Dict[str, str] = {}
    load: bool = False
    network: Optional[str] = None
    output: Union[str, Dict[str, str], None] = None
    platforms: Optional[List[str]] = None
    progress: Union[str, bool] = "auto"
    pull: bool = False
    push: bool = False
    secrets: Union[str, List[str]] = []
    ssh: Optional[str] = None
    tags: Union[str, List[str]] = []
    target: Optional[str] = None


class Image(BaseModel):
    name: str
    tag: str = "latest"
    template: str = "dockerfile"
    registry: str
    platforms: List[Architecture] = []
    labels: Dict[str, str] = {}
    build: BuildConfig = BuildConfig()

    def get_name(self) -> str:
        name = self.registry + "/" + self.name
        if self.tag:
            name += ":" + self.tag
        return name

    @classmethod
    def from_file(cls, filepath: Path) -> Image:
        """Load an image from a file."""
        with current_directory(filepath.parent):
            content = load(filepath.read_bytes(), Loader=SafeLoader)
            try:
                img = Image(**content)
            except ValidationError as err:
                logger.debug(f"Failed to validate configuration {filepath}")
                logger.error(err)
                raise
            img.build.file = img.build.file.absolute()
            img.build.context = img.build.context.absolute()
        return img


class Catalog(BaseModel):
    images: List[Image]

    @classmethod
    def from_directory(cls, directory: Path) -> Catalog:
        """Load config from an entire directory."""
        images = []
        files = directory.glob("**/builder.yml")
        for file in files:
            images.append(Image.from_file(file))
        try:
            config = cls(images=images)
        except ValidationError as err:
            logger.debug(f"Failed to validate global configuration: {images}")
            logger.error(err)
            raise err
        return config
