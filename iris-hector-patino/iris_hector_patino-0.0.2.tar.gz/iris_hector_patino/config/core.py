from pathlib import Path
from typing import List

from pydantic import BaseModel
from strictyaml import YAML, load

import iris_hector_patino

PACKAGE_ROOT = Path(iris_hector_patino.__file__).resolve().parent
ROOT = PACKAGE_ROOT.parent
CONFIG_FILE_PATH = PACKAGE_ROOT / "config.yml"
DATASET_DIR = PACKAGE_ROOT / "datasets"
TRAINED_MODEL_DIR = PACKAGE_ROOT / "trained_models"


class AppConfig(BaseModel):
    """
    Aplication-level config
    """

    # names in config.yml
    package_name: str
    training_data_file: str
    test_data_file: str
    pipeline_save_file: str
    id_column: str
    shuffle: bool


class ModelConfig(BaseModel):
    """
    All configurations relevant to the model
    training and feature engineering
    """

    target: str
    test_size: float
    random_state: int
    pipeline_name: str
    pipeline_save_file: str
    n_estimators: int
    learning_rate: float
    max_depth: int
    gamma: float
    subsample: float
    features_to_combine: List[str]


class Config(BaseModel):
    """
    Master config class.
    """

    app_config: AppConfig
    model_config: ModelConfig


def find_config_file() -> Path:
    """
    Find the config file in the project root
    """
    if CONFIG_FILE_PATH.is_file():
        return CONFIG_FILE_PATH
    else:
        raise Exception(f"Could not find config file at {CONFIG_FILE_PATH}")


def fetch_config_from_yaml(cfg_path: Path = None) -> YAML:
    """
    Parse YAML containing the package configuration
    """
    if not cfg_path:
        cfg_path = find_config_file()
    if cfg_path:
        with open(cfg_path, "r") as config_file:
            parsed_config = load(config_file.read())
            return parsed_config
    raise OSError(f"Could not find config file at {cfg_path}")


def create_and_validate_config(parsed_config: YAML = None) -> Config:
    """Run validation on config values."""
    if parsed_config is None:
        parsed_config = fetch_config_from_yaml()
    # specify the data attribute from the strictymal YAML type.
    _config = Config(
        app_config=AppConfig(**parsed_config.data),
        model_config=ModelConfig(**parsed_config.data),
    )
    return _config


config = create_and_validate_config()
