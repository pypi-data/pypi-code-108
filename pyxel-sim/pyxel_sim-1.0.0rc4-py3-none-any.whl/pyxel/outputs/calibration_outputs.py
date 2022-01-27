#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""TBW."""
import typing as t
from pathlib import Path

import dask.delayed as delayed
import pandas as pd
from dask.delayed import Delayed
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


# Define type aliases
ValidName = Literal[
    "detector.image.array", "detector.signal.array", "detector.pixel.array"
]
ValidFormat = Literal["fits", "hdf", "npy", "txt", "csv", "png"]


class CalibrationOutputs(Outputs):
    """TBW."""

    def __init__(
        self,
        output_folder: t.Union[str, Path],
        save_data_to_file: t.Optional[
            t.Sequence[t.Mapping[ValidName, t.Sequence[ValidFormat]]]
        ] = None,
        save_calibration_data: t.Optional[
            t.Sequence[t.Mapping[str, t.Sequence[str]]]
        ] = None,
    ):
        super().__init__(
            output_folder=output_folder, save_data_to_file=save_data_to_file
        )

        # Parameter(s) specific for 'Calibration'
        self.save_calibration_data = (
            save_calibration_data
        )  # type: t.Optional[t.Sequence[t.Mapping[str, t.Sequence[str]]]]

    def save_processors(self, processors: pd.DataFrame) -> t.Sequence[Delayed]:
        """TBW."""
        lst = []  # type: t.List[delayed.Delayed]

        if self.save_data_to_file:

            for _, serie in processors.iterrows():
                id_island = serie["island"]  # type: int
                id_processor = serie["id_processor"]  # type: int
                processor = serie["processor"]  # type: Delayed

                # TODO: Create folders ?
                prefix = f"island{id_island:02d}_processor{id_processor:02d}"

                output_filenames = delayed(self.save_to_file)(
                    processor=processor, prefix=prefix, with_auto_suffix=False
                )  # type: Delayed
                lst.append(output_filenames)

        return lst

    def save_calibration_outputs(
        self, dataset: "xr.Dataset", logs: pd.DataFrame
    ) -> None:
        """Save the calibration outputs such as dataset and logs.

        Parameters
        ----------
        dataset: Dataset
        logs: DataFrame
        """

        save_methods = {"nc": self.save_to_netcdf}  # type: t.Dict[str, SaveToFile]

        if self.save_calibration_data is not None:

            for (
                dct
            ) in self.save_calibration_data:  # type: t.Mapping[str, t.Sequence[str]]
                first_item, *_ = dct.items()
                obj, format_list = first_item

                if obj == "logs":
                    for format in format_list:
                        if format == "csv":
                            filename = self.output_dir.joinpath("logs.csv")
                            logs.to_csv(filename)
                        elif format == "xlsx":
                            filename = self.output_dir.joinpath("logs.xlsx")
                            logs.to_excel(filename)
                        else:
                            raise NotImplementedError(
                                f"Saving to format {format} not implemented"
                            )

                elif obj == "dataset":

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
