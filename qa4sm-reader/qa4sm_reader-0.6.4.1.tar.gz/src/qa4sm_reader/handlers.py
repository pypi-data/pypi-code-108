# -*- coding: utf-8 -*-
import warnings

from qa4sm_reader import globals
from parse import *
import warnings as warn


class MixinVarmeta:
    """Mixin class to provide functions that are common to the MetricVariable and ConfidenceInterval subclasses"""

    @property
    def pretty_name(self):
        """Create a nice name for the variable"""
        # remove CI part
        if self.is_CI:
            template = "Confidence interval ({}) of ".format(self.bound)
        else:
            template = ""
        template = template + globals._variable_pretty_name[self.g]

        if self.g == 0:
            name = template.format(self.metric)

        elif self.g == 2:
            name = template.format(self.Metric.pretty_name, self.metric_ds[1]['pretty_title'],
                               self.ref_ds[1]['pretty_title'])
        elif self.g == 3:
            name = template.format(self.Metric.pretty_name, self.metric_ds[1]['pretty_title'],
                               self.ref_ds[1]['pretty_title'], self.other_ds[1]['pretty_title'])

        return name

    @property
    def id(self):
        """Id of the metric dataset for g = 2 or 3, of the reference dataset for g = 0"""
        if self.metric_ds:
            return self.metric_ds[0]
        else:
            return self.ref_ds[0]

    def get_varmeta(self) -> (tuple, tuple, tuple):
        """
        Get the datasets from the current variable. Each dataset is provided with shape
        (id, dict{names})

        Returns
        -------
        ref_ds : id, dict
            reference dataset
        mds : id, dict
            this is the dataset for which the metric is calculated
        dss : id, dict
            this is the additional dataset in TC variables
        """
        if self.g == 0:
            ref_ds = self.Datasets.dataset_metadata(self.Datasets._ref_id())
            mds, dss = None, None

        else:
            ref_ds = self.Datasets.dataset_metadata(self.parts['ref_id'])
            mds = self.Datasets.dataset_metadata(self.parts['sat_id0'])
            dss = None
            # if metric is TC, add third dataset
            if self.g == 3:
                mds = self.Datasets.dataset_metadata(self.parts['mds_id'])
                dss = self.Datasets.dataset_metadata(self.parts['sat_id1'])
                if dss == mds:
                    dss = self.Datasets.dataset_metadata(self.parts['sat_id0'])
                # need this to respect old file naming convention
                self.other_dss = [
                    self.Datasets.dataset_metadata(self.parts['sat_id0']),
                    self.Datasets.dataset_metadata(self.parts['sat_id1'])
                ]

        return ref_ds, mds, dss


class QA4SMDatasets():
    """
    Class that provides information on all datasets in the results file. Ids and dcs refer to the
    1-based and 0-based index number of the datasets, respectively. For newer validations, these are always
    the same
    """

    def __init__(self, global_attrs):
        """
        Parameters
        ----------
        global_attrs: dict
            Global attributes of the QA4SM validation result
        """
        # attributes of the result file
        self.meta = global_attrs

    def _ref_dc(self) -> int:
        """
        Get the position of the reference dataset from the results file as a 0-based index

        Returns
        -------
        ref_dc : int
        """
        ref_dc = 0

        try:
            val_ref = self.meta[globals._ref_ds_attr]
            ref_dc = parse(globals._ds_short_name_attr, val_ref)[0]
        except KeyError as e:
            warn("The netCDF file does not contain the attribute {}".format(globals._ref_ds_attr))
            raise e

        return ref_dc

    def _ref_id(self) -> int:
        """Get the dataset id for the reference"""
        dc = self._ref_dc()
        ref_id = dc - self.offset

        return ref_id

    @property
    def offset(self) -> int:
        """Check that the dc number given to the reference is 0, change the ids if not"""
        offset = 0
        if self._ref_dc() != 0:
            offset = -1

        return offset

    def _dcs(self) -> dict:
        """
        Return the ids as in the global attributes and attribute key for each dataset
        that is not the reference

        Returns
        -------
        dcs: dict
            dictionary of the shape {id : attribute key}
        """
        dcs = {}
        for k in self.meta.keys():
            parsed = parse(globals._ds_short_name_attr, k)
            if parsed is not None and len(list(parsed)) == 1:
                dc = list(parsed)[0]
                if dc != self._ref_dc():
                    dcs[dc] = k

        return dcs

    def _fetch_attribute(self, template, dc):
        """
        Try to get the meta attribute from the netCDF file, and fall back to globals if missing

        Parameters
        ----------
        template: str
            globals variable assigned to an attribute (e.g. _version_short_name_attr for val_dc_version{:d})
        dc: int
            The dc of the dataset as in the global metadata of the results file

        Returns
        -------
        meta: str
            Required attribute value
        """
        # try to get from self.meta
        try:
            meta = self.meta[
                globals.__dict__[template].format(dc)
            ]
        # try to get from globals
        except KeyError:
            # if there is an option to use
            if template in globals._backups.keys():
                try:
                    backup_var = globals._backups[template]
                    # use the version short name (should be always in netCDF)
                    meta = globals.__dict__[backup_var][
                        self.meta[globals._version_short_name_attr.format(dc)]
                    ]
                # globals fallback has failed. Raise an exception
                except KeyError or AttributeError:
                    raise Exception(
                        "Either the attribute {} is missing from the netCDF template, or the dictionaries"
                        "in globals are not updated for the datasets used".format(
                            globals._version_short_name_attr.format(dc)
                        )
                    )
            # give warning and return an empty value
            else:
                warnings.warn(
                    "There is no attribute {} in the netCDF dataset. An empty string is returned".format(
                        globals.__dict__[template].format(dc)
                    )
                )
                meta = ""

        return meta

    def _dc_names(self, dc:int) -> dict:
        """
        Get dataset meta values for the passed dc

        Parameters
        ----------
        dc : int
            The dc of the dataset as in the global metadata of the results file

        Returns
        -------
        names : dict
            short name, pretty_name and short_version and pretty_version of the
            dc dataset.
        """
        names = {}

        names['short_name'] = self._fetch_attribute("_ds_short_name_attr", dc)
        names['pretty_name'] = self._fetch_attribute("_ds_pretty_name_attr", dc)
        names['short_version'] = self._fetch_attribute("_version_short_name_attr", dc)
        names['pretty_version'] = self._fetch_attribute("_version_pretty_name_attr", dc)
        names['pretty_variable'] = self._fetch_attribute("_val_dc_variable_pretty_name", dc)
        # not from dataset:
        names['mu'] = "{}".format(globals._metric_units_HTML[names['short_name']])
        # combined name for plots:
        names['pretty_title'] = '{} ({})'.format(names['pretty_name'], names['pretty_version'])

        return names

    @property
    def ref_id(self):
        """Id of the reference dataset as in the variable names"""
        return self._ref_dc() - self.offset

    @property
    def others_id(self):
        """Id of the other datasets as in the variable names"""
        return [dc - self.offset for dc in self._dcs().keys()]

    def _id2dc(self, id:int) -> int:
        """
        Offset ids according to the self.offset value

        Parameters
        ----------
        id: int
            1-based index value of the dataset
        """
        return id + self.offset

    def n_datasets(self) -> int:
        """Counts the total number of datasets (reference + others)"""
        n_others = len(self._dcs().keys())

        return n_others + 1

    @property
    def ref(self) -> dict:
        """Get a dictionary of the dataset metadata for the reference dataset"""
        dc_name = self._dc_names(self._ref_dc())

        return dc_name

    @property
    def others(self) -> list:
        """Get a list with the datset metadata for oll the non-reference datasets"""
        others_meta = []
        for dc in self._dcs():
            dc_name = self._dc_names(dc)
            others_meta.append(dc_name)

        return others_meta

    def dataset_metadata(self, id:int, element:str or list=None) -> tuple:
        """
        Get the metadata for the dataset specified by the id. This function is used by the QA4SMMetricVariable class

        Parameters
        ----------
        elements : str or list
            one of: 'all','short_name','pretty_name','short_version','pretty_version'

        Returns
        -------
        meta: tuple
            tuple with (dataset id, names dict)
        """
        dc = self._id2dc(id=id)
        names = self._dc_names(dc=dc)

        if element is None:
            meta = names

        elif isinstance(element, str):
            if not element in names.keys():
                raise ValueError("Elements must be one of '{}'".format(', '.join(names.keys())))

            meta = names[element]

        else:
            meta = {e: names[e] for e in element}

        return (id, meta)


class QA4SMVariable():
    """Super class for all variable types in the validations (MetricVariable, CI and Metadata)"""

    def __init__(self, varname, global_attrs, values=None):
        """
        Validation results for a validation metric and a combination of datasets.

        Parameters
        ---------
        varname : str
            Name of the variable
        global_attrs : dict
            Global attributes of the results.
        values : pd.DataFrame, optional (default: None)
            Values of the variable, to store together with the metadata.

        Attributes
        ----------
        metric : str
            metric name
        g : int
            group number
        ref_df : QA4SMNamedAttributes
            reference dataset
        other_dss : list
            list of QA4SMNamedAttributes for the datasets that are not reference
        metric_ds : QA4SMNamedAttributes
            metric-relative dataset in case of TC metric
        """

        self.varname = varname
        self.attrs = global_attrs
        self.values = values

        self.metric, self.g, self.parts = self._parse_varname()
        self.Datasets = QA4SMDatasets(self.attrs)

    def initialize(self):
        """Initialize the subclass for the variable type (metric, CI or metadata)"""
        if self.ismetric and not self.is_CI:
            return MetricVariable(self.varname, self.attrs, self.values)

        elif self.ismetric and self.is_CI:
            return ConfidenceInterval(self.varname, self.attrs, self.values)

        else:
            return Metadata(self.varname, self.attrs, self.values)

    @property
    def isempty(self) -> bool:
        """Check whether values are associated with the object or not"""
        return self.values is None or self.values.empty

    @property
    def is_CI(self):
        """True if the Variable is the confidence interval of a metric"""
        if self.g:
            return "bound" in self.parts.keys()
        else:
            return False

    @property
    def ismetric(self) -> bool:
        return self.g is not None

    def _parse_varname(self) -> (str, int, dict):
        """
        Parse the name to get the metric, group and variable data

        Returns
        -------
        metric : str
            metric name
        g : int
            group
        parts : dict
            dictionary of MetricVariable data
        """
        metr_groups = list(globals.metric_groups.keys())
        # check which group it belongs to
        for g in metr_groups:
            template = globals.var_name_ds_sep[g]
            if template is None:
                template = ''
            pattern = '{}{}'.format(globals.var_name_metric_sep[g], template)
            # parse infromation from pattern and name
            parts = parse(pattern, self.varname)

            if parts is not None and parts['metric'] in globals.metric_groups[g]:
                return parts['metric'], g, parts.named
            # perhaps it's a CI variable
            else:
                pattern = '{}{}'.format(globals.var_name_CI[g], template)
                parts = parse(pattern, self.varname)
                if parts is not None and parts['metric'] in globals.metric_groups[g]:
                    return parts['metric'], g, parts.named

        return None, None, None


class MetricVariable(QA4SMVariable, MixinVarmeta):
    """Class that describes a metric variable, i.e. the metric for a specific set of Datasets"""

    def __init__(self, varname, global_attrs, values=None):
        super().__init__(varname, global_attrs, values)

        self.Metric = QA4SMMetric(self.metric)
        self.ref_ds, self.metric_ds, self.other_ds = self.get_varmeta()


class ConfidenceInterval(QA4SMVariable, MixinVarmeta):
    """Class for a MetricVariable representing confidence intervals"""

    def __init__(self, varname, global_attrs, values=None):
        super().__init__(varname, global_attrs, values)

        self.Metric = QA4SMMetric(self.metric)
        self.ref_ds, self.metric_ds, self.other_ds = self.get_varmeta()

        self.bound = self.parts["bound"]


class Metadata(QA4SMVariable):
    """Class for a MetricVariable representing metadata (only with ISMN as reference)"""

    def __init__(self, varname, global_attrs, values=None):
        super().__init__(varname, global_attrs, values)

    @property
    def key_meta(self) -> bool:
        """Filter out variables such as idx, lat, lon, gpi, time, _row_size etc."""
        return self.varname in globals.metadata.keys()  # todo: retrieve without globals?

    @property
    def pretty_name(self) -> str:
        """Pretty name of the metadata"""
        if self.varname in globals.metadata.keys():
            return globals.metadata[self.varname][0]
        else:
            return self.varname


class QA4SMMetric():
    """Class for validation metric"""
    def __init__(self, name, variables_list=None):

        self.name = name
        self.pretty_name = globals._metric_name[self.name]

        if variables_list:
            self.variables = variables_list
            self.g = self._get_attribute('g')
            self.attrs = self._get_attribute('attrs')

    def _get_attribute(self, attr:str):
        """
        Absorb Var attribute when is equal for all variables (e.g. group, reference dataset)

        Parameters
        ----------
        attr : str
            attribute name for the class QA4SMMetricVariable

        Returns
        -------
        value : attribute value
        """
        for n, Var in enumerate(self.variables):
            value = getattr(Var, attr)
            if n != 0:
                assert value == previous, "The attribute {} is not equal in all variables".format(attr)
            previous = value

        return value

    @property
    def has_CIs(self):
        """Boolean property for metrics with or without confidence intervals"""
        it_does = False
        for n, Var in enumerate(self.variables):
            if Var.is_CI():
                it_does = True
                break

        return  it_does
