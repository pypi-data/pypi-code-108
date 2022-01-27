#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""Single outputs."""

import typing as t
from pathlib import Path

from typing_extensions import Literal

from pyxel.outputs import Outputs

if t.TYPE_CHECKING:
    import xarray as xr

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


class ExposureOutputs(Outputs):
    """TBW."""

    def __init__(
        self,
        output_folder: t.Union[str, Path],
        save_data_to_file: t.Optional[
            t.Sequence[t.Mapping[ValidName, t.Sequence[ValidFormat]]]
        ] = None,
        save_exposure_data: t.Optional[
            t.Sequence[t.Mapping[str, t.Sequence[str]]]
        ] = None,
    ):
        super().__init__(
            output_folder=output_folder, save_data_to_file=save_data_to_file
        )

        self.save_exposure_data = (
            save_exposure_data
        )  # type: t.Optional[t.Sequence[t.Mapping[str, t.Sequence[str]]]]

    def save_exposure_outputs(self, dataset: "xr.Dataset") -> None:
        """Save the observation outputs such as the dataset.

        Parameters
        ----------
        dataset: Dataset
        """

        save_methods = {"nc": self.save_to_netcdf}  # type: t.Dict[str, SaveToFile]

        if self.save_exposure_data is not None:

            for dct in self.save_exposure_data:  # type: t.Mapping[str, t.Sequence[str]]

                first_item, *_ = dct.items()
                obj, format_list = first_item

                if obj == "dataset":

                    if format_list is not None:
                        for out_format in format_list:

                            if out_format not in save_methods.keys():
                                raise ValueError(
                                    "Format " + out_format + " not a valid save method!"
                                )

                            func = save_methods[out_format]
                            func(data=dataset, name=obj)

                else:
                    raise NotImplementedError(f"Object {obj} unknown.")
