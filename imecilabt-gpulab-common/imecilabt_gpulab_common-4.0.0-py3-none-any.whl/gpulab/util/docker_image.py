import re
from dataclasses import dataclass
from typing import Optional

DOCKER_IMAGE_USERPASS_PATTERN = re.compile('^([a-zA-Z0-9_+-]+):([^@]+)@([^@]+)$')

# from https://docs.docker.com/engine/reference/commandline/tag/:
# Name components may contain lowercase letters, digits and separators.
# A separator is defined as a period, one or two underscores, or one or more dashes.
# A name component may not start or end with a separator.
# A tag name must be valid ASCII and may contain lowercase and uppercase letters,
# digits, underscores, periods and dashes. A tag name may not start with a period
# or a dash and may contain a maximum of 128 characters.
DOCKER_IMAGE_AND_TAG_PATTERN = re.compile('^(.+):([a-zA-Z0-9_][a-zA-Z0-9_.-]+)$')


@dataclass
class DockerImageName:
    """
    GPULab uses an extended format for docker images, which includes user/password authentication details

    This class provides easy access to all relevant parts

    Official docker base image/tag reference, see https://docs.docker.com/engine/reference/commandline/tag/
    """

    image: str  # "image" in docker terminology: includes private repo DNS (but not tag)
    tag: str = 'latest'
    user: Optional[str] = None
    password: Optional[str] = None

    def __post_init__(self):
        assert (self.user is None) == (self.password is None)
        # No empty strings:
        assert self.tag
        assert self.image
        assert self.user is None or self.user
        assert self.password is None or self.password

    # noinspection PyMethodFirstArgAssignment
    @classmethod
    def from_str(cls, image: str) -> 'DockerImageName':
        assert image is not None, 'image is None'
        assert isinstance(image, str), f'image is not a str but a {type(image)}'
        assert image.strip(), f'image is empty: {image!r}'
        match = DOCKER_IMAGE_USERPASS_PATTERN.match(image)
        if match:
            user, password, image = match.group(1, 2, 3)
            match = DOCKER_IMAGE_AND_TAG_PATTERN.match(image)
            if match:
                image, tag = match.group(1, 2)
                res = DockerImageName(image=image, tag=tag, user=user, password=password)
            else:
                res = DockerImageName(image=image, user=user, password=password)
        else:
            match = DOCKER_IMAGE_AND_TAG_PATTERN.match(image)
            if match:
                image, tag = match.group(1, 2)
                res = DockerImageName(image=image, tag=tag)
            else:
                res = DockerImageName(image=image)
        # assert str(res) == image  # self test   (doesn't work due to latest!)
        return res

    def __str__(self):
        res = f'{self.user}:{self.password}@' if self.user else ''
        res = f'{res}{self.image}'
        return f'{res}:{self.tag}' if self.tag else res

    @property
    def has_auth(self):
        return self.user is not None

    @property
    def includes_registry(self):
        # from https://docs.docker.com/engine/reference/commandline/tag/:
        # An image name is made up of slash-separated name components, optionally prefixed by a registry hostname.
        # The hostname must comply with standard DNS rules, but may not contain underscores.
        # If a hostname is present, it may optionally be followed by a port number in the format :8080.
        # If not present, the command uses Docker’s public registry located at registry-1.docker.io by default.

        # So we assume any dot is part of the DNS hostname of the registry
        return '.' in self.image

    @property
    def registry(self):
        if self.includes_registry:
            first_slash = self.image.index('/')
            return self.image[:first_slash]
        else:
            return 'registry-1.docker.io'  # public dockerhub registry

    @property
    def image_without_registry(self):
        if self.includes_registry:
            first_slash = self.image.index('/')
            return self.image[first_slash+1:]
        else:
            return self.image

    @property
    def image_with_tag(self):
        return f'{self.image}:{self.tag}'
