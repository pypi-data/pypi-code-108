import os

import yaml
from pydantic import BaseModel


class Config(BaseModel):
    port: int


def parse_config(root: str = None) -> Config:
    """
    Args:
        None
    Returns:
        Config built from set resources path
    """
    root = root if root else os.path.expanduser("~")
    with open(os.path.join(root, ".umm/config.yaml")) as f:
        config = yaml.full_load(f)
    return Config.parse_obj(config)
