import sys
from pathlib import Path
from typing import Dict

from ruamel.yaml import YAML

from cognite.airworkflow.util import env


def load_yaml(path: Path) -> Dict:
    yaml = YAML(typ="safe").load(path)
    assert isinstance(yaml, dict)
    return yaml


def get_url_dict() -> Dict:
    path_to_dict = env.get_env_value("PWD")
    REPO_BASE_DIR = Path(path_to_dict)
    try:
        repo_config_path = REPO_BASE_DIR / "repoconfig.yaml"
    except FileNotFoundError:
        print("Please put the repoconfig.yaml in the main directory structure")
        sys.exit(1)
    return load_url_dict(repo_config_path)


def load_url_dict(repo_config_path):
    yamlload = load_yaml(repo_config_path)

    try:
        urldict = yamlload["Projectproperties"]
        return urldict

    except KeyError:
        print("Please use the right format for the config file")
        sys.exit(1)
