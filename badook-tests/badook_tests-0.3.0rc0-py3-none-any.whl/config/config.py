from typing import Optional
from .settings import Settings


_config: Settings = None


def set_config(config_file_path: Optional[str]):
    global _config
    _config = Settings(config_file_path=config_file_path)


def set_config_from_settings(settings: Settings):
    global _config
    _config = settings


def get_config():
    return _config
