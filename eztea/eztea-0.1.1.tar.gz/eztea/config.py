import os
import os.path
from typing import Type, TypeVar

from dotenv import load_dotenv
from validr import fields

__all__ = ("load_env_config",)

T = TypeVar("T")


def load_env_config(
    *,
    model_type: Type[T],
    env_prefix: str,
    default_envfile: str = None,
) -> T:
    """
    Load envfile and convert to config model type.

    Args:
        model_type: validr.modelclass type
        env_prefix: env variable key prefix, eg: 'MY_APP_'
        default_envfile: default envfile path, optional
    """
    envfile_path = os.getenv(f"{env_prefix}CONFIG")
    if not envfile_path:
        if default_envfile and os.path.exists(default_envfile):
            envfile_path = default_envfile
    if envfile_path:
        envfile_path = os.path.abspath(os.path.expanduser(envfile_path))
        print(f"* Load envfile at {envfile_path}")
        load_dotenv(envfile_path)
    configs = {}
    for name in fields(model_type):
        key = (env_prefix + name).upper()
        value = os.environ.get(key, None)
        if value is not None:
            configs[name] = value
    return model_type(configs)
