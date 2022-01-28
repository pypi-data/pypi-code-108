from pathlib import Path

import yaml

__all__ = (
    "load_config",
    "safe_load_config",
)


def load_config():
    config_path = Path.home().joinpath(".meili", "cfg.yaml")

    with open(config_path, "r") as cfg_file:
        config = yaml.safe_load(cfg_file)
        return config


def safe_load_config():
    try:
        return load_config()
    except (FileNotFoundError, yaml.YAMLError):
        pass
