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

import abc
from datetime import datetime
from dateutil.tz import tzlocal, sys
from decimal import Decimal
from future.utils import with_metaclass
import json
import numpy as np
import pandas as pd
from six import string_types

from datarobot.mlops.common.enums import DataFormat, DataType
from datarobot.mlops.common.exception import DRUnsupportedType
from datarobot.mlops.event import Event

"""
Currently there are the following independent types of information:

GeneralStats: model ID, timestamp
DeploymentStats: number of predictions, execution time
PredictionsStats: predictions, class names

These parameters may be combined and reported in different ways and structures:

Reporting deployment stats includes: model ID, timestamp, num predictions, execution time.
Reporting predictions includes: timestamp, predictions and class names.

DeploymentStatsContainer and PredictionStatsContainer are responsible
for implementing to_iterable() method for data structuring.
"""


def estimate_metric_size(metric):
    """
    Estimate the memory usage of object metric
    :param metric:
    :return: size of metric in bytes
    """
    estimate_size = sys.getsizeof(metric)

    if hasattr(metric, "__dict__"):
        estimate_size += sum([sys.getsizeof(x) for x in metric.__dict__.values() if x is not None])
    return estimate_size


class SerializationConstants:
    class GeneralConstants:
        MODEL_ID_FIELD_NAME = "modelId"
        TIMESTAMP_FIELD_NAME = "timestamp"

    class DeploymentStatsConstants:
        NUM_PREDICTIONS_FIELD_NAME = "numPredictions"
        EXECUTION_TIME_FIELD_NAME = "executionTime"

    class PredictionsStatsConstants:
        PREDICTIONS_FIELD_NAME = "predictions"
        ASSOCIATION_IDS_FIELD_NAME = "associationIds"
        RESULTS_FIELD_NAME = "results"
        CLASS_NAMES_FIELD_NAME = "classNames"

    class PredictionsDataConstants:
        PREDICTIONS_FIELD_NAME = "predictions"
        ASSOCIATION_IDS_FIELD_NAME = "associationIds"
        FEATURES_FIELD_NAME = "features"
        CLASS_NAMES_FIELD_NAME = "classNames"

    class EventConstants:
        EVENT_TYPE_FIELD_NAME = "eventType"
        ORG_ID_FIELD_NAME = "orgId"
        ENTITY_ID_FIELD_NAME = "deploymentId"  # todo this is changing
        MESSAGE_FIELD_NAME = "message"
        PREDICTION_REQUEST_DATA_FIELD_NAME = "predictionRequestData"


class GeneralStats:
    """
    General statistics.
    """

    def __init__(self, model_id, timestamp=None):
        self._model_id = model_id
        if timestamp is None:
            micro_timestamp = datetime.now(tzlocal()).strftime("%Y-%m-%d %H:%M:%S.%f%z")
            self._timestamp = micro_timestamp[0:23] + micro_timestamp[26:]
        else:
            self._timestamp = timestamp

    def get_model_id(self):
        return self._model_id

    def get_timestamp(self):
        return self._timestamp


class DeploymentStats:
    """
    Class to keep data about deployment statistics.
    """
    def __init__(self, num_predictions, execution_time):
        self._num_predictions = num_predictions
        self._execution_time = execution_time

    def get_num_predictions(self):
        return self._num_predictions

    def get_execution_time(self):
        return self._execution_time


class PredictionsStats:
    """
    Class to keep data about predictions statistics.
    """

    def __init__(self, predictions, class_names, association_ids=None):
        self._predictions = predictions
        self._class_names = class_names
        self._association_ids = association_ids

    def get_predictions(self):
        return self._predictions

    def get_class_names(self):
        return self._class_names

    def get_association_ids(self):
        return self._association_ids


class FeatureDataStats:
    """
    Class to keep feature data.
    """

    def __init__(self, feature_data):
        self._feature_data = feature_data

    def get_feature_data(self):
        return self._feature_data


class PredictionsData:
    """
    Class to keep features and predictions data together
    """
    def __init__(self, feature_data=None, predictions=None, association_ids=None, class_names=None):
        self._feature_data = feature_data
        self._has_feature_data = False if feature_data is None else True
        self._predictions = predictions
        self._association_ids = association_ids
        self._class_names = class_names

    def get_num_rows(self):
        if self.has_feature_data():
            return len(self._feature_data)
        else:
            return len(self._predictions)

    def get_predictions(self):
        return self._predictions

    def get_class_names(self):
        return self._class_names

    def get_association_ids(self):
        return self._association_ids

    def has_feature_data(self):
        return self._has_feature_data

    def get_feature_data_df(self):
        return self._feature_data


class StatsContainer(with_metaclass(abc.ABCMeta)):
    def __init(self):
        pass

    @abc.abstractmethod
    def to_iterable(self):
        """
        """

    @abc.abstractmethod
    def get_estimate_size(self):
        """
        Return current stats estimated size in memory
        :return: estimated size of object in bytes
        """

    @abc.abstractmethod
    def data_type(self):
        """
        Get type of the data current metric represents.
        Check @DataType.

        :return: type of the data for current metric.
        :rtype: DataType
        """

    def serialize(self, data_format):
        if data_format == DataFormat.JSON:
            return self.to_iterable()
        elif data_format == DataFormat.BYTE_ARRAY:
            json_str = json.dumps(self.to_iterable())
            return bytearray(json_str, encoding="utf8")
        else:
            raise NotImplementedError("Metric serialization does not support data format {}"
                                      .format(data_format))

    def serialize_iterable(self, data_format, stat_iterable):
        if data_format == DataFormat.JSON:
            return stat_iterable
        elif data_format == DataFormat.BYTE_ARRAY:
            json_str = json.dumps(stat_iterable)
            return bytearray(json_str, encoding="utf8")
        else:
            raise NotImplementedError("Metric serialization does not support data format {}"
                                      .format(data_format))


class DeploymentStatsContainer(StatsContainer):
    """
    Deployment stats data formatter.
    """
    def __init__(self, general_stats, deployment_stats):
        if not isinstance(general_stats, GeneralStats):
            raise DRUnsupportedType("Wrong value type for general_stats. Expected: {}, provided: {}"
                                    .format(GeneralStats, type(general_stats)))
        if not isinstance(deployment_stats, DeploymentStats):
            raise DRUnsupportedType(
                "Wrong value type for deployment_stats. Expected: {}, provided: {}"
                .format(DeploymentStats, type(deployment_stats))
            )

        self._general_stats = general_stats
        self._deployment_stats = deployment_stats
        self._estimate_size = (estimate_metric_size(self._general_stats)
                               + estimate_metric_size(self._deployment_stats))

    def get_estimate_size(self):
        return self._estimate_size

    def data_type(self):
        return DataType.DEPLOYMENT_STATS

    def to_iterable(self):
        ret = dict()
        ret[SerializationConstants.GeneralConstants.TIMESTAMP_FIELD_NAME] = \
            self._general_stats.get_timestamp()
        ret[SerializationConstants.GeneralConstants.MODEL_ID_FIELD_NAME] = \
            self._general_stats.get_model_id()
        ret[SerializationConstants.DeploymentStatsConstants.NUM_PREDICTIONS_FIELD_NAME] = \
            self._deployment_stats.get_num_predictions()
        ret[SerializationConstants.DeploymentStatsConstants.EXECUTION_TIME_FIELD_NAME] = \
            self._deployment_stats.get_execution_time()
        return ret


class PredictionsStatsContainer(StatsContainer):
    """
    Predictions stats data formatter.
    """
    def __init__(self, general_stats, predictions_stats):
        if not isinstance(general_stats, GeneralStats):
            raise DRUnsupportedType("Wrong value type for general_stats. Expected: {}, provided: {}"
                                    .format(GeneralStats, type(general_stats)))
        if not isinstance(predictions_stats, PredictionsStats):
            raise DRUnsupportedType(
                "Wrong value type for predictions_stats. Expected: {}, provided: {}"
                .format(PredictionsStats, type(predictions_stats))
            )

        self._general_stats = general_stats
        self._predictions_stats = predictions_stats

    def data_type(self):
        return DataType.TARGET_DRIFT

    def to_iterable(self):
        results_array = []
        results_object = dict()
        results_object[SerializationConstants.GeneralConstants.TIMESTAMP_FIELD_NAME] =\
            self._general_stats.get_timestamp()
        results_object[SerializationConstants.PredictionsStatsConstants.PREDICTIONS_FIELD_NAME] = \
            self._predictions_stats.get_predictions()

        # If association_ids are specified, then include them
        if self._predictions_stats.get_association_ids():
            results_object[
                SerializationConstants.PredictionsStatsConstants.ASSOCIATION_IDS_FIELD_NAME] = \
                self._predictions_stats.get_association_ids()

        results_object[SerializationConstants.GeneralConstants.MODEL_ID_FIELD_NAME] = \
            self._general_stats.get_model_id()
        results_array.append(results_object)

        ret = dict()
        ret[SerializationConstants.PredictionsStatsConstants.RESULTS_FIELD_NAME] = results_array
        if self._predictions_stats.get_class_names() is not None:
            ret[SerializationConstants.PredictionsStatsConstants.CLASS_NAMES_FIELD_NAME] = \
                self._predictions_stats.get_class_names()
        return ret


class FeatureDataStatsContainer(StatsContainer):
    """
    Feature data formatter.
    """
    def __init__(self, feature_data_stats):
        if not isinstance(feature_data_stats, FeatureDataStats):
            raise DRUnsupportedType(
                "Wrong value type for feature_data_stats. Expected: {}, provided: {}"
                .format(FeatureDataStats, type(feature_data_stats))
            )

        self._feature_data_stats = feature_data_stats

    def data_type(self):
        return DataType.FEATURE_DATA

    def to_iterable(self):
        return self._feature_data_stats.get_feature_data()


class PredictionsDataContainer(StatsContainer):
    """
    Features and Predictions data formatter.
    """

    def __init__(self, general_stats, predictions_data):
        if not isinstance(general_stats, GeneralStats):
            raise DRUnsupportedType("Wrong value type for general_stats. Expected: {}, provided: {}"
                                    .format(GeneralStats, type(general_stats)))
        if not isinstance(predictions_data, PredictionsData):
            raise DRUnsupportedType(
                "Wrong value type for predictions data. Expected: {}, provided: {}".format(
                    PredictionsData, type(predictions_data)
                )
            )

        self._general_stats = general_stats
        self._predictions_data = predictions_data
        self._num_rows = predictions_data.get_num_rows()
        self._estimate_size = (estimate_metric_size(self._num_rows)
                               + estimate_metric_size(self._general_stats)
                               + estimate_metric_size(self._predictions_data))

    def get_estimate_size(self):
        return self._estimate_size

    def get_num_rows(self):
        return self._num_rows

    def data_type(self):
        return DataType.PREDICTIONS_DATA

    def to_iterable(self):
        predictions_data_object = dict()
        predictions_data_object[SerializationConstants.GeneralConstants.TIMESTAMP_FIELD_NAME] = \
            self._general_stats.get_timestamp()
        if self._general_stats.get_model_id():
            predictions_data_object[SerializationConstants.GeneralConstants.MODEL_ID_FIELD_NAME] = \
                self._general_stats.get_model_id()

        # If features are specified, include them
        if self._predictions_data.has_feature_data():
            feature_data = self._feature_dataframe_to_feature_dict(
                self._predictions_data.get_feature_data_df()
            )
            predictions_data_object[
                SerializationConstants.PredictionsDataConstants.FEATURES_FIELD_NAME
            ] = feature_data

        # If predictions are specified, include them
        if self._predictions_data.get_predictions():
            predictions_data_object[
                SerializationConstants.PredictionsDataConstants.PREDICTIONS_FIELD_NAME
            ] = self._predictions_data.get_predictions()

        # If association_ids are specified, then include them
        if self._predictions_data.get_association_ids():
            predictions_data_object[
                SerializationConstants.PredictionsStatsConstants.ASSOCIATION_IDS_FIELD_NAME] = \
                self._predictions_data.get_association_ids()

        if self._predictions_data.get_class_names():
            predictions_data_object[
                SerializationConstants.PredictionsDataConstants.CLASS_NAMES_FIELD_NAME
            ] = self._predictions_data.get_class_names()

        return predictions_data_object

    def _feature_dataframe_to_feature_dict(self, feature_dataframe):
        if not isinstance(feature_dataframe, pd.DataFrame):
            raise DRUnsupportedType("feature_data argument has to be of type '{}'", pd.DataFrame)

        # Building feature data structure from dataframe
        feature_data = {}

        headers = list(feature_dataframe.columns)
        try:
            values = feature_dataframe.to_npy()
        except AttributeError:
            # pandas before 0.24 doesn't have .to_numpy()
            values = feature_dataframe.values

        # save columns of values into a dictionary:
        # {"feature1": [0.1, 0.2, 0.7], "feature2": ["aa", "bb", "cc"]}.
        for i in range(0, len(headers)):
            vals = values[:, i].tolist()
            supported_type = False
            missing_values = 0
            for j in range(0, len(vals)):
                if isinstance(vals[j], float):
                    # Missing values of any column type are encoded as float nan in the pandas df.
                    # We need to read another column to determine the type of the column.
                    if np.isnan(vals[j]):
                        missing_values += 1
                        continue
                    supported_type = True
                    break
                if isinstance(vals[j], int):
                    supported_type = True
                    break
                if isinstance(vals[j], string_types):
                    supported_type = True
                    break
                if isinstance(vals[j], Decimal):
                    # Decimal type cannot be json serialized; convert column to float.
                    for k in range(j, len(vals)):
                        vals[k] = float(vals[k])
                    supported_type = True
                    break
                else:
                    # TODO: once we have a logging mechanism, this should be logged and col skipped
                    raise DRUnsupportedType(
                        "feature_data field type is not supported '{}'".format(type(vals[j]))
                    )

            # If all values are NaN, then also include the feature
            if missing_values == len(vals):
                supported_type = True

            if supported_type:
                feature_data[headers[i]] = vals

        return feature_data


class EventContainer(StatsContainer):
    """
    External event data formatter.
    """
    def __init__(self, event):
        if not isinstance(event, Event):
            raise DRUnsupportedType(
                "Wrong value type for event. Expected: {}, provided: {}"
                .format(Event, type(event))
            )
        self._event = event
        self._estimate_size = estimate_metric_size(self._event)

    def get_estimate_size(self):
        return self._estimate_size

    def data_type(self):
        return DataType.EXTERNAL_EVENT

    def to_iterable(self):
        ret = dict()
        ret[SerializationConstants.GeneralConstants.TIMESTAMP_FIELD_NAME] = \
            self._event.get_timestamp()
        ret[SerializationConstants.EventConstants.EVENT_TYPE_FIELD_NAME] = \
            self._event.get_event_type()
        ret[SerializationConstants.EventConstants.MESSAGE_FIELD_NAME] = \
            self._event.get_message()
        ret[SerializationConstants.EventConstants.ORG_ID_FIELD_NAME] = \
            self._event.get_org_id()
        ret[SerializationConstants.EventConstants.ENTITY_ID_FIELD_NAME] = \
            self._event.get_entity_id()
        ret[SerializationConstants.EventConstants.PREDICTION_REQUEST_DATA_FIELD_NAME] = \
            self._event.get_prediction_request_data()
        return ret
