# coding: utf-8
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

import numpy as np
import pandas as pd
import pytest
import responses

from datarobot import Feature
from datarobot.models.pairwise_statistics import (
    PairwiseConditionalProbabilities,
    PairwiseCorrelations,
    PairwiseJointProbabilities,
    PairwiseProbabilitiesBase,
)
from datarobot.utils import from_api
from tests.test_features import get_feature_response_multicategorical


class TestPairwiseStatistics(object):
    @pytest.fixture()
    def correlation_response(self):
        # Wrong lexicographical order to check if output gets ordered
        label_names = [u"🐶", "A"]
        statistic_values = np.array([[np.nan, 1.0], [2.0, 3.0]])
        data = self._get_data_field_for_statistics_api_response(
            label_names, statistic_values, label_relevance=None
        )
        response = {
            "statisticType": "correlation",
            "projectId": "5f8461253b8f1a2bd46ab5aa",
            "featureName": "multicategorical_column",
            "data": data,
        }
        return response

    @pytest.fixture()
    def joint_probability_response(self):
        data = self._get_data_field_for_probabilities_response()
        response = {
            "statisticType": "jointProbability",
            "projectId": "5f8461253b8f1a2bd46ab5aa",
            "featureName": "multicategorical_column",
            "data": data,
        }
        return response

    @pytest.fixture()
    def conditional_probability_response(self):
        data = self._get_data_field_for_probabilities_response()
        response = {
            "statisticType": "conditionalProbability",
            "projectId": "5f8461253b8f1a2bd46ab5aa",
            "featureName": "multicategorical_column",
            "data": data,
        }
        return response

    @pytest.fixture()
    def pairwise_correlation_instance(self, correlation_response):
        converted_response = from_api(correlation_response)
        return PairwiseCorrelations(
            feature_name=converted_response["feature_name"], data=converted_response["data"]
        )

    @pytest.fixture()
    def pairwise_joint_probabilities_instance(self, joint_probability_response):
        converted_response = from_api(joint_probability_response)
        return PairwiseJointProbabilities(
            feature_name=converted_response["feature_name"], data=converted_response["data"]
        )

    @pytest.fixture()
    def pairwise_conditional_probabilities_instance(self, conditional_probability_response):
        converted_response = from_api(conditional_probability_response)
        return PairwiseConditionalProbabilities(
            feature_name=converted_response["feature_name"], data=converted_response["data"]
        )

    def _get_data_field_for_probabilities_response(self):
        data = []
        for multiplier, relevance_configuration in enumerate(
            [(0, 0), (0, 1), (1, 0), (1, 1)], start=1
        ):
            # Wrong lexicographical order to check if output gets ordered
            label_names = [u"🐶", "A"]
            statistic_values = np.array([[np.nan, 1.0], [2.0, 3.0]])
            data.extend(
                self._get_data_field_for_statistics_api_response(
                    label_names, statistic_values * multiplier, relevance_configuration
                )
            )
        return data

    def _get_data_field_for_statistics_api_response(
        self, label_names, statistic_values, label_relevance=None
    ):
        """
        Creates the content of a pairwise statistics response ``data`` field for one relevance
        configuration.

        Parameters
        ----------
        label_names : list(str)
        statistic_values : numpy.ndarray
        label_relevance : tuple(int), optional
            Label relevance. The value of label_relevance[0] gets assigned to the first label of
            the label_configuration, label_relevance[1] gets assigned to the second label. By
            default no relevance gets assigned (required for correlation).

        Returns
        -------
        list(dict)
            Content of the pairwise statistics response ``data`` field for one relevance
            configuration, following the schema of the API response.
        """
        data = []
        for label_name_column, statistic_column in zip(label_names, statistic_values):
            for label_name_row, statistic_value in zip(label_names, statistic_column):
                if label_relevance:
                    label_configuration = [
                        {"label": label_name_column, "relevance": label_relevance[0]},
                        {"label": label_name_row, "relevance": label_relevance[1]},
                    ]
                else:
                    label_configuration = [{"label": label_name_column}, {"label": label_name_row}]
                if statistic_value is None or np.isnan(statistic_value):
                    # If the statistic_value is missing, there will be no statisticValue key
                    data.append({"labelConfiguration": label_configuration})
                else:
                    data.append(
                        {
                            "statisticValue": statistic_value,
                            "labelConfiguration": label_configuration,
                        }
                    )
        return data

    def test_to_statistic_dataframe(self, correlation_response):
        data = from_api(correlation_response["data"])
        actual = PairwiseCorrelations._to_statistic_dataframe(data)

        self._assert_statistic_dataframe(actual)

    def _assert_statistic_dataframe(self, actual):
        values = np.array([[3.0, 2.0], [1.0, np.nan]])
        expected = pd.DataFrame(values, index=[u"A", u"🐶"], columns=[u"A", u"🐶"])
        pd.testing.assert_frame_equal(actual, expected)

    def test_to_statistic_dataframes(self, joint_probability_response):
        data = from_api(joint_probability_response["data"])
        actual = PairwiseProbabilitiesBase._to_statistic_dataframes(data)

        self._assert_statistic_dataframes(actual)

    def _assert_statistic_dataframes(self, actual):
        expected = {}
        # Indexes and columns are expected to be sorted lexicographical
        values = np.array([[3.0, 2.0], [1.0, np.nan]])
        sorted_labels = [u"A", u"🐶"]
        expected[(0, 0)] = pd.DataFrame(values, index=sorted_labels, columns=sorted_labels)
        expected[(0, 1)] = pd.DataFrame(values * 2, index=sorted_labels, columns=sorted_labels)
        expected[(1, 0)] = pd.DataFrame(values * 3, index=sorted_labels, columns=sorted_labels)
        expected[(1, 1)] = pd.DataFrame(values * 4, index=sorted_labels, columns=sorted_labels)
        assert len(actual) == len(expected)
        for label_configuration in expected.keys():
            pd.testing.assert_frame_equal(
                actual[label_configuration], expected[label_configuration]
            )

    @responses.activate
    def test_get_correlations(self, correlation_response):
        multilabel_insights_key = "5f8461253b8f1a2bd46ab5aa"
        responses.add(
            responses.GET,
            (
                "https://host_name.com/multilabelInsights/"
                "{}/pairwiseStatistics/?statisticType=correlation"
            ).format(multilabel_insights_key),
            json=correlation_response,
            match_querystring=True,
        )
        pairwise_correlations = PairwiseCorrelations.get(multilabel_insights_key)

        self._assert_correlations(pairwise_correlations, correlation_response)

    def _assert_correlations(self, pairwise_correlations, correlation_response):
        assert pairwise_correlations.values == from_api(correlation_response["data"])
        assert (
            str(pairwise_correlations)
            == "PairwiseCorrelations(feature_name=multicategorical_column)"
        )
        self._assert_statistic_dataframe(pairwise_correlations.statistic_dataframe)

    @responses.activate
    def test_get_correlations_via_feature(self, correlation_response):
        multilabel_insights_key = "5f8461253b8f1a2bd46ab5aa"
        project_id = "5f8461253b8f1a2bd46ab5ab"
        feature_name = "multicategorical_column"
        feature_response_multicategorical = get_feature_response_multicategorical(
            multilabel_insights_key, project_id, feature_name
        )
        responses.add(
            responses.GET,
            "https://host_name.com/projects/{}/features/{}/".format(project_id, feature_name),
            json=feature_response_multicategorical,
        )
        responses.add(
            responses.GET,
            (
                "https://host_name.com/multilabelInsights/"
                "{}/pairwiseStatistics/?statisticType=correlation"
            ).format(multilabel_insights_key),
            json=correlation_response,
            match_querystring=True,
        )
        feature = Feature.get(project_id, feature_name)
        pairwise_correlations = feature.get_pairwise_correlations()
        self._assert_correlations(pairwise_correlations, correlation_response)

    def test_correlation_as_dataframe(self, pairwise_correlation_instance):
        expected = pairwise_correlation_instance.statistic_dataframe
        actual = pairwise_correlation_instance.as_dataframe()

        pd.testing.assert_frame_equal(actual, expected)

    @responses.activate
    def test_get_joint_probabilities(self, joint_probability_response):
        multilabel_insights_key = "5f8461253b8f1a2bd46ab5aa"
        responses.add(
            responses.GET,
            (
                "https://host_name.com/multilabelInsights/"
                "{}/pairwiseStatistics/?statisticType=jointProbability"
            ).format(multilabel_insights_key),
            json=joint_probability_response,
            match_querystring=True,
        )
        pairwise_joint_probabilities = PairwiseJointProbabilities.get(multilabel_insights_key)

        self._assert_joint_probabilities(pairwise_joint_probabilities, joint_probability_response)

    def _assert_joint_probabilities(self, pairwise_joint_probabilities, joint_probability_response):
        assert pairwise_joint_probabilities.values == from_api(joint_probability_response["data"])
        assert (
            str(pairwise_joint_probabilities)
            == "PairwiseJointProbabilities(feature_name=multicategorical_column)"
        )
        self._assert_statistic_dataframes(pairwise_joint_probabilities.statistic_dataframes)

    @responses.activate
    def test_get_joint_probabilities_via_feature(self, joint_probability_response):
        multilabel_insights_key = "5f8461253b8f1a2bd46ab5aa"
        project_id = "5f8461253b8f1a2bd46ab5ab"
        feature_name = "multicategorical_column"
        feature_response_multicategorical = get_feature_response_multicategorical(
            multilabel_insights_key, project_id, feature_name
        )
        responses.add(
            responses.GET,
            "https://host_name.com/projects/{}/features/{}/".format(project_id, feature_name),
            json=feature_response_multicategorical,
        )
        responses.add(
            responses.GET,
            (
                "https://host_name.com/multilabelInsights/"
                "{}/pairwiseStatistics/?statisticType=jointProbability"
            ).format(multilabel_insights_key),
            json=joint_probability_response,
            match_querystring=True,
        )
        feature = Feature.get(project_id, feature_name)
        pairwise_joint_probabilities = feature.get_pairwise_joint_probabilities()
        self._assert_joint_probabilities(pairwise_joint_probabilities, joint_probability_response)

    @responses.activate
    def test_get_conditional_probabilities(self, conditional_probability_response):
        multilabel_insights_key = "5f8461253b8f1a2bd46ab5aa"
        responses.add(
            responses.GET,
            (
                "https://host_name.com/multilabelInsights/"
                "{}/pairwiseStatistics/?statisticType=conditionalProbability"
            ).format(multilabel_insights_key),
            json=conditional_probability_response,
            match_querystring=True,
        )
        pairwise_conditional_probabilities = PairwiseConditionalProbabilities.get(
            multilabel_insights_key
        )

        self._assert_conditional_probabilities(
            pairwise_conditional_probabilities, conditional_probability_response
        )

    def _assert_conditional_probabilities(
        self, pairwise_conditional_probabilities, conditional_probability_response
    ):
        assert pairwise_conditional_probabilities.values == from_api(
            conditional_probability_response["data"]
        )
        assert (
            str(pairwise_conditional_probabilities)
            == "PairwiseConditionalProbabilities(feature_name=multicategorical_column)"
        )
        self._assert_statistic_dataframes(pairwise_conditional_probabilities.statistic_dataframes)

    @responses.activate
    def test_get_conditional_probabilities_via_feature(self, conditional_probability_response):
        multilabel_insights_key = "5f8461253b8f1a2bd46ab5aa"
        project_id = "5f8461253b8f1a2bd46ab5ab"
        feature_name = "multicategorical_column"
        feature_response_multicategorical = get_feature_response_multicategorical(
            multilabel_insights_key, project_id, feature_name
        )
        responses.add(
            responses.GET,
            "https://host_name.com/projects/{}/features/{}/".format(project_id, feature_name),
            json=feature_response_multicategorical,
        )
        responses.add(
            responses.GET,
            (
                "https://host_name.com/multilabelInsights/"
                "{}/pairwiseStatistics/?statisticType=conditionalProbability"
            ).format(multilabel_insights_key),
            json=conditional_probability_response,
            match_querystring=True,
        )
        feature = Feature.get(project_id, feature_name)
        pairwise_joint_probabilities = feature.get_pairwise_conditional_probabilities()
        self._assert_conditional_probabilities(
            pairwise_joint_probabilities, conditional_probability_response
        )

    @pytest.mark.parametrize(
        "fixture_name",
        ["pairwise_conditional_probabilities_instance", "pairwise_joint_probabilities_instance"],
    )
    def test_pairwise_probabilities_as_dataframe(self, request, fixture_name):
        for label_configuration in [(0, 0), (0, 1), (1, 0), (1, 1)]:
            pairwise_statistics_instance = request.getfixturevalue(fixture_name)
            actual = pairwise_statistics_instance.as_dataframe(label_configuration)
            expected = pairwise_statistics_instance.statistic_dataframes[label_configuration]
            pd.testing.assert_frame_equal(expected, actual)

    @pytest.mark.parametrize(
        "fixture_name",
        ["pairwise_conditional_probabilities_instance", "pairwise_joint_probabilities_instance"],
    )
    def test_pairwise_probabilities_as_dataframe_not_a_valid_label_configuration(
        self, request, fixture_name
    ):
        pairwise_statistics_instance = request.getfixturevalue(fixture_name)
        invalid_label_configuration = (2, -1)
        expected_error_msg = (
            "You have passed an invalid label configuration. Valid options are "
            "\(0, 0\), \(0, 1\), \(1, 0\) and \(1, 1\)"
        )
        with pytest.raises(ValueError, match=expected_error_msg):
            pairwise_statistics_instance._as_dataframe(invalid_label_configuration)
