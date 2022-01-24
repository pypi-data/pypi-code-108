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

from datarobot import SegmentationTask as datarobot_segmentation_task
from datarobot.enums import DEFAULT_MAX_WAIT
from datarobot.utils import parse_time
from datarobot.utils.waiters import wait_for_async_resolution


class SegmentationTask(datarobot_segmentation_task):
    """ A Segmentation Task is used for segmenting an existing project into multiple child
    projects. Each child project (or segment) will be a separate autopilot run. Currently
    only user defined segmentation are supported.

    Example for creating a new SegmentationTask for Time Series segmentation with a
    user defined id column:

    .. highlight:: python
    .. code-block:: python

        from datarobot._experimental import SegmentationTask

        # Create the SegmentationTask
        segmentation_task_results = SegmentationTask.create(
            project_id=project.id,
            target=target,
            use_time_series=True,
            datetime_partition_column=datetime_partition_column,
            multiseries_id_columns=[multiseries_id_column],
            user_defined_segment_id_columns=[user_defined_segment_id_column]
        )

        # Retrieve the completed SegmentationTask object from the job results
        segmentation_task = segmentation_task_results['completedJobs'][0]

    Example for creating a new SegmentationTask for Time Series segmentation using
    an automated clustering model for segmentation:

    .. highlight:: python
    .. code-block:: python

        from datarobot._experimental import ModelPackage
        from datarobot._experimental import SegmentationTask

        # Retrieve the top clustering model from a project
        clustering_models = project.get_models()
        top_clustering_model = clustering_models[0]

        # Add the clustering model to the registry, so that it can be used
        # for segmentation.
        model_package = ModelPackage.create(model_id=top_clustering_model.id)

        # Create the SegmentationTask
        segmentation_task_results = SegmentationTask.create(
            project_id=project.id,
            target=target,
            use_time_series=True,
            datetime_partition_column=datetime_partition_column,
            multiseries_id_columns=[multiseries_id_column],
            model_package_id=model_package.id
        )

        # Retrieve the completed SegmentationTask object from the job results
        segmentation_task = segmentation_task_results['completedJobs'][0]

    Attributes
    ----------
    id : ObjectId
        The id of the segmentation task.
    project_id : ObjectId
        The associated id of the parent project.
    type : str
        What type of job the segmentation task is associated with, e.g. auto_ml or auto_ts.
    created  : datetime
        The date this segmentation task was created.
    segments_count : int
        The number of segments the segmentation task generated.
    segments : list of strings
        The segment names that the segmentation task generated.
    metadata : dict
        List of features that help to identify the parameters used by the segmentation task.
    data : dict
        Optional parameters that are associated with enabled metadata for the segmentation task.
    """

    _converter = t.Dict(
        {
            t.Key("id"): t.String,
            t.Key("project_id"): t.String,
            t.Key("name"): t.String,
            t.Key("type"): t.String,
            t.Key("created"): parse_time,
            t.Key("segments_count"): t.Int,
            t.Key("segments"): t.List(t.String),
            t.Key("metadata"): t.Dict(
                {
                    t.Key("use_time_series"): t.Bool,
                    t.Key("use_multiseries_id_columns"): t.Bool,
                    t.Key("use_automated_segmentation"): t.Bool,
                }
            ).ignore_extra("*"),
            t.Key("data"): t.Dict(
                {
                    t.Key("datetime_partition_column", optional=True): t.String | t.Null,
                    t.Key("multiseries_id_columns", optional=True): t.List(t.String) | t.Null,
                    t.Key("user_defined_segment_id_columns", optional=True): t.List(t.String)
                    | t.Null,
                    t.Key("model_package_id", optional=True): t.String | t.Null,
                }
            ).ignore_extra("*"),
        }
    ).ignore_extra("*")

    @classmethod
    def create(
        cls,
        project_id,
        target,
        use_time_series=False,
        datetime_partition_column=None,
        multiseries_id_columns=None,
        user_defined_segment_id_columns=None,
        model_package_id=None,
        max_wait=DEFAULT_MAX_WAIT,
    ):
        """
        Creates segmentation tasks for the project based on the defined parameters.

        Parameters
        ----------
        project_id : basestring
            The associated id of the parent project.
        target : basestring
            The column that represents the target in the dataset.
        use_time_series : bool
            Whether AutoTS or AutoML segmentations should be generated.
        datetime_partition_column : basestring or null
            Required for Time Series.
            The name of the column whose values as dates are used to assign a row
            to a particular partition.
        multiseries_id_columns : list of str or null
            Required for Time Series.
            A list of the names of multiseries id columns to define series within the training
            data. Currently only one multiseries id column is supported.
        user_defined_segment_id_columns : list of str or null
            Required when using a column for segmentation.
            A list of the segment id columns to use to define what columns are used to manually
            segment data. Currently only one user defined segment id column is supported.
        model_package_id : basestring
            Required when using automated segmentation.
            The associated id of the model in the DataRobot Model Registry that will be used to
            perform automated segmentation on a dataset.
        max_wait : integer
            The number of seconds to wait

        Returns
        -------
        segmentation_tasks : dict
            Dictionary containing the numberOfJobs, completedJobs, and failedJobs. completedJobs
            is a list of SegmentationTask objects, while failed jobs is a list of dictionaries
            indicating problems with submitted tasks.
        """

        payload = {
            "target": target,
            "use_time_series": use_time_series,
        }
        if use_time_series:
            if datetime_partition_column is None:
                raise ValueError(
                    "A datetime_partition_column value must be specified for time series."
                )
            payload.update({"datetime_partition_column": datetime_partition_column})

            if multiseries_id_columns is None:
                raise ValueError(
                    "A multiseries_id_columns value must be specified for time series."
                )
            if not isinstance(multiseries_id_columns, (list, tuple)):
                raise ValueError(
                    "Expected list of str for multiseries_id_columns, got: {}".format(
                        multiseries_id_columns
                    )
                )
            payload.update({"multiseries_id_columns": multiseries_id_columns})

        if user_defined_segment_id_columns is not None:
            if not isinstance(user_defined_segment_id_columns, (list, tuple)):
                raise ValueError(
                    "Expected list of str for user_defined_segment_id_columns, got: {}".format(
                        user_defined_segment_id_columns
                    )
                )
            payload.update({"user_defined_segment_id_columns": user_defined_segment_id_columns})
            payload.update({"use_automated_segmentation": False})
        elif model_package_id is not None:
            payload.update({"model_package_id": model_package_id})
            payload.update({"use_automated_segmentation": True})
        else:
            raise ValueError(
                "Either a user_defined_segment_id_columns value or a model_package_id must "
                "be defined to create a new segmentation task."
            )

        response = cls._client.post(cls._base_url.format(project_id), data=payload)
        results_url = wait_for_async_resolution(
            cls._client, response.headers["Location"], max_wait=max_wait
        )
        results_response = cls._client.get(results_url)

        data = results_response.json()
        successful_jobs = []
        if len(data["completedJobs"]) > 0:
            successful_jobs = [cls.from_location(x["url"]) for x in data["completedJobs"]]

        return {
            "numberOfJobs": data["numberOfJobs"],
            "completedJobs": successful_jobs,
            "failedJobs": data["failedJobs"],
        }
