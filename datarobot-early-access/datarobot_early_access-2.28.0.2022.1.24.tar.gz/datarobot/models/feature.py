#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import pandas as pd
from six.moves.urllib.parse import quote
import trafaret as t

from datarobot._compat import Int, String
from datarobot.enums import DEFAULT_MAX_WAIT
from datarobot.models.api_object import APIObject
from datarobot.models.pairwise_statistics import (
    PairwiseConditionalProbabilities,
    PairwiseCorrelations,
    PairwiseJointProbabilities,
)
from datarobot.utils.waiters import wait_for_async_resolution

from ..errors import InvalidUsageError
from ..utils import deprecation_warning, encode_utf8_if_py2, from_api


class HasHistogram(object):
    def get_histogram(self, bin_limit=None):
        """Retrieve a feature histogram

        Parameters
        ----------
        bin_limit : int or None
            Desired max number of histogram bins. If omitted, by default
            endpoint will use 60.

        Returns
        -------
        featureHistogram : FeatureHistogram
            The requested histogram with desired number or bins
        """
        return FeatureHistogram.get(self.project_id, self.name, bin_limit)


class Feature(APIObject, HasHistogram):
    """ A feature from a project's dataset

    These are features either included in the originally uploaded dataset or added to it via
    feature transformations.  In time series projects, these will be distinct from the
    :class:`ModelingFeature <datarobot.models.ModelingFeature>` s created during partitioning;
    otherwise, they will correspond to the same features.  For more information about input and
    modeling features, see the :ref:`time series documentation<input_vs_modeling>`.

    The ``min``, ``max``, ``mean``, ``median``, and ``std_dev`` attributes provide information about
    the distribution of the feature in the EDA sample data.  For non-numeric features or features
    created prior to these summary statistics becoming available, they will be None.  For features
    where the summary statistics are available, they will be in a format compatible with the data
    type, i.e. date type features will have their summary statistics expressed as ISO-8601
    formatted date strings.

    Attributes
    ----------
    id : int
        the id for the feature - note that `name` is used to reference the feature instead of `id`
    project_id : str
        the id of the project the feature belongs to
    name : str
        the name of the feature
    feature_type : str
        the type of the feature, e.g. 'Categorical', 'Text'
    importance : float or None
        numeric measure of the strength of relationship between the feature and target (independent
        of any model or other features); may be None for non-modeling features such as partition
        columns
    low_information : bool
        whether a feature is considered too uninformative for modeling (e.g. because it has too few
        values)
    unique_count : int
        number of unique values
    na_count : int or None
        number of missing values
    date_format : str or None
        For Date features, the date format string for how this feature
        was interpreted, compatible with https://docs.python.org/2/library/time.html#time.strftime .
        For other feature types, None.
    min : str, int, float, or None
        The minimum value of the source data in the EDA sample
    max : str, int, float, or None
        The maximum value of the source data in the EDA sample
    mean : str, int, or, float
        The arithmetic mean of the source data in the EDA sample
    median : str, int, float, or None
        The median of the source data in the EDA sample
    std_dev : str, int, float, or None
        The standard deviation of the source data in the EDA sample
    time_series_eligible : bool
        Whether this feature can be used as the datetime partition column in a time series project.
    time_series_eligibility_reason : str
        Why the feature is ineligible for the datetime partition column in a time series project,
        or 'suitable' when it is eligible.
    time_step : int or None
        For time series eligible features, a positive integer determining the interval at which
        windows can be specified. If used as the datetime partition column on a time series
        project, the feature derivation and forecast windows must start and end at an integer
        multiple of this value. None for features that are not time series eligible.
    time_unit : str or None
        For time series eligible features, the time unit covered by a single time step, e.g. 'HOUR',
        or None for features that are not time series eligible.
    target_leakage : str
        Whether a feature is considered to have target leakage or not.  A value of
        'SKIPPED_DETECTION' indicates that target leakage detection was not run on the feature.
        'FALSE' indicates no leakage, 'MODERATE' indicates a moderate risk of target leakage, and
        'HIGH_RISK' indicates a high risk of target leakage
    feature_lineage_id : str
        id of a lineage for automatically discovered features or derived time series features.
    key_summary: list of dict
        Statistics for top 50 keys (truncated to 103 characters) of
        Summarized Categorical column example:

        {\'key\':\'DataRobot\',
        \'summary\':{\'min\':0, \'max\':29815.0, \'stdDev\':6498.029, \'mean\':1490.75,
        \'median\':0.0, \'pctRows\':5.0}}

        where,
            key: string or None
                name of the key
            summary: dict
                statistics of the key

                max: maximum value of the key.
                min: minimum value of the key.
                mean: mean value of the key.
                median: median value of the key.
                stdDev: standard deviation of the key.
                pctRows: percentage occurrence of key in the EDA sample of the feature.
    multilabel_insights_key : str or None
        For multicategorical columns this will contain a key for multilabel insights. The key is
        unique for a project, feature and EDA stage combination. This will be the key for the most
        recent, finished EDA stage.
    """

    _converter = t.Dict(
        {
            t.Key("id"): Int,
            t.Key("project_id"): String,
            t.Key("name"): String,
            t.Key("feature_type", optional=True): String,
            t.Key("importance", optional=True): t.Float,
            t.Key("low_information"): t.Bool,
            t.Key("unique_count"): Int,
            t.Key("na_count", optional=True): Int,
            t.Key("date_format", optional=True): String,
            t.Key("min", optional=True): String | Int | t.Float | t.Null,
            t.Key("max", optional=True): String | Int | t.Float | t.Null,
            t.Key("mean", optional=True): String | Int | t.Float | t.Null,
            t.Key("median", optional=True): String | Int | t.Float | t.Null,
            t.Key("std_dev", optional=True): String | Int | t.Float | t.Null,
            t.Key("time_series_eligible"): t.Bool,
            t.Key("time_series_eligibility_reason"): String,
            t.Key("time_step", optional=True): Int,
            t.Key("time_unit", optional=True): String,
            t.Key("target_leakage", optional=True): String,
            t.Key("feature_lineage_id", optional=True): String | t.Null,
            t.Key("key_summary", optional=True): t.List(
                t.Dict(
                    {
                        t.Key("key"): String(allow_blank=True),
                        t.Key("summary"): t.Dict(
                            {
                                t.Key("max"): t.Float | Int,
                                t.Key("min"): t.Float | Int,
                                t.Key("mean"): t.Float | Int,
                                t.Key("median"): t.Float | Int,
                                t.Key("std_dev"): t.Float | Int,
                                t.Key("pct_rows"): t.Float | Int,
                            }
                        ).allow_extra("*"),
                    }
                ).allow_extra("*")
            ),
            t.Key("multilabel_insights", optional=True): t.Dict(
                {t.Key("multilabel_insights_key"): String}
            ).allow_extra("*"),
        }
    ).allow_extra("*")

    def __init__(
        self,
        id,
        project_id=None,
        name=None,
        feature_type=None,
        importance=None,
        low_information=None,
        unique_count=None,
        na_count=None,
        date_format=None,
        min=None,
        max=None,
        mean=None,
        median=None,
        std_dev=None,
        time_series_eligible=None,
        time_series_eligibility_reason=None,
        time_step=None,
        time_unit=None,
        target_leakage=None,
        feature_lineage_id=None,
        key_summary=None,
        multilabel_insights=None,
    ):
        if isinstance(id, dict):
            deprecation_warning(
                "Feature instantiation from a dict",
                "v2.3",
                "v3.0",
                message="Use Feature.from_data instead",
            )
            self.__init__(**from_api(id))
        else:
            self.id = id
            self.project_id = project_id
            self.name = name
            self.feature_type = feature_type
            self.importance = importance
            self.low_information = low_information
            self.unique_count = unique_count
            self.na_count = na_count
            self.date_format = date_format
            self.min = min
            self.max = max
            self.mean = mean
            self.median = median
            self.std_dev = std_dev
            self.time_series_eligible = time_series_eligible
            self.time_series_eligibility_reason = time_series_eligibility_reason
            self.time_step = time_step
            self.time_unit = time_unit
            self.target_leakage = target_leakage
            self.feature_lineage_id = feature_lineage_id
            self.key_summary = key_summary
            self.multilabel_insights_key = (
                multilabel_insights["multilabel_insights_key"] if multilabel_insights else None
            )

    def __repr__(self):
        return encode_utf8_if_py2(u"Feature({})".format(self.name))

    @classmethod
    def get(cls, project_id, feature_name):
        """Retrieve a single feature

        Parameters
        ----------
        project_id : str
            The ID of the project the feature is associated with.
        feature_name : str
            The name of the feature to retrieve

        Returns
        -------
        feature : Feature
            The queried instance
        """
        path = cls._build_url(project_id, feature_name)
        return cls.from_location(path)

    @classmethod
    def _build_url(cls, project_id, feature_name):
        return "projects/{}/features/{}/".format(
            project_id,
            feature_name if isinstance(feature_name, int) else quote(feature_name.encode("utf-8")),
        )

    def get_multiseries_properties(self, multiseries_id_columns, max_wait=DEFAULT_MAX_WAIT):
        """ Retrieve time series properties for a potential multiseries datetime partition column

        Multiseries time series projects use multiseries id columns to model multiple distinct
        series within a single project.  This function returns the time series properties (time step
        and time unit) of this column if it were used as a datetime partition column with the
        specified multiseries id columns, running multiseries detection automatically if it had not
        previously been successfully ran.

        Parameters
        ----------
        multiseries_id_columns : list of str
            the name(s) of the multiseries id columns to use with this datetime partition column.
            Currently only one multiseries id column is supported.
        max_wait : int, optional
            if a multiseries detection task is run, the maximum amount of time to wait for it to
            complete before giving up

        Returns
        -------
        properties : dict
            A dict with three keys:

                - time_series_eligible : bool, whether the column can be used as a partition column
                - time_unit : str or null, the inferred time unit if used as a partition column
                - time_step : int or null, the inferred time step if used as a partition column
        """

        def _extract_properties():
            retrieve_url = "{}multiseriesProperties/".format(
                self._build_url(self.project_id, self.name)
            )
            response = self._client.get(retrieve_url)
            response_schema = t.Dict(
                {
                    t.Key("datetimePartitionColumn"): String(),
                    t.Key("detectedMultiseriesIdColumns"): t.List(
                        t.Dict(
                            {
                                t.Key("multiseriesIdColumns"): t.List(String()),
                                t.Key("timeUnit"): String(),
                                t.Key("timeStep"): Int(),
                            }
                        ).ignore_extra("*")
                    ),
                }
            ).ignore_extra("*")
            response_data = response_schema.check(response.json())
            detected_columns = response_data["detectedMultiseriesIdColumns"]

            detected = next(
                (
                    col_set
                    for col_set in detected_columns
                    if set(col_set["multiseriesIdColumns"]) == set(multiseries_id_columns)
                ),
                None,
            )
            if detected is not None:
                return (
                    True,
                    {
                        "time_series_eligible": True,
                        "time_unit": detected["timeUnit"],
                        "time_step": detected["timeStep"],
                    },
                )
            return False, {"time_series_eligible": False, "time_unit": None, "time_step": None}

        detect_url = "projects/{}/multiseriesProperties/".format(self.project_id)
        was_detected, properties = _extract_properties()
        if was_detected:
            return properties

        detection_job = self._client.post(
            detect_url,
            data={
                "datetimePartitionColumn": self.name,
                "multiseriesIdColumns": multiseries_id_columns,
            },
        ).headers["Location"]
        wait_for_async_resolution(self._client, detection_job, max_wait=max_wait)
        return _extract_properties()[1]

    def get_cross_series_properties(
        self, datetime_partition_column, cross_series_group_by_columns, max_wait=DEFAULT_MAX_WAIT
    ):
        """ Retrieve cross-series properties for multiseries ID column.

        This function returns the cross-series properties (eligibility
        as group-by column) of this column if it were used with specified datetime partition column
        and with current multiseries id column, running cross-series group-by validation
        automatically if it had not previously been successfully ran.

        Parameters
        ----------
        datetime_partition_column : datetime partition column
        cross_series_group_by_columns : list of str
            the name(s) of the columns to use with this multiseries ID column.
            Currently only one cross-series group-by column is supported.
        max_wait : int, optional
            if a multiseries detection task is run, the maximum amount of time to wait for it to
            complete before giving up

        Returns
        -------
        properties : dict
            A dict with three keys:

                - name : str, column name
                - eligibility : str, reason for column eligibility
                - isEligible : bool, is column eligible as cross-series group-by
        """

        def _extract_properties():
            retrieve_url = (
                u"projects/{}/multiseriesIds/{}/crossSeriesProperties/?"
                u"crossSeriesGroupByColumns={}"
            ).format(self.project_id, self.name, cross_series_group_by_columns[0])

            response = self._client.get(retrieve_url)
            response_schema = t.Dict(
                {
                    t.Key("multiseriesId"): String(),
                    t.Key("crossSeriesGroupByColumns"): t.List(
                        t.Dict(
                            {
                                t.Key("name"): String(),
                                t.Key("eligibility"): String(),
                                t.Key("isEligible"): t.Bool(),
                            }
                        ).ignore_extra("*")
                    ),
                }
            ).ignore_extra("*")

            response_data = response_schema.check(response.json())
            for col in response_data["crossSeriesGroupByColumns"]:
                if col["name"] == cross_series_group_by_columns[0]:
                    if col["eligibility"] == "notAnalyzed":
                        return False, col
                    else:
                        return True, col
            return (
                False,
                {
                    "eligibility": "notAnalyzed",
                    "isEligible": False,
                    "name": cross_series_group_by_columns[0],
                },
            )

        validation_url = "projects/{}/crossSeriesProperties/".format(self.project_id)
        was_detected, properties = _extract_properties()
        if was_detected:
            return properties

        req_data = {
            "datetimePartitionColumn": datetime_partition_column,
            "multiseriesIdColumn": self.name,
            "crossSeriesGroupByColumns": cross_series_group_by_columns,
        }
        detection_job = self._client.post(validation_url, data=req_data).headers["Location"]
        wait_for_async_resolution(self._client, detection_job, max_wait=max_wait)
        return _extract_properties()[1]

    def get_multicategorical_histogram(self):
        """Retrieve multicategorical histogram for this feature

        .. versionadded:: v2.24

        Returns
        -------
        :class:`datarobot.models.MulticategoricalHistogram`

        Raises
        ------
        datarobot.errors.InvalidUsageError
            if this method is called on a unsuited feature
        ValueError
            if no multilabel_insights_key is present for this feature
        """
        if self.multilabel_insights_key:
            return MulticategoricalHistogram.get(self.multilabel_insights_key)
        elif self.feature_type != "Multicategorical":
            raise InvalidUsageError(
                "Multicategorical Histograms are only available for features"
                "with feature_type Multicategorical. "
                "This feature is of type: {}".format(self.feature_type)
            )
        else:
            raise ValueError("A valid multilabel_insights_key is required, but not present")

    def get_pairwise_correlations(self):
        """Retrieve pairwise label correlation for multicategorical features

        .. versionadded:: v2.24

        Returns
        -------
        :class:`datarobot.models.PairwiseCorrelations`

        Raises
        ------
        datarobot.errors.InvalidUsageError
            if this method is called on a unsuited feature
        ValueError
            if no multilabel_insights_key is present for this feature
        """
        if self.multilabel_insights_key:
            return PairwiseCorrelations.get(self.multilabel_insights_key)
        elif self.feature_type != "Multicategorical":
            raise InvalidUsageError(
                "Pairwise Correlation is only available for features"
                "with feature_type Multicategorical. "
                "This feature is of type: {}".format(self.feature_type)
            )
        else:
            raise ValueError("A valid multilabel_insights_key is required, but not present")

    def get_pairwise_joint_probabilities(self):
        """Retrieve pairwise label joint probabilities for multicategorical features

        .. versionadded:: v2.24

        Returns
        -------
        :class:`datarobot.models.PairwiseJointProbabilities`

        Raises
        ------
        datarobot.errors.InvalidUsageError
            if this method is called on a unsuited feature
        ValueError
            if no multilabel_insights_key is present for this feature
        """
        if self.multilabel_insights_key:
            return PairwiseJointProbabilities.get(self.multilabel_insights_key)
        elif self.feature_type != "Multicategorical":
            raise InvalidUsageError(
                "Pairwise Joint Probability is only available for features"
                "with feature_type Multicategorical. "
                "This feature is of type: {}".format(self.feature_type)
            )
        else:
            raise ValueError("A valid multilabel_insights_key is required, but not present")

    def get_pairwise_conditional_probabilities(self):
        """Retrieve pairwise label conditional probabilities for multicategorical features

        .. versionadded:: v2.24

        Returns
        -------
        :class:`datarobot.models.PairwiseConditionalProbabilities`

        Raises
        ------
        datarobot.errors.InvalidUsageError
            if this method is called on a unsuited feature
        ValueError
            if no multilabel_insights_key is present for this feature
        """
        if self.multilabel_insights_key:
            return PairwiseConditionalProbabilities.get(self.multilabel_insights_key)
        elif self.feature_type != "Multicategorical":
            raise InvalidUsageError(
                "Pairwise Conditional Probability is only available for features"
                "with feature_type Multicategorical. "
                "This feature is of type: {}".format(self.feature_type)
            )
        else:
            raise ValueError("A valid multilabel_insights_key is required, but not present")


class ModelingFeature(APIObject, HasHistogram):
    """ A feature used for modeling

    In time series projects, a new set of modeling features is created after setting the
    partitioning options.  These features are automatically derived from those in the project's
    dataset and are the features used for modeling.  Modeling features are only accessible once
    the target and partitioning options have been set.  In projects that don't use time series
    modeling, once the target has been set, ModelingFeatures and Features will behave
    the same.

    For more information about input and modeling features, see the
    :ref:`time series documentation<input_vs_modeling>`.

    As with the :class:`Feature <datarobot.models.Feature>` object, the `min`, `max, `mean`,
    `median`, and `std_dev` attributes provide information about the distribution of the feature in
    the EDA sample data.  For non-numeric features, they will be None.  For features where the
    summary statistics are available, they will be in a format compatible with the data type, i.e.
    date type features will have their summary statistics expressed as ISO-8601 formatted date
    strings.

    Attributes
    ----------
    project_id : str
        the id of the project the feature belongs to
    name : str
        the name of the feature
    feature_type : str
        the type of the feature, e.g. 'Categorical', 'Text'
    importance : float or None
        numeric measure of the strength of relationship between the feature and target (independent
        of any model or other features); may be None for non-modeling features such as partition
        columns
    low_information : bool
        whether a feature is considered too uninformative for modeling (e.g. because it has too few
        values)
    unique_count : int
        number of unique values
    na_count : int or None
        number of missing values
    date_format : str or None
        For Date features, the date format string for how this feature
        was interpreted, compatible with https://docs.python.org/2/library/time.html#time.strftime .
        For other feature types, None.
    min : str, int, float, or None
        The minimum value of the source data in the EDA sample
    max : str, int, float, or None
        The maximum value of the source data in the EDA sample
    mean : str, int, or, float
        The arithmetic mean of the source data in the EDA sample
    median : str, int, float, or None
        The median of the source data in the EDA sample
    std_dev : str, int, float, or None
        The standard deviation of the source data in the EDA sample
    parent_feature_names : list of str
        A list of the names of input features used to derive this modeling feature.  In cases where
        the input features and modeling features are the same, this will simply contain the
        feature's name.  Note that if a derived feature was used to create this modeling feature,
        the values here will not necessarily correspond to the features that must be supplied at
        prediction time.
    key_summary: list of dict
        Statistics for top 50 keys (truncated to 103 characters) of
        Summarized Categorical column example:

        {\'key\':\'DataRobot\',
        \'summary\':{\'min\':0, \'max\':29815.0, \'stdDev\':6498.029, \'mean\':1490.75,
        \'median\':0.0, \'pctRows\':5.0}}

        where,
            key: string or None
                name of the key
            summary: dict
                statistics of the key

                max: maximum value of the key.
                min: minimum value of the key.
                mean: mean value of the key.
                median: median value of the key.
                stdDev: standard deviation of the key.
                pctRows: percentage occurrence of key in the EDA sample of the feature.
    """

    _converter = t.Dict(
        {
            t.Key("project_id"): String,
            t.Key("name"): String,
            t.Key("feature_type", optional=True): String,
            t.Key("importance", optional=True): t.Float,
            t.Key("low_information"): t.Bool,
            t.Key("unique_count"): Int,
            t.Key("na_count", optional=True): Int,
            t.Key("date_format", optional=True): String,
            t.Key("min", optional=True): String | Int | t.Float | t.Null,
            t.Key("max", optional=True): String | Int | t.Float | t.Null,
            t.Key("mean", optional=True): String | Int | t.Float | t.Null,
            t.Key("median", optional=True): String | Int | t.Float | t.Null,
            t.Key("std_dev", optional=True): String | Int | t.Float | t.Null,
            t.Key("parent_feature_names"): t.List(String),
            t.Key("is_restored_after_reduction", optional=True): t.Bool,
            t.Key("key_summary", optional=True): t.List(
                t.Dict(
                    {
                        t.Key("key"): String(allow_blank=True),
                        t.Key("summary"): t.Dict(
                            {
                                t.Key("max"): t.Float | Int,
                                t.Key("min"): t.Float | Int,
                                t.Key("mean"): t.Float | Int,
                                t.Key("median"): t.Float | Int,
                                t.Key("std_dev"): t.Float | Int,
                                t.Key("pct_rows"): t.Float | Int,
                            }
                        ).allow_extra("*"),
                    }
                ).allow_extra("*")
            ),
        }
    ).ignore_extra("*")

    def __init__(
        self,
        project_id=None,
        name=None,
        feature_type=None,
        importance=None,
        low_information=None,
        unique_count=None,
        na_count=None,
        date_format=None,
        min=None,
        max=None,
        mean=None,
        median=None,
        std_dev=None,
        parent_feature_names=None,
        key_summary=None,
        is_restored_after_reduction=None,
    ):
        self.project_id = project_id
        self.name = name
        self.feature_type = feature_type
        self.importance = importance
        self.low_information = low_information
        self.unique_count = unique_count
        self.na_count = na_count
        self.date_format = date_format
        self.min = min
        self.max = max
        self.mean = mean
        self.median = median
        self.std_dev = std_dev
        self.parent_feature_names = parent_feature_names
        self.key_summary = key_summary
        self.is_restored_after_reduction = is_restored_after_reduction

    def __repr__(self):
        return encode_utf8_if_py2(u"ModelingFeature({})".format(self.name))

    @classmethod
    def get(cls, project_id, feature_name):
        """Retrieve a single modeling feature

        Parameters
        ----------
        project_id : str
            The ID of the project the feature is associated with.
        feature_name : str
            The name of the feature to retrieve

        Returns
        -------
        feature : ModelingFeature
            The requested feature
        """
        path = cls._build_url(project_id, feature_name)
        return cls.from_location(path)

    @classmethod
    def _build_url(cls, project_id, feature_name):
        return "projects/{}/modelingFeatures/{}/".format(
            project_id, quote(feature_name.encode("utf-8"))
        )


class DatasetFeature(APIObject):
    """ A feature from a project's dataset

    These are features either included in the originally uploaded dataset or added to it via
    feature transformations.

    The ``min``, ``max``, ``mean``, ``median``, and ``std_dev`` attributes provide information about
    the distribution of the feature in the EDA sample data.  For non-numeric features or features
    created prior to these summary statistics becoming available, they will be None.  For features
    where the summary statistics are available, they will be in a format compatible with the data
    type, i.e. date type features will have their summary statistics expressed as ISO-8601
    formatted date strings.

    Attributes
    ----------
    id : int
        the id for the feature - note that `name` is used to reference the feature instead of `id`
    dataset_id : str
        the id of the dataset the feature belongs to
    dataset_version_id : str
        the id of the dataset version the feature belongs to
    name : str
        the name of the feature
    feature_type : str, optional
        the type of the feature, e.g. 'Categorical', 'Text'
    low_information : bool, optional
        whether a feature is considered too uninformative for modeling (e.g. because it has too few
        values)
    unique_count : int, optional
        number of unique values
    na_count : int, optional
        number of missing values
    date_format : str, optional
        For Date features, the date format string for how this feature
        was interpreted, compatible with https://docs.python.org/2/library/time.html#time.strftime .
        For other feature types, None.
    min : str, int, float, optional
        The minimum value of the source data in the EDA sample
    max : str, int, float, optional
        The maximum value of the source data in the EDA sample
    mean : str, int, float, optional
        The arithmetic mean of the source data in the EDA sample
    median : str, int, float, optional
        The median of the source data in the EDA sample
    std_dev : str, int, float, optional
        The standard deviation of the source data in the EDA sample
    time_series_eligible : bool, optional
        Whether this feature can be used as the datetime partition column in a time series project.
    time_series_eligibility_reason : str, optional
        Why the feature is ineligible for the datetime partition column in a time series project,
        or 'suitable' when it is eligible.
    time_step : int, optional
        For time series eligible features, a positive integer determining the interval at which
        windows can be specified. If used as the datetime partition column on a time series
        project, the feature derivation and forecast windows must start and end at an integer
        multiple of this value. None for features that are not time series eligible.
    time_unit : str, optional
        For time series eligible features, the time unit covered by a single time step, e.g. 'HOUR',
        or None for features that are not time series eligible.
    target_leakage : str, optional
        Whether a feature is considered to have target leakage or not.  A value of
        'SKIPPED_DETECTION' indicates that target leakage detection was not run on the feature.
        'FALSE' indicates no leakage, 'MODERATE' indicates a moderate risk of target leakage, and
        'HIGH_RISK' indicates a high risk of target leakage
    target_leakage_reason: string, optional
        The descriptive text explaining the reason for target leakage, if any.
    """

    _converter = t.Dict(
        {
            t.Key("id") >> "id_": Int,
            t.Key("dataset_id"): String,
            t.Key("dataset_version_id"): String,
            t.Key("name"): String,
            t.Key("feature_type", optional=True): String,
            t.Key("low_information", optional=True): t.Bool,
            t.Key("unique_count", optional=True): Int,
            t.Key("na_count", optional=True): Int,
            t.Key("date_format", optional=True): String,
            t.Key("min", optional=True) >> "min_": String | Int | t.Float | t.Null,
            t.Key("max", optional=True) >> "max_": String | Int | t.Float | t.Null,
            t.Key("mean", optional=True): String | Int | t.Float | t.Null,
            t.Key("median", optional=True): String | Int | t.Float | t.Null,
            t.Key("std_dev", optional=True): String | Int | t.Float | t.Null,
            t.Key("time_series_eligible", optional=True): t.Bool,
            t.Key("time_series_eligibility_reason", optional=True): String,
            t.Key("time_step", optional=True): Int,
            t.Key("time_unit", optional=True): String,
            t.Key("target_leakage", optional=True): String,
            t.Key("target_leakage_reason", optional=True): String,
        }
    ).allow_extra("*")

    def __init__(
        self,
        id_,
        dataset_id=None,
        dataset_version_id=None,
        name=None,
        feature_type=None,
        low_information=None,
        unique_count=None,
        na_count=None,
        date_format=None,
        min_=None,
        max_=None,
        mean=None,
        median=None,
        std_dev=None,
        time_series_eligible=None,
        time_series_eligibility_reason=None,
        time_step=None,
        time_unit=None,
        target_leakage=None,
        target_leakage_reason=None,
    ):
        self.id = id_
        self.dataset_id = dataset_id
        self.dataset_version_id = dataset_version_id
        self.name = name
        self.feature_type = feature_type
        self.low_information = low_information
        self.unique_count = unique_count
        self.na_count = na_count
        self.date_format = date_format
        self.min = min_
        self.max = max_
        self.mean = mean
        self.median = median
        self.std_dev = std_dev
        self.time_series_eligible = time_series_eligible
        self.time_series_eligibility_reason = time_series_eligibility_reason
        self.time_step = time_step
        self.time_unit = time_unit
        self.target_leakage = target_leakage
        self.target_leakage_reason = target_leakage_reason

    def __repr__(self):
        return encode_utf8_if_py2(u"Feature({}, dataset_id={})".format(self.name, self.dataset_id))

    def get_histogram(self, bin_limit=None):
        """Retrieve a feature histogram

        Parameters
        ----------
        bin_limit : int or None
            Desired max number of histogram bins. If omitted, by default
            endpoint will use 60.

        Returns
        -------
        featureHistogram : DatasetFeatureHistogram
            The requested histogram with desired number or bins
        """
        return DatasetFeatureHistogram.get(self.dataset_id, self.name, bin_limit)


class BaseFeatureHistogram(APIObject):
    """ A histogram plot data for a specific feature

    .. versionadded:: v2.14

    Histogram is a popular way of visual representation of feature values
    distribution. Here histogram is represented as an ordered collection of bins.
    For categorical features every bin represents exactly one of feature values
    and the count in that bin is the number of occurrences of that value.
    For numeric features every bin represents a range of values (low end inclusive,
    high end exclusive) and the count in the bin is the total number of occurrences of all
    values in this range. In addition, each bin may contain a target feature average for values
    in that bin (see ``target`` description below).

    Notes
    -----

    ``HistogramBin`` contains:

    * ``label`` : (str) for categorical features: the value of the feature,
      for numeric: the low end of bin range,
      so that the difference between two consecutive bin labels is the length
      of the bin
    * ``count`` : (int or float) number of values in this bin's range
      If project uses weights, the value is equal to the sum of weights of
      all feature values in bin's range
    * ``target`` : (float or None) Average of the target feature values for the bin.
      Present only for informative features if project target has already been selected and
      AIM processing has finished. For multiclass projects the value is always null.

    Attributes
    ----------
    plot : list
        a list of dictionaries with a schema described as ``HistogramBin``

    """

    _converter = t.Dict(
        {
            t.Key("plot"): t.List(
                t.Dict(
                    {
                        t.Key("label"): String,
                        t.Key("count"): Int | t.Float,
                        t.Key("target", default=None): t.Float | t.Null,
                    }
                )
            )
        }
    )

    _root_path = None

    def __init__(self, plot):
        self.plot = plot

    def __repr__(self):
        return encode_utf8_if_py2(u"{}()".format(self.__class__.__name__))

    @classmethod
    def get(cls, object_id, feature_name, bin_limit=None, key_name=None):
        """Retrieve a single feature histogram

        Parameters
        ----------
        object_id : str
            The ID of the object the feature is associated with.
        feature_name : str
            The name of the feature to retrieve
        bin_limit : int or None
            Desired max number of histogram bins. If omitted, by default
            endpoint will use 60.
        key_name: string or None
            (Only required for summarized categorical feature)
            Name of the top 50 keys for which plot to be retrieved

        Returns
        -------
        featureHistogram : FeatureHistogram
            The queried instance with `plot` attribute in it.
        """
        path = cls._build_url(object_id, feature_name, bin_limit, key_name)
        return cls.from_location(path)

    @classmethod
    def _build_url(cls, project_id, feature_name, bin_limit=None, key_name=None):
        url = "{}/{}/featureHistograms/{}/".format(
            cls._root_path, project_id, quote(feature_name.encode("utf-8"))
        )

        if bin_limit is not None:  # makes sure pass 0 to endpoint
            url = "{}?binLimit={}".format(url, bin_limit)
        if key_name is not None:
            url = "{}?key={}".format(url, quote(key_name.encode("utf-8")))
        return url


class FeatureHistogram(BaseFeatureHistogram):

    _root_path = "projects"

    @classmethod
    def get(cls, project_id, feature_name, bin_limit=None, key_name=None):
        """Retrieve a single feature histogram

        Parameters
        ----------
        project_id : str
            The ID of the project the feature is associated with.
        feature_name : str
            The name of the feature to retrieve
        bin_limit : int or None
            Desired max number of histogram bins. If omitted, by default
            endpoint will use 60.
        key_name: string or None
            (Only required for summarized categorical feature)
            Name of the top 50 keys for which plot to be retrieved

        Returns
        -------
        featureHistogram : FeatureHistogram
            The queried instance with `plot` attribute in it.
        """
        return super(FeatureHistogram, cls).get(project_id, feature_name, bin_limit, key_name)


class DatasetFeatureHistogram(BaseFeatureHistogram):

    _root_path = "datasets"

    @classmethod
    def get(cls, dataset_id, feature_name, bin_limit=None, key_name=None):
        """Retrieve a single feature histogram

        Parameters
        ----------
        dataset_id : str
            The ID of the Dataset the feature is associated with.
        feature_name : str
            The name of the feature to retrieve
        bin_limit : int or None
            Desired max number of histogram bins. If omitted, by default
            the endpoint will use 60.
        key_name: string or None
            (Only required for summarized categorical feature)
            Name of the top 50 keys for which plot to be retrieved

        Returns
        -------
        featureHistogram : FeatureHistogram
            The queried instance with `plot` attribute in it.
        """
        return super(DatasetFeatureHistogram, cls).get(
            dataset_id, feature_name, bin_limit, key_name
        )


class InteractionFeature(APIObject):
    """
    Interaction feature data

    .. versionadded:: v2.21

    Attributes
    ----------
    rows: int
        Total number of rows
    source_columns: list(str)
        names of two categorical features which were combined into this one
    bars: list(dict)
        dictionaries representing frequencies of each independent value from the source columns
    bubbles: list(dict)
        dictionaries representing frequencies of each combined value in the interaction feature.
    """

    _converter = t.Dict(
        {
            t.Key("rows"): Int,
            t.Key("source_columns"): t.List(String, min_length=2, max_length=2),
            t.Key("bars"): t.List(
                t.Dict(
                    {
                        t.Key("column_name"): String,
                        t.Key("counts"): t.List(
                            t.Dict({t.Key("value"): String, t.Key("count"): Int}),
                            min_length=2,
                            max_length=2,
                        ),
                    }
                ).allow_extra("*")
            ),
            t.Key("bubbles"): t.List(
                t.Dict(
                    {
                        t.Key("count"): Int,
                        t.Key("source_data"): t.List(
                            t.Dict({t.Key("value"): String, t.Key("column_name"): String}),
                            min_length=2,
                            max_length=2,
                        ),
                    }
                ).allow_extra("*")
            ),
        }
    ).allow_extra("*")

    def __init__(self, rows, source_columns, bars, bubbles):
        self.rows = rows
        self.bars = bars
        self.bubbles = bubbles
        self.source_columns = source_columns

    @classmethod
    def _url(cls, project_id, feature_name):
        safe_feature_name = quote(feature_name.encode("utf-8"))
        return "projects/{}/interactionFeatures/{}/".format(project_id, safe_feature_name)

    @classmethod
    def get(cls, project_id, feature_name):
        """
        Retrieve a single Interaction feature

        Parameters
        ----------
        project_id : str
            The id of the project the feature belongs to
        feature_name : str
            The name of the Interaction feature to retrieve

        Returns
        -------
        feature : InteractionFeature
            The queried instance
          """
        feature_url = cls._url(project_id, feature_name)
        return cls.from_location(feature_url)


class FeatureLineage(APIObject):
    """ Lineage of an automatically engineered feature.

    Attributes
    ----------
    steps: list
        list of steps which were applied to build the feature.

    `steps` structure is:

    id : int
        step id starting with 0.
    step_type: str
        one of the data/action/json/generatedData.
    name: str
        name of the step.
    description: str
        description of the step.
    parents: list[int]
        references to other steps id.
    is_time_aware: bool
        indicator of step being time aware. Mandatory only for *action* and *join* steps.
        *action* step provides additional information about feature derivation window
        in the `timeInfo` field.
    catalog_id: str
        id of the catalog for a *data* step.
    catalog_version_id: str
        id of the catalog version for a *data* step.
    group_by: list[str]
        list of columns which this *action* step aggregated by.
    columns: list
        names of columns involved into the feature generation. Available only for *data* steps.
    time_info: dict
        description of the feature derivation window which was applied to this *action* step.
    join_info: list[dict]
        *join* step details.

    `columns` structure is

    data_type: str
        the type of the feature, e.g. 'Categorical', 'Text'
    is_input: bool
        indicates features which provided data to transform in this lineage.
    name: str
        feature name.
    is_cutoff: bool
        indicates a cutoff column.

    `time_info` structure is:

    latest: dict
        end of the feature derivation window applied.
    duration: dict
        size of the feature derivation window applied.

    `latest` and `duration` structure is:

    time_unit: str
        time unit name like 'MINUTE', 'DAY', 'MONTH' etc.
    duration: int
        value/size of this duration object.

    `join_info` structure is:

    join_type: str
        kind of join, left/right.
    left_table: dict
        information about a dataset which was considered as left.
    right_table: str
        information about a dataset which was considered as right.

    `left_table` and `right_table` structure is:

    columns: list[str]
        list of columns which datasets were joined by.
    datasteps: list[int]
        list of *data* steps id which brought the *columns* into the current step dataset.
    """

    _join_table_trafaret = t.Dict(
        {t.Key("datasteps"): t.List(Int(gte=1)), t.Key("columns"): t.List(String)}
    )

    _duration_trafaret = t.Dict(
        {
            t.Key("duration"): Int,
            t.Key("time_unit"): String,
            t.Key("is_original", optional=True): t.Bool | t.Null,
        }
    )

    _columns_trafaret = t.Dict(
        {
            t.Key("name"): String,
            t.Key("data_type"): String,
            t.Key("is_input"): t.Bool,
            t.Key("is_cutoff", optional=True): t.Bool,
        }
    ).allow_extra("*")

    _converter = t.Dict(
        {
            t.Key("steps"): t.List(
                t.Dict(
                    {
                        t.Key("id"): Int(gte=0) | t.Null,
                        t.Key("step_type"): t.Regexp(regexp="data|join|generatedColumn|action"),
                        t.Key("parents"): t.List(Int),
                        t.Key("name", optional=True): String,
                        t.Key("description", optional=True): String | t.Null,
                        t.Key("data_type", optional=True): String | t.Null,
                        t.Key("catalog_id", optional=True): String | t.Null,
                        t.Key("catalog_version_id", optional=True): String | t.Null,
                        t.Key("columns", optional=True): t.List(_columns_trafaret),
                        t.Key("is_time_aware", optional=True): t.Bool,
                        t.Key("join_info", optional=True): t.Dict(
                            {
                                t.Key("join_type"): t.Regexp(regexp="left|right"),
                                t.Key("left_table"): _join_table_trafaret,
                                t.Key("right_table"): _join_table_trafaret,
                            }
                        ).ignore_extra("*"),
                        t.Key("group_by", optional=True): t.List(String) | t.Null,
                        t.Key("time_info", optional=True): t.Dict(
                            {
                                t.Key("latest", optional=True): _duration_trafaret,
                                t.Key("duration", optional=True): _duration_trafaret,
                                t.Key("lag", optional=True): _duration_trafaret,
                            }
                        )
                        | t.Null,
                    }
                ).ignore_extra("*")
            ),
        }
    ).ignore_extra("*")

    def __init__(
        self, steps=None,
    ):
        self.steps = steps

    @classmethod
    def get(cls, project_id, id):
        """ Retrieve a single FeatureLineage.

        Parameters
        ----------
        project_id : str
            The id of the project the feature belongs to
        id : str
            id of a feature lineage to retrieve

        Returns
        -------
        lineage : FeatureLineage
            The queried instance
        """
        return cls.from_location("projects/{}/featureLineages/{}/".format(project_id, id))


class MulticategoricalHistogram(APIObject):
    """
    Histogram for Multicategorical feature.

    .. versionadded:: v2.24

    Notes
    -----

    ``HistogramValues`` contains:

    * ``values.[].label`` : string - Label name
    * ``values.[].plot`` : list - Histogram for label
    * ``values.[].plot.[].label_relevance`` : int - Label relevance value
    * ``values.[].plot.[].row_count`` : int - Row count where label has given relevance
    * ``values.[].plot.[].row_pct`` : float - Percentage of rows where label has given relevance

    Attributes
    ----------
    feature_name : str
        Name of the feature
    values : list(dict)
        List of Histogram values with a schema described as ``HistogramValues``

    """

    _converter = t.Dict(
        {
            t.Key("feature_name"): String,
            t.Key("histogram"): t.List(
                t.Dict(
                    {
                        t.Key("label"): String,
                        t.Key("plot"): t.List(
                            t.Dict(
                                {
                                    t.Key("label_relevance"): Int,
                                    t.Key("row_count"): Int,
                                    t.Key("row_pct"): t.Float,
                                }
                            ).allow_extra("*")
                        ),
                    }
                ).allow_extra("*")
            ),
        }
    ).allow_extra("*")

    def __init__(self, feature_name, histogram):
        self.values = histogram
        self.feature_name = feature_name

    def __repr__(self):
        return encode_utf8_if_py2(u"{}()".format(self.__class__.__name__))

    @classmethod
    def get(cls, multilabel_insights_key):
        """Retrieves multicategorical histogram

        You might find it more convenient to use
        :meth:`Feature.get_multicategorical_histogram
        <datarobot.models.Feature.get_multicategorical_histogram>`
        instead.

        Parameters
        ----------
        multilabel_insights_key: string
            Key for multilabel insights, unique for a project, feature and EDA stage combination.
            The multilabel_insights_key can be retrieved via
            ``Feature.multilabel_insights_key``.

        Returns
        -------
        MulticategoricalHistogram
            The multicategorical histogram for multilabel_insights_key
        """
        url = "multilabelInsights/{}/histogram/".format(multilabel_insights_key)
        return cls.from_location(url)

    def to_dataframe(self):
        """
        Convenience method to get all the information from this multicategorical_histogram instance
        in form of a ``pandas.DataFrame``.

        Returns
        -------
        pandas.DataFrame
            Histogram information as a multicategorical_histogram. The dataframe will contain these
            columns: feature_name, label, label_relevance, row_count and row_pct
        """
        rows = []
        for label_values in self.values:
            label = label_values["label"]
            for plot_value in label_values["plot"]:
                row = {
                    "feature_name": self.feature_name,
                    "label": label,
                    "label_relevance": plot_value["label_relevance"],
                    "row_count": plot_value["row_count"],
                    "row_pct": plot_value["row_pct"],
                }
                rows.append(row)
        return pd.DataFrame(rows)
