#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""TBW."""
import logging
import typing as t

# from numbers import Number
from pathlib import Path
from time import strftime

# import attr
import dask.delayed as delayed
import h5py as h5
import numpy as np
import pandas as pd
import xarray as xr
from astropy.io import fits as fits
from dask.delayed import Delayed

# from matplotlib import pyplot as plt
from typing_extensions import Literal

from pyxel import __version__ as version

from .outputs import PlotArguments, apply_run_number  # , update_plot, PlotType,

if t.TYPE_CHECKING:
    # from ..calibration import ResultType
    from ..detectors import Detector
    from ..pipelines import Processor

    class SaveToFile(t.Protocol):
        """TBW."""

        def __call__(
            self, data: t.Any, name: str, with_auto_suffix: bool = True
        ) -> Path:
            """TBW."""
            ...


# # Specific for CalibrationPlot
# @attr.s(auto_attribs=True, slots=True, frozen=True)
# class ChampionsPlot:
#     """TBW."""
#
#     plot_args: t.Optional[PlotArguments] = None
#
#
# @attr.s(auto_attribs=True, slots=True, frozen=True)
# class PopulationPlot:
#     """TBW."""
#
#     columns: t.Optional[t.Tuple[int, int]] = None  # TODO: Check this, with validator ?
#     plot_args: t.Optional[PlotArguments] = None
#
#
# @attr.s(auto_attribs=True, slots=True, frozen=True)
# class FittingPlot:
#     """TBW."""
#
#     plot_args: t.Optional[PlotArguments] = None
#
#
# @attr.s(auto_attribs=True, slots=True, frozen=True)
# class CalibrationPlot:
#     """TBW."""
#
#     champions_plot: t.Optional[ChampionsPlot] = None
#     population_plot: t.Optional[PopulationPlot] = None
#     fitting_plot: t.Optional[FittingPlot] = None


# Define type aliases
ValidName = Literal[
    "detector.image.array", "detector.signal.array", "detector.pixel.array"
]
ValidFormat = Literal["fits", "hdf", "npy", "txt", "csv", "png"]


class CalibrationOutputs:
    """TBW."""

    def __init__(
        self,
        output_folder: t.Union[str, Path],
        save_data_to_file: t.Optional[
            t.Sequence[t.Mapping[ValidName, t.Sequence[ValidFormat]]]
        ] = None,
        save_parameter_to_file: t.Optional[dict] = None,
        save_calibration_data: t.Optional[
            t.Sequence[t.Mapping[str, t.Sequence[str]]]
        ] = None,
        # calibration_plot: t.Optional[CalibrationPlot] = None,
    ):
        self._log = logging.getLogger(__name__)

        # self.input_file = None  # type: t.Optional[Path]

        # Parameter(s) specific for 'Calibration'
        self.save_calibration_data = (
            save_calibration_data
        )  # type: t.Optional[t.Sequence[t.Mapping[str, t.Sequence[str]]]]

        # self.calibration_plot = calibration_plot  # type: t.Optional[CalibrationPlot]

        self.user_plt_args = None  # type: t.Optional[PlotArguments]
        self.save_parameter_to_file = save_parameter_to_file  # type: t.Optional[dict]
        self.output_dir = (
            Path(output_folder).joinpath("run_" + strftime("%Y%m%d_%H%M%S")).resolve()
        )  # type: Path

        # if save_data_to_file is None:
        #     self.save_data_to_file = [{'detector.image.array': ['fits']}]       # type: list
        # else:
        # TODO: Not related to a plot. Use by 'single' and 'parametric' modes.
        self.save_data_to_file = (
            save_data_to_file
        )  # type: t.Optional[t.Sequence[t.Mapping[ValidName, t.Sequence[ValidFormat]]]]

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
        #
        # self.plt_args = {}  # type: dict
        #
        # # TODO: Create an object self._fig here ?
        # fig, ax = plt.subplots(1, 1)
        #
        # self._fig = fig  # type: plt.Figure
        # self._ax = ax  # type: plt.Axes
        #
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
    # def save_to_png(
    #     self, data: np.ndarray, name: str, with_auto_suffix: bool = True
    # ) -> Path:
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
    #
    #     if with_auto_suffix:
    #         filename = apply_run_number(self.output_dir.joinpath(f"{name}_??.png"))
    #     else:
    #         filename = self.output_dir / f"{name}.png"
    #
    #     full_filename = filename.resolve()  # type: Path
    #
    #     # TODO: Create a new figure ! Check this
    #     dpi = 300
    #     self._fig.set_size_inches(min(col / dpi, 10.0), min(row / dpi, 10.0))
    #
    #     # ax = plt.Axes(fig, [0.0, 0.0, 1.0, 1.0])
    #     # ax.set_axis_off()
    #     #
    #     # fig.add_axes(ax)
    #     # plt.imshow(data, cmap="gray", extent=[0, col, 0, row])
    #     self._fig.savefig(full_filename, dpi=dpi)
    #
    #     return full_filename

    def save_to_fits(
        self, data: np.ndarray, name: str, with_auto_suffix: bool = True
    ) -> Path:
        """Write array to FITS file."""
        name = str(name).replace(".", "_")

        if with_auto_suffix:
            filename = apply_run_number(self.output_dir.joinpath(f"{name}_??.fits"))
        else:
            filename = self.output_dir / f"{name}.fits"

        full_filename = filename.resolve()  # type: Path
        self._log.info("Save to FITS - filename: '%s'", full_filename)

        hdu = fits.PrimaryHDU(data)
        hdu.header["PYXEL_V"] = (str(version), "Pyxel version")
        hdu.writeto(full_filename, overwrite=False, output_verify="exception")

        return full_filename

    def save_to_hdf(
        self, data: "Detector", name: str, with_auto_suffix: bool = True
    ) -> Path:
        """Write detector object to HDF5 file."""
        name = str(name).replace(".", "_")

        if with_auto_suffix:
            filename = apply_run_number(self.output_dir.joinpath(f"{name}_??.h5"))
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
        self, data: np.ndarray, name: str, with_auto_suffix: bool = True
    ) -> Path:
        """Write data to txt file."""
        name = str(name).replace(".", "_")

        if with_auto_suffix:
            filename = apply_run_number(self.output_dir.joinpath(f"{name}_??.txt"))
        else:
            filename = self.output_dir / f"{name}.txt"

        full_filename = filename.resolve()  # type: Path
        np.savetxt(full_filename, data, delimiter=" | ", fmt="%.8e")

        return full_filename

    def save_to_csv(
        self, data: pd.DataFrame, name: str, with_auto_suffix: bool = True
    ) -> Path:
        """Write Pandas Dataframe or Numpy array to a CSV file."""
        name = str(name).replace(".", "_")

        if with_auto_suffix:
            filename = apply_run_number(self.output_dir.joinpath(f"{name}_??.csv"))
        else:
            filename = self.output_dir / f"{name}.csv"

        full_filename = filename.resolve()
        try:
            data.to_csv(full_filename, float_format="%g")
        except AttributeError:
            np.savetxt(full_filename, data, delimiter=",", fmt="%.8e")

        return full_filename

    def save_to_npy(
        self, data: np.ndarray, name: str, with_auto_suffix: bool = True
    ) -> Path:
        """Write Numpy array to Numpy binary npy file."""
        name = str(name).replace(".", "_")

        if with_auto_suffix:
            filename = apply_run_number(self.output_dir.joinpath(f"{name}_??.npy"))
        else:
            filename = self.output_dir / f"{name}.npy"

        full_filename = filename.resolve()  # type: Path

        np.save(file=full_filename, arr=data)
        return full_filename

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

    def save_to_file(
        self,
        processor: "Processor",
        prefix: t.Optional[str] = None,
        with_auto_suffix: bool = True,
    ) -> t.Sequence[Path]:
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
                        data=data, name=name, with_auto_suffix=with_auto_suffix
                    )  # type: Path

                    filenames.append(filename)

        return filenames

    # # TODO: Specific to 'calibration_plot'
    # def champions_plot(
    #     self,
    #     results: t.Mapping[str, t.Union[Number, np.ndarray]],
    #     champions_file: Path,
    #     island_id: int,
    # ) -> None:
    #     """TBW."""
    #     data = np.loadtxt(champions_file)
    #     generations = data[:, 0].astype(int)
    #     title = "Calibrated parameter: "
    #
    #     a = 1
    #     for key, param_value in results.items():
    #         plt_args = {"xlabel": "generation", "linestyle": "-", "sci_y": True}
    #
    #         param_name = key[slice(key.rfind(".") + 1, None)]
    #         plt_args["ylabel"] = param_name
    #
    #         if param_name == "fitness":
    #             plt_args["title"] = "Champion fitness"
    #             plt_args["color"] = "red"
    #             plt_args["ylabel"] = "fitness"
    #
    #         elif param_name == "island":
    #             continue
    #
    #         else:
    #             if key.rfind(".arguments") == -1:
    #                 mdn = key[: key.rfind("." + param_name)]
    #             else:
    #                 mdn = key[: key.rfind(".arguments")]
    #             model_name = mdn[slice(mdn.rfind(".") + 1, None)]
    #             plt_args["title"] = title + model_name + " / " + param_name
    #             plt_args["ylabel"] = param_name
    #
    #         b = 1
    #         if isinstance(param_value, Number):
    #             column = data[:, a]
    #             self.plot_graph(x=generations, y=column, args=plt_args)
    #
    #         elif isinstance(param_value, np.ndarray):
    #             b = len(param_value)
    #             column = data[:, slice(a, a + b)]
    #             self.plot_graph(x=generations, y=column, args=plt_args)
    #             self._fig.legend([f"index {i}" for i in range(b)])
    #
    #         self.save_plot(filename=f"calibrated_{param_name!s}_id{island_id!s}")
    #         a += b
    #
    # # TODO: Specific to 'calibration_plot' ??
    # def population_plot(
    #     self,
    #     # results: dict,
    #     population_file: Path,
    #     island_id: int,
    # ) -> None:
    #     """TBW."""
    #     assert self.calibration_plot
    #
    #     data = np.loadtxt(population_file)  # type: np.ndarray
    #     fitnesses = np.log10(data[:, 1])
    #     a, b = 2, 1  # 1st parameter and fitness
    #     if self.calibration_plot.population_plot:
    #         if self.calibration_plot.population_plot.columns:
    #             col = self.calibration_plot.population_plot.columns
    #             a, b = col[0], col[1]
    #     x = data[:, a]
    #     y = data[:, b]
    #
    #     plt_args = {
    #         "title": "Population of the last generation",
    #         "size": 8,
    #         "cbar_label": "log(fitness)",
    #     }
    #     if b == 0:
    #         plt_args["ylabel"] = "generation"
    #     elif b == 1:
    #         plt_args["ylabel"] = "fitness"
    #     else:
    #         plt_args["ylabel"] = "champions file column #" + str(b)
    #
    #     if a == 0:
    #         plt_args["xlabel"] = "generation"
    #     elif a == 1:
    #         plt_args["xlabel"] = "fitness"
    #     else:
    #         plt_args["xlabel"] = "champions file column #" + str(a)
    #
    #     if a == 1 or b == 1:
    #         plt_args["sci_y"] = True
    #         self.plot_scatter(x, y, args=plt_args)
    #     else:
    #         self.plot_scatter(x, y, color=fitnesses, args=plt_args)
    #
    #     self.save_plot(filename=f"population_id{island_id}")

    # TODO: Specific to 'calibration_plot'
    def calibration_outputs(self, processor_list: "t.Sequence[Processor]") -> None:
        """TBW."""
        if self.save_data_to_file:
            for processor in processor_list:
                self.save_to_file(processor)

                # if self._single_plot:
                #    self.single_to_plot(processor)

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

    # TODO: Specific to 'calibration_plot'
    # def calibration_plots(self, results: t.Mapping, fitness: float) -> None:
    #     """TBW."""
    #     assert self.calibration_plot
    #
    #     if self.calibration_plot:
    #         if self.calibration_plot.champions_plot:
    #             self.user_plt_args = None
    #
    #             if self.calibration_plot.champions_plot.plot_args:
    #                 self.user_plt_args = self.calibration_plot.champions_plot.plot_args
    #
    #             for iid, file_ch in enumerate(
    #                 self.output_dir.glob("champions_id*.out")
    #             ):
    #                 self.champions_plot(
    #                     results={"fitness": fitness, **results},
    #                     champions_file=file_ch,
    #                     island_id=iid,
    #                 )
    #
    #         if self.calibration_plot.population_plot:
    #             self.user_plt_args = None
    #             if self.calibration_plot.population_plot.plot_args:
    #                 self.user_plt_args = self.calibration_plot.population_plot.plot_args
    #
    #             for iid, file_pop in enumerate(
    #                 self.output_dir.glob("population_id*.out")
    #             ):
    #                 self.population_plot(
    #                     # results=results,
    #                     population_file=file_pop,
    #                     island_id=iid,
    #                 )

    # # TODO: Specific to 'calibration_plot' ??
    # def fitting_plot(
    #     self, target_data: np.ndarray, simulated_data: np.ndarray, data_i: int
    # ) -> None:
    #     """TBW."""
    #     assert self.calibration_plot
    #
    #     if self.calibration_plot.fitting_plot:
    #         self._ax.plot(target_data, ".-", label=f"target data #{data_i}")
    #         self._ax.plot(simulated_data, ".-", label=f"simulated data #{data_i}")
    #         self._fig.canvas.draw_idle()
    #
    # # TODO: Specific to 'calibration_plot' ??
    # def fitting_plot_close(self, result_type: "ResultType", island: int) -> None:
    #     """TBW."""
    #     assert self.calibration_plot
    #
    #     if self.calibration_plot.fitting_plot:
    #         self.user_plt_args = None
    #         if self.calibration_plot.fitting_plot.plot_args is None:
    #             raise RuntimeError
    #
    #         self.user_plt_args = self.calibration_plot.fitting_plot.plot_args
    #
    #         user_plt_args_dct = None  # type: t.Optional[t.Mapping[str, t.Any]]
    #         if isinstance(self.user_plt_args, PlotArguments):
    #             user_plt_args_dct = self.user_plt_args.to_dict()
    #
    #         args = {
    #             "title": f"Target and Simulated ({result_type}) "
    #             f"data, "
    #             f"island {island}"
    #         }
    #         ax_args0, plt_args0 = self.update_args(
    #             plot_type=PlotType.Graph, new_args=args
    #         )
    #         ax_args, plt_args = self.update_args(
    #             plot_type=PlotType.Graph,
    #             new_args=user_plt_args_dct,
    #             ax_args=ax_args0,
    #             plt_args=plt_args0,
    #         )
    #         update_plot(ax_args=ax_args, ax=self._ax)
    #         # plt.legend()
    #         self._fig.legend()
    #
    #         self.save_plot(filename=f"fitted_datasets_id{island}")
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

    def save_calibration_outputs(self, dataset: xr.Dataset, logs: pd.DataFrame) -> None:
        """Save the calibration outputs such as dataset and logs.

        Parameters
        ----------
        dataset: xr.Dataset
        logs: pd.DataFrame

        Returns
        -------
        None
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
