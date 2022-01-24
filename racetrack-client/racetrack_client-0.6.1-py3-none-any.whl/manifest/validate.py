import re
from pathlib import Path

from racetrack_client.log.context_error import wrap_context
from racetrack_client.manifest import Manifest
from racetrack_client.manifest.load import FATMAN_MANIFEST_FILENAME, load_manifest_from_yaml
from racetrack_client.log.logs import get_logger
from racetrack_client.utils.semver import SemanticVersion

logger = get_logger(__name__)


def load_validated_manifest(path: str) -> Manifest:
    """
    Load and validate manifest from a path. Raise exception in case of a defect.
    :param path path to a Fatman manifest file or to a directory with it
    :return loaded, valid Manifest
    """
    manifest_path = Path(path)
    if manifest_path.is_dir():
        manifest_path = manifest_path / FATMAN_MANIFEST_FILENAME

    with wrap_context('loading manifest'):
        manifest = load_manifest_from_yaml(manifest_path)
    with wrap_context('validating manifest'):
        validate_manifest(manifest)

    logger.debug(f'Manifest file "{manifest_path}" is valid')
    return manifest


def validate_manifest(manifest: Manifest):
    """Check whether manifest is valid. Raise exception in case of error"""
    if manifest.lang != 'python3':
        assert manifest.python is None, f'"python" configuration should be filled only for python jobs'
    if manifest.lang != 'golang':
        assert manifest.golang is None, f'"golang" configuration should be filled only for golang jobs'
    if manifest.lang != 'docker-http':
        assert manifest.docker is None, f'"docker" configuration should be filled only for docker-http jobs'

    assert re.match(r"[^@]+@[^@]+\.[^@]+", manifest.owner_email), '"owner_email" is not a valid email'

    with wrap_context('parsing Fatman version'):
        SemanticVersion(manifest.version)

    assert 1 <= manifest.replicas <= 15, 'replicas count out of allowed range'
