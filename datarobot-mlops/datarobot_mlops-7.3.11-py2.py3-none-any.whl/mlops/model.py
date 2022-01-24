#  Copyright (c) 2019 DataRobot, Inc. and its affiliates. All rights reserved.
#  Last updated 2021.
#
#  DataRobot, Inc. Confidential.
#  This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.
#  The copyright notice above does not evidence any actual or intended publication of
#  such source code.
#
#  This file and its contents are subject to DataRobot Tool and Utility Agreement.
#  For details, see
#  https://www.datarobot.com/wp-content/uploads/2021/07/DataRobot-Tool-and-Utility-Agreement.pdf.

from builtins import str
import pandas as pd
from six import string_types

from datarobot.mlops.common import config
from datarobot.mlops.common.config import ConfigConstants
from datarobot.mlops.common.exception import DRUnsupportedType, DRCommonException
from datarobot.mlops.channel.output_channel_queue import (
    OutputChannelQueueAsync,
    OutputChannelQueueSync
)
from datarobot.mlops.event import Event
from datarobot.mlops.metric import GeneralStats, DeploymentStats, \
    PredictionsData, PredictionsDataContainer, DeploymentStatsContainer, \
    EventContainer


class Model(object):

    DEFAULT_ASYNC_REPORTING = False

    def __init__(self):
        self._stats_counter = {}
        self._report_queue = None
        if config.get_config_default(
                ConfigConstants.ASYNC_REPORTING, self.DEFAULT_ASYNC_REPORTING):
            self._report_queue = OutputChannelQueueAsync()
        else:
            self._report_queue = OutputChannelQueueSync()

    def __del__(self):
        if self._report_queue is not None:
            del self._report_queue

    def shutdown(self, timeout_sec=0):
        self._report_queue.shutdown(timeout_sec=timeout_sec)

    def _validate_input_association_ids(self, predictions, association_ids):
        if not isinstance(association_ids, list):
            raise DRUnsupportedType("association_ids argument has to be of type '{}'", list)
        if len(predictions) != len(association_ids):
            raise DRCommonException("Number of predictions and association ids should be the same")
        if len(set(association_ids)) != len(association_ids):
            raise DRCommonException("All association ids should be unique, "
                                    "association ids uniquely identify each individual prediction")

    def _validate_input_features_and_predictions(self, feature_data_df, predictions):
        for feature_name, feature_values in feature_data_df.iteritems():
            if len(feature_values) != len(predictions):
                raise DRUnsupportedType(
                    """The number of feature values for feature '{}' ({}) does not match the number
                      of prediction values {}""".format(
                        feature_name, len(feature_values), len(predictions)
                    )
                )

    def _validate_predictions(self, predictions, class_names):
        if not isinstance(predictions, list):
            raise DRUnsupportedType("'predictions' should be a list of probabilities or numbers")

        likely_classification_predictions = False
        likely_regression_predictions = False
        class_names_present = False
        likely_num_classes = 0
        if class_names is not None:
            if not isinstance(class_names, list):
                raise DRUnsupportedType("'class_names' should be a list")
            if len(class_names) < 2:
                raise DRCommonException("'class_names' should contain at least 2 values")
            for class_name in class_names:
                if not isinstance(class_name, string_types):
                    raise DRUnsupportedType(
                        "Each class name is expected to be a string, but received {}".format(
                            type(class_name)
                        )
                    )
            class_names_present = True
            likely_num_classes = len(class_names)

        first_prediction = predictions[0]
        if isinstance(first_prediction, list):
            likely_classification_predictions = True
            likely_num_classes = len(first_prediction)
        elif isinstance(first_prediction, float) or isinstance(first_prediction, int):
            likely_regression_predictions = True
        else:
            raise DRUnsupportedType("Predictions with type '{}' not supported".format(
                str(type(first_prediction))
            ))

        # Now verify that the remaining list of elements have the same instance / format
        for index, prediction in enumerate(predictions):
            if (
                    likely_regression_predictions and
                    not isinstance(prediction, float) and
                    not isinstance(prediction, int)
            ):
                raise DRUnsupportedType(
                    """Invalid prediction '{}' at index '{}', expecting a prediction value of
                    type int or float""".format(str(prediction), index)
                )
            if likely_classification_predictions:
                if not isinstance(prediction, list):
                    raise DRUnsupportedType(
                        """Invalid prediction '{}' at index '{}', expecting list of prediction
                        probabilities""".format(str(prediction), index)
                    )
                if len(prediction) < 2:
                    raise DRCommonException(
                        """Invalid prediction '{}' at index '{}', expecting list of size at least 2
                        """.format(str(prediction), index)
                    )
                if len(prediction) != likely_num_classes:
                    raise DRCommonException(
                        """Invalid prediction '{}' at index '{}', length of class probabilities in
                        the prediction does not match, expected '{}', got '{}'""".format(
                            str(prediction), index, likely_num_classes, len(prediction)
                        )
                    )
                if class_names_present:
                    if len(prediction) != len(class_names):
                        raise DRUnsupportedType(
                            """Number of prediction probabilities '[{}]'({}) at index {} does not
                             match class_names length {}""".format(
                                str(prediction), len(prediction), index, len(class_names)
                            )
                        )
                for prob in prediction:
                    if not isinstance(prob, float):
                        raise DRCommonException(
                            """Probability value '{}' in prediction '{}' at index '{}' is not
                            a float value""".format(prob, prediction, index)
                        )
                    if prob > 1.0 or prob < 0.0:
                        raise DRCommonException(
                            """Probability value '{}' in prediction '{}' at index '{}' is not
                            between 0 and 1""".format(prob, prediction, index)
                        )

    def _report_stats(self, deployment_id, model_id, stats_serializer):
        """
        This function is used for reporting metrics and events.
        """
        data_type = stats_serializer.data_type()

        # Keep account of number of records submitted to channel
        if self._report_queue.submit(stats_serializer, deployment_id):
            if data_type not in self._stats_counter:
                self._stats_counter[data_type] = 0
            self._stats_counter[data_type] += 1
            return True
        return False

    def get_stats_counters(self):
        return self._stats_counter

    def _get_general_stats(self, model_id):
        return GeneralStats(model_id)

    def report_deployment_stats(self, deployment_id, model_id,
                                num_predictions,
                                execution_time_ms=None
                                ):
        """
        Report the number of predictions and execution time
        to DataRobot MLOps.

        :param deployment_id: the deployment for these metrics
        :type deployment_id: str
        :param model_id: the model for these metrics
        :type model_id: str
        :param num_predictions: number of predictions
        :type num_predictions: int
        :param execution_time_ms: time in milliseconds
        :type execution_time_ms: float
        :returns: report status - True on success, False otherwise.
        :rtype: bool
        """
        deployment_stats = DeploymentStats(num_predictions, execution_time_ms)
        deployment_stats_container = DeploymentStatsContainer(self._get_general_stats(model_id),
                                                              deployment_stats)

        return self._report_stats(deployment_id, model_id, deployment_stats_container)

    def report_predictions_data(
            self, deployment_id, model_id,
            features_df=None, predictions=None, association_ids=None, class_names=None
    ):
        """
        Report features and predictions to DataRobot MLOps for tracking and monitoring.

        :param deployment_id: the deployment for these metrics
        :type deployment_id: str
        :param model_id: the model for these metrics
        :type model_id: str
        :param features_df: Dataframe containing features to track and monitor.  All the features
            in the dataframe are reported.  Omit the features from the dataframe that do not need
            reporting.
        :type features_df: pandas dataframe
        :param predictions: List of predictions.  For Regression deployments, this is 1D list
            containing prediction values.  For Classification deployments, this is a 2D list, in
            which the inner list is the list of probabilities for each class type
            Binary Classification: e.g. [[0.2, 0.8], [0.3, 0.7]].
            Regression Predictions: e.g. [1, 2, 4, 3, 2]
        :type predictions: list

        At least one of `features` or `predictions` must be specified.

        :param association_ids: an optional list of association IDs corresponding to each
            prediction used for accuracy calculations.  Association IDs have to be unique for each
            prediction reported.  Number of `predictions` should be equal to number of
            `association_ids` in the list
        :type association_ids: list
        :param class_names: names of predicted classes, e.g. ["class1", "class2", "class3"].  For
            classification deployments, class names must be in the same order as the prediction
            probabilities reported. If not specified, this prediction order defaults to the order
            of the class names on the deployment.
            This argument is ignored for Regression deployments.
        :type class_names: list
        :returns: report status - True on success, False otherwise.
        :rtype: bool
        """
        if features_df is None and not predictions:
            raise DRCommonException("One of `features_df` or `predictions` argument is required")

        if predictions:
            self._validate_predictions(predictions, class_names)

        if features_df is not None and not isinstance(features_df, pd.DataFrame):
            raise DRUnsupportedType("features_df argument has to be of type '{}'", pd.DataFrame)

        if predictions and association_ids:
            self._validate_input_association_ids(predictions, association_ids)

        # If dataframe provided we do a deep copy, in case is modified before processing
        feature_data_df = None
        if features_df is not None:
            feature_data_df = features_df.copy(deep=True)

        if feature_data_df is not None and predictions:
            self._validate_input_features_and_predictions(feature_data_df, predictions)

        return self._report_metric(deployment_id, model_id,
                                   feature_data_df, predictions, association_ids, class_names)

    def report_event(self, deployment_id, model_id, event):
        # type: (Event) -> bool
        """
        Wrap event in a container and use report_stats() to place in queue.
        :returns: report status - True on success, False otherwise.
        :rtype: bool
        """
        # automatically set deployment ID so user's code doesn't need to
        if event.is_entity_a_deployment():
            event.set_entity_id(deployment_id)
        event_container = EventContainer(event)
        return self._report_stats(deployment_id, model_id, event_container)

    def _report_metric(self, deployment_id, model_id,
                       feature_data, predictions, association_ids, class_names):
        predictions_data = PredictionsData(feature_data, predictions,
                                           association_ids, class_names)
        predictions_data_container = PredictionsDataContainer(
            self._get_general_stats(model_id), predictions_data
        )
        return self._report_stats(deployment_id, model_id, predictions_data_container)
