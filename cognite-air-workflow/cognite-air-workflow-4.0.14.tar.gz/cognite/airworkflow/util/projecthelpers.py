# import os
from pathlib import Path
from typing import Dict, Set

from ruamel.yaml import YAML

# import cognite.airworkflow.util.file as file
from cognite.airworkflow.util import env


def load_yaml(path: Path) -> Dict:
    yaml = YAML(typ="safe").load(path)
    assert isinstance(yaml, dict)
    return yaml


working_path = env.get_env_value("PWD")
ROOT_DIR = Path(working_path)
FUNCTIONS_PATH = ROOT_DIR / "functions"
IGNORE_MODELS_PATH = ROOT_DIR / ".ignore_models"

# Paths within a functions folder
FUNCTION_REL_PATH = Path("function")
REPOCONFIG_PATH = Path("repoconfig.yaml")
FUNCTION_REL_CONFIG_PATH = FUNCTION_REL_PATH / "config.yaml"


def project_name_finder() -> Set:
    repo_config = load_yaml(REPOCONFIG_PATH)["Projectproperties"].keys()
    return set(repo_config)
