import os
from typing import List, Union, Dict, Optional, Type

import yaml
from deepmerge import Merger
from pydantic import BaseModel, ValidationError

default_merger = Merger(
    # pass in a list of tuple, with the
    # strategies you are looking to apply
    # to each type.
    [(dict, ["merge"])],
    # next, choose the fallback strategies,
    # applied to all other types:
    ["override"],
    # finally, choose the strategies in
    # the case where the types conflict:
    ["override"],
)


class _Optional(str):
    """
    Wrap a file path with this class to mark it as optional.

    Optional paths don't raise an :class:`IOError` if file is not found.
    """


class ESBgmConfigSchema(BaseModel):
    startdelay: int
    musicdir: str
    restart: bool
    startsong: Optional[str]
    mainprocess: str
    emulation_names: List[str]


def merge(*dicts):
    if len(dicts) < 2:
        raise Exception("Need at least two dicts to merge")

    base = {}
    for dict in dicts:
        default_merger.merge(base, dict)

    return base


def load_registry(base_dir: str,
                  setting_paths: List[Union[str, _Optional]],
                  schema: Type[BaseModel]) -> Dict:
    registry = {}
    for path_str in setting_paths:
        path = os.path.join(base_dir, path_str)
        if os.path.exists(path):
            with open(path) as fs:
                registry = merge(registry, yaml.safe_load(fs))
        elif not isinstance(path_str, _Optional):
            raise IOError("No such file: {0}".format(path_str))

    try:
        registry = schema(**registry)
    except ValidationError as e:
        raise ValueError(e)

    return registry.dict()
