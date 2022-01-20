from qa4sm_reader.img import QA4SMImg, SpatialExtentError
from qa4sm_reader.handlers import QA4SMMetric
import qa4sm_reader.globals as glob
from qa4sm_reader.plotter import QA4SMPlotter
import qa4sm_reader.plotting_methods as plm

from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from typing import Union
from warnings import warn

from qa4sm_reader.exceptions import ComparisonError


class QA4SMComparison:
    """
    Class that provides comparison plots and table for a list of netCDF files. As initialising a QA4SMImage can
    take some time, the class can be updated keeping memory of what has already been initialized
    """

    def __init__(self, paths: list or str, extent: tuple = None, get_intersection: bool = True):
        """
        Initialise the QA4SMImages from the paths to netCDF files specified

        Parameters
        ----------
        paths : list or str
            list of paths or single path to .nc validation results files to use for the comparison
        extent : tuple, optional (default: None)
            Area to subset the values for. At the moment has not been implemented as a choice in the service
            (min_lon, max_lon, min_lat, max_lat)
        get_intersection : bool, default is True
            Whether to get the intersection or union of the two spatial exents

        Attributes
        ----------
        compared : list of <QA4SMImg object>
            all the initialized images for the comparison
        ref : tuple
            QA4SMImage for the reference validation
        """
        self.paths = paths
        self.extent = extent

        self.compared = self._init_imgs(extent=extent, get_intersection=get_intersection)
        self.ref = self._check_ref()
        self.union = not get_intersection

    def _init_imgs(self, extent: tuple = None, get_intersection: bool = True) -> list:
        """
        Initialize the QA4SMImages for the selected validation results files. If 'extent' is specified, this is used. If
        not, by default the intersection of results is taken and the images are initialized with it, unless 'get_union'
        is specified. In this case, only diff_table and diff_boxplots can be created (as only non-pairwise methods).

        Parameters
        ----------
        extent: tuple, optional. Default is None
            exent of stapial subset (minlon, maxlon, minlat, maxlat)
        get_intersection : bool, optional. Default is True.
            if extent is not specified, we can either take the union or intersection of the original extents of the
            passed .nc files. This affects the diff_table and diff_boxplot methods, whereas the diff_corr, diff_mapplot
            and diff_plot ALWAYS consider the intersection.

        Returns
        -------
        compared : list of <QA4SMImg object>
            all the initialized images for the comparison
        """
        if self.single_image:
            if isinstance(self.paths, list):
                self.paths = self.paths[0]

            img = QA4SMImg(self.paths, extent=extent, empty=True)
            if not len(img.datasets.others) > 1:
                raise ComparisonError(
                    "A single validation was initialized, with a single "
                    "non-reference dataset. You should add another comparison term."
                )

            return [img]

        compared = []
        for n, path in enumerate(self.paths):
            if extent:
                try:
                    img = QA4SMImg(path, extent=extent, empty=True)
                    compared.append(img)
                except SpatialExtentError as e:
                    e.message = "One of the initialised validation result files has no points in the " \
                                "given spatial subset: " + ", ".join(*extent) + \
                                ".\nYou should change subset to a valid one, or not pass any."
                    raise e
            else:
                # save the state 'union' or 'intersection' to a class attribute
                self.union = True
                img = QA4SMImg(path, empty=True)

                compared.append(img)

        if get_intersection:
            extent = self._combine_geometry(
                get_intersection=get_intersection,
                imgs=compared,
            )
            self.extent = extent
            self.union = False

        return compared

    def init_union(self):
        """Re-initialize the images using the union of spatial extents"""
        self.compared = self._init_imgs(extent=None, get_intersection=False)
        # make sure the new state is stored in the class attribute
        assert self.union

    def _check_ref(self) -> str:
        """Check that all initialized validation results have the same dataset as reference """
        for n, img in enumerate(self.compared):
            ref = img.datasets.ref
            if n != 0:
                if not ref == previous:
                    raise ComparisonError(
                        "The initialized validation results have different reference "
                        "datasets. This is currently not supported"
                    )
            previous = ref

        return ref

    @property
    def common_metrics(self) -> dict:
        """Get dict {short_name: pretty_name} of metrics that can be used in the comparison"""
        for n, img in enumerate(self.compared):
            img_metrics = {}
            for metric in img.metrics:
                # hardcoded because n_obs cannot be compared. todo: exclude empty metrics (problem: the values are not loaded here)
                if metric in glob.metric_groups[0] or metric in ["tau", "p_tau"]:
                    continue
                img_metrics[metric] = glob._metric_name[metric]
            if n == 0:
                common_metrics = img_metrics
                continue
            common_keys = common_metrics.keys() & img_metrics.keys()
            common_metrics = {k: common_metrics[k] for k in common_keys}

        return common_metrics

    @property
    def overlapping(self) -> bool:
        """Return True if the initialised validation results have overlapping spatial extents, else False"""
        if self.single_image:  # one validation is always on the same bounds
            return True

        polys = []
        for img in self.compared:  # get names and extents for all images
            minlon, maxlon, minlat, maxlat = img.extent
            bounds = [(minlon, minlat), (maxlon, minlat),
                      (maxlon, maxlat), (minlon, maxlat)]
            Pol = Polygon(bounds)
            polys.append(Pol)

        for n, Pol in enumerate(polys):
            if n == 0:
                output = Pol  # define starting point
            output = output.intersection(Pol)

        return output.bounds != ()

    @property
    def single_image(self) -> bool:
        """Whether the initialized image(s) are 1 (double) or 2 (single)"""
        if isinstance(self.paths, str):
            return True
        else:
            return len(self.paths) == 1

    @property
    def validation_names(self) -> list:
        """Create pretty names for the validations that are compared. Should always return 2 values"""
        names = []
        template = "Validation {}: {} validated against {}"
        for n, img in enumerate(self.compared):
            datasets = img.datasets
            if len(datasets.others) == 2:
                for n, ds_meta in enumerate(datasets.others):
                    name = template.format(
                        n, ds_meta["pretty_title"],
                        datasets.ref["pretty_title"]
                    )
                    names.append(name)
                break
            else:
                other = img.datasets.others[0]
                name = template.format(
                    n, other["pretty_title"],
                    img.datasets.ref["pretty_title"]
                )
                names.append(name)

        return names

    def _check_pairwise(self) -> Union[bool, ComparisonError]:
        """
        Checks that the current initialized supports pairwise comparison methods

        Raise
        -----
        ComparisonException : if not
        """
        pairwise = True
        for n, img in enumerate(self.compared):
            if img.datasets.n_datasets() > 2 or n > 1:
                pairwise = False
                break

        if not pairwise:
            raise ComparisonError(
                "For pairwise comparison methods, only two "
                "validation results with two datasets each can be compared"
            )

    def get_reference_points(self) -> tuple:
        """
        Get lon, lat arrays for all the reference points in the two validations from the DataArray directly
        (avoid getting them from one of the variables)

        Returns
        -------
        ref_points: np.array
            2D array of lons, lats
        """
        lat, lon, gpi = glob.index_names

        lon_list, lat_list = [], []
        for img in self.compared:
            lon_list.append(img.ds[lon].values)
            lat_list.append(img.ds[lat].values)

        ref_points = np.vstack((
            np.concatenate(lon_list),
            np.concatenate(lat_list),
        )).T

        return ref_points

    def _combine_geometry(
            self,
            imgs: list,
            get_intersection: bool = True,
            return_polys=False
    ) -> tuple:
        """
        Return the union or the intersection of the spatial extents of the provided validations; in case of intersection,
        check that the validations are overlapping

        Parameters
        ----------
        imgs : list
            list with the QA4SMImg corresponding to the paths
        get_intersection : bool, optional. Default is True.
            get extent of the intersection between the two images
        return_polys: bool, default is False.
            whether to return a dictionary with the polygons

        Return
        ------
        extent: tuple
            spatial extent deriving from union or intersection of inputs
        """
        polys = {}

        for n, img in enumerate(imgs):
            minlon, maxlon, minlat, maxlat = img.extent
            bounds = [(minlon, minlat), (maxlon, minlat),
                      (maxlon, maxlat), (minlon, maxlat)]
            Pol = Polygon(bounds)
            name = "Validation {}: ".format(n) + img.name
            polys[name] = Pol

        for n, Pol in enumerate(polys.values()):
            if n == 0:
                # define starting point
                output = Pol
            if not get_intersection or self.single_image:
                # get maximum extent
                output = output.union(Pol)
            # get maximum common
            else:
                output = output.intersection(Pol)
                if not output:
                    raise SpatialExtentError(
                        "The spatial extents of the chosen validation results do "
                        "not overlap. Set 'get_intersection' to False to perform the comparison."
                    )
        polys["selection"] = output

        minlon, minlat, maxlon, maxlat = output.bounds

        if return_polys:
            return (minlon, maxlon, minlat, maxlat), polys

        else:
            return minlon, maxlon, minlat, maxlat

    def visualize_extent(
            self,
            intersection: bool = True,
            plot_points: bool = False,
    ):
        """
        Method to get and visualize the comparison extent including the reference points.

        Parameters
        ----------
        intersection : bool, optional. Default is True.
            choose to visualize the intersection or union output of the comparison
        plot_points : bool, default is False.
            whether to show the reference points in the image
        """
        # self.compared has not been initialized yet
        extent, polys = self._combine_geometry(
            imgs=self.compared,
            get_intersection=intersection,
            return_polys=True,
        )
        ref_points = None
        if plot_points:
            ref_points = self.get_reference_points()

        # same for all initialized images, as reference dataset is the same
        ref_grid_stepsize = self.compared[0].ref_dataset_grid_stepsize

        ref = self._check_ref()["short_name"]
        plm.plot_spatial_extent(
            polys=polys,
            ref_points=ref_points,
            overlapping=self.overlapping,
            intersection_extent=extent,
            reg_grid=(ref != "ISMN"),
            grid_stepsize=ref_grid_stepsize
        )

    def _get_data(self, metric: str) -> dict:  # todo: use new handlers to get metadata for Variable
        """
        Get the list of image Variable names from a metric

        Parameters
        ----------
        metric: str
            name of metric

        Returns
        -------
        varnames: dict
            dict of {"varlist":[list of var dfs], "ci_list":[list of CIs dfs]
        """
        varnames = {"varlist": [], "ci_list": []}
        n = 0
        for i, img in enumerate(self.compared):
            for Var in img._iter_vars(
                    type="metric",
                    filter_parms={"metric": metric}
            ):
                var_cis = []
                id = i
                varname = Var.varname
                data = img._ds2df(varnames=[varname])[varname]
                if not Var.is_CI:
                    if self.single_image:
                        id = n
                    col_name = "Validation {}:\n{}\n".format(
                        id, QA4SMPlotter._box_caption(Var, tc=Var.g == 3)
                    )
                    data = data.rename(col_name)
                    varnames["varlist"].append(data)
                    n += 1
                    # get CIs too, if present
                    for CI_Var in img._iter_vars(
                            type="ci",
                            filter_parms={"metric": metric, "metric_ds": Var.metric_ds}
                    ):
                        # a bit of necessary code repetition
                        varname = CI_Var.varname
                        data = img._ds2df(varnames=[varname])[varname]
                        col_name = CI_Var.bound
                        data = data.rename(col_name)
                        var_cis.append(data)

                if var_cis:
                    varnames["ci_list"].append(var_cis)

        return varnames

    def subset_with_extent(self, dfs: list) -> list:
        """
        Return the original dataframe with only the values included in the selected extent. Basically the
        same method as in QA4SMImg, but it is done here to avoid re-initializing the images

        Returns
        -------
        subset : pd.Series or pd.DataFrame
            initial input with only valid entries in the index
        """
        if self.extent is None:
            return dfs

        lat, lon, gpi = glob.index_names
        subset = []
        for df in dfs:
            mask = (df.index.get_level_values(lon) >= self.extent[0]) & (
                        df.index.get_level_values(lon) <= self.extent[1]) & \
                   (df.index.get_level_values(lat) >= self.extent[2]) & (
                               df.index.get_level_values(lat) <= self.extent[3])
            df.where(mask, inplace=True)
            subset.append(df)

        return subset

    def rename_with_stats(self, df):
        """Rename columns of df by adding the content of QA4SMPlotter._box_stats()"""
        renamed = [
            name + plm._box_stats(df[name]) for name in df.columns
        ]
        df.columns = renamed

        return df

    def _handle_multiindex(self, dfs: list) -> pd.DataFrame:
        """
        Handle ValueError 'cannot handle a non-unique multi-index!' when non-unique multi-index is different in
        the two dfs (e.g. multiple station depths). Update: should have been solved by simply adding gpi to the
        Dataframe index

        Parameters
        ----------
        dfs : pd.DataFrame
            DataFrame of variables to be plotted
        """
        try:
            pair_df = pd.concat(dfs, axis=1, join="outer")
        except ValueError:
            pair_df = []
            if self.overlapping:
                # take mean of non-unique values in multi-index (practically speaking, different depths)
                for df in dfs:
                    df = df.groupby(df.index).mean()
                    pair_df.append(df)
                pair_df = pd.concat(pair_df, axis=1)
                lat, lon, gpi = glob.index_names
                pair_df.index.set_names([lat, lon], inplace=True)
            else:
                # take all values; they cannot be compared directly anyway. Index can be dropped as lon, lat info
                # will not be used in this comparison
                for df in dfs:
                    df.reset_index(drop=True, inplace=True)
                    pair_df.append(df)
                pair_df = pd.concat(pair_df, axis=1)

        return pair_df

    def _get_pairwise(
            self,
            metric: str,
            add_stats: bool = True,
            return_cis=False
    ) -> pd.DataFrame:
        """
        Get the data and names for pairwise comparisons, meaning: two validations with one satellite dataset each. Includes
        a method to subset the metric values to the selected spatial extent.

        Parameters
        ----------
        metric: str
            name of metric to get data on
        add_stats: bool
            If true, add statistics to the label

        Returns
        -------
        renamed: pd.DataFrame
            Renamed dataframe, ready to be plotted
        """
        to_plot, names = [], []
        # check wether the comparison has one single image and the number of sat datasets
        if self.single_image and not self.perform_checks():
            raise ComparisonError(
                "More than two non-reference datasets are not supported at the moment"
            )
        var_data = self._get_data(metric)

        subset = self.subset_with_extent(var_data["varlist"])
        pair_df = self._handle_multiindex(subset)

        if self.overlapping:
            diff = pair_df.iloc[:, 0] - pair_df.iloc[:, 1]
            diff = diff.rename(
                "Difference of common points\nbetween validations 0 and 1\n"
            )
            pair_df = pd.concat([pair_df, diff], axis=1)
        if add_stats:
            pair_df = self.rename_with_stats(pair_df)

        if return_cis and var_data["ci_list"]:

            cis_dfs = []
            for var_cis in var_data["ci_list"]:
                cis_subset = self.subset_with_extent(var_cis)
                ci_df = self._handle_multiindex(cis_subset)
                cis_dfs.append(ci_df)

            return pair_df, cis_dfs

        elif return_cis and not var_data["ci_list"]:
            return pair_df, None

        else:
            return pair_df

    def perform_checks(self, overlapping=False, union=False, pairwise=False):
        """Performs selected checks and throws error is they're not passed"""
        if self.single_image:
            return len(self.compared[0].datasets.others) <= 2

        # these checks are for multiple images
        else:
            if overlapping:
                if not self.overlapping:
                    raise SpatialExtentError(
                        "This method works only in case the initialized "
                        "validations have overlapping spatial extents."
                    )
            # todo: check behavior here if union is initialized through init_union
            if union and not self.extent:
                if self.union:
                    raise SpatialExtentError(
                        "If the comparison is based on the 'union' of spatial extents, "
                        "this method cannot be called, as it is based on a point-by-point comparison"
                    )
            if pairwise:
                self._check_pairwise()

    def diff_table(self, metrics: list) -> pd.DataFrame:
        """
        Create a table where all the metrics for the different validation runs are compared

        Parameters
        ----------
        metrics: list
            list of metrics to create the table for
        """
        self.perform_checks(pairwise=True)
        table = {}
        for metric in metrics:
            ref = self._check_ref()["short_name"]
            units = glob._metric_description_HTML[metric].format(
                glob._metric_units_HTML[ref]
            )
            description = glob._metric_name[metric] + units
            medians = self._get_pairwise(metric).median()
            # a bit of a hack here
            table[description] = [
                medians[0],
                medians[1],
                medians[0] - medians[1]
            ]
        columns = self.validation_names
        columns.append("Difference of the medians (0 - 1)")
        table = pd.DataFrame.from_dict(
            data=table,
            orient="index",
            columns=columns,
        )

        table = table.applymap(plm._format_floats)

        return table

    def diff_boxplot(self, metric: str, **kwargs):
        """
        Create a boxplot where two validations are compared. If the comparison is on the subsets union,
        the shown difference corresponds only to the points in the common spatial extent.

        Parameters
        ----------
        metric: str
            metric name which the plot is based on
        """
        self.perform_checks(pairwise=True)
        df, ci = self._get_pairwise(metric=metric, return_cis=True)
        # prepare axis name
        Metric = QA4SMMetric(metric)
        ref_ds = self.ref['short_name']
        um = glob._metric_description[metric].format(glob._metric_units[ref_ds])
        figwidth = glob.boxplot_width * (len(df.columns) + 1)
        figsize = [figwidth, glob.boxplot_height]
        fig, axes = plm.boxplot(
            df,
            ci=ci,
            label="{} {}".format(Metric.pretty_name, um),
            figsize=figsize,
        )
        # titles for the plot
        fonts = {"fontsize": 12}
        title_plot = "Comparison of {} {}\nagainst the reference {}".format(Metric.pretty_name, um,
                                                                            self.ref["pretty_title"])
        axes.set_title(title_plot, pad=glob.title_pad, **fonts)

        plm.make_watermark(fig, glob.watermark_pos, offset=0.04)
        plt.tight_layout()

    def diff_mapplot(self, metric: str, **kwargs):
        """
        Create a pairwise mapplot of the difference between the validations, for a metric. Difference is other - reference

        Parameters
        ----------
        metric: str
            metric from the .nc result file attributes that the plot is based on
        **kwargs : kwargs
            plotting keyword arguments
        """
        self.perform_checks(overlapping=True, union=True, pairwise=True)
        df = self._get_pairwise(metric=metric, add_stats=False).dropna()
        Metric = QA4SMMetric(metric)
        um = glob._metric_description[metric].format(glob._metric_units[self.ref['short_name']])
        # make mapplot
        cbar_label = "Difference between {} and {}".format(*df.columns)

        fig, axes = plm.mapplot(
            df.iloc[:, 2],
            metric=metric,
            ref_short=self.ref['short_name'],
            diff_map=True,
            label=cbar_label
        )
        fonts = {"fontsize": 12}
        title_plot = "Overview of the difference in {} {}\nagainst the reference {}".format(Metric.pretty_name, um,
                                                                                            self.ref["pretty_title"])
        axes.set_title(title_plot, pad=glob.title_pad, **fonts)

        plm.make_watermark(fig, glob.watermark_pos, offset=0.08)

    def wrapper(self, method: str, metric=None, **kwargs):
        """
        Call the method using a list of paths and the already initialised images

        Properties
        ----------
        method: str
            a method from the lookup table in diff_method
        metric: str
            metric from the .nc result file attributes that the plot is based on
        **kwargs : kwargs
            plotting keyword arguments
        """
        diff_methods_lut = {'boxplot': self.diff_boxplot,
                            'mapplot': self.diff_mapplot}
        try:
            diff_method = diff_methods_lut[method]
        except KeyError as e:
            warn(
                'Difference method not valid. Choose one of %s' % ', '.join(diff_methods_lut.keys())
            )
            raise e

        if not metric:
            raise ComparisonError(
                "If you chose '{}' as a method, you should specify"
                " a metric (e.g. 'R').".format(method)
            )

        return diff_method(
            metric=metric,
            **kwargs
        )
