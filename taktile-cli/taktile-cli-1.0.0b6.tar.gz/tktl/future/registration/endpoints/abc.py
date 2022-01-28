import abc
import pathlib
import typing as t

import numpy as np  # type: ignore
import pandas as pd  # type: ignore
from fastapi import Response
from pydantic import BaseModel
from taktile_types.enums.endpoint import EndpointKinds, ProfileKinds

XType = t.Union[
    pd.Series, pd.DataFrame, np.ndarray, BaseModel, t.Any, pathlib.Path, None
]
YType = XType


class Endpoint(abc.ABC):
    kind: EndpointKinds

    def __init__(
        self,
        name: str,
        position: int,
        func: t.Callable[..., t.Coroutine[t.Any, t.Any, Response]],
        X: XType = None,
        y: YType = None,
        profile_columns: t.Optional[t.List[str]] = None,
        profile: t.Optional[ProfileKinds] = None,
        **kwargs,
    ):
        self._kwargs = kwargs
        self._name = name
        self._position = position
        self._func = func
        self._X = X
        self._y = y
        self._profile_columns = profile_columns
        self._profile_kind = profile
        self._tags = kwargs.get("tags", [])

    @property
    def kwargs(self):
        return self._kwargs

    @property
    def name(self):
        return self._name

    @property
    def position(self):
        return self._position

    @property
    def func(self):
        return self._func

    @property
    def X(self):
        return self._X

    @property
    def y(self):
        return self._y

    @property
    def profile_kind(self):
        return self._profile_kind

    @property
    def profile_columns(self):
        return self._profile_columns

    @property
    def input_names(self):
        return []

    @property
    def output_names(self):
        return ""

    @property
    def tags(self) -> t.List[str]:
        return self._tags

    @staticmethod
    @abc.abstractmethod
    def supported(
        *, X: XType = None, y: YType = None, profile: t.Optional[str] = None,
    ) -> bool:
        """supported.
        Given the parameters, is this type of endpoint supported?

        Parameters
        ----------
        X : XType
        y : yType
        profile : t.Optional[str]
            the paramters

        Returns
        -------
        bool - true if supported, false else

        """


TaskType = t.Union[t.Tuple, t.Callable]


class EndpointResponse(t.NamedTuple):
    return_value: YType
    tasks: t.Sequence[TaskType] = []
