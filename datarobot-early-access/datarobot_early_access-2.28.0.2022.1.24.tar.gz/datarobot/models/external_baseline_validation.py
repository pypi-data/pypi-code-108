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

from datarobot.models.api_object import APIObject


class ExternalBaselineValidationInfo(APIObject):
    """An object containing information about external time series baseline predictions
    validation results.

    Attributes
    ----------
    baseline_validation_job_id : str
        the identifier of the baseline validation job
    project_id : str
        the identifier of the project
    catalog_version_id : str
        the identifier of the catalog version used in the validation job
    target : str
        the name of the target feature
    datetime_partition_column : str
        the name of the column whose values as dates are used to assign a row
        to a particular partition
    is_external_baseline_dataset_valid : bool
        whether the external baseline dataset passes the validation check
    multiseries_id_columns : list of str or null
        a list of the names of multiseries id columns to define series
        within the training data.  Currently only one multiseries id column is supported.
    holdout_start_date : str or None
        the start date of holdout scoring data
    holdout_end_date : str or None
        the end date of holdout scoring data
    backtests : list of dicts containing validation_start_date and validation_end_date or None
        the configurd backtets of the time series project
    forecast_window_start : int
        offset into the future to define how far forward relative to the forecast point the
        forecast window should start.
    forecast_window_end : int
        offset into the future to define how far forward relative to the forecast point the
        forecast window should end.
    message : str or None
        the description of the issue with external baseline validation job

    """

    _get_url = "projects/{pid}/externalTimeSeriesBaselineDataValidationJobs/{job_id}/"

    _converter = t.Dict(
        {
            t.Key("baseline_validation_job_id"): t.String(),
            t.Key("project_id"): t.String(),
            t.Key("catalog_version_id"): t.String(),
            t.Key("target"): t.String(),
            t.Key("datetime_partition_column"): t.String(),
            t.Key("is_external_baseline_dataset_valid"): t.Bool(),
            t.Key("multiseries_id_columns", optional=True): t.List(
                t.String(), max_length=1, min_length=1
            ),
            t.Key("holdout_start_date", optional=True): t.String(),
            t.Key("holdout_end_date", optional=True): t.String(),
            t.Key("backtests", optional=True): t.List(
                t.Dict(
                    {
                        t.Key("validation_start_date"): t.String(),
                        t.Key("validation_end_date"): t.String(),
                    }
                )
            ),
            t.Key("forecast_window_start", optional=True): t.Int(),
            t.Key("forecast_window_end", optional=True): t.Int(),
            t.Key("message", optional=True): t.String(),
        }
    ).ignore_extra("*")

    def __init__(
        self,
        baseline_validation_job_id,
        project_id,
        catalog_version_id,
        target,
        datetime_partition_column,
        is_external_baseline_dataset_valid,
        multiseries_id_columns=None,
        holdout_start_date=None,
        holdout_end_date=None,
        backtests=None,
        forecast_window_start=None,
        forecast_window_end=None,
        message=None,
    ):
        self.baseline_validation_job_id = baseline_validation_job_id
        self.project_id = project_id
        self.catalog_version_id = catalog_version_id
        self.target = target
        self.datetime_partition_column = datetime_partition_column
        self.is_external_baseline_dataset_valid = is_external_baseline_dataset_valid
        self.multiseries_id_columns = multiseries_id_columns
        self.holdout_start_date = holdout_start_date
        self.holdout_end_date = holdout_end_date
        self.backtests = backtests
        self.forecast_window_start = forecast_window_start
        self.forecast_window_end = forecast_window_end
        self.message = message

    @classmethod
    def get(cls, project_id, validation_job_id):
        """
        Get information about external baseline validation job

        Parameters
        ----------
        project_id : string
            the identifier of the project
        validation_job_id : string
            the identifier of the external baseline validation job

        Returns
        -------
        info: ExternalBaselineValidationInfo
            information about external baseline validation job

        """
        server_data = cls._client.get(cls._get_url.format(pid=project_id, job_id=validation_job_id))
        return cls.from_server_data(server_data.json())
