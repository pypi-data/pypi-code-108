from typing import List, Optional, Set, Tuple
import os
import logging

from datasets import Dataset, Features, Value, Sequence, load_from_disk
import attrs
from attrs import frozen


logger = logging.getLogger(__name__)


def type2features(cls) -> Features:
    """
    A helper function for turning an attrs class into the corresponding dataset.Features object
    """

    # if Optional grab actual type
    if type(cls) is type(Optional[str]):
        cls = cls.__args__[0]

    # if list, sequence of inner type
    if type(cls) is type(List[str]):
        return Sequence(type2features(cls.__args__[0]))

    # scalars
    if cls is str:
        return Value("string")
    if cls is int:
        return Value("int32")
    if cls is float:
        return Value("float32")

    # if is an attrs class, recurse and update
    if attrs.has(cls):
        features = {}
        for field in attrs.fields(cls):
            field_feature = type2features(field.type)
            features[field.name] = field_feature
        return Features(**features)

    raise NotImplementedError(str(types))


def try_load_dataset(filename: str) -> Optional[Dataset]:
    """
    Tries to load the dataset from a cache. Returns None if the path does not exist or if there was an error.
    """
    if os.path.exists(filename):
        try:
            dataset = load_from_disk(filename)
            logger.debug(f"loaded cached dataset from {filename}")
            return dataset
        except Exception as e:
            logger.error(f"could not load dataset from {filename}: {e}")
    return None


@frozen
class Args:
    as_objs: bool
    as_dataset: bool
    as_dataframe: bool


def check_args(as_objs: bool, as_dataset: bool, as_dataframe: bool) -> Args:

    if sum([as_objs, as_dataframe, as_dataset]) > 1:
        raise ValueError(
            "Only one of 'as_objs', 'as_dataframe', or 'as_dataste' must be set."
        )

    # as_dataframe is the default
    if not (as_objs or as_dataset):
        as_dataframe = True

    return Args(as_objs=as_objs, as_dataset=as_dataset, as_dataframe=as_dataframe)
