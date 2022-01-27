import os
from pathlib import Path
from typing import Dict, List, Tuple

import cognite.airworkflow.constants as const
from cognite.airworkflow.model.config import Config
from cognite.airworkflow.model.deployment import Deployment
from cognite.airworkflow.util import file, yaml


def write_dependency_yamls(config: Dict[Path, Config]):
    for model_path, values in config.items():
        if values.dependencies:
            dep_dict = {i.split("==")[0]: i.split("==")[1] for i in values.dependencies}
            yaml.write_yaml(
                model_path / const.FUNCTION_REL_DEPLOYMENT_PATH,
                dep_dict,
                create_dirs=True,
            )


def get_parallel_deployment(model_name: str, project: str, config: Dict[Path, Config] = None) -> List[Deployment]:
    config = config if config else get_master_config()[0]
    for path, info in config.items():
        if path.name == model_name:
            model_version = info.model_version
            return [Deployment(project, path, model_version, info.secret_names)]

    raise ValueError(f"Model/Function named {model_name} is not defined. Please check that it's not ignored.")


def get_function_paths() -> List[Path]:
    ignore_models = file.read_file_to_list(const.IGNORE_MODELS_PATH)
    directory_contents = os.listdir(const.FUNCTIONS_PATH)
    directory_paths = list(
        map(
            lambda x: const.FUNCTIONS_PATH / x,
            filter(lambda x: x not in ignore_models, directory_contents),
        )
    )
    function_paths = [x / const.FUNCTION_REL_CONFIG_PATH for x in directory_paths if os.path.isdir(x)]
    return function_paths


def get_project_to_config_map(master_config: Dict[Path, Config]) -> Dict[str, Dict[Path, Config]]:
    project_to_config: Dict[str, Dict[Path, Config]] = {}

    for path, config in master_config.items():
        for project_name in config.deploy:
            project = project_name
            if project not in project_to_config:
                project_to_config[project] = {}
            project_to_config[project][path] = config

    return project_to_config


def get_master_config() -> Tuple[Dict[Path, Config], Dict[str, Dict[Path, Config]]]:
    function_paths = get_function_paths()
    master_config = yaml.load_and_validate_multiple(function_paths, const.CONFIG_SCHEMA_PATH)
    write_dependency_yamls(master_config)
    project_to_config = get_project_to_config_map(master_config)
    return master_config, project_to_config


if __name__ == "__main__":
    print(get_master_config())
