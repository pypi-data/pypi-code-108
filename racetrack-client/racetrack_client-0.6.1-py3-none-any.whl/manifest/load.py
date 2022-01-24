from pathlib import Path
from typing import Dict, Optional

import yaml
from racetrack_client.log.context_error import wrap_context
from racetrack_client.manifest.manifest import Manifest
from racetrack_client.utils.dataclass import parse_dict_dataclass, parse_yaml_dataclass
from racetrack_client.log.logs import get_logger

logger = get_logger(__name__)

FATMAN_MANIFEST_FILENAME = 'fatman.yaml'


def load_manifest_from_yaml(path: Path) -> Manifest:
    """Load Manifest from a YAML file. Data types validation happens here when parsing YAML."""
    if not path.is_file():
        raise FileNotFoundError(f"manifest file '{path}' doesn't exist")

    with wrap_context('loading YAML'):
        with path.open() as file:
            manifest_dict = yaml.load(file, Loader=yaml.FullLoader)

    return load_manifest_from_dict(manifest_dict)


def load_manifest_from_dict(manifest_dict: Dict) -> Manifest:
    """Return manifest as data class"""
    with wrap_context('parsing manifest data types'):
        return parse_dict_dataclass(manifest_dict, Manifest)


def parse_manifest_or_empty(manifest_yaml: Optional[str]) -> Optional[Manifest]:
    """Parse YAML string as Manifest. In case of error return None"""
    if not manifest_yaml:
        return None
    try:
        return parse_yaml_dataclass(manifest_yaml, Manifest)
    except Exception as e:
        logger.error(f'Fatman Manifest YAML contains syntax error: {e}')
        return None
