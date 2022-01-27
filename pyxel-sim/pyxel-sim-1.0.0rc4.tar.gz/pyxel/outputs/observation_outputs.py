#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""TBW."""

import operator
import typing as t
from pathlib import Path

from typing_extensions import Literal

from pyxel.observation import ParameterMode
from pyxel.outputs import Outputs

if t.TYPE_CHECKING:
    from pyxel.observation import ObservationResult

    class SaveToFile(t.Protocol):
        """TBW."""

        def __call__(
            self, data: t.Any, name: str, with_auto_suffix: bool = True
        ) -> Path:
            """TBW."""
            ...


ValidName = Literal[
    "detector.image.array", "detector.signal.array", "detector.pixel.array"
]
ValidFormat = Literal["fits", "hdf", "npy", "txt", "csv", "png"]


class ObservationOutputs(Outputs):
    """TBW."""

    def __init__(
        self,
        output_folder: t.Union[str, Path],
        save_data_to_file: t.Optional[
            t.Sequence[t.Mapping[ValidName, t.Sequence[ValidFormat]]]
        ] = None,
        save_observation_data: t.Optional[
            t.Sequence[t.Mapping[str, t.Sequence[str]]]
        ] = None,
    ):
        super().__init__(
            output_folder=output_folder, save_data_to_file=save_data_to_file
        )

        self.save_observation_data = (
            save_observation_data
        )  # type: t.Optional[t.Sequence[t.Mapping[str, t.Sequence[str]]]]

    def save_observation_datasets(
        self, result: "ObservationResult", mode: "ParameterMode"
    ) -> None:
        """Save the result datasets from parametric mode on disk.

        Parameters
        ----------
        result: Result
        mode: ParameterMode

        Returns
        -------
        None
        """

        dataset_names = ("dataset", "parameters", "logs")

        save_methods = {"nc": self.save_to_netcdf}  # type: t.Dict[str, SaveToFile]

        if self.save_observation_data is not None:

            for (
                dct
            ) in self.save_observation_data:  # type: t.Mapping[str, t.Sequence[str]]
                first_item, *_ = dct.items()
                obj, format_list = first_item

                if obj not in dataset_names:
                    raise ValueError(
                        "Please specify a valid result dataset names ('dataset', 'parameters', 'logs')."
                    )

                if mode == ParameterMode.Sequential and obj == "dataset":
                    dct = operator.attrgetter(obj)(result)
                    for key, value in dct.items():

                        if format_list is not None:
                            for out_format in format_list:

                                if out_format not in save_methods.keys():
                                    raise ValueError(
                                        "Format "
                                        + out_format
                                        + " not a valid save method!"
                                    )

                                func = save_methods[out_format]
                                func(data=value, name=obj + "_" + key)

                else:
                    ds = operator.attrgetter(obj)(result)

                    if format_list is not None:
                        for out_format in format_list:

                            if out_format not in save_methods.keys():
                                raise ValueError(
                                    "Format " + out_format + " not a valid save method!"
                                )

                            func = save_methods[out_format]
                            func(data=ds, name=obj)
