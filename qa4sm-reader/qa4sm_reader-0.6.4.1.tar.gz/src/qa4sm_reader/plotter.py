# -*- coding: utf-8 -*-
import warnings
from pathlib import Path

import pandas as pd
from typing import Union
import numpy as np
import matplotlib.pyplot as plt

from qa4sm_reader.img import QA4SMImg
import qa4sm_reader.globals as globals
from qa4sm_reader import plotting_methods as plm

from qa4sm_reader.exceptions import PlotterError
from warnings import warn


class QA4SMPlotter():
    """
    Class to create image files of plots from the validation results in a QA4SMImage
    """

    def __init__(self, image: QA4SMImg, out_dir: str = None):
        """
        Create box plots from results in a qa4sm output file.

        Parameters
        ----------
        image : QA4SMImg
            The results object.
        out_dir : str, optional (default: None)
            Path to output generated plot. If None, defaults to the current working directory.
        """
        self.img = image
        self.out_dir = self.get_dir(out_dir=out_dir)

        self.ref = image.datasets.ref

        try:
            self.img.vars
        except AttributeError:
            raise PlotterError(
                "The initialized QA4SMImg object has not been loaded. 'load_data' needs "
                "to be set to 'True' in the initialization of the Image."
            )

    def get_dir(self, out_dir: str) -> Path:
        """Use output path if specified, otherwise same directory as the one storing the netCDF file"""
        if out_dir:
            out_dir = Path(out_dir)  # use directory if specified
            if not out_dir.exists():
                out_dir.mkdir()  # make if not existing
        else:
            out_dir = self.img.filepath.parent  # use default otherwise

        return out_dir

    def _standard_filename(self, out_name: str, out_type: str = 'png') -> Path:
        """
        Standardized behaviour for filenames: if provided name has extension, it is kept; otherwise, it is saved as
        .png to self.out_dir

        Parameters
        ----------
        out_name : str
            output filename (with or without extension)
        out_type : str, optional
            contains file extensions to be plotted. If None, uses 'png'

        Returns
        -------
        outname: pathlib.Path
            correct path of the file
        """
        out_name = Path(out_name)
        # provide output directory
        out_path = self.out_dir.joinpath(out_name)

        # provide output file type
        if not out_path.suffix:
            if out_type[0] != '.':
                out_type = '.' + out_type
            out_path = out_path.with_suffix(out_type)

        return out_path

    @staticmethod
    def _box_caption(Var, tc: bool = False) -> str:
        """
        Create the dataset part of the box (axis) caption

        Parameters
        ----------
        Var: MetricVar
            variable for a metric
        tc: bool, default is False
            True if TC. Then, caption starts with "Other Data:"

        Returns
        -------
        capt: str
            box caption
        """
        ref_meta, mds_meta, other_meta = Var.get_varmeta()
        ds_parts = []
        id, meta = mds_meta
        if tc:
            id, meta = other_meta
        ds_parts.append('{}-{}\n({})\nVariable: {} [{}]'.format(
            id,
            meta['pretty_name'],
            meta['pretty_version'],
            meta['pretty_variable'],
            meta['mu'])
        )
        capt = '\n and \n'.join(ds_parts)

        if tc:
            capt = 'Other Data:\n' + capt

        return capt

    @staticmethod
    def _get_parts_name(Var, type='boxplot_basic') -> list:
        """
        Create parts for title according to the type of plot

        Parameters
        ----------
        Var: MetricVar
            variable for a metric
        type: str
            type of plot

        Returns
        -------
        parts: list of parts for title
        """
        parts = []
        ref, mds, other = [meta for meta in Var.get_varmeta()]
        if type == 'boxplot_basic':
            parts.append(ref[0])
            parts.extend([ref[1]['pretty_name'], ref[1]['pretty_version']])

        elif type in ['boxplot_tc', 'mapplot_basic', 'mapplot_tc']:
            parts.append(mds[0])
            parts.extend([mds[1]['pretty_name'], mds[1]['pretty_version']])
            parts.append(ref[0])
            parts.extend([ref[1]['pretty_name'], ref[1]['pretty_version']])

            if type == 'mapplot_tc':
                parts.append(other[0])
                parts.extend([other[1]['pretty_name'], other[1]['pretty_version']])

        return parts

    @staticmethod
    def _titles_lut(type: str) -> str:
        """
        Lookup table for plot titles

        Parameters
        ----------
        type: str
            type of plot
        """
        titles = {
            'boxplot_basic': 'Intercomparison of {} \nwith {}-{} ({}) as the reference\n ',
            'boxplot_tc': 'Intercomparison of {} \nfor {}-{} ({}) \nwith {}-{} ({}) as the reference\n ',
            'mapplot_basic': '{} for {}-{} ({}) with {}-{} ({}) as the reference',
            'mapplot_tc': '{} for {}-{} ({}) with {}-{} ({}) and {}-{} ({}) as the references',
            'metadata': 'Intercomparison of {} by {}\nwith reference: {}',
        }

        try:
            return titles[type]

        except KeyError:
            raise PlotterError(
                f"type '{type}' is not in the lookup table"
            )

    @staticmethod
    def _filenames_lut(type: str) -> str:
        """
        Lookup table for file names

        Parameters
        ----------
        type: str
            type of plot
        """
        # we stick to old naming convention
        names = {
            'boxplot_basic': 'boxplot_{}',
            'mapplot_common': 'overview_{}',
            'boxplot_tc': 'boxplot_{}_for_{}-{}',
            'mapplot_double': 'overview_{}-{}_and_{}-{}_{}',
            'mapplot_tc': 'overview_{}-{}_and_{}-{}_and_{}-{}_{}_for_{}-{}',
            'metadata': 'boxplot_{}_metadata_{}',
            'table': 'statistics_table',
        }

        try:
            return names[type]

        except KeyError:
            raise PlotterError(
                f"type '{type}' is not in the lookup table"
            )

    def create_title(self, Var, type: str) -> str:
        """
        Create title of the plot

        Parameters
        ----------
        Var: MetricVar
            variable for a metric
        type: str
            type of plot
        """
        parts = [globals._metric_name[Var.metric]]
        parts.extend(self._get_parts_name(Var=Var, type=type))
        title = self._titles_lut(type=type).format(*parts)

        return title

    def create_filename(self, Var, type: str) -> str:
        """
        Create name of the file

        Parameters
        ----------
        Var: MetricVar
            variable for a metric
        type: str
            type of plot
        """
        name = self._filenames_lut(type=type)
        ref_meta, mds_meta, other_meta = Var.get_varmeta()
        # fetch parts of the name for the variable
        if type not in ["mapplot_tc", "mapplot_double"]:
            parts = [Var.metric]
            if mds_meta:
                parts.extend([mds_meta[0], mds_meta[1]['short_name']])
        else:
            parts = [ref_meta[0], ref_meta[1]['short_name']]
            if type == "mapplot_tc":
                # necessary to respect old naming convention
                for dss in Var.other_dss:
                    parts.extend([dss[0], dss[1]['short_name']])
                parts.extend([Var.metric, mds_meta[0], mds_meta[1]['short_name']])
            parts.extend([mds_meta[0], mds_meta[1]['short_name'], Var.metric])

        name = name.format(*parts)

        return name

    def _yield_values(
            self,
            metric: str,
            tc: bool = False,
            stats: bool = True,
            mean_ci: bool = True,
    ) -> tuple:
        """
        Get iterable with pandas dataframes for all variables of a metric to plot

        Parameters
        ----------
        metric: str
            metric name
        tc: bool, default is False
            True if TC. Then, caption starts with "Other Data:"
        stats: bool
            If true, append the statistics to the caption
        mean_ci: bool
            If True, 'Mean CI: {value}' is added to the caption

        Yield
        -----
        df: pd.DataFrame with variable values and caption name
        Var: QA4SMMetricVariable
            variable corresponding to the dataframe
        ci: pd.DataFrame with "upper" and "lower" CI
        """
        Vars = self.img._iter_vars(type="metric", filter_parms={"metric": metric})

        for n, Var in enumerate(Vars):
            values = Var.values[Var.varname]
            # changes if it's a common-type Var
            if Var.g == 0:
                box_cap_ds = 'All datasets'
            else:
                box_cap_ds = self._box_caption(Var, tc=tc)
            # setting in global for caption stats
            if globals.boxplot_printnumbers:
                box_cap = '{}'.format(box_cap_ds)
                if stats:
                    box_stats = plm._box_stats(values)
                    box_cap = box_cap + "\n{}".format(box_stats)
            else:
                box_cap = box_cap_ds
            df = values.to_frame(box_cap)

            ci = self.img.get_cis(Var)
            if ci:  # could be that variable doesn't have CIs - empty list
                ci = pd.concat(ci, axis=1)
                label = ""
                if mean_ci:
                    # get the mean CI range
                    diff = ci["upper"] - ci["lower"]
                    ci_range = float(diff.mean())
                    label = "\nMean CI range: {:.3g}".format(ci_range)
                df.columns = [
                    df.columns[0] + label
                ]
            else:
                ci = None
            # values are all Nan or NaNf - not plotted
            df_arr = df.to_numpy()
            if np.isnan(df_arr).all() or df_arr.size == 0:
                continue

            yield df, Var, ci

    def _boxplot_definition(
            self,
            metric: str,
            df: pd.DataFrame,
            type: str,
            ci=None,
            offset=0.07,
            Var=None,
            **kwargs
    ) -> tuple:
        """
        Define parameters of plot

        Parameters
        ----------
        df: pd.DataFrame to plot
        type: str
            one of _titles_lut
        ci : list of Dataframes containing "upper" and "lower" CIs
        xticks: list
            caption to each boxplot (or triplet thereof)
        offset: float
            offset of boxplots
        Var: QA4SMMetricVariable, optional. Default is None
            Specified in case mds meta is needed
        """
        # plot label
        parts = [globals._metric_name[metric]]
        parts.append(globals._metric_description[metric].format(
            globals._metric_units[self.ref['short_name']]))
        label = "{}{}".format(*parts)
        # generate plot
        figwidth = globals.boxplot_width * (len(df.columns) + 1)
        # otherwise it's too narrow
        if metric == "n_obs":
            figwidth = figwidth + 0.2
        figsize = [figwidth, globals.boxplot_height]
        fig, ax = plm.boxplot(
            df=df,
            ci=ci,
            label=label,
            figsize=figsize,
        )
        if not Var:
            # when we only need reference dataset from variables (i.e. is the same):
            for Var in self.img._iter_vars(type="metric", filter_parms={"metric": metric}):
                Var = Var
                break
        if not type == "metadata":
            title = self.create_title(Var, type=type)
            ax.set_title(title, pad=globals.title_pad)
        # add watermark
        if self.img.has_CIs:
            offset = 0.08  # offset smaller as CI variables have a larger caption
        if Var.g == 0:
            offset = 0.03  # offset larger as common metrics have a shorter caption
        if globals.watermark_pos not in [None, False]:
            plm.make_watermark(fig, offset=offset)

        return fig, ax

    def _save_plot(self, out_name: str, out_types: str = 'png') -> list:
        """
        Save plot with name to self.out_dir

        Parameters
        ----------
        out_name: str
            name of output file
        out_types: str or list
            extensions which the files should be saved in

        Returns
        -------
        fnames: list of file names with all the extensions
        """
        fnames = []
        if isinstance(out_types, str):
            out_types = [out_types]
        for ext in out_types:
            fname = self._standard_filename(out_name, out_type=ext)
            if fname.exists():
                warn('Overwriting file {}'.format(fname.name))
            try:
                plt.savefig(fname, dpi='figure', bbox_inches='tight')
            except ValueError:
                continue
            fnames.append(fname.absolute())

        return fnames

    def boxplot_basic(
            self, metric: str,
            out_name: str = None,
            out_types: str = 'png',
            save_files: bool = False,
            **plotting_kwargs
    ) -> Union[list, None]:
        """
        Creates a boxplot for common and double metrics. Saves a figure and returns Matplotlib fig and ax objects for
        further processing.

        Parameters
        ----------
        metric : str
            metric that is collected from the file for all datasets and combined
            into one plot.
        out_name: str
            name of output file
        out_types: str or list
            extensions which the files should be saved in
        save_files: bool, optional. Default is False
            wether to save the file in the output directory
        plotting_kwargs: arguments for _boxplot_definition function

        Returns
        -------
        fnames: list of file names with all the extensions
        """
        fnames, values = [], []
        ci = []
        # we take the last iterated value for Var and use it for the file name
        for df, Var, var_ci in self._yield_values(metric=metric):
            values.append(df)
            if var_ci is not None:
                ci.append(var_ci)

        # handle empty results
        if not values:
            return None
        # put all Variables in the same dataframe
        values = pd.concat(values)
        # create plot
        fig, ax = self._boxplot_definition(
            metric=metric,
            df=values,
            type='boxplot_basic',
            ci=ci,
            **plotting_kwargs
        )
        if not out_name:
            out_name = self.create_filename(Var, type='boxplot_basic')
        # save or return plotting objects
        if save_files:
            fnames = self._save_plot(out_name, out_types=out_types)
            plt.close('all')

            return fnames

        else:
            return fig, ax

    def boxplot_tc(
            self, metric: str,
            out_name: str = None,
            out_types: str = 'png',
            save_files: bool = False,
            **plotting_kwargs
    ) -> list:
        """
        Creates a boxplot for TC metrics. Saves a figure and returns Matplotlib fig and ax objects for
        further processing.

        Parameters
        ----------
        metric : str
            metric that is collected from the file for all datasets and combined
            into one plot.
        out_name: str
            name of output file
        out_types: str or list
            extensions which the files should be saved in
        save_files: bool, optional. Default is False
            wether to save the file in the output directory
        plotting_kwargs: arguments for _boxplot_definition function

        Returns
        -------
        fnames: list of file names with all the extensions
        """
        fnames = []
        # group Vars and CIs relative to the same dataset
        metric_tc, ci = {}, {}
        for df, Var, var_ci in self._yield_values(metric=metric, tc=True):
            id, names = Var.metric_ds
            if var_ci is not None:
                if id in ci.keys():
                    ci[id].append(var_ci)
                else:
                    ci[id] = [var_ci]
            if id in metric_tc.keys():
                metric_tc[id][0].append(df)
            else:
                metric_tc[id] = [df], Var

        for id, values in metric_tc.items():
            dfs, Var = values
            df = pd.concat(dfs)
            # values are all Nan or NaNf - not plotted
            if np.isnan(df.to_numpy()).all():
                continue
            # necessary if statement to prevent key error when no CIs are in the netCDF
            if ci:
                ci_id = ci[id]
            else:
                ci_id = None
            # create plot
            fig, ax = self._boxplot_definition(
                metric=metric,
                df=df,
                ci=ci_id,
                type='boxplot_tc',
                Var=Var,
                **plotting_kwargs
            )
            # save. Below workaround to avoid same names
            if not out_name:
                save_name = self.create_filename(Var, type='boxplot_tc')
            else:
                save_name = out_name
            # save or return plotting objects
            if save_files:
                fns = self._save_plot(save_name, out_types=out_types)
                fnames.extend(fns)
                plt.close('all')

        if save_files:
            return fnames

    def mapplot_var(
            self, Var,
            out_name: str = None,
            out_types: str = 'png',
            save_files: bool = False,
            compute_dpi:bool = True,
            **style_kwargs,
    ) -> Union[list, tuple]:
        """
        Plots values to a map, using the values as color. Plots a scatterplot for
        ISMN and a image plot for other input values.

        Parameters
        ----------
        Var : QA4SMMetricVariab;e
            Var in the image to make the map for.
        out_name: str
            name of output file
        out_types: str or list
            extensions which the files should be saved in
        save_files: bool, optional. Default is False
            wether to save the file in the output directory
        compute_dpi : bool, optional. Default is True.
            if selected, the output resolution of the image is
            calculated on the basis of the resolution of the
            reference dataset and the extent of the validation
            (i.e., hiigh resolution, global validations will
            have the maximum available dpi).
            Otherwise, high resolution datasets are assigned the
            maximum dpi as per globals.max_dpi
        style_kwargs: arguments for mapplot function

        Returns
        -------
        fnames: list of file names with all the extensions
        """
        ref_meta, mds_meta, other_meta = Var.get_varmeta()
        metric = Var.metric
        ref_grid_stepsize = self.img.ref_dataset_grid_stepsize
        res, unit = self.img.res_info.values()
        extent = self.img.extent

        if res is not None:
            if compute_dpi and extent is not None:
                dpi = plm.output_dpi(
                    res,
                    unit,
                    extent,
                )

                style_kwargs["dpi"] = dpi

            elif not compute_dpi and unit == "km" and res <= 1:
                style_kwargs["dpi"] = globals.dpi_max

        # create mapplot
        fig, ax = plm.mapplot(df=Var.values[Var.varname],
                              metric=metric,
                              ref_short=ref_meta[1]['short_name'],
                              ref_grid_stepsize=ref_grid_stepsize,
                              plot_extent=None,  # if None, extent is sutomatically adjusted (as opposed to img.extent)
                              **style_kwargs)

        # title and plot settings depend on the metric group
        if Var.g == 0:
            title = "{} between all datasets".format(globals._metric_name[metric])
            save_name = self.create_filename(Var, type='mapplot_common')
        elif Var.g == 2:
            title = self.create_title(Var=Var, type='mapplot_basic')
            save_name = self.create_filename(Var, type='mapplot_double')
        else:
            title = self.create_title(Var=Var, type='mapplot_tc')
            save_name = self.create_filename(Var, type='mapplot_tc')

        # overwrite output file name if given
        if out_name:
            save_name = out_name

        # use title for plot, make watermark
        ax.set_title(title, pad=globals.title_pad)
        if globals.watermark_pos not in [None, False]:
            plm.make_watermark(fig, globals.watermark_pos, for_map=True, offset=0.04)

        # save file or just return the image
        if save_files:
            fnames = self._save_plot(save_name, out_types=out_types)

            return fnames

        else:
            return fig, ax

    def mapplot_metric(
            self, metric: str,
            out_types: str = 'png',
            save_files: bool = False,
            **plotting_kwargs
    ) -> list:
        """
        Mapplot for all variables for a given metric in the loaded file.

        Parameters
        ----------
        metric : str
            Name of a metric. File is searched for variables for that metric.
        out_types: str or list
            extensions which the files should be saved in
        save_files: bool, optional. Default is False
            wether to save the file in the output directory
        plotting_kwargs: arguments for mapplot function

        Returns
        -------
        fnames : list
            List of files that were created
        """
        fnames = []
        for Var in self.img._iter_vars(type="metric", filter_parms={"metric": metric}):
            if not (np.isnan(Var.values.to_numpy()).all() or Var.is_CI):
                fns = self.mapplot_var(Var,
                                       out_name=None,
                                       out_types=out_types,
                                       save_files=save_files,
                                       **plotting_kwargs)
            # values are all Nan or NaNf - not plotted
            else:
                continue
            if save_files:
                fnames.extend(fns)
                plt.close('all')

        if fnames:
            return fnames

    def plot_metric(
            self, metric: str,
            out_types: str = 'png',
            save_all: bool = True,
            **plotting_kwargs
    ) -> tuple:
        """
        Plot and save boxplot and mapplot for a certain metric

        Parameters
        ----------
        metric: str
            name of the metric
        out_types: str or list
            extensions which the files should be saved in
        save_all: bool, optional. Default is True.
            all plotted images are saved to the output directory
        plotting_kwargs: arguments for mapplot function.
        """
        Metric = self.img.metrics[metric]
        if Metric.g == 0 or Metric.g == 2:
            fnames_bplot = self.boxplot_basic(metric=metric,
                                              out_types=out_types,
                                              save_files=save_all,
                                              **plotting_kwargs)
        elif Metric.g == 3:
            fnames_bplot = self.boxplot_tc(metric=metric,
                                           out_types=out_types,
                                           save_files=save_all,
                                           **plotting_kwargs)
        fnames_mapplot = self.mapplot_metric(metric=metric,
                                             out_types=out_types,
                                             save_files=save_all,
                                             **plotting_kwargs)

        return fnames_bplot, fnames_mapplot

    def meta_single(
            self,
            metric: str,
            metadata: str,
            df: pd.DataFrame = None,
            axis=None,
            plot_type: str = "catplot",
            **plotting_kwargs
    ) -> Union[tuple, None]:
        """
        Boxplot of a metric grouped by the given metadata.

        Parameters
        ----------
        metric : str
            specified metric
        metadata : str
            specified metadata
        df : pd.DataFrame, optional
            metric values can be specified, in which case they will be used from here and
            not parsed from the metric name
        axis : matplotlib.axes.Axis, optional
            if provided, the function will create the plot on the specified axis
        plot_type : str, default is 'catplot'
            one of 'catplot' or 'multiplot', defines the type of plots for the 'classes' and 'continuous'
            metadata types

        Returns
        -------
        fig : matplotlib.figure.Figure
            the boxplot
        ax : matplotlib.axes.Axes
        """
        values = []
        for data, Var, var_ci in self._yield_values(metric=metric, stats=False, mean_ci=False):
            values.append(data)

        values = pd.concat(values, axis=1)
        # override values from metric
        if df is not None:
            values = df
        # get meta and select only metric values with metadata available
        meta_values = self.img.metadata[metadata].values.dropna()
        values = values.reindex(index=meta_values.index)
        mu = globals._metric_description[metric].format(globals._metric_units[self.ref['short_name']])

        out = plm.boxplot_metadata(
            df=values,
            metadata_values=meta_values,
            ax_label=Var.Metric.pretty_name + mu,
            axis=axis,
            plot_type=plot_type,
            **plotting_kwargs
        )

        if axis is None:
            fig, ax = out

            return fig, ax

    def meta_combo(
            self,
            metric: str,
            metadata: str,
            metadata_discrete: str,
    ):
        """
        Cross-boxplot between two given metadata types

        Parameters
        ----------
        metric : str
            specified metric
        metadata: str
            'continuous' or 'classes' metadata which provides the number of subplots (bins)
        metadata_discrete : str
            'discrete' metadata which is shown in the subplots

        Returns
        -------
        fig : matplotlib.figure.Figure
            the boxplot
        ax : matplotlib.axes.Axes
        """
        values = []
        for df, Var, ci in self._yield_values(metric=metric, stats=False, mean_ci=False):
            values.append(df)
        values = pd.concat(values, axis=1)

        metric_name = globals._metric_name[metric]
        metric_units = globals._metric_description[metric].format(
            globals._metric_units[self.img.datasets.ref["short_name"]]
        )

        Meta_cont = self.img.metadata[metadata]
        meta_values = Meta_cont.values.dropna()

        bin_funct = plm.bin_function_lut(globals.metadata[metadata][2])
        binned_values = bin_funct(
            df=values,
            metadata_values=meta_values,
            meta_key=metadata,
        )
        # dictionary with subset values
        values_subset = {
            a_bin: values.reindex(index=binned_values[a_bin].index) for a_bin in binned_values.keys()
        }
        kwargs = {
            "metric": metric,
            "metadata": metadata_discrete,
            "common_y": metric_name + metric_units
        }
        n_datasets = len(self.img.datasets.others)
        fig, axes = plm.aggregate_subplots(
            to_plot=values_subset,
            funct=self.meta_single,
            n_bars=n_datasets,
            **kwargs
        )

        return fig, axes

    def plot_metadata(
            self, metric: str,
            metadata: str,
            metadata_discrete: str = None,
            save_file: bool = False,
            out_types: str = 'png',
            **plotting_kwargs
    ):
        """
        Wrapper built around the 'meta_single' or 'meta_combo' functions to produce a metadata-based boxplot of a
        metric.

        Parameters
        __________
        metric : str
            name of metric to plot
        metadata : str
            name of metadata to subdivide the metric results
        metadata_discrete : str
            name of the metadata of the type 'discrete'

        Retrun
        ------
        fig : matplotlib.figure.Figure
            the boxplot
        ax : matplotlib.axes.Axes
        """
        if metadata_discrete is None:
            fig, ax = self.meta_single(
                metric=metric, metadata=metadata, **plotting_kwargs
            )
            metadata_tuple = [metadata]

        else:
            metadata_tuple = [metadata, metadata_discrete]
            if not any(globals.metadata[i][2] == "discrete" for i in metadata_tuple):
                raise ValueError(
                    "One of the provided metadata names should correspond to the 'discrete' type, see globals.py"
                )
            if all(globals.metadata[i][2] == "discrete" for i in metadata_tuple):
                raise ValueError(
                    "At least one of the provided metadata should not be of the 'continuous' type"
                )
            fig, ax = self.meta_combo(
                metric=metric, metadata=metadata,
                metadata_discrete=metadata_discrete, **plotting_kwargs
            )
        meta_names = [globals.metadata[i][0] for i in metadata_tuple]
        title = self._titles_lut("metadata").format(
            globals._metric_name[metric],
            ", ".join(meta_names),
            self.img.datasets.ref["pretty_title"]
        )
        fig.suptitle(title)

        plm.make_watermark(fig=fig, offset=0)

        if save_file:
            out_name = self._filenames_lut("metadata").format(
                metric,
                "_and_".join(metadata_tuple)
            )
            self._save_plot(out_name, out_types=out_types)

            return out_name

        else:
            return fig, ax

    def plot_save_metadata(self, metric):
        """
        Plots and saves three metadata boxplots per metric (defined in globals.py):

        1. Boxplot by land cover class (2010 map)
        2. Boxplot by Koeppen-Geiger climate classification
        3. Boxplot by instrument depth and soil type (granularity)

        Parameters
        ----------
        metric : str
            name of metric

        Return
        ------
        filenames: list
            list of file names
        """
        filenames = []

        # makes no sense to plot the metadata for some metrics
        if metric in globals._metadata_exclude:
            return filenames

        for type, meta_keys in globals.out_metadata_plots.items():
            # the presence of instrument_depth in the out file depends on the ismn release version
            if all(meta_key in self.img.metadata.keys() for meta_key in meta_keys):
                outfile = self.plot_metadata(metric, *meta_keys, save_file=True)
                filenames.append(outfile)
            else:
                warnings.warn(
                    "Not all: " + ", ".join(meta_keys) + " are present in the netCDF variables"
                )

        return filenames

    def save_stats(self):
        """Saves the summary statistics to a .csv file and returns the name"""
        table = self.img.stats_df()
        filename = self._filenames_lut("table") + '.csv'
        filepath = self.out_dir.joinpath(filename)

        table.to_csv(path_or_buf=filepath)

        return filepath
