#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""Sampling outputs."""

import typing as t
from pathlib import Path

import xarray as xr

from .single_outputs import SingleOutputs

if t.TYPE_CHECKING:

    class SaveToFile(t.Protocol):
        """TBW."""

        def __call__(
            self, data: t.Any, name: str, with_auto_suffix: bool = True
        ) -> Path:
            """TBW."""
            ...


class DynamicOutputs(SingleOutputs):
    """TBW."""

    def __init__(
        self,
        output_folder: t.Union[str, Path],
        save_data_to_file: t.Optional[
            t.Sequence[t.Mapping[str, t.Sequence[str]]]
        ] = None,
        save_dynamic_data: t.Optional[
            t.Sequence[t.Mapping[str, t.Sequence[str]]]
        ] = None,
    ):
        super().__init__(
            output_folder=output_folder, save_data_to_file=save_data_to_file
        )
        self.save_dynamic_data = (
            save_dynamic_data
        )  # type: t.Optional[t.Sequence[t.Mapping[str, t.Sequence[str]]]]

    def save_to_netcdf(
        self, data: xr.Dataset, name: str, with_auto_suffix: bool = False
    ) -> Path:
        """Write Xarray dataset to NetCDF file.

        Parameters
        ----------
        data: xr.Dataset
        name: str

        Returns
        -------
        filename: path
        """
        name = str(name).replace(".", "_")
        filename = self.output_dir.joinpath(name + ".nc")
        data.to_netcdf(filename)
        return filename

    def save_dynamic_outputs(self, dataset: xr.Dataset) -> None:
        """Save the dynamic outputs such as the dataset.

        Parameters
        ----------
        dataset: xr.Dataset

        Returns
        -------
        None
        """

        save_methods = {"nc": self.save_to_netcdf}  # type: t.Dict[str, SaveToFile]

        if self.save_dynamic_data is not None:

            for dct in self.save_dynamic_data:  # type: t.Mapping[str, t.Sequence[str]]

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
