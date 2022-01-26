#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""TBW."""
import logging
import operator
import typing as t
from pathlib import Path
from time import strftime

import h5py as h5
import numpy as np
import pandas as pd
import xarray as xr
from astropy.io import fits as fits

from pyxel import __version__ as version
from pyxel.observation import ParameterMode

from .outputs import apply_run_number

if t.TYPE_CHECKING:
    from ..detectors import Detector
    from ..parametric import ParametricResult
    from ..pipelines import Processor

    class SaveToFile(t.Protocol):
        """TBW."""

        def __call__(self, data: t.Any, name: str) -> Path:
            """TBW."""
            ...


# # TODO Specific to parametric
# @attr.s(auto_attribs=True, slots=True, frozen=True)
# class Result:
#     """TBW."""
#
#     result: np.ndarray  # TODO: Use a `DataFrame` ?
#     plot: np.ndarray


# @attr.s(auto_attribs=True, slots=True)
# class ParametricPlot:
#     """TBW."""
#
#     x: str
#     y: str
#     plot_args: PlotArguments
#
#     @classmethod
#     def from_dict(cls, dct: dict) -> "ParametricPlot":
#         """TBW."""
#         return cls(x=dct["x"], y=dct["y"], plot_args=dct["plot_args"])


class ParametricOutputs:
    """TBW."""

    def __init__(
        self,
        output_folder: t.Union[str, Path],
        save_data_to_file: t.Optional[
            t.Sequence[t.Mapping[str, t.Sequence[str]]]
        ] = None,
        save_parametric_data: t.Optional[
            t.Sequence[t.Mapping[str, t.Sequence[str]]]
        ] = None,
        # save_parameter_to_file: t.Optional[dict] = None,
        # parametric_plot: t.Optional[ParametricPlot] = None,
    ):
        self._log = logging.getLogger(__name__)

        # self.input_file = None  # type: t.Optional[Path]

        # Parameter(s) specific for 'Parametric'
        # self.parametric_plot = None  # type: t.Optional[ParametricPlot]
        # if parametric_plot is not None:
        #    self.parametric_plot = parametric_plot

        # self.parameter_keys = []  # type: t.List[str]

        # self.user_plt_args = None  # type: t.Optional[PlotArguments]
        # self.save_parameter_to_file = save_parameter_to_file  # type: t.Optional[dict]
        self.output_dir = (
            Path(output_folder).joinpath("run_" + strftime("%Y%m%d_%H%M%S")).resolve()
        )  # type: Path

        # TODO: Not related to a plot. Use by 'single' and 'parametric' modes.
        self.save_data_to_file = (
            save_data_to_file
        )  # type: t.Optional[t.Sequence[t.Mapping[str, t.Sequence[str]]]]

        self.save_parametric_data = (
            save_parametric_data
        )  # type: t.Optional[t.Sequence[t.Mapping[str, t.Sequence[str]]]]

        # TODO: reenable
        # if self.output_dir.exists():
        #    raise IsADirectoryError("Directory exists.")

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # self.default_ax_args = {
        #     "xlabel": None,
        #     "ylabel": None,
        #     "title": None,
        #     "axis": None,
        #     "grid": False,
        #     "xscale": "linear",
        #     "yscale": "linear",
        #     "xticks": None,
        #     "yticks": None,
        #     "xlim": [None, None],
        #     "ylim": [None, None],
        #     "sci_x": False,
        #     "sci_y": False,
        # }  # type: dict
        # self.default_ax_args = PlotArguments()
        #
        # self.default_plot_args = {
        #     "color": None,
        #     "marker": ".",
        #     "linestyle": "",
        # }  # type: dict
        #
        # self.default_hist_args = {
        #     "bins": None,
        #     "range": None,
        #     "density": None,
        #     "log": False,
        #     "cumulative": False,
        #     "histtype": "step",
        #     "color": None,
        #     "facecolor": None,
        # }  # type: dict
        # self.default_scatter_args = {"size": None, "cbar_label": None}  # type: dict

        # self.plt_args = {}  # type: dict

        # TODO: Create an object self._fig here ?
        # fig, ax = plt.subplots(1, 1)

        # self._fig = fig  # type: plt.Figure
        # self._ax = ax  # type: plt.Axes

        # plt.close(self._fig)

    def __repr__(self):
        cls_name = self.__class__.__name__  # type: str
        return f"{cls_name}<output_dir={self.output_dir!r}>"

    # @property
    # def fig(self) -> plt.Figure:
    #     """Get the current ``Figure``."""
    #     return self._fig

    def new_file(self, filename: str) -> Path:
        """TBW."""
        new_filename = self.output_dir.joinpath(filename)  # type: Path
        new_filename.touch()

        return new_filename

    # # TODO: Specific to 'single_plot' ?
    # def save_to_png(self, data: np.ndarray, name: str) -> Path:
    #     """Write array to bitmap PNG image file.
    #
    #     Parameters
    #     ----------
    #     data : array
    #     name : str
    #
    #     Returns
    #     -------
    #     Path
    #         TBW.
    #     """
    #     row, col = data.shape
    #     name = str(name).replace(".", "_")
    #     filename = apply_run_number(
    #         self.output_dir.joinpath(f"{name}_??.png")
    #     )  # type: Path
    #
    #     dpi = 300
    #     self._fig.set_size_inches(min(col / dpi, 10.0), min(row / dpi, 10.0))
    #
    #     # ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    #     # ax.set_axis_off()
    #     #
    #     # fig.add_axes(ax)
    #     # plt.imshow(data, cmap="gray", extent=[0, col, 0, row])
    #     self._fig.savefig(filename, dpi=dpi)
    #
    #     return filename

    def save_to_fits(self, data: np.ndarray, name: str) -> Path:
        """Write array to FITS file.

        Parameters
        ----------
        data
        name

        Returns
        -------
        Path
            TBW.
        """
        name = str(name).replace(".", "_")
        filename = apply_run_number(
            self.output_dir.joinpath(f"{name}_??.fits")
        ).resolve()  # type: Path

        self._log.info("Save to FITS - filename: '%s'", filename)

        hdu = fits.PrimaryHDU(data)
        hdu.header["PYXEL_V"] = (str(version), "Pyxel version")
        hdu.writeto(filename, overwrite=False, output_verify="exception")

        return filename

    def save_to_hdf(self, data: "Detector", name: str) -> Path:
        """Write detector object to HDF5 file."""
        name = str(name).replace(".", "_")
        filename = apply_run_number(self.output_dir.joinpath(f"{name}_??.h5"))
        with h5.File(filename, "w") as h5file:
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

    def save_to_txt(self, data: np.ndarray, name: str) -> Path:
        """Write data to txt file."""
        name = str(name).replace(".", "_")
        filename = apply_run_number(self.output_dir.joinpath(name + "_??.txt"))
        np.savetxt(filename, data, delimiter=" | ", fmt="%.8e")
        return filename

    def save_to_csv(self, data: pd.DataFrame, name: str) -> Path:
        """Write Pandas Dataframe or Numpy array to a CSV file."""
        name = str(name).replace(".", "_")
        filename = apply_run_number(
            self.output_dir.joinpath(name + "_??.csv")
        )  # type: Path
        try:
            data.to_csv(filename, float_format="%g")
        except AttributeError:
            np.savetxt(filename, data, delimiter=",", fmt="%.8e")
        return filename

    def save_to_npy(self, data: np.ndarray, name: str) -> Path:
        """Write Numpy array to Numpy binary npy file."""
        name = str(name).replace(".", "_")
        filename = apply_run_number(self.output_dir.joinpath(name + "_??.npy"))
        np.save(file=filename, arr=data)
        return filename

    def save_to_netcdf(self, data: xr.Dataset, name: str) -> Path:
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

    def save_to_file(self, processor: "Processor") -> t.Sequence[Path]:
        """Save outputs into file(s).

        Parameters
        ----------
        processor : Processor


        Returns
        -------
        list of ``Path``
            TBW.
        """
        save_methods = {
            "fits": self.save_to_fits,
            "hdf": self.save_to_hdf,
            "npy": self.save_to_npy,
            "txt": self.save_to_txt,
            "csv": self.save_to_csv,
            # "png": self.save_to_png,
        }  # type: t.Dict[str, SaveToFile]

        filenames = []  # type: t.List[Path]

        if self.save_data_to_file is not None:
            for dct in self.save_data_to_file:  # type: t.Mapping[str, t.Sequence[str]]
                # Get first entry of `dict` 'item'
                first_item, *_ = dct.items()

                obj, format_list = first_item
                data = processor.get(obj)  # type: np.ndarray

                if format_list is not None:
                    for out_format in format_list:
                        func = save_methods[out_format]  # type: SaveToFile
                        filename = func(data=data, name=obj)  # type: Path

                        filenames.append(filename)

        return filenames

    def save_parametric_datasets(
        self, result: "ParametricResult", mode: "ParameterMode"
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

        if self.save_parametric_data is not None:

            for (
                dct
            ) in self.save_parametric_data:  # type: t.Mapping[str, t.Sequence[str]]
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

    # def save_plot(self, filename: str = "figure_??") -> Path:
    #     """Save plot figure in PNG format, close figure and create new canvas for next plot."""
    #     new_filename = self.output_dir.joinpath(filename + ".png")  # type: Path
    #     output_filename = apply_run_number(new_filename).resolve()  # type: Path
    #
    #     self._log.info("Save plot in filename '%s'", output_filename)
    #     self._fig.savefig(output_filename)
    #     # plt.close('all')
    #     # plt.figure()
    #
    #     return output_filename
    #
    # def plot_graph(
    #     self, x: np.ndarray, y: np.ndarray, args: t.Optional[dict] = None
    # ) -> None:
    #     """TBW.
    #
    #     Parameters
    #     ----------
    #     x
    #     y
    #     args
    #     """
    #     ax_args0, plt_args0 = self.update_args(plot_type=PlotType.Graph, new_args=args)
    #
    #     user_plt_args_dct = None  # type: t.Optional[t.Mapping]
    #     if isinstance(self.user_plt_args, PlotArguments):
    #         user_plt_args_dct = self.user_plt_args.to_dict()
    #
    #     ax_args, plt_args = self.update_args(
    #         plot_type=PlotType.Graph,
    #         new_args=user_plt_args_dct,
    #         ax_args=ax_args0,
    #         plt_args=plt_args0,
    #     )
    #
    #     self._ax.plot(
    #         x,
    #         y,
    #         color=plt_args["color"],
    #         marker=plt_args["marker"],
    #         linestyle=plt_args["linestyle"],
    #     )
    #     update_plot(ax_args=ax_args, ax=self._ax)
    #     # plt.draw()
    #
    # def plot_histogram(self, data: np.ndarray, args: t.Optional[dict] = None) -> None:
    #     """TBW.
    #
    #     Parameters
    #     ----------
    #     data
    #     args
    #     """
    #     assert self.user_plt_args is not None
    #
    #     user_plt_args_dct = None  # type: t.Optional[t.Mapping]
    #     if isinstance(self.user_plt_args, PlotArguments):
    #         user_plt_args_dct = self.user_plt_args.to_dict()
    #
    #     ax_args0, plt_args0 = self.update_args(
    #         plot_type=PlotType.Histogram, new_args=args
    #     )
    #     ax_args, plt_args = self.update_args(
    #         plot_type=PlotType.Histogram,
    #         new_args=user_plt_args_dct,
    #         ax_args=ax_args0,
    #         plt_args=plt_args0,
    #     )
    #     if isinstance(data, np.ndarray):
    #         data = data.flatten()
    #
    #     self._ax.hist(
    #         x=data,
    #         bins=plt_args["bins"],
    #         range=plt_args["range"],
    #         density=plt_args["density"],
    #         log=plt_args["log"],
    #         cumulative=plt_args["cumulative"],
    #         histtype=plt_args["histtype"],
    #         color=plt_args["color"],
    #         facecolor=plt_args["facecolor"],
    #     )
    #
    #     update_plot(ax_args=ax_args, ax=self._ax)
    #
    # def plot_scatter(
    #     self,
    #     x: np.ndarray,
    #     y: np.ndarray,
    #     color: t.Optional[str] = None,
    #     args: t.Optional[dict] = None,
    # ) -> None:
    #     """TBW.
    #
    #     Parameters
    #     ----------
    #     x
    #     y
    #     color
    #     args
    #     """
    #     user_plt_args_dct = None  # type: t.Optional[t.Mapping]
    #
    #     if isinstance(self.user_plt_args, PlotArguments):
    #         user_plt_args_dct = self.user_plt_args.to_dict()
    #
    #     ax_args0, plt_args0 = self.update_args(
    #         plot_type=PlotType.Scatter, new_args=args
    #     )
    #     ax_args, plt_args = self.update_args(
    #         plot_type=PlotType.Scatter,
    #         new_args=user_plt_args_dct,
    #         ax_args=ax_args0,
    #         plt_args=plt_args0,
    #     )
    #
    #     # fig = plt.gcf()
    #     # ax = fig.axes
    #
    #     if color is not None:
    #         sp = self._ax.scatter(x, y, c=color, s=plt_args["size"])
    #         cbar = self._fig.colorbar(sp)
    #         cbar.set_label(plt_args["cbar_label"])
    #
    #     else:
    #         self._ax.scatter(x, y, s=plt_args["size"])
    #
    #     update_plot(ax_args=ax_args, ax=self._ax)
    #     # plt.draw()
    #     # fig.canvas.draw_idle()

    # # TODO: Specific to 'parametric_plot' ?
    # def params_func(self, param: "Parametric") -> None:
    #     """Extract all parametric keys from `param`."""
    #     assert self.parameter_keys is not None
    #
    #     # TODO: Re-initialized 'self.parameters' ??
    #
    #     for var in param.enabled_steps:  # type: ParameterValues
    #         if var.key not in self.parameter_keys:
    #             self.parameter_keys += [var.key]
    #
    #     if self.save_parameter_to_file and self.save_parameter_to_file["parameter"]:
    #         for par in self.save_parameter_to_file["parameter"]:
    #             if par is not None and par not in self.parameter_keys:
    #                 self.parameter_keys += [par]
    #
    # # TODO: This function should be moved in `Parametric`
    # # TODO: Specific to 'parametric_plot' ?
    # def extract_func(self, processor: "Processor") -> Result:
    #     """TBW."""
    #     assert self.parameter_keys is not None
    #
    #     # self.single_output(processor.detector)    # TODO: extract other things (optional)
    #
    #     res_row = []  # type: t.List[np.ndarray]
    #     for key in self.parameter_keys:
    #         value = processor.get(key)  # type: np.ndarray
    #         res_row.append(value)
    #
    #     # Extract all parameters keys from 'proc'
    #     # all_attr_getters = operator.attrgetter(self.parameter_keys)  # type: t.Callable
    #     # res_row = all_attr_getters(processor)  # type: t.Tuple[t.Any, ...]
    #
    #     # TODO: Refactor this
    #     plt_row = []  # type: t.List[np.ndarray]
    #     if self.parametric_plot:
    #         for key in [self.parametric_plot.x, self.parametric_plot.y]:
    #             if key is not None:
    #                 value = processor.get(key)
    #                 plt_row.append(value)
    #
    #     return Result(
    #         result=np.array(res_row, dtype=float),
    #         plot=np.array(plt_row, dtype=float),
    #     )
    #
    # # TODO: Specific to 'parametric_mode' ?
    # def merge_func(self, result_list: t.Sequence[Result]) -> np.ndarray:
    #     """TBW."""
    #     assert self.parameter_keys is not None
    #
    #     if self.save_parameter_to_file:
    #         result_array = np.array([k.result for k in result_list])
    #         save_methods = {
    #             "npy": self.save_to_npy,
    #             "txt": self.save_to_txt,
    #             "csv": self.save_to_csv,
    #         }  # type: t.Dict[str, SaveToFile]
    #
    #         for out_format in self.save_parameter_to_file["file_format"]:
    #             func = save_methods[out_format]  # type: SaveToFile
    #             file = func(data=result_array, name="parameters")  # type: Path
    #
    #             if file.suffix in (".txt", ".csv"):
    #                 with file.open("r+") as f:
    #                     content = f.read()
    #                     f.seek(0, 0)
    #                     f.write(
    #                         "# "
    #                         + "".join([pp + " // " for pp in self.parameter_keys])
    #                         + "\n"
    #                         + content
    #                     )
    #     plot_array = np.array([k.plot for k in result_list])  # type: np.ndarray
    #     return plot_array
    #
    # # TODO: Specific to 'parametric_plot' ?
    # def plotting_func(self, plot_array: np.ndarray) -> None:
    #     """TBW.
    #
    #     Parameters
    #     ----------
    #     plot_array : array
    #     """
    #     if not self.parametric_plot:
    #         raise RuntimeError
    #
    #     x_key = self.parametric_plot.x  # type: str
    #     y_key = self.parametric_plot.y  # type: str
    #
    #     self.user_plt_args = self.parametric_plot.plot_args
    #
    #     x = plot_array[:, 0]  # type: np.ndarray
    #     y = plot_array[:, 1]  # type: np.ndarray
    #
    #     par_name = x_key[
    #         x_key[: x_key[: x_key.rfind(".")].rfind(".")].rfind(".") + 1 :  # noqa: E203
    #     ]
    #     res_name = y_key[
    #         y_key[: y_key[: y_key.rfind(".")].rfind(".")].rfind(".") + 1 :  # noqa: E203
    #     ]
    #
    #     args = {"xlabel": par_name, "ylabel": res_name}
    #
    #     if isinstance(x, np.ndarray):
    #         x = x.flatten()
    #     if isinstance(y, np.ndarray):
    #         y = y.flatten()
    #
    #     self.plot_graph(x=x, y=y, args=args)
    #     self.save_plot(filename="parametric_??")
    #
    # def update_args(
    #     self,
    #     plot_type: PlotType,
    #     new_args: t.Optional[t.Mapping] = None,
    #     ax_args: t.Optional[dict] = None,
    #     plt_args: t.Optional[dict] = None,
    # ) -> t.Tuple[dict, dict]:
    #     """TBW."""
    #     if new_args is None:
    #         new_args = {}
    #
    #     if ax_args is None:
    #         ax_args = self.default_ax_args.to_dict()
    #
    #     if plt_args is None:
    #         if plot_type is PlotType.Histogram:
    #             plt_args = self.default_hist_args.copy()
    #         elif plot_type is PlotType.Graph:
    #             plt_args = self.default_plot_args.copy()
    #         elif plot_type is PlotType.Scatter:
    #             plt_args = self.default_scatter_args.copy()
    #         else:
    #             raise ValueError
    #
    #     for key in new_args:
    #         if key in plt_args.keys():
    #             plt_args[key] = new_args[key]
    #         elif key in ax_args.keys():
    #             ax_args[key] = new_args[key]
    #         else:
    #             raise KeyError('Not valid plotting key in "plot_args": "%s"' % key)
    #
    #     return ax_args, plt_args
