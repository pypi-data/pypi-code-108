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

from datarobot._compat import String

from .. import errors
from ..enums import DEFAULT_MAX_WAIT, JOB_TYPE, PREDICT_JOB_STATUS, PREDICTION_PREFIX
from ..utils import (
    deprecated,
    from_api,
    get_id_from_response,
    raw_prediction_response_to_dataframe,
    recognize_sourcedata,
    retry,
)
from .job import AbstractSpecificJob


def wait_for_async_predictions(project_id, predict_job_id, max_wait=DEFAULT_MAX_WAIT):
    """
    Given a Project id and PredictJob id poll for status of process
    responsible for predictions generation until it's finished

    Parameters
    ----------
    project_id : str
        The identifier of the project
    predict_job_id : str
        The identifier of the PredictJob
    max_wait : int, optional
        Time in seconds after which predictions creation is considered
        unsuccessful

    Returns
    -------
    predictions : pandas.DataFrame
        Generated predictions.

    Raises
    ------
    AsyncPredictionsGenerationError
        Raised if status of fetched PredictJob object is ``error``
    AsyncTimeoutError
        Predictions weren't generated in time, specified by ``max_wait``
        parameter
    """
    # Note: Don't need this in 3.0. (Use `Job.get_result_when_complete` method instead.)
    for index in retry.wait(max_wait):
        try:
            predict_job = PredictJob.get(project_id, predict_job_id)
        except errors.PendingJobFinished:
            return PredictJob.get_predictions(project_id, predict_job_id)
        if predict_job.status in (PREDICT_JOB_STATUS.ERROR, PREDICT_JOB_STATUS.ABORTED):
            e_msg = "Predictions generation unsuccessful"
            raise errors.AsyncPredictionsGenerationError(e_msg)

    timeout_msg = "Predictions generation timed out in {} seconds".format(max_wait)
    raise errors.AsyncTimeoutError(timeout_msg)


class PredictJob(AbstractSpecificJob):

    """ Tracks asynchronous work being done within a project

    Attributes
    ----------
    id : int
        the id of the job
    project_id : str
        the id of the project the job belongs to
    status : str
        the status of the job - will be one of ``datarobot.enums.QUEUE_STATUS``
    job_type : str
        what kind of work the job is doing - will be 'predict' for predict jobs
    is_blocked : bool
        if true, the job is blocked (cannot be executed) until its dependencies are resolved
    message : str
        a message about the state of the job, typically explaining why an error occurred
    """

    _extra_fields = frozenset(["message"])
    _converter_extra = t.Dict(
        {t.Key("message", optional=True, default=""): String(allow_blank=True)}
    )

    def __init__(self, data, completed_resource_url=None):
        super(PredictJob, self).__init__(data, completed_resource_url=completed_resource_url)
        from . import Model

        data = from_api(data)
        self.model = Model(project_id=data.get("project_id"), id=data.get("model_id"))

    def __repr__(self):
        return "PredictJob({}, status={})".format(self.model, self.status)  # pragma:no cover

    @classmethod
    def _job_type(cls):
        return JOB_TYPE.PREDICT

    @classmethod
    def from_job(cls, job):
        """ Transforms a generic Job into a PredictJob

        Parameters
        ----------
        job: Job
            A generic job representing a PredictJob

        Returns
        -------
        predict_job: PredictJob
            A fully populated PredictJob with all the details of the job

        Raises
        ------
        ValueError:
            If the generic Job was not a predict job, e.g. job_type != JOB_TYPE.PREDICT
        """
        return super(PredictJob, cls).from_job(job)

    @classmethod
    @deprecated(
        deprecated_since_version="v2.3",
        will_remove_version="v3.0",
        message="Please use Model.request_predictions instead.",
    )
    def create(cls, model, sourcedata):
        """
        .. note::
           Deprecated in v2.3 in favor of ``Project.upload_dataset`` and
           ``Model.request_predictions``. That workflow allows you to reuse the same dataset
           for predictions from multiple models within one project.

        Starts predictions generation for provided data
        using previously created model.

        Parameters
        ----------
        model : Model
            Model to use for predictions generation
        sourcedata : str, file or pandas.DataFrame
            Data to be used for predictions.
            If this parameter is a str, it can be either a path to a local file
            or raw file content. If using a file on disk, the filename must
            consist of ASCII characters only. The file must be a CSV, and cannot
            be compressed

        Returns
        -------
        predict_job_id : str
            id of created job, can be used as parameter to ``PredictJob.get``
            or ``PredictJob.get_predictions`` methods or
            ``wait_for_async_predictions`` function

        Raises
        ------
        InputNotUnderstoodError
            If the parameter for sourcedata didn't resolve into known data types

        Examples
        --------
        .. code-block:: python

            model = Model.get('project-id', 'model-id')
            predict_job = PredictJob.create(model, './data_to_predict.csv')
        """
        url = "projects/{}/predictions/".format(model.project.id)
        form_data = {"model_id": model.id}
        default_fname = "predict.csv"
        filesource_kwargs = recognize_sourcedata(sourcedata, default_fname)

        response = cls._client.build_request_with_file(
            url=url, form_data=form_data, method="post", **filesource_kwargs
        )
        return get_id_from_response(response)

    @classmethod
    def _job_path(cls, project_id, job_id):
        return "projects/{}/predictJobs/{}/".format(project_id, job_id)

    @classmethod
    def get(cls, project_id, predict_job_id):
        """
        Fetches one PredictJob. If the job finished, raises PendingJobFinished
        exception.

        Parameters
        ----------
        project_id : str
            The identifier of the project the model on which prediction
            was started belongs to
        predict_job_id : str
            The identifier of the predict_job

        Returns
        -------
        predict_job : PredictJob
            The pending PredictJob

        Raises
        ------
        PendingJobFinished
            If the job being queried already finished, and the server is
            re-routing to the finished predictions.
        AsyncFailureError
            Querying this resource gave a status code other than 200 or 303
        """
        return super(PredictJob, cls).get(project_id, predict_job_id)

    @classmethod
    def get_predictions(cls, project_id, predict_job_id, class_prefix=PREDICTION_PREFIX.DEFAULT):
        """
        Fetches finished predictions from the job used to generate them.

        .. note::
            The prediction API for classifications now returns an additional prediction_values
            dictionary that is converted into a series of class_prefixed columns in the final
            dataframe. For example, <label> = 1.0 is converted to 'class_1.0'. If you are on an
            older version of the client (prior to v2.8), you must update to v2.8 to correctly pivot
            this data.

        Parameters
        ----------
        project_id : str
            The identifier of the project to which belongs the model used
            for predictions generation
        predict_job_id : str
            The identifier of the predict_job
        class_prefix : str
            The prefix to append to labels in the final dataframe (e.g., apple -> class_apple)

        Returns
        -------
        predictions : pandas.DataFrame
            Generated predictions

        Raises
        ------
        JobNotFinished
            If the job has not finished yet
        AsyncFailureError
            Querying the predict_job in question gave a status code other than 200 or 303
        """
        # Note: Don't need this in 3.0. (Use `Job.get_result` method instead.)
        url = cls._job_path(project_id, predict_job_id)
        response = cls._client.get(url, allow_redirects=False)

        if response.status_code == 200:
            data = response.json()
            raise errors.JobNotFinished("Pending job status is {}".format(data["status"]))
        elif response.status_code == 303:
            location = response.headers["Location"]
            response = cls._client.get(location, join_endpoint=False)
            return raw_prediction_response_to_dataframe(response.json(), class_prefix)
        else:
            e_msg = "Server unexpectedly returned status code {}"
            raise errors.AsyncFailureError(e_msg.format(response.status_code))
