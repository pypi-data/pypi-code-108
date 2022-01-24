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
from collections import namedtuple
import itertools

import pandas as pd
from six.moves.urllib_parse import parse_qs, urlparse
import trafaret as t

from datarobot import enums, errors
from datarobot._compat import Int, String

from ..utils import from_api
from .api_object import APIObject

_FEATURE = "Explanation_{}_feature_name"
_FEATURE_VAL = "Explanation_{}_feature_value"
_STRENGTH = "Explanation_{}_strength"


class RowsIterator(object):
    """
    Yields all available records one-by-one.

    While iterating, fetches rows from API with a series of requests with specified limit
    Stops iterating when API has no more objects to fetch
    """

    _trafaret = t.Dict(
        {t.Key("data"): t.List(t.Dict().allow_extra("*")), t.Key("next"): String | t.Null}
    ).allow_extra("*")

    def __init__(self, client, path, limit=None):
        self.client = client
        self.path = path
        self.query_params = dict(limit=limit)

        self._queue = []
        self._stop_flag = None

    def __iter__(self):
        return self

    def next(self):
        if self._stop_flag and not self._queue:
            raise StopIteration()

        if not self._queue:
            items, next_url = self._load_more()
            self._queue.extend(items)
            if not self._queue:
                raise StopIteration()

            self._stop_flag = next_url is None
            self._stop_flag |= self.is_exhausted(len(items), self.query_params.get("limit"))
            if next_url is not None:
                self._save_next_url(next_url)

        data_dict = self._queue.pop(0)
        return data_dict

    __next__ = next

    @staticmethod
    def is_exhausted(loaded_count, limit):
        if limit is None:
            # If there was no limit param, assume all items were fetched
            return True

        # If we asked for 20 items but got 10 items that means our collection is exhausted
        return loaded_count < limit

    def _load_more(self):
        """Fetch more items from API, validate response, save next url"""
        response = self.client.get(self.path, params=self.query_params)
        if response.status_code != 200:
            e_msg = "Server returned unexpected status code"
            raise errors.ServerError(
                e_msg.format(response.status_code), response.status_code,
            )

        body = self._trafaret.check(response.json())
        return body["data"], body["next"]

    def _save_next_url(self, next_url):
        """Next URL should contain `limit` & `offset` query params"""
        parsed = urlparse(next_url)
        parsed_qs = parse_qs(parsed.query)
        self.query_params = {key: int(values_list[0]) for key, values_list in parsed_qs.items()}


TrainingPredictionsRow = namedtuple(
    "TrainingPredictionsRow",
    (
        "row_id,partition_id,prediction,prediction_values,"
        "timestamp,forecast_point,forecast_distance,series_id,"
        "prediction_explanations,shap_metadata"
    ),
)


class TrainingPredictionsIterator(RowsIterator):
    """
    Lazily fetches training predictions from DataRobot API in chunks of specified size and then
    iterates rows from responses as named tuples. Each row represents a training prediction
    computed for a dataset's row. Each named tuple has the following structure:

    Attributes
    ----------
    row_id : int
        id of the record in original dataset for which training prediction is calculated
    partition_id : str or float
        id of the data partition that the row belongs to
    prediction : float
        the model's prediction for this data row
    prediction_values : list of dictionaries
        an array of dictionaries with a schema described as ``PredictionValue``
    timestamp : str or None
        (New in version v2.11) an ISO string representing the time of the prediction
        in time series project; may be None for non-time series projects
    forecast_point : str or None
        (New in version v2.11) an ISO string representing the point in time
        used as a basis to generate the predictions in time series project;
        may be None for non-time series projects
    forecast_distance : str or None
        (New in version v2.11) how many time steps are between the forecast point and the
        timestamp in time series project; None for non-time series projects
    series_id : str or None
        (New in version v2.11) the id of the series in a multiseries project;
        may be NaN for single series projects; None for non-time series projects
    prediction_explanations : list of dict or None
        (New in version v2.21) The prediction explanations for each feature. The total elements in
        the array are bounded by ``max_explanations`` and feature count. Only present if prediction
        explanations were requested. Schema described as ``PredictionExplanations``.
    shap_metadata : dict or None
        (New in version v2.21) The additional information necessary to understand SHAP based
        prediction explanations. Only present if `explanation_algorithm` equals
        `datarobot.enums.EXPLANATIONS_ALGORITHM.SHAP` was added in compute request. Schema
        described as ``ShapMetadata``.

    Notes
    -----
    Each ``PredictionValue`` dict contains these keys:

        label
            describes what this model output corresponds to. For regression
            projects, it is the name of the target feature. For classification and multiclass
            projects, it is a label from the target feature.
        value
            the output of the prediction. For regression projects, it is the
            predicted value of the target. For classification and multiclass projects, it is
            the predicted probability that the row belongs to the class identified by the label.

    Each ``PredictionExplanations`` dictionary contains these keys:

        label : string
            describes what output was driven by this prediction explanation. For regression
            projects, it is the name of the target feature. For classification projects, it is the
            class whose probability increasing would correspond to a positive strength of this
            prediction explanation.
        feature : string
            the name of the feature contributing to the prediction
        feature_value : object
            the value the feature took on for this row. The type corresponds to the feature
            (boolean, integer, number, string)
        strength : float
            algorithm-specific explanation value attributed to feature in this row

    ``ShapMetadata`` dictionary contains these keys:

        shap_remaining_total : float
            The total of SHAP values for features beyond the ``max_explanations``. This can be
            identically 0 in all rows, if `max_explanations` is greater than the number of features
            and thus all features are returned.
        shap_base_value : float
            the model's average prediction over the training data. SHAP values are deviations from
            the base value.
        warnings : dict or None
            SHAP values calculation warnings (e.g. additivity check failures in XGBoost models).
            Schema described as ``ShapWarnings``.

    ``ShapWarnings`` dictionary contains these keys:

        mismatch_row_count : int
            the count of rows for which additivity check failed
        max_normalized_mismatch : float
            the maximal relative normalized mismatch value

    Examples
    --------
    .. code-block:: python

        import datarobot as dr

        # Fetch existing training predictions by their id
        training_predictions = dr.TrainingPredictions.get(project_id, prediction_id)

        # Iterate over predictions
        for row in training_predictions.iterate_rows()
            print(row.row_id, row.prediction)
    """

    _row_trafaret = t.Dict(
        {
            t.Key("row_id"): Int(),
            t.Key("partition_id"): String() | t.Float(),
            t.Key("prediction"): t.Float() | String(),
            t.Key("prediction_values"): t.List(
                t.Dict({t.Key("label"): t.Float | String, t.Key("value"): t.Float}).ignore_extra(
                    "*"
                )
            ),
            t.Key("timestamp", default=None): String | t.Null,
            t.Key("forecast_point", default=None): String | t.Null,
            t.Key("forecast_distance", default=None): Int | t.Null,
            t.Key("series_id", default=None): String | Int | t.Null,
            t.Key("prediction_explanations", default=None): t.List(
                t.Dict(
                    {
                        t.Key("feature"): String(),
                        t.Key("feature_value"): String(),
                        t.Key("strength"): t.Float(),
                        t.Key("label"): t.Float() | String(),
                    }
                )
            )
            | t.Null(),
            t.Key("shap_metadata", optional=True, default=None): t.Dict(
                {
                    t.Key("shap_base_value"): t.Float(),
                    t.Key("shap_remaining_total"): t.Float(),
                    t.Key("warnings", optional=True): t.Dict(
                        {
                            t.Key("mismatch_row_count"): Int(),
                            t.Key("max_normalized_mismatch"): t.Float(),
                        }
                    ),
                }
            )
            | t.Null(),
        }
    ).ignore_extra("*")

    def next(self):
        row_dict = super(TrainingPredictionsIterator, self).next()
        row_dict = self._row_trafaret.check(row_dict)
        return TrainingPredictionsRow(**row_dict)

    __next__ = next

    def _load_more(self):
        rows, next_url = super(TrainingPredictionsIterator, self)._load_more()
        return from_api(rows), next_url


class TrainingPredictions(APIObject):
    """
    Represents training predictions metadata and provides access to prediction results.

    Attributes
    ----------
    project_id : str
        id of the project the model belongs to
    model_id : str
        id of the model
    prediction_id : str
        id of generated predictions
    data_subset : datarobot.enums.DATA_SUBSET
        data set definition used to build predictions.
        Choices are:

        - `datarobot.enums.DATA_SUBSET.ALL`
            for all data available. Not valid for models in datetime partitioned projects.
        - `datarobot.enums.DATA_SUBSET.VALIDATION_AND_HOLDOUT`
            for all data except training set. Not valid for models in datetime partitioned projects.
        - `datarobot.enums.DATA_SUBSET.HOLDOUT`
            for holdout data set only.
        - `datarobot.enums.DATA_SUBSET.ALL_BACKTESTS`
            for downloading the predictions for all backtest validation folds.
            Requires the model to have successfully scored all backtests.
            Datetime partitioned projects only.
    explanation_algorithm : datarobot.enums.EXPLANATIONS_ALGORITHM
        (New in version v2.21) Optional. If set to shap, the response will include prediction
        explanations based on the SHAP explainer (SHapley Additive exPlanations). Defaults to null
        (no prediction explanations).
    max_explanations : int
        (New in version v2.21) The number of top contributors that are included in prediction
        explanations. Max 100. Defaults to null for datasets narrower than 100 columns, defaults to
        100 for datasets wider than 100 columns.
    shap_warnings : list
        (New in version v2.21) Will be present if ``explanation_algorithm`` was set to
        `datarobot.enums.EXPLANATIONS_ALGORITHM.SHAP` and there were additivity failures during SHAP
        values calculation.

    Notes
    -----
    Each element in ``shap_warnings`` has the following schema:

    partition_name : str
        the partition used for the prediction record.
    value : object
        the warnings related to this partition.

    The objects in ``value`` are:

    mismatch_row_count : int
        the count of rows for which additivity check failed.
    max_normalized_mismatch : float
        the maximal relative normalized mismatch value.

    Examples
    --------
    Compute training predictions for a model on the whole dataset

    .. code-block:: python

        import datarobot as dr

        # Request calculation of training predictions
        training_predictions_job = model.request_training_predictions(dr.enums.DATA_SUBSET.ALL)
        training_predictions = training_predictions_job.get_result_when_complete()
        print('Training predictions {} are ready'.format(training_predictions.prediction_id))

        # Iterate over actual predictions
        for row in training_predictions.iterate_rows():
            print(row.row_id, row.partition_id, row.prediction)

    List all training predictions for a project

    .. code-block:: python

        import datarobot as dr

        # Fetch all training predictions for a project
        all_training_predictions = dr.TrainingPredictions.list(project_id)

        # Inspect all calculated training predictions
        for training_predictions in all_training_predictions:
            print(
                'Prediction {} is made for data subset "{}"'.format(
                    training_predictions.prediction_id,
                    training_predictions.data_subset,
                )
            )

    Retrieve training predictions by id

    .. code-block:: python

        import datarobot as dr

        # Getting training predictions by id
        training_predictions = dr.TrainingPredictions.get(project_id, prediction_id)

        # Iterate over actual predictions
        for row in training_predictions.iterate_rows():
            print(row.row_id, row.partition_id, row.prediction)
    """

    def __init__(
        self,
        project_id,
        prediction_id,
        model_id=None,
        data_subset=None,
        explanation_algorithm=None,
        max_explanations=None,
        shap_warnings=None,
    ):
        self.project_id = project_id
        self.model_id = model_id
        self.prediction_id = prediction_id
        self.path = self.build_path(project_id, prediction_id)
        self.data_subset = data_subset
        self.explanation_algorithm = explanation_algorithm
        self.max_explanations = max_explanations
        self.shap_warnings = shap_warnings

    @staticmethod
    def build_path(project_id, prediction_id=None):
        if prediction_id is not None:
            return "projects/{}/trainingPredictions/{}/".format(project_id, prediction_id)

        return "projects/{}/trainingPredictions/".format(project_id)

    @classmethod
    def from_location(
        cls,
        location,
        data_subset=None,
        model_id=None,
        explanation_algorithm=None,
        max_explanations=None,
        shap_warnings=None,
    ):
        head, tail = location.split("/trainingPredictions/", 1)
        project_id, prediction_id = head.split("/")[-1], tail.split("/")[0]
        return cls(
            project_id,
            prediction_id,
            data_subset=data_subset,
            model_id=model_id,
            explanation_algorithm=explanation_algorithm,
            max_explanations=max_explanations,
            shap_warnings=shap_warnings,
        )

    @classmethod
    def list(cls, project_id):
        """
        Fetch all the computed training predictions for a project.

        Parameters
        ----------
        project_id : str
            id of the project

        Returns
        -------
        A list of :py:class:`TrainingPredictions` objects
        """
        _trafaret = t.Dict(
            {
                t.Key("data"): t.List(
                    t.Dict(
                        {
                            t.Key("url"): String(),
                            t.Key("model_id"): String(),
                            t.Key("data_subset"): String(),
                            t.Key("explanation_algorithm", optional=True): String() | t.Null(),
                            t.Key("max_explanations", optional=True): Int() | t.Null(),
                            t.Key("shap_warnings", optional=True): t.Dict(
                                {
                                    t.Key("partition_name"): String(),
                                    t.Key("value"): t.Dict(
                                        {
                                            t.Key("mismatch_row_count"): Int(),
                                            t.Key("max_normalized_mismatch"): t.Float(),
                                        }
                                    ),
                                }
                            )
                            | t.Null(),
                        }
                    ).ignore_extra("*")
                ),
            }
        ).ignore_extra("*")

        path = cls.build_path(project_id)
        converted = from_api(cls._server_data(path), keep_null_keys=True)
        validated = _trafaret.check(converted)["data"]
        return [
            cls.from_location(
                item["url"],
                data_subset=item["data_subset"],
                model_id=item["model_id"],
                explanation_algorithm=item.get("explanation_algorithm"),
                max_explanations=item.get("max_explanations"),
                shap_warnings=item.get("shap_warnings"),
            )
            for item in validated
        ]

    @classmethod
    def get(cls, project_id, prediction_id):
        """
        Retrieve training predictions on a specified data set.

        Parameters
        ----------
        project_id : str
            id of the project the model belongs to
        prediction_id : str
            id of the prediction set

        Returns
        -------
        :py:class:`TrainingPredictions` object which is ready to operate with specified predictions
        """
        return cls(project_id, prediction_id)

    def iterate_rows(self, batch_size=None):
        """
        Retrieve training prediction rows as an iterator.

        Parameters
        ----------
        batch_size : int, optional
            maximum number of training prediction rows to fetch per request

        Returns
        -------
        iterator : :py:class:`TrainingPredictionsIterator`
            an iterator which yields named tuples representing training prediction rows
        """
        return TrainingPredictionsIterator(self._client, self.path, limit=batch_size)

    def get_all_as_dataframe(self, class_prefix=enums.PREDICTION_PREFIX.DEFAULT, serializer="json"):
        """
        Retrieve all training prediction rows and return them as a pandas.DataFrame.

        Returned dataframe has the following structure:
            - row_id : row id from the original dataset
            - prediction : the model's prediction for this row
            - class_<label> : the probability that the target is this class (only appears for
              classification and multiclass projects)
            - timestamp : the time of the prediction (only appears for out of time validation or
              time series projects)
            - forecast_point : the point in time used as a basis to generate the predictions
              (only appears for time series projects)
            - forecast_distance : how many time steps are between timestamp and forecast_point
              (only appears for time series projects)
            - series_id : he id of the series in a multiseries project
              or None for a single series project
              (only appears for time series projects)

        Parameters
        ----------
        class_prefix : str, optional
            The prefix to append to labels in the final dataframe. Default is ``class_``
            (e.g., apple -> class_apple)
        serializer : str, optional
            Serializer to use for the download. Options: ``json`` (default) or ``csv``.

        Returns
        -------
        dataframe: pandas.DataFrame
        """

        serializers = {
            "json": self._get_all_as_dataframe_json,
            "csv": self._get_all_as_dataframe_csv,
        }

        if serializer not in serializers:
            raise ValueError('Unknown serializer "{}", use "json" or "csv"'.format(serializer))

        return serializers[serializer](class_prefix)

    def _get_all_as_dataframe_json(self, class_prefix):
        rows = self.iterate_rows()

        tmp, rows = itertools.tee(rows)
        first_row = next(tmp, None)
        is_classification = first_row is not None and len(first_row.prediction_values) > 1
        is_datetime_partitioned = self._is_datetime_partitioned

        if is_classification:
            labels = (p["label"] for p in first_row.prediction_values)
            columns = self._get_classification_columns(
                labels,
                class_prefix=class_prefix,
                is_datetime_partitioned=is_datetime_partitioned,
                prediction_explanations=first_row.prediction_explanations,
            )
            return self._build_classification_dataframe(rows, columns, is_datetime_partitioned)
        elif self._is_time_series_project:
            return self._build_timeseries_dataframe(rows)
        else:
            return self._build_regression_dataframe(
                rows, is_datetime_partitioned, first_row.prediction_explanations
            )

    @property
    def _is_time_series_project(self):
        from datarobot.models import Project

        project = Project.get(self.project_id)
        return project.use_time_series

    @property
    def _is_datetime_partitioned(self):
        from datarobot.models import Project

        project = Project.get(self.project_id)
        return project.is_datetime_partitioned

    @staticmethod
    def _build_timeseries_dataframe(rows):
        columns = (
            "row_id",
            "partition_id",
            "prediction",
            "timestamp",
            "forecast_point",
            "forecast_distance",
            "series_id",
        )
        data = (
            (
                row.row_id,
                row.partition_id,
                row.prediction,
                row.timestamp,
                row.forecast_point,
                row.forecast_distance,
                row.series_id,
            )
            for row in rows
        )
        return pd.DataFrame.from_records(data, columns=columns)

    @staticmethod
    def _build_regression_dataframe(rows, is_datetime_partitioned, prediction_explanations):
        if is_datetime_partitioned:
            columns = (
                "row_id",
                "partition_id",
                "prediction",
                "timestamp",
            )
        else:
            columns = (
                "row_id",
                "partition_id",
                "prediction",
            )
        if prediction_explanations:
            for i in range(len(prediction_explanations)):
                idx = i + 1
                columns += (
                    _FEATURE.format(idx),
                    _FEATURE_VAL.format(idx),
                    _STRENGTH.format(idx),
                )
            columns += (
                "shap_remaining_total",
                "shap_base_value",
            )

        data = []
        for row in rows:
            data_row = (
                row.row_id,
                row.partition_id,
                row.prediction,
            )
            if is_datetime_partitioned:
                data_row += (row.timestamp,)
            if row.prediction_explanations:
                for prediction_explanation in row.prediction_explanations:
                    data_row += (
                        prediction_explanation["feature"],
                        prediction_explanation["feature_value"],
                        prediction_explanation["strength"],
                    )
                data_row += (
                    row.shap_metadata["shap_remaining_total"],
                    row.shap_metadata["shap_base_value"],
                )
            data.append(data_row)
        return pd.DataFrame.from_records(data, columns=columns)

    @staticmethod
    def _build_classification_dataframe(rows, columns, is_datetime_partitioned):
        data_list = []
        for row in rows:
            data_row = (row.row_id, row.partition_id, row.prediction)
            data_row += tuple(prediction["value"] for prediction in row.prediction_values)
            if is_datetime_partitioned:
                data_row += (row.timestamp,)
            if row.prediction_explanations:
                data_row += (
                    row.prediction_explanations[0]["label"],
                    row.shap_metadata["shap_remaining_total"],
                    row.shap_metadata["shap_base_value"],
                )
                for prediction_explanation in row.prediction_explanations:
                    data_row += (
                        prediction_explanation["feature"],
                        prediction_explanation["feature_value"],
                        prediction_explanation["strength"],
                    )
            data_list.append(data_row)

        return pd.DataFrame(data_list, columns=columns)

    @staticmethod
    def _get_classification_columns(
        class_labels, class_prefix, is_datetime_partitioned, prediction_explanations
    ):
        columns = ("row_id", "partition_id", "prediction")
        columns += tuple("{}{}".format(class_prefix, label) for label in class_labels)
        if is_datetime_partitioned:
            columns += ("timestamp",)
        if prediction_explanations:
            columns += (
                "explained_class",
                "shap_remaining_total",
                "shap_base_value",
            )
            for i in range(len(prediction_explanations)):
                idx = i + 1
                columns += (
                    _FEATURE.format(idx),
                    _FEATURE_VAL.format(idx),
                    _STRENGTH.format(idx),
                )
        return columns

    def _get_all_as_dataframe_csv(self, class_prefix):
        resp = self._client.get(self.path, headers={"Accept": "text/csv"}, stream=True)
        if resp.status_code == 200:
            return pd.read_csv(resp.raw)

        raise errors.ServerError(
            "Server returned unknown status code: {}".format(resp.status_code), resp.status_code,
        )

    def download_to_csv(self, filename, encoding="utf-8", serializer="json"):
        """
        Save training prediction rows into CSV file.

        Parameters
        ----------
        filename : str or file object
            path or file object to save training prediction rows
        encoding : string, optional
            A string representing the encoding to use in the output file, defaults to
            'utf-8'
        serializer : str, optional
            Serializer to use for the download. Options: ``json`` (default) or ``csv``.
        """
        df = self.get_all_as_dataframe(serializer=serializer)
        df.to_csv(
            path_or_buf=filename, header=True, index=False, encoding=encoding,
        )
