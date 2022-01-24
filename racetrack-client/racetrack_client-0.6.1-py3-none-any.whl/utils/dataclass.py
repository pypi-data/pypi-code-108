import dataclasses
from typing import Dict, List, Type, TypeVar

import dacite
import yaml

T = TypeVar("T")


def parse_dict_dataclass(obj_dict: Dict, clazz: Type[T]) -> T:
    """Cast dict object to expected dataclass"""
    return dacite.from_dict(data_class=clazz, data=obj_dict, config=dacite.Config(check_types=True, strict=True))


def parse_dict_dataclasses(obj_list: List[Dict], clazz: Type[T]) -> List[T]:
    """Cast list of dict objects to expected dataclass types"""
    return [parse_dict_dataclass(obj_dict, clazz) for obj_dict in obj_list]


def parse_yaml_dataclass(yaml_obj: str, clazz: Type[T]) -> T:
    """Parse YAML and convert it to expected dataclass"""
    data = yaml.load(yaml_obj, Loader=yaml.FullLoader)
    return parse_dict_dataclass(data, clazz)


def dataclass_to_yaml_str(dt) -> str:
    data_dict = dataclasses.asdict(dt)
    data_dict = _remove_none(data_dict)
    return yaml.dump(data_dict)


def _remove_none(obj):
    """Remove unwanted null values"""
    if isinstance(obj, list):
        return [_remove_none(x) for x in obj if x is not None]
    elif isinstance(obj, dict):
        return {k: _remove_none(v) for k, v in obj.items() if k is not None and v is not None}
    else:
        return obj
