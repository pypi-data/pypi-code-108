from dataclasses import dataclass
from typing import Optional, List, Dict, Any


@dataclass
class Manifest:
    """Fatman Manifest file - build recipe to get deployable image from source code workspace"""

    # name of the Fatman Workload
    name: str

    # email address of the Fatman's owner to reach out
    owner_email: str

    git: 'GitManifest'

    # version of the Fatman
    version: str = '0.0.1'

    # Language wrapper used to embed model
    lang: str = 'python3'

    # Python-specific configuration
    python: Optional['PythonManifest'] = None

    # Go/Golang-specific configuration
    golang: Optional['GoManifest'] = None

    # Docker-specific configuration
    docker: Optional['DockerManifest'] = None

    # type of deployed image: docker image, packer, AMI
    image_type: str = 'docker'

    # system-wide packages that should be installed with apt
    system_dependencies: Optional[List[str]] = None

    # env vars for building
    build_env: Optional[Dict[str, str]] = None
    # env vars for runtime
    runtime_env: Optional[Dict[str, str]] = None
    # secret env vars loaded from an external file applied on building
    secret_build_env_file: Optional[str] = None
    # secret env vars loaded from an external file applied at runtime
    secret_runtime_env_file: Optional[str] = None

    # labels - fatman metadata for humans
    labels: Optional[Dict[str, Any]] = None

    # list of public fatman endpoints that can be accessed without authentication
    public_endpoints: Optional[List[str]] = None

    # number of instances of the Fatman
    replicas: int = 1


@dataclass
class PythonManifest:
    requirements_path: Optional[str] = None
    # path to a Python file with a entrypoint class
    entrypoint_path: str = ''
    # base name of Python entrypoint class
    entrypoint_class: str = ''


@dataclass
class GoManifest:
    # relative path to Go modules requirements
    gomod: str = 'go.mod'


@dataclass
class GitManifest:
    # URL of git remote: HTTPS, SSH or directory path to a remote repository
    remote: str
    branch: Optional[str] = None
    # subdirectory relative to git repo root
    directory: str = '.'


@dataclass
class DockerManifest:
    dockerfile_path: Optional[str] = None
