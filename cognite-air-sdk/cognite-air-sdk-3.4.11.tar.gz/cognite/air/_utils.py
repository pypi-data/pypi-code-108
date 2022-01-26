import json
import os
from pathlib import Path
from typing import Dict

from ruamel.yaml import YAML

from cognite.air import constants
from cognite.air.utils import strip_patch_from_version


def get_local_testing(data):
    if constants.SA_EXT_ID in data.keys():
        return False
    yaml_path = path_to_yaml(data)
    definitions = [i["id"] for i in json.loads(retrieve_field_definitions(yaml_path))]
    for i in definitions:
        if i not in data.keys():
            return False
    return True


def path_to_yaml(data: Dict) -> Path:
    yaml_path = retrieve_local_testing(data, constants.AIR_DATA_PATH_TO_YAML)
    if yaml_path:
        return Path(yaml_path)
    else:
        raise ValueError("No path to local config.yaml is given.")


def _load_yaml(path: Path) -> Dict:
    yaml = YAML(typ="safe").load(path)
    assert isinstance(yaml, dict)
    return yaml


def retrieve_field_definitions(path_to_config: Path):
    fields: Dict = _load_yaml(path_to_config).get("fields", {})
    output = []
    for i in fields.keys():
        output.append({**{"id": i}, **fields[i]})
    return json.dumps(output)


def retrieve_backfilling(data):
    path_to_config = path_to_yaml(data)
    return _load_yaml(path_to_config).get("modelSettings").get("backfill")


def retrieve_model_name(data: Dict):
    model_name = retrieve_local_testing(data, constants.AIR_DATA_MODEL_NAME, False)
    if model_name:
        return model_name
    cwd = os.getcwd()
    model_name = Path(cwd).parent.parent.parts[-1]
    return model_name


def retrieve_model_version(data):
    path_to_config = path_to_yaml(data)
    model_version = _load_yaml(path_to_config).get("modelSettings").get("modelVersion")
    return strip_patch_from_version(model_version)


def retrieve_local_testing(data, field, alternative=None):
    local_test = data.get(constants.AIR_DATA_LOCAL_TESTING)
    validate_local_test(local_test)
    value = local_test.get(field)
    if value is None:
        return alternative
    return value


def validate_local_test(local_test):
    if not isinstance(local_test, dict):
        raise ValueError(f"{constants.AIR_DATA_LOCAL_TESTING} needs to contain a dictionary.")
    for key in local_test.keys():
        if key not in constants.AIR_DATA_ALLOWED_KEYS:
            raise ValueError(f"{key} not a valid field in {constants.AIR_DATA_LOCAL_TESTING}")
    if constants.AIR_DATA_PATH_TO_YAML not in local_test.keys():
        raise ValueError(f"No path to local yaml given: {constants.AIR_DATA_PATH_TO_YAML}")


def create_fake_backfilling_asset():
    pass
