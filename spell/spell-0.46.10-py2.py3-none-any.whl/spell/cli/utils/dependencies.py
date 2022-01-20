import os

from spell.shared.dependencies import (
    CondaDependencies,
    in_virtualenv,
    NoEnvFound,
    PipDependencies,
)


def dependencies_from_env():
    if os.environ.get("CONDA_DEFAULT_ENV"):
        return CondaDependencies.from_env()
    elif in_virtualenv():
        return PipDependencies.from_env()
    raise NoEnvFound
