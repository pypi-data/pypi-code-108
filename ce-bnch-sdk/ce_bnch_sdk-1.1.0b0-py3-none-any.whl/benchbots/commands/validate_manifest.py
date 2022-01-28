from typing import Dict

import jsonschema
import yaml

from benchling_sdk.benchbots.types.manifest import Manifest


class DuplicateNameError(Exception):
    pass


def validate_manifest_yaml(manifest_yaml: str) -> None:
    manifest_json = yaml.load(manifest_yaml, Loader=yaml.SafeLoader)
    validate_manifest(manifest_json)


def validate_manifest(manifest: Dict) -> None:
    jsonschema.validate(instance=manifest, schema=Manifest.json_schema())

    seen_names = set()
    for dependency in manifest.get("dependencies", []):
        name = dependency["name"]
        if name in seen_names:
            raise DuplicateNameError(f'Duplicate name "{name}" found in manifest dependencies')
        seen_names.add(name)
