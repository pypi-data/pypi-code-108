#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.
#
#
"""Single outputs."""

import logging
import typing as t

# import warnings
from pathlib import Path
from time import strftime

import attr
import h5py as h5
import numpy as np
import pandas as pd
from astropy.io import fits as fits

from pyxel import __version__ as version

from .outputs import PlotArguments, PlotType, apply_run_number  # , update_plot

# from matplotlib import pyplot as plt


if t.TYPE_CHECKING:
    from ..detectors import Detector
    from ..pipelines import Processor

    class SaveToFile(t.Protocol):
        """TBW."""

        def __call__(self, data: t.Any, name: str) -> Path:
            """TBW."""
            ...


@attr.s(auto_attribs=True, slots=True, frozen=True)
class SinglePlot:
    """TBW."""

    plot_type: PlotType = attr.ib(converter=PlotType)
    x: str = "detector.photon.array"  # TODO: Check if the value is valid
    y: str = "detector.image.array"  # TODO: Check if the value is valid
    plot_args: t.Optional[PlotArguments] = None


class SingleOutputs:
    """TBW."""

    def __init__(
        self,
        output_folder: t.Union[str, Path],
        save_data_to_file: t.Optional[
            t.Sequence[t.Mapping[str, t.Sequence[str]]]
        ] = None,
        # single_plot: t.Optional[SinglePlot] = None,
    ):
        self._log = logging.getLogger(__name__)

        # self.input_file = None  # type: t.Optional[Path]

        # Parameter(s) specific for 'Single'
        # self._single_plot = None  # type: t.Optional[SinglePlot]
        # if single_plot:
        #     self._single_plot = single_plot

        # self.user_plt_args = None  # type: t.Optional[PlotArguments]
        self.output_dir = (
            Path(output_folder).joinpath("run_" + strftime("%Y%m%d_%H%M%S")).resolve()
        )  # type: Path

        # TODO: Not related to a plot. Use by 'single' and 'parametric' modes.
        self.save_data_to_file = (
            save_data_to_file
        )  # type: t.Optional[t.Sequence[t.Mapping[str, t.Sequence[str]]]]

        if self.output_dir.exists():
            raise IsADirectoryError("Directory exists.")

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

    # # TODO: Specific to 'single_plot'
    # # TODO: This function is doing too much.
    # def single_output(self, processor: "Processor") -> None:
    #     """Save data into a file and/or generate pictures.
    #
    #     Parameters
    #     ----------
    #     processor
    #     """
    #     warnings.warn(
    #         "Use function 'save_to_file' and 'single_plot'.", DeprecationWarning
    #     )
    #
    #     assert self._single_plot is not None
    #
    #     # if not self.save_data_to_file:
    #     #     self.save_data_to_file = [{"detector.image.array": ["fits"]}]
    #
    #     self.save_to_file(processor)
    #
    #     self.single_to_plot(processor)

    # # TODO: Specific to 'single_plot'
    # def single_to_plot(self, processor: "Processor") -> None:
    #     """Generate picture(s).
    #
    #     Parameters
    #     ----------
    #     processor
    #     """
    #     assert self._single_plot is not None
    #
    #     self.user_plt_args = None
    #     # todo: default plots with plot_args?
    #     color = None
    #
    #     if self._single_plot.plot_args:
    #         plot_args = self._single_plot.plot_args  # type: PlotArguments
    #         self.user_plt_args = plot_args
    #
    #     x = processor.get(self._single_plot.x)
    #     y = processor.get(self._single_plot.y)
    #
    #     x = x.flatten()
    #     y = y.flatten()
    #
    #     if self._single_plot.plot_type is PlotType.Graph:
    #         self.plot_graph(x=x, y=y)
    #         fname = "graph_??"  # type: str
    #
    #     elif self._single_plot.plot_type is PlotType.Histogram:
    #         self.plot_histogram(y)
    #         fname = "histogram_??"
    #
    #     elif self._single_plot.plot_type is PlotType.Scatter:
    #         self.plot_scatter(x, y, color)
    #         fname = "scatter_??"
    #
    #     else:
    #         raise NotImplementedError
    #
    #     self.save_plot(filename=fname)
    #
    #     # plt.close()

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

        if self.save_data_to_file:

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
