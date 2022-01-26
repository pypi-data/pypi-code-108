#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021, 2022.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""Classes for creating outputs."""
import logging
import os
import re
import typing as t
from glob import glob
from pathlib import Path
from time import strftime

import h5py as h5
import numpy as np
import pandas as pd
import xarray as xr
from typing_extensions import Literal

from pyxel import __version__ as version

if t.TYPE_CHECKING:
    from pyxel.detectors import Detector
    from pyxel.pipelines import Processor

    class SaveToFile(t.Protocol):
        """TBW."""

        def __call__(
            self,
            data: t.Any,
            name: str,
            with_auto_suffix: bool = True,
            run_number: t.Optional[int] = None,
        ) -> Path:
            """TBW."""
            ...


ValidName = Literal[
    "detector.image.array", "detector.signal.array", "detector.pixel.array"
]
ValidFormat = Literal["fits", "hdf", "npy", "txt", "csv", "png"]


class Outputs:
    """TBW."""

    def __init__(
        self,
        output_folder: t.Union[str, Path],
        save_data_to_file: t.Optional[
            t.Sequence[t.Mapping[ValidName, t.Sequence[ValidFormat]]]
        ] = None,
    ):
        self._log = logging.getLogger(__name__)

        self.output_dir = create_output_directory(output_folder)  # type: Path

        # TODO: Not related to a plot. Use by 'single' and 'parametric' modes.
        self.save_data_to_file = (
            save_data_to_file
        )  # type: t.Optional[t.Sequence[t.Mapping[ValidName, t.Sequence[ValidFormat]]]]

    def __repr__(self):
        cls_name = self.__class__.__name__  # type: str
        return f"{cls_name}<output_dir={self.output_dir!r}>"

    def save_to_fits(
        self,
        data: np.ndarray,
        name: str,
        with_auto_suffix: bool = True,
        run_number: t.Optional[int] = None,
    ) -> Path:
        """Write array to FITS file."""
        name = str(name).replace(".", "_")

        if with_auto_suffix:
            filename = apply_run_number(
                template_filename=self.output_dir.joinpath(f"{name}_?.fits"),
                run_number=run_number,
            )
        else:
            filename = self.output_dir / f"{name}.fits"

        full_filename = filename.resolve()  # type: Path
        self._log.info("Save to FITS - filename: '%s'", full_filename)

        from astropy.io import fits  # Late import to speed-up general import time

        hdu = fits.PrimaryHDU(data)
        hdu.header["PYXEL_V"] = (str(version), "Pyxel version")
        hdu.writeto(full_filename, overwrite=False, output_verify="exception")

        return full_filename

    def save_to_hdf(
        self,
        data: "Detector",
        name: str,
        with_auto_suffix: bool = True,
        run_number: t.Optional[int] = None,
    ) -> Path:
        """Write detector object to HDF5 file."""
        name = str(name).replace(".", "_")

        if with_auto_suffix:
            filename = apply_run_number(
                template_filename=self.output_dir.joinpath(f"{name}_?.h5"),
                run_number=run_number,
            )
        else:
            filename = self.output_dir / f"{name}.h5"

        full_filename = filename.resolve()  # type: Path

        with h5.File(full_filename, "w") as h5file:
            h5file.attrs["pyxel-version"] = str(version)
            if name == "detector":
                detector_grp = h5file.create_group("detector")
                for array, name in zip(
                    [
                        data.signal.array,
                        data.image.array,
                        data.photon.array,
                        data.pixel.array,
                        data.charge.frame,
                    ],
                    ["Signal", "Image", "Photon", "Pixel", "Charge"],
                ):
                    dataset = detector_grp.create_dataset(name, shape=np.shape(array))
                    dataset[:] = array
            else:
                raise NotImplementedError
                # detector_grp = h5file.create_group("data")
                # dataset = detector_grp.create_dataset(name, shape=np.shape(data))
                # dataset[:] = data
        return filename

    def save_to_txt(
        self,
        data: np.ndarray,
        name: str,
        with_auto_suffix: bool = True,
        run_number: t.Optional[int] = None,
    ) -> Path:
        """Write data to txt file."""
        name = str(name).replace(".", "_")

        if with_auto_suffix:
            filename = apply_run_number(
                template_filename=self.output_dir.joinpath(f"{name}_?.txt"),
                run_number=run_number,
            )
        else:
            filename = self.output_dir / f"{name}.txt"

        full_filename = filename.resolve()  # type: Path
        np.savetxt(full_filename, data, delimiter=" | ", fmt="%.8e")

        return full_filename

    def save_to_csv(
        self,
        data: pd.DataFrame,
        name: str,
        with_auto_suffix: bool = True,
        run_number: t.Optional[int] = None,
    ) -> Path:
        """Write Pandas Dataframe or Numpy array to a CSV file."""
        name = str(name).replace(".", "_")

        if with_auto_suffix:
            filename = apply_run_number(
                template_filename=self.output_dir.joinpath(f"{name}_?.csv"),
                run_number=run_number,
            )
        else:
            filename = self.output_dir / f"{name}.csv"

        full_filename = filename.resolve()
        try:
            data.to_csv(full_filename, float_format="%g")
        except AttributeError:
            np.savetxt(full_filename, data, delimiter=",", fmt="%.8e")

        return full_filename

    def save_to_npy(
        self,
        data: np.ndarray,
        name: str,
        with_auto_suffix: bool = True,
        run_number: t.Optional[int] = None,
    ) -> Path:
        """Write Numpy array to Numpy binary npy file."""
        name = str(name).replace(".", "_")

        if with_auto_suffix:
            filename = apply_run_number(
                template_filename=self.output_dir.joinpath(f"{name}_?.npy"),
                run_number=run_number,
            )
        else:
            filename = self.output_dir / f"{name}.npy"

        full_filename = filename.resolve()  # type: Path

        if os.path.exists(full_filename):
            raise FileExistsError(f"File {str(full_filename)} already exists!")

        np.save(file=full_filename, arr=data)
        return full_filename

    def save_to_file(
        self,
        processor: "Processor",
        prefix: t.Optional[str] = None,
        with_auto_suffix: bool = True,
        run_number: t.Optional[int] = None,
    ) -> t.Sequence[Path]:
        """Save outputs into file(s).

        Parameters
        ----------
        run_number
        prefix
        with_auto_suffix
        processor : Processor

        Returns
        -------
        list of Path
            TBW.
        """
        save_methods = {
            "fits": self.save_to_fits,
            "hdf": self.save_to_hdf,
            "npy": self.save_to_npy,
            "txt": self.save_to_txt,
            "csv": self.save_to_csv,
            # "png": self.save_to_png,
        }  # type: t.Mapping[ValidFormat, SaveToFile]

        filenames = []  # type: t.List[Path]

        dct: t.Mapping[ValidName, t.Sequence[ValidFormat]]
        if self.save_data_to_file:
            for dct in self.save_data_to_file:
                # TODO: Why looking at first entry ? Check this !
                # Get first entry of `dict` 'item'
                first_item: t.Tuple[ValidName, t.Sequence[ValidFormat]]
                first_item, *_ = dct.items()

                obj: ValidName
                format_list: t.Sequence[ValidFormat]
                obj, format_list = first_item

                data = processor.get(obj)  # type: np.ndarray

                if prefix:
                    name = f"{prefix}_{obj}"  # type: str
                else:
                    name = obj

                out_format: ValidFormat
                for out_format in format_list:
                    func = save_methods[out_format]  # type: SaveToFile
                    filename = func(
                        data=data,
                        name=name,
                        with_auto_suffix=with_auto_suffix,
                        run_number=run_number,
                    )  # type: Path

                    filenames.append(filename)

        return filenames

    def save_to_netcdf(
        self, data: xr.Dataset, name: str, with_auto_suffix: bool = False
    ) -> Path:
        """Write Xarray dataset to NetCDF file.

        Parameters
        ----------
        data: Dataset
        name: str

        Returns
        -------
        filename: Path
        """
        name = str(name).replace(".", "_")
        filename = self.output_dir.joinpath(name + ".nc")
        data.to_netcdf(filename)
        return filename


# TODO: Refactor this in 'def apply_run_number(folder, template_filename) -> Path'.
#       See #332.
def apply_run_number(
    template_filename: Path, run_number: t.Optional[int] = None
) -> Path:
    """Convert the file name numeric placeholder to a unique number.

    Parameters
    ----------
    template_filename
    run_number

    Returns
    -------
    output_path: Path
    """
    template_str = str(template_filename)

    def get_number(string: str) -> int:
        search = re.search(r"\d+$", string.split(".")[-2])
        if not search:
            return 0
        else:
            return int(search.group())

    if "?" in template_str:
        if run_number is not None:
            path_str = template_str.replace("?", "{}")
            output_str = path_str.format(run_number + 1)
        else:
            path_str_for_glob = template_str.replace("?", "*")
            dir_list = glob(path_str_for_glob)
            num_list = sorted([get_number(d) for d in dir_list])
            if len(num_list):
                next_num = num_list[-1] + 1
            else:
                next_num = 1
            path_str = template_str.replace("?", "{}")
            output_str = path_str.format(next_num)

    output_path = Path(output_str)

    return output_path


# TODO: the log file should directly write in 'output_dir'
def save_log_file(output_dir: Path) -> None:
    """Move log file to the outputs directory of the simulation."""
    log_file = Path("pyxel.log").resolve(strict=True)  # type: Path

    new_log_filename = output_dir.joinpath(log_file.name)
    log_file.rename(new_log_filename)


def create_output_directory(output_folder: t.Union[str, Path]) -> Path:
    """Create output directory in the output folder.

    Parameters
    ----------
    output_folder: str or Path

    Returns
    -------
    output_dir: Path
    """

    add = ""
    count = 0

    while True:
        try:
            output_dir = (
                Path(output_folder)
                .joinpath("run_" + strftime("%Y%m%d_%H%M%S") + add)
                .resolve()
            )  # type: Path

            output_dir.mkdir(parents=True, exist_ok=False)

        except FileExistsError:
            count += 1
            add = "_" + str(count)
            continue

        else:
            return output_dir
