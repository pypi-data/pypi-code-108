import pathlib
import typing as t

import pandas as pd  # type: ignore
from taktile_types.enums.endpoint import EndpointKinds, ProfileKinds

from .abc import XType, YType
from .arrow import ArrowEndpoint


class ProfiledEndpoint(ArrowEndpoint):
    kind: EndpointKinds = EndpointKinds.PROFILED

    @property
    def input_names(self):
        return self.profile_columns

    @property
    def output_names(self):
        return self.y.name

    @property
    def profile_columns(self) -> t.Optional[t.List[str]]:
        return (
            self._profile_columns
            if self._profile_columns is not None
            else self.X.columns.to_list()
        )

    @staticmethod
    def supported(
        *, X: XType = None, y: YType = None, profile: t.Optional[str] = None,
    ) -> bool:

        if profile not in ProfileKinds.set():
            return False

        strict = isinstance(X, pd.DataFrame) and isinstance(y, pd.Series)
        lazy = isinstance(X, pathlib.Path) and isinstance(y, pathlib.Path)

        return strict or lazy
