# -*- coding: utf-8 -*-
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
import abc
from collections import defaultdict

import numpy as np
import pandas as pd
import six
import trafaret as t

from datarobot._compat import Int, String
from datarobot.models.api_object import APIObject
from datarobot.utils import encode_utf8_if_py2

VALID_RELEVANCE_CONFIGURATIONS = {(0, 0), (0, 1), (1, 0), (1, 1)}


@six.add_metaclass(abc.ABCMeta)
class PairwiseStatisticsBase(APIObject):
    _converter = t.Dict(
        {
            t.Key("feature_name"): String,
            t.Key("data"): t.List(
                t.Dict(
                    {
                        t.Key("label_configuration"): t.List(
                            t.Dict(
                                {t.Key("relevance", optional=True): Int, t.Key("label"): String}
                            ),
                            min_length=2,
                            max_length=2,
                        ),
                        # In case of missing values we will have None here, which gets removed in
                        # from_location call (keep_atters can not be used because data is a list)
                        t.Key("statistic_value", optional=True): t.Float,
                    }
                ).allow_extra("*")
            ),
        }
    ).allow_extra("*")

    def __init__(self, feature_name, data):
        self.feature_name = feature_name
        self.values = data

    def __repr__(self):
        return encode_utf8_if_py2(
            u"{}(feature_name={})".format(self.__class__.__name__, self.feature_name)
        )

    @classmethod
    def _get(cls, multilabel_insights_key, statistic_type):
        url = "multilabelInsights/{}/pairwiseStatistics/?statisticType={}".format(
            multilabel_insights_key, statistic_type
        )
        return cls.from_location(url)

    @staticmethod
    def _sort_index_and_columns(df):
        """
        Sorts the index and columns of a pairwise statistics dataframe.
        The dataframe is expected to have a shape of (num_labels, num_labels) and to have the same
        label_names in the index and the columns.
        """
        df = df.sort_index()
        df = df[df.index]
        return df


class PairwiseCorrelations(PairwiseStatisticsBase):
    """
    Correlation of label pairs for multicategorical feature.

    .. versionadded:: v2.24

    Notes
    -----
    ``CorrelationValues`` contain:

    * ``values.[].label_configuration`` : list of length 2 - Configuration of the label pair
    * ``values.[].label_configuration.[].label`` : str – Label name
    * ``values.[].statistic_value`` : float – Statistic value

    Attributes
    ----------
    feature_name : str
        Name of the feature
    values : list(dict)
        List of correlation values with a schema described as ``CorrelationValues``
    statistic_dataframe : pandas.DataFrame
        Correlation values for all label pairs as a DataFrame
    """

    def __init__(self, *args, **kwargs):
        super(PairwiseCorrelations, self).__init__(*args, **kwargs)
        self.statistic_dataframe = self._to_statistic_dataframe(self.values)

    @staticmethod
    def _to_statistic_dataframe(correlation_values):
        """
        Converts the correlation values to a dataframe.

        Parameters
        ----------
        correlation_values : list(dict)
            List of correlation values following the ``CorrelationValues`` schema outlined in the
            class description.

        Returns
        -------
        pandas.DataFrame
            The correlation values as a pandas.DataFrame
        """
        columns = defaultdict(dict)
        for statistic_value in correlation_values:
            row_label = six.ensure_text(statistic_value["label_configuration"][0]["label"])
            column_label = six.ensure_text(statistic_value["label_configuration"][1]["label"])
            columns[column_label][row_label] = statistic_value.get("statistic_value", np.nan)

        statistic_dataframe = pd.DataFrame(columns)
        statistic_dataframe = PairwiseCorrelations._sort_index_and_columns(statistic_dataframe)

        return statistic_dataframe

    @classmethod
    def get(cls, multilabel_insights_key):
        """Retrieves pairwise correlations

        You might find it more convenient to use
        :meth:`Feature.get_pairwise_correlations
        <datarobot.models.Feature.get_pairwise_correlations>`
        instead.

        Parameters
        ----------
        multilabel_insights_key: string
            Key for multilabel insights, unique for a project, feature and EDA stage combination.
            The multilabel_insights_key can be retrieved via
            ``Feature.multilabel_insights_key``.

        Returns
        -------
        PairwiseCorrelations
            The pairwise label correlations
        """
        return cls._get(multilabel_insights_key, "correlation")

    def as_dataframe(self):
        """The pairwise label correlations as a (num_labels x num_labels) DataFrame.

        Returns
        -------
        pandas.DataFrame
            The pairwise label correlations. Index and column names allow the interpretation of the
            values.
        """
        return self.statistic_dataframe


@six.add_metaclass(abc.ABCMeta)
class PairwiseProbabilitiesBase(PairwiseStatisticsBase):
    def __init__(self, *args, **kwargs):
        super(PairwiseProbabilitiesBase, self).__init__(*args, **kwargs)
        self.statistic_dataframes = self._to_statistic_dataframes(self.values)

    @staticmethod
    def _to_statistic_dataframes(statistic_values):
        """
        Converts the statistic values into DataFrames. There will be one DataFrame for each
        relevance configuration.

        Parameters
        ----------
        statistic_values : list(dict)
            List of statistic values following the ``ProbabilityValues`` schema outlined in the
            class description of PairwiseJointProbabilities or PairwiseConditionalProbabilities.

        Returns
        -------
        dict(pandas.DataFrame)
            The keys of the returned dictionary are the relevance configurations
            e.g. (0, 0), (0, 1) etc. The values are the static_values for this relevance
            configuration as pandas.DataFrame.
        """
        grouped_statistic_values = defaultdict(lambda: defaultdict(dict))
        for statistic_value in statistic_values:
            relevance_configuration = (
                statistic_value["label_configuration"][0]["relevance"],
                statistic_value["label_configuration"][1]["relevance"],
            )
            row_label = six.ensure_text(statistic_value["label_configuration"][0]["label"])
            column_label = six.ensure_text(statistic_value["label_configuration"][1]["label"])
            grouped_statistic_values[relevance_configuration][column_label][
                row_label
            ] = statistic_value.get("statistic_value", np.nan)
        statistic_dataframes = {}
        for relevance_configuration, columns in grouped_statistic_values.items():
            df = pd.DataFrame(columns)
            df = PairwiseProbabilitiesBase._sort_index_and_columns(df)
            statistic_dataframes[relevance_configuration] = df
        return statistic_dataframes

    def _as_dataframe(self, relevance_configuration):
        if relevance_configuration not in VALID_RELEVANCE_CONFIGURATIONS:
            raise ValueError(
                "You have passed an invalid label configuration. "
                "Valid options are (0, 0), (0, 1), (1, 0) and (1, 1)"
            )
        return self.statistic_dataframes[relevance_configuration]


class PairwiseJointProbabilities(PairwiseProbabilitiesBase):
    """
    Joint probabilities of label pairs for multicategorical feature.

    .. versionadded:: v2.24

    Notes
    -----
    ``ProbabilityValues`` contain:

    * ``values.[].label_configuration`` : list of length 2 - Configuration of the label pair
    * ``values.[].label_configuration.[].relevance`` : int – 0 for absence of the labels,
      1 for the presence of labels
    * ``values.[].label_configuration.[].label`` : str – Label name
    * ``values.[].statistic_value`` : float – Statistic value

    Attributes
    ----------
    feature_name : str
        Name of the feature
    values : list(dict)
        List of joint probability values with a schema described as ``ProbabilityValues``
    statistic_dataframes : dict(pandas.DataFrame)
        Joint Probability values as DataFrames for different relevance combinations.

        E.g. The probability P(A=0,B=1) can be retrieved via:
        ``pairwise_joint_probabilities.statistic_dataframes[(0,1)].loc['A', 'B']``
    """

    @classmethod
    def get(cls, multilabel_insights_key):
        """Retrieves pairwise joint probabilities

        You might find it more convenient to use
        :meth:`Feature.get_pairwise_joint_probabilities
        <datarobot.models.Feature.get_pairwise_joint_probabilities>`
        instead.

        Parameters
        ----------
        multilabel_insights_key: string
            Key for multilabel insights, unique for a project, feature and EDA stage combination.
            The multilabel_insights_key can be retrieved via
            ``Feature.multilabel_insights_key``.

        Returns
        -------
        PairwiseJointProbabilities
            The pairwise joint probabilities
        """
        return cls._get(multilabel_insights_key, "jointProbability")

    def as_dataframe(self, relevance_configuration):
        """Joint probabilities of label pairs as a (num_labels x num_labels) DataFrame.

        Parameters
        ----------
        relevance_configuration: tuple of length 2
            Valid options are (0, 0), (0, 1), (1, 0) and (1, 1). Values of 0 indicate absence of
            labels and 1 indicates presence of labels. The first value describes the
            presence for the labels in axis=0 and the second value describes the presence for the
            labels in axis=1.

            For example the matrix values for a relevance configuration of (0, 1) describe the
            probabilities of absent labels in the index axis and present labels in the column
            axis.

            E.g. The probability P(A=0,B=1) can be retrieved via:
            ``pairwise_joint_probabilities.as_dataframe((0,1)).loc['A', 'B']``

        Returns
        -------
        pandas.DataFrame
            The joint probabilities for the requested ``relevance_configuration``. Index and column
            names allow the interpretation of the values.
        """
        return self._as_dataframe(relevance_configuration)


class PairwiseConditionalProbabilities(PairwiseProbabilitiesBase):
    """
    Conditional probabilities of label pairs for multicategorical feature.

    .. versionadded:: v2.24

    Notes
    -----
    ``ProbabilityValues`` contain:

    * ``values.[].label_configuration`` : list of length 2 - Configuration of the label pair
    * ``values.[].label_configuration.[].relevance`` : int – 0 for absence of the labels,
      1 for the presence of labels
    * ``values.[].label_configuration.[].label`` : str – Label name
    * ``values.[].statistic_value`` : float – Statistic value

    Attributes
    ----------
    feature_name : str
        Name of the feature
    values : list(dict)
        List of conditional probability values with a schema described as ``ProbabilityValues``
    statistic_dataframes : dict(pandas.DataFrame)
        Conditional Probability values as DataFrames for different relevance combinations.
        The label names in the columns are the events, on which we condition. The label names in the
        index are the events whose conditional probability given the indexes is in the dataframe.

        E.g. The probability P(A=0|B=1) can be retrieved via:
        ``pairwise_conditional_probabilities.statistic_dataframes[(0,1)].loc['A', 'B']``
    """

    @classmethod
    def get(cls, multilabel_insights_key):
        """Retrieves pairwise conditional probabilities

        You might find it more convenient to use
        :meth:`Feature.get_pairwise_conditional_probabilities
        <datarobot.models.Feature.get_pairwise_conditional_probabilities>`
        instead.

        Parameters
        ----------
        multilabel_insights_key: string
            Key for multilabel insights, unique for a project, feature and EDA stage combination.
            The multilabel_insights_key can be retrieved via
            ``Feature.multilabel_insights_key``.

        Returns
        -------
        PairwiseConditionalProbabilities
            The pairwise conditional probabilities
        """
        return cls._get(multilabel_insights_key, "conditionalProbability")

    def as_dataframe(self, relevance_configuration):
        """Conditional probabilities of label pairs as a (num_labels x num_labels) DataFrame.
        The label names in the columns are the events, on which we condition. The label names in the
        index are the events whose conditional probability given the indexes is in the dataframe.

        E.g. The probability P(A=0|B=1) can be retrieved via:
        ``pairwise_conditional_probabilities.as_dataframe((0, 1)).loc['A', 'B']``

        Parameters
        ----------
        relevance_configuration: tuple of length 2
            Valid options are (0, 0), (0, 1), (1, 0) and (1, 1). Values of 0 indicate absence of
            labels and 1 indicates presence of labels. The first value describes the
            presence for the labels in axis=0 and the second value describes the presence for the
            labels in axis=1.

            For example the matrix values for a relevance configuration of (0, 1) describe the
            probabilities of absent labels in the index axis given the
            presence of labels in the column axis.

        Returns
        -------
        pandas.DataFrame
            The conditional probabilities for the requested ``relevance_configuration``.
            Index and column names allow the interpretation of the values.
        """
        return self._as_dataframe(relevance_configuration)
