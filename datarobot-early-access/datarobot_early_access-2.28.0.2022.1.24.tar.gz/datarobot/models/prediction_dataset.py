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
import trafaret as t

from datarobot._compat import Int, String
from datarobot.models.api_object import APIObject
from datarobot.utils import parse_time


class PredictionDataset(APIObject):

    """ A dataset uploaded to make predictions

    Typically created via `project.upload_dataset`

    Attributes
    ----------
    id : str
        the id of the dataset
    project_id : str
        the id of the project the dataset belongs to
    created : str
        the time the dataset was created
    name : str
        the name of the dataset
    num_rows : int
        the number of rows in the dataset
    num_columns : int
        the number of columns in the dataset
    forecast_point : datetime.datetime or None
        For time series projects only. This is the default point relative to which predictions will
        be generated, based on the forecast window of the project.  See the time series
        :ref:`predictions documentation <time_series_predict>` for more information.
    predictions_start_date : datetime.datetime or None, optional
        For time series projects only. The start date for bulk predictions. Note that this
        parameter is for generating historical predictions using the training data. This parameter
        should be provided in conjunction with ``predictions_end_date``. Can't be provided with the
        ``forecast_point`` parameter.
    predictions_end_date : datetime.datetime or None, optional
        For time series projects only. The end date for bulk predictions, exclusive. Note that this
        parameter is for generating historical predictions using the training data. This parameter
        should be provided in conjunction with ``predictions_start_date``. Can't be provided with
        the ``forecast_point`` parameter.
    relax_known_in_advance_features_check : bool, optional
        (New in version v2.15) For time series projects only. If True, missing values in the
        known in advance features are allowed in the forecast window at the prediction time.
        If omitted or False, missing values are not allowed.
    data_quality_warnings : dict, optional
        (New in version v2.15) A dictionary that contains available warnings about potential
        problems in this prediction dataset. Available warnings include:

        has_kia_missing_values_in_forecast_window : bool
            Applicable for time series projects. If True, known in advance features
            have missing values in forecast window which may decrease prediction accuracy.
        insufficient_rows_for_evaluating_models : bool
            Applicable for datasets which are used as external test sets. If True, there is not
            enough rows in dataset to calculate insights.
        single_class_actual_value_column : bool
            Applicable for datasets which are used as external test sets. If True, actual value
            column has only one class and such insights as ROC curve can not be calculated.
            Only applies for binary classification projects or unsupervised projects.

    forecast_point_range : list[datetime.datetime] or None, optional
        (New in version v2.20) For time series projects only. Specifies the range of dates available
        for use as a forecast point.
    data_start_date : datetime.datetime or None, optional
        (New in version v2.20) For time series projects only. The minimum primary date of this
        prediction dataset.
    data_end_date : datetime.datetime or None, optional
        (New in version v2.20) For time series projects only. The maximum primary date of this
        prediction dataset.
    max_forecast_date : datetime.datetime or None, optional
        (New in version v2.20) For time series projects only. The maximum forecast date of this
        prediction dataset.
    actual_value_column : string, optional
        (New in version v2.21) Optional, only available for unsupervised projects,
        in case dataset was uploaded with actual value column specified. Name of the
        column which will be used to calculate the classification metrics and insights.
    detected_actual_value_columns : list of dict, optional
        (New in version v2.21) For unsupervised projects only, list of detected actual value
        columns information containing missing count and name for each column.
    contains_target_values : bool, optional
        (New in version v2.21)  Only for supervised projects. If True, dataset contains target
        values and can be used to calculate the classification metrics and insights.
    secondary_datasets_config_id: string or None, optional
        (New in version v2.23) The Id of the alternative secondary dataset config
        to use during prediction for Feature discovery project.
    """

    _path_template = "projects/{}/predictionDatasets/{}/"

    _converter = t.Dict(
        {
            t.Key("id"): String(),
            t.Key("project_id"): String(),
            t.Key("created"): String(),
            t.Key("name"): String(),
            t.Key("num_rows"): Int(),
            t.Key("num_columns"): Int(),
            t.Key("forecast_point", optional=True): parse_time,
            t.Key("predictions_start_date", optional=True): parse_time,
            t.Key("predictions_end_date", optional=True): parse_time,
            t.Key("relax_known_in_advance_features_check", optional=True): t.Bool(),
            # do not forget to update `test_data_quality_warnings`
            # in datarobot-python-api-tests repo
            t.Key("data_quality_warnings"): t.Dict(
                {
                    t.Key("has_kia_missing_values_in_forecast_window"): t.Bool(),
                    t.Key("insufficient_rows_for_evaluating_models"): t.Bool(),
                    t.Key("single_class_actual_value_column"): t.Bool(),
                }
            ).allow_extra("*"),
            t.Key("forecast_point_range", optional=True): t.List(parse_time),
            t.Key("data_start_date", optional=True): parse_time,
            t.Key("data_end_date", optional=True): parse_time,
            t.Key("max_forecast_date", optional=True): parse_time,
            t.Key("actual_value_column", optional=True): String(),
            t.Key("detected_actual_value_columns", optional=True): t.List(
                t.Dict({t.Key("missing_count"): Int(), t.Key("name"): String()}).ignore_extra("*")
            ),
            t.Key("contains_target_values", optional=True): t.Bool(),
            t.Key("secondary_datasets_config_id", optional=True): String(),
        }
    ).allow_extra("*")

    def __init__(
        self,
        project_id,
        id,
        name,
        created,
        num_rows,
        num_columns,
        forecast_point=None,
        predictions_start_date=None,
        predictions_end_date=None,
        relax_known_in_advance_features_check=None,
        data_quality_warnings=None,
        forecast_point_range=None,
        data_start_date=None,
        data_end_date=None,
        max_forecast_date=None,
        actual_value_column=None,
        detected_actual_value_columns=None,
        contains_target_values=None,
        secondary_datasets_config_id=None,
    ):
        self.project_id = project_id
        self.id = id
        self.name = name
        self.created = created
        self.num_rows = num_rows
        self.num_columns = num_columns
        self.forecast_point = forecast_point
        self.predictions_start_date = predictions_start_date
        self.predictions_end_date = predictions_end_date
        self.relax_known_in_advance_features_check = relax_known_in_advance_features_check
        self.data_quality_warnings = data_quality_warnings
        self.forecast_point_range = forecast_point_range
        self.data_start_date = data_start_date
        self.data_end_date = data_end_date
        self.max_forecast_date = max_forecast_date
        self.detected_actual_value_columns = detected_actual_value_columns
        self.actual_value_column = actual_value_column
        self.contains_target_values = contains_target_values
        self._path = self._path_template.format(project_id, id)
        self.secondary_datasets_config_id = secondary_datasets_config_id

    def __repr__(self):
        return "PredictionDataset({!r})".format(self.name)

    @classmethod
    def get(cls, project_id, dataset_id):
        """
        Retrieve information about a dataset uploaded for predictions

        Parameters
        ----------
        project_id:
            the id of the project to query
        dataset_id:
            the id of the dataset to retrieve

        Returns
        -------
        dataset: PredictionDataset
            A dataset uploaded to make predictions
        """
        path = cls._path_template.format(project_id, dataset_id)
        return cls.from_location(path)

    def delete(self):
        """ Delete a dataset uploaded for predictions

        Will also delete predictions made using this dataset and cancel any predict jobs using
        this dataset.
        """
        self._client.delete(self._path)
