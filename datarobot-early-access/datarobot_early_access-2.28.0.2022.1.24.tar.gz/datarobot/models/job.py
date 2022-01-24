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
"""
  AbstractJob
  ^        ^
  |        |
  +        +
Job       AbstractSpecificJob
            ^             ^
            |             |
            +             +
        ModelJob       PredictJob


Subclasses of AbstractJob can override _converter_extra and _extra_fields to indicate extra object
attributes which come in the job data. They must implement the methods which raise
NotImplementedError

The Job class represents jobs of any type (whether or not we have classes for more specific job
types) with only the data and methods that work for jobs of any type.

We also have classes representing specific jobs. Some of the functionality for these jobs is shared
and hence is implemented in AbstractSpecificJob.

AbstractSpecificJob and AbstractJob should be non-public and may change. Users should only rely
on the concrete classes.
"""
import trafaret as t

from datarobot._compat import Int, String
from datarobot.models.feature_fit import FeatureFit
from datarobot.models.shap_impact import ShapImpact
from datarobot.models.validators import feature_impact_trafaret, single_feature_impact_trafaret
from datarobot.utils.waiters import wait_for_async_resolution

from .. import errors
from ..client import get_client, staticproperty
from ..enums import DEFAULT_MAX_WAIT, JOB_TYPE, PREDICTION_PREFIX, QUEUE_STATUS
from ..utils import from_api, raw_prediction_response_to_dataframe
from .feature_effect import FeatureEffects, FeatureEffectsMulticlass
from .model import Model, PrimeModel
from .prediction_explanations import PredictionExplanations, PredictionExplanationsInitialization
from .prime_file import PrimeFile
from .rating_table import RatingTable
from .reason_codes import ReasonCodes, ReasonCodesInitialization
from .ruleset import Ruleset
from .training_predictions import TrainingPredictions


class AbstractJob(object):
    """ Generic representation of a job in the queue
    """

    # Subclasses can override this:
    _converter_extra = t.Dict()
    _extra_fields = frozenset()

    # Subclasses should not override any of this:
    _client = staticproperty(get_client)
    _converter_common = t.Dict(
        {
            t.Key("id", optional=True): Int,
            t.Key("status", optional=True): t.Enum(
                QUEUE_STATUS.ABORTED,
                QUEUE_STATUS.COMPLETED,
                QUEUE_STATUS.ERROR,
                QUEUE_STATUS.INPROGRESS,
                QUEUE_STATUS.QUEUE,
            ),
            t.Key("project_id", optional=True): String,
            t.Key("model_id", optional=True): String,
            t.Key("is_blocked"): t.Bool,
        }
    )

    def __init__(self, data, completed_resource_url=None):
        # Importing here to dodge circular dependency
        from . import Project

        if not isinstance(data, dict):
            raise ValueError("job data must be a dict")
        self._completed_resource_url = completed_resource_url
        data = from_api(data)

        converter = (self._converter_common + self._converter_extra).allow_extra("*")
        self._safe_data = converter.check(data)
        self.job_type = self._get_job_type(self._safe_data)
        self.status = self._safe_data.get("status")
        self.id = self._safe_data.get("id")
        self.project = Project(self._safe_data.get("project_id"))
        self.project_id = self._safe_data.get("project_id")
        self.model_id = self._safe_data.get("model_id")
        self.model = Model(self.model_id) if self.model_id else None
        self.is_blocked = self._safe_data.get("is_blocked")
        for k in self._extra_fields:
            v = self._safe_data.get(k)
            setattr(self, k, v)

    @classmethod
    def _get_job_type(cls, safe_data):
        raise NotImplementedError

    def __repr__(self):
        return "Job({}, status={})".format(self.job_type, self.status)

    @classmethod
    def _data_and_completed_url_for_job(cls, url):
        response = cls._client.get(url, allow_redirects=False)

        if response.status_code in (200, 303):
            data = response.json()
            completed_url = response.headers["Location"] if response.status_code == 303 else None
            return data, completed_url
        else:
            e_msg = "Server unexpectedly returned status code {}"
            raise errors.AsyncFailureError(e_msg.format(response.status_code))

    def refresh(self):
        """
        Update this object with the latest job data from the server.
        """
        data, completed_url = self._data_and_completed_url_for_job(self._this_job_path())
        self.__init__(data, completed_resource_url=completed_url)

    def get_result(self, params=None):
        """
        Parameters
        ----------
        params : dict or None
            Query parameters to be added to request to get results.

        For featureEffects and featureFit, source param is required to define source,
        otherwise the default is `training`

        Returns
        -------
        result : object
            Return type depends on the job type:
                - for model jobs, a Model is returned
                - for predict jobs, a pandas.DataFrame (with predictions) is returned
                - for featureImpact jobs, a list of dicts by default (see ``with_metadata``
                  parameter of the ``FeatureImpactJob`` class and its ``get()`` method).
                - for primeRulesets jobs, a list of Rulesets
                - for primeModel jobs, a PrimeModel
                - for primeDownloadValidation jobs, a PrimeFile
                - for reasonCodesInitialization jobs, a ReasonCodesInitialization
                - for reasonCodes jobs, a ReasonCodes
                - for predictionExplanationInitialization jobs, a
                  PredictionExplanationsInitialization
                - for predictionExplanations jobs, a PredictionExplanations
                - for featureEffects, a FeatureEffects
                - for featureFit, a FeatureFit

        Raises
        ------
        JobNotFinished
            If the job is not finished, the result is not available.
        AsyncProcessUnsuccessfulError
            If the job errored or was aborted
        """
        self.refresh()
        if self.status in [QUEUE_STATUS.ERROR, QUEUE_STATUS.ABORTED]:
            raise errors.AsyncProcessUnsuccessfulError
        if not self._completed_resource_url:
            raise errors.JobNotFinished
        completed_resource_path = self._client.strip_endpoint(self._completed_resource_url)
        return self._make_result_from_location(completed_resource_path, params)

    def _make_result_from_json(self, server_data):
        if self.job_type == JOB_TYPE.MODEL:
            return Model.from_server_data(server_data)
        elif self.job_type == JOB_TYPE.PREDICT:
            return raw_prediction_response_to_dataframe(server_data, PREDICTION_PREFIX.DEFAULT)
        elif self.job_type == JOB_TYPE.FEATURE_IMPACT:
            # Note: a custom FeatureImpactJob class is used for high level API now.
            return server_data["featureImpacts"]
        elif self.job_type == JOB_TYPE.FEATURE_EFFECTS:
            return FeatureEffects.from_server_data(server_data)
        elif self.job_type == JOB_TYPE.FEATURE_FIT:
            return FeatureFit.from_server_data(server_data)
        elif self.job_type == JOB_TYPE.PRIME_RULESETS:
            return [Ruleset.from_server_data(ruleset_data) for ruleset_data in server_data]
        elif self.job_type == JOB_TYPE.PRIME_MODEL:
            return PrimeModel.from_server_data(server_data)
        elif self.job_type == JOB_TYPE.PRIME_VALIDATION:
            return PrimeFile.from_server_data(server_data)
        elif self.job_type == JOB_TYPE.REASON_CODES_INITIALIZATION:
            return ReasonCodesInitialization.from_server_data(server_data)
        elif self.job_type == JOB_TYPE.PREDICTION_EXPLANATIONS_INITIALIZATION:
            return PredictionExplanationsInitialization.from_server_data(server_data)
        elif self.job_type == JOB_TYPE.REASON_CODES:
            return ReasonCodes.from_location(server_data["reasonCodesRecordLocation"])
        elif self.job_type == JOB_TYPE.PREDICTION_EXPLANATIONS:
            return PredictionExplanations.from_location(
                server_data["predictionExplanationsRecordLocation"]
            )
        elif self.job_type == JOB_TYPE.RATING_TABLE_VALIDATION:
            return RatingTable.from_server_data(server_data)
        elif self.job_type == JOB_TYPE.SHAP_IMPACT:
            return ShapImpact.from_server_data(server_data)
        else:
            raise ValueError("Unrecognized job type {}.".format(self.job_type))

    def _make_result_from_location(self, location, params=None):
        if self.job_type == JOB_TYPE.TRAINING_PREDICTIONS:
            return TrainingPredictions.from_location(location)

        server_data = self._client.get(location, params=params).json()
        return self._make_result_from_json(server_data)

    def wait_for_completion(self, max_wait=DEFAULT_MAX_WAIT):
        """
        Waits for job to complete.

        Parameters
        ----------
        max_wait : int, optional
            How long to wait for the job to finish.
        """
        try:
            wait_for_async_resolution(self._client, self._this_job_path(), max_wait=max_wait)
        finally:
            # We are gonna try to update the job data, that's OK if it fails too (rare cases)
            self.refresh()

    def get_result_when_complete(self, max_wait=DEFAULT_MAX_WAIT, params=None):
        """
        Parameters
        ----------
        max_wait : int, optional
            How long to wait for the job to finish.

        params : dict, optional
            Query parameters to be added to request.

        Returns
        -------
        result: object
            Return type is the same as would be returned by `Job.get_result`.

        Raises
        ------
        AsyncTimeoutError
            If the job does not finish in time
        AsyncProcessUnsuccessfulError
            If the job errored or was aborted
        """
        if self.job_type == JOB_TYPE.MODEL_EXPORT:
            # checking this here instead of in _make_result to avoid waiting for the response
            raise ValueError(
                "Can't return the result for a model export job. Use "
                "Job.wait_for_completion to wait for the job to complete and "
                "Model.download_export to download the finished export."
            )

        self.wait_for_completion(max_wait=max_wait)
        return self._make_result_from_location(self._completed_resource_url, params=params)

    def _this_job_path(self):
        return self._job_path(self.project.id, self.id)

    @classmethod
    def _job_path(cls, project_id, job_id):
        raise NotImplementedError

    @classmethod
    def get(cls, project_id, job_id):
        # Note: For 3.0 (when the behavior of all job types' `get` methods can be made consistent),
        #       the implementation can move here.
        raise NotImplementedError

    def cancel(self):
        """
        Cancel this job. If this job has not finished running, it will be
        removed and canceled.
        """
        self._client.delete(self._this_job_path())


class Job(AbstractJob):

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
        what kind of work the job is doing - will be one of ``datarobot.enums.JOB_TYPE``
    is_blocked : bool
        if true, the job is blocked (cannot be executed) until its dependencies are resolved
    """

    _converter_extra = t.Dict(
        {t.Key("job_type", optional=True) >> "job_type": String, t.Key("url") >> "url": String}
    )

    def __init__(self, data, completed_resource_url=None):
        super(Job, self).__init__(data, completed_resource_url=completed_resource_url)
        self._job_details_path = self._client.strip_endpoint(self._safe_data["url"])

    @classmethod
    def _get_job_type(cls, safe_data):
        # For generic jobs, job_type comes from the data.
        return safe_data.get("job_type")

    @classmethod
    def _job_path(cls, project_id, job_id):
        # Path where you can get jobs of this kind.
        return "projects/{}/jobs/{}/".format(project_id, job_id)

    @classmethod
    def get(cls, project_id, job_id):
        """
        Fetches one job.

        Parameters
        ----------
        project_id : str
            The identifier of the project in which the job resides
        job_id : str
            The job id

        Returns
        -------
        job : Job
            The job

        Raises
        ------
        AsyncFailureError
            Querying this resource gave a status code other than 200 or 303
        """
        url = cls._job_path(project_id, job_id)
        data, completed_url = cls._data_and_completed_url_for_job(url)
        return cls(data, completed_resource_url=completed_url)


class AbstractSpecificJob(AbstractJob):
    @classmethod
    def _job_type(cls):
        raise NotImplementedError

    @classmethod
    def _get_job_type(cls, _):
        return cls._job_type()

    @classmethod
    def from_job(cls, job):
        if not job.job_type == cls._job_type():
            raise ValueError("wrong job_type: {}".format(job.job_type))
        if isinstance(job, AbstractSpecificJob):
            job.refresh()
            return job
        else:
            response = cls._client.get(job._job_details_path)
            data = response.json()
            return cls(data)

    @classmethod
    def from_id(cls, project_id, job_id):
        url = cls._job_path(project_id, job_id)
        response = cls._client.get(url, allow_redirects=False)
        data = response.json()
        return cls(data)

    @classmethod
    def get(cls, project_id, job_id):
        # Note: In v3.0 the desired behavior here will be the same as in Job, so we can delete this
        url = cls._job_path(project_id, job_id)
        response = cls._client.get(url, allow_redirects=False)
        if response.status_code == 200:
            data = response.json()
            return cls(data)
        elif response.status_code == 303:
            raise errors.PendingJobFinished
        else:
            e_msg = "Server unexpectedly returned status code {}"
            raise errors.AsyncFailureError(e_msg.format(response.status_code))


class TrainingPredictionsJob(Job):
    def __init__(self, data, model_id, data_subset, **kwargs):
        super(Job, self).__init__(data, **kwargs)
        self._model_id = model_id
        self._data_subset = data_subset

    @classmethod
    def get(cls, project_id, job_id, model_id=None, data_subset=None):
        """
        Fetches one training predictions job.

        The resulting
        :py:class:`TrainingPredictions <datarobot.models.training_predictions.TrainingPredictions>`
        object will be annotated with `model_id` and `data_subset`.

        Parameters
        ----------
        project_id : str
            The identifier of the project in which the job resides
        job_id : str
            The job id
        model_id : str
            The identifier of the model used for computing training predictions
        data_subset : dr.enums.DATA_SUBSET, optional
            Data subset used for computing training predictions

        Returns
        -------
        job : TrainingPredictionsJob
            The job
        """
        url = cls._job_path(project_id, job_id)
        data, completed_url = cls._data_and_completed_url_for_job(url)
        return cls(
            data, model_id=model_id, data_subset=data_subset, completed_resource_url=completed_url,
        )

    def _make_result_from_location(self, location, params=None):
        return TrainingPredictions.from_location(
            location, model_id=self._model_id, data_subset=self._data_subset,
        )

    def refresh(self):
        """
        Update this object with the latest job data from the server.
        """
        data, completed_url = self._data_and_completed_url_for_job(self._this_job_path())
        self.__init__(
            data,
            model_id=self._model_id,
            data_subset=self._data_subset,
            completed_resource_url=completed_url,
        )


class FeatureImpactJob(Job):
    """Custom Feature Impact job to handle different return value structures.

    The original implementation had just the the data and the new one also includes some metadata.

    In general, we aim to keep the number of Job classes low by just utilizing the `job_type`
    attribute to control any specific formatting; however in this case when we needed to support
    a new representation with the _same_ job_type, customzing the behavior of
    `_make_result_from_location` allowed us to achieve our ends without complicating the
    `_make_result_from_json` method.
    """

    # This is a default value used by a new instantiated job. This can be overriden in `__init__()`
    # but for existing instances it will not change on subsequent `__init__()` calls without
    # explicit `with_metadata` parameter (which `refresh()` does).
    _with_metadata = False

    def __init__(self, data, completed_resource_url=None, with_metadata=False):
        super(FeatureImpactJob, self).__init__(data, completed_resource_url=completed_resource_url)
        # We might be in existing instance with .refresh() called, that does not know about
        # with_metadata parameter. Only set instance attribute if it is set to True explicitly,
        # otherwise default to class attribute that is False.
        if with_metadata:
            self._with_metadata = with_metadata

    @classmethod
    def get(cls, project_id, job_id, with_metadata=False):
        """
        Fetches one job.

        Parameters
        ----------
        project_id : str
            The identifier of the project in which the job resides
        job_id : str
            The job id
        with_metadata : bool
            To make this job return the metadata (i.e. the full object of the completed resource)
            set the `with_metadata` flag to True.

        Returns
        -------
        job : Job
            The job

        Raises
        ------
        AsyncFailureError
            Querying this resource gave a status code other than 200 or 303
        """
        url = cls._job_path(project_id, job_id)
        data, completed_url = cls._data_and_completed_url_for_job(url)
        return cls(data, completed_resource_url=completed_url, with_metadata=with_metadata)

    def _make_result_from_location(self, location, params=None):
        """Custom extension of get_result_when_complete to use a customized formatter"""
        server_data = self._client.get(location, params=params).json()
        return filter_feature_impact_result(server_data, with_metadata=self._with_metadata)


class FeatureEffectsMulticlassJob(Job):
    def _make_result_from_location(self, location, params=None):
        return FeatureEffectsMulticlass.from_location(location)


def _filter_feature_impact_result(data, validator_config):
    # The trafaret used might allow extra fields, but we want this method to return only known
    # fields. Be conservative in what you do, be liberal in what you accept from others.
    exposed_fields = [k.name for k in validator_config.keys]
    return {k: v for k, v in data.items() if k in exposed_fields}


def filter_feature_impact_result(data, with_metadata):
    """Filter Feature Impact response according to specific validator configuration.

    Parameters
    ----------
    data : dict
        A (previously validated) data to filter.
    with_metadata : bool
        The flag indicating if the result should include the metadata as well.

    Returns
    -------
    dict or list
        A filtered data.
    """
    if not with_metadata:
        return [
            _filter_feature_impact_result(item, single_feature_impact_trafaret)
            for item in data["featureImpacts"]
        ]
    return _filter_feature_impact_result(data, feature_impact_trafaret)
