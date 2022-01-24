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
import collections
from datetime import datetime
import json
import warnings
import webbrowser

import six
import trafaret as t

from datarobot._compat import Int, String
from datarobot.models.api_object import APIObject
from datarobot.models.credential import CredentialDataSchema
from datarobot.models.restore_discarded_features import DiscardedFeaturesInfo
from datarobot.models.sharing import SharingAccess

from .. import errors
from ..enums import (
    AUTOPILOT_MODE,
    CV_METHOD,
    DEFAULT_MAX_WAIT,
    DEFAULT_TIMEOUT,
    LEADERBOARD_SORT_KEY,
    MONOTONICITY_FEATURELIST_DEFAULT,
    PROJECT_STAGE,
    QUEUE_STATUS,
    TARGET_TYPE,
    UnsupervisedTypeEnum,
    VARIABLE_TYPE_TRANSFORM,
    VERBOSITY_LEVEL,
)
from ..errors import ProjectHasNoRecommendedModelWarning
from ..helpers import AdvancedOptions
from ..helpers.eligibility_result import EligibilityResult
from ..helpers.partitioning_methods import PartitioningMethod
from ..utils import (
    camelize,
    datetime_to_string,
    deprecation_warning,
    encode_utf8_if_py2,
    from_api,
    get_duplicate_features,
    get_id_from_location,
    get_id_from_response,
    is_urlsource,
    logger,
    parse_time,
    recognize_sourcedata,
    retry,
    underscorize,
)
from ..utils.pagination import unpaginate
from ..utils.waiters import wait_for_async_resolution
from .external_baseline_validation import ExternalBaselineValidationInfo
from .feature import Feature, ModelingFeature
from .featurelist import Featurelist, ModelingFeaturelist
from .job import Job
from .model import CombinedModel
from .modeljob import ModelJob
from .predict_job import PredictJob
from .prediction_dataset import PredictionDataset
from .prime_file import PrimeFile
from .segmentation import SegmentationTask

logger = logger.get_logger(__name__)


class Project(APIObject):
    """A project built from a particular training dataset

    Attributes
    ----------
    id : str
        the id of the project
    project_name : str
        the name of the project
    project_description : str
        an optional description for the project
    mode : int
        the autopilot mode currently selected for the project - 0 for full autopilot, 1 for
        semi-automatic, and 2 for manual
    target : str
        the name of the selected target features
    target_type : str
        Indicating what kind of modeling is being done in this project Options are: 'Regression',
        'Binary' (Binary classification), 'Multiclass' (Multiclass classification),
        'Multilabel' (Multilabel classification)
    holdout_unlocked : bool
        whether the holdout has been unlocked
    metric : str
        the selected project metric (e.g. `LogLoss`)
    stage : str
        the stage the project has reached - one of ``datarobot.enums.PROJECT_STAGE``
    partition : dict
        information about the selected partitioning options
    positive_class : str
        for binary classification projects, the selected positive class; otherwise, None
    created : datetime
        the time the project was created
    advanced_options : dict
        information on the advanced options that were selected for the project settings,
        e.g. a weights column or a cap of the runtime of models that can advance autopilot stages
    recommender : dict
        information on the recommender settings of the project (i.e. whether it is a recommender
        project, or the id columns)
    max_train_pct : float
        the maximum percentage of the project dataset that can be used without going into the
        validation data or being too large to submit any blueprint for training
    max_train_rows : int
        the maximum number of rows that can be trained on without going into the validation data
        or being too large to submit any blueprint for training
    scaleout_max_train_pct : float
        the maximum percentage of the project dataset that can be used to successfully train a
        scaleout model without going into the validation data.  May exceed `max_train_pct`, in which
        case only scaleout models can be trained up to this point.
    scaleout_max_train_rows : int
        the maximum number of rows that can be used to successfully train a scaleout model without
        going into the validation data.  May exceed `max_train_rows`, in which case only scaleout
        models can be trained up to this point.
    file_name : str
        the name of the file uploaded for the project dataset
    credentials : list, optional
        a list of credentials for the datasets used in relationship configuration
        (previously graphs).
    feature_engineering_prediction_point : str, optional
        for Feature Discovery projects that are not time-aware, this parameter identifies the column
        in the primary dataset which should be used as the prediction point.
    unsupervised_mode : bool, optional
        (New in version v2.20) defaults to False, indicates whether this is an unsupervised project.
    relationships_configuration_id : str, optional
        (New in version v2.21) id of the relationships configuration to use
    query_generator_id: str, optional
        (New in version v2.27) id of the query generator applied for time series data prep
    segmentation : dict, optional
        information on the segmentation options for segmented project
    """

    _path = "projects/"
    _clone_path = "projectClones/"
    _scaleout_modeling_mode_converter = String()
    _advanced_options_converter = t.Dict(
        {
            t.Key("weights", optional=True): String(),
            t.Key("blueprint_threshold", optional=True): Int(),
            t.Key("response_cap", optional=True): t.Or(t.Bool(), t.Float()),
            t.Key("seed", optional=True): Int(),
            t.Key("smart_downsampled", optional=True): t.Bool(),
            t.Key("majority_downsampling_rate", optional=True): t.Float(),
            t.Key("offset", optional=True): t.List(String()),
            t.Key("exposure", optional=True): String(),
            t.Key("events_count", optional=True): String(),
            t.Key("scaleout_modeling_mode", optional=True): _scaleout_modeling_mode_converter,
            t.Key("only_include_monotonic_blueprints", optional=True): t.Bool(),
            t.Key("default_monotonic_decreasing_featurelist_id", optional=True): String()
            | t.Null(),
            t.Key("default_monotonic_increasing_featurelist_id", optional=True): String()
            | t.Null(),
            t.Key("allowed_pairwise_interaction_groups", optional=True): t.List(t.List(String))
            | t.Null(),
            t.Key("blend_best_models", optional=True): t.Bool(),
            t.Key("scoring_code_only", optional=True): t.Bool(),
            t.Key("shap_only_mode", optional=True): t.Bool(),
            t.Key("prepare_model_for_deployment", optional=True): t.Bool(),
            t.Key("consider_blenders_in_recommendation", optional=True): t.Bool(),
            t.Key("min_secondary_validation_model_count", optional=True): Int(),
            t.Key("autopilot_data_sampling_method", optional=True): String(),
            t.Key("run_leakage_removed_feature_list", optional=True): t.Bool(),
            t.Key("autopilot_with_feature_discovery", optional=True): t.Bool(),
            t.Key("feature_discovery_supervised_feature_reduction", optional=True): t.Bool(),
            t.Key("exponentially_weighted_moving_alpha", optional=True): t.Float(gt=0.0, lte=1.0),
            t.Key("external_time_series_baseline_dataset_id", optional=True): t.String(),
        }
    ).ignore_extra("*")

    _feature_engineering_graph_converter = t.Dict(
        {
            t.Key("id"): String(),
            t.Key("linkage_keys", optional=True): t.List(String, min_length=1, max_length=10),
        }
    ).ignore_extra("*")

    _common_credentials = t.Dict(
        {
            t.Key("catalog_version_id", optional=True): String(),
            t.Key("url", optional=True): String(),
        }
    )

    _password_credentials = (
        t.Dict({t.Key("user"): String(), t.Key("password"): String()}) + _common_credentials
    )

    _stored_credentials = t.Dict({t.Key("credential_id"): String()}) + _common_credentials

    _feg_credentials_converter = t.List(_password_credentials | _stored_credentials, max_length=50)

    _segmentation_converter = t.Dict(
        {
            t.Key("segmentation_task_id", optional=True): t.String(),
            t.Key("parent_project_id", optional=True): t.String(),
            t.Key("segment", optional=True): t.String(),
        }
    ).ignore_extra("*")

    _converter = t.Dict(
        {
            t.Key("_id", optional=True) >> "id": String(allow_blank=True),
            t.Key("id", optional=True) >> "id": String(allow_blank=True),
            t.Key("project_name", optional=True) >> "project_name": String(allow_blank=True),
            t.Key("project_description", optional=True): String(),
            t.Key("autopilot_mode", optional=True) >> "mode": Int,
            t.Key("target", optional=True): String(),
            t.Key("target_type", optional=True): String(allow_blank=True),
            t.Key("holdout_unlocked", optional=True): t.Bool(),
            t.Key("metric", optional=True) >> "metric": String(allow_blank=True),
            t.Key("stage", optional=True) >> "stage": String(allow_blank=True),
            t.Key("partition", optional=True): t.Dict().allow_extra("*"),
            t.Key("positive_class", optional=True): t.Or(Int(), t.Float(), String()),
            t.Key("created", optional=True): parse_time,
            t.Key("advanced_options", optional=True): _advanced_options_converter,
            t.Key("recommender", optional=True): t.Dict().allow_extra("*"),
            t.Key("max_train_pct", optional=True): t.Float(),
            t.Key("max_train_rows", optional=True): Int(),
            t.Key("scaleout_max_train_pct", optional=True): t.Float(),
            t.Key("scaleout_max_train_rows", optional=True): Int(),
            t.Key("file_name", optional=True): String(allow_blank=True),
            t.Key("credentials", optional=True): _feg_credentials_converter,
            t.Key("feature_engineering_prediction_point", optional=True): String(),
            t.Key("unsupervised_mode", default=False): t.Bool(),
            t.Key("use_feature_discovery", optional=True, default=False): t.Bool(),
            t.Key("relationships_configuration_id", optional=True): String(),
            t.Key("query_generator_id", optional=True): String(),
            t.Key("segmentation", optional=True): _segmentation_converter,
        }
    ).allow_extra("*")

    def __init__(
        self,
        id=None,
        project_name=None,
        mode=None,
        target=None,
        target_type=None,
        holdout_unlocked=None,
        metric=None,
        stage=None,
        partition=None,
        positive_class=None,
        created=None,
        advanced_options=None,
        recommender=None,
        max_train_pct=None,
        max_train_rows=None,
        scaleout_max_train_pct=None,
        scaleout_max_train_rows=None,
        file_name=None,
        credentials=None,
        feature_engineering_prediction_point=None,
        unsupervised_mode=None,
        use_feature_discovery=None,
        relationships_configuration_id=None,
        project_description=None,
        query_generator_id=None,
        segmentation=None,
    ):
        if isinstance(id, dict):
            # Backwards compatibility - we once upon a time supported this
            deprecation_warning(
                "Project instantiation from a dict",
                deprecated_since_version="v2.3",
                will_remove_version="v3.0",
                message="Use Project.from_data instead",
            )
            self.__init__(**id)
        else:
            self.id = id
            self.project_name = project_name
            self.project_description = project_description
            self.mode = mode
            self.target = target
            self.target_type = target_type
            self.holdout_unlocked = holdout_unlocked
            self.metric = metric
            self.stage = stage
            self.partition = partition
            self.positive_class = positive_class
            self.created = created
            self.advanced_options = advanced_options
            self.recommender = recommender
            self.max_train_pct = max_train_pct
            self.max_train_rows = max_train_rows
            self.scaleout_max_train_pct = scaleout_max_train_pct
            self.scaleout_max_train_rows = scaleout_max_train_rows
            self.file_name = file_name
            self.credentials = credentials
            self.feature_engineering_prediction_point = feature_engineering_prediction_point
            self.unsupervised_mode = unsupervised_mode
            self.use_feature_discovery = use_feature_discovery
            self.relationships_configuration_id = relationships_configuration_id
            self.query_generator_id = query_generator_id
            self.segmentation = segmentation

    @property
    def use_time_series(self):
        return bool(self.partition and self.partition.get("use_time_series"))

    @property
    def calendar_id(self):
        return self.partition.get("calendar_id") if self.use_time_series else None

    @property
    def is_datetime_partitioned(self):
        return bool(self.partition and self.partition.get("cv_method") == CV_METHOD.DATETIME)

    @property
    def is_segmented(self):
        return bool(self.segmentation and self.segmentation.get("parent_project_id") is None)

    def _set_values(self, data):
        """
        An internal helper to set attributes of the instance

        Parameters
        ----------
        data : dict
            Only those keys that match self._fields will be updated
        """
        data = self._converter.check(from_api(data))
        for k, v in six.iteritems(data):
            if k in self._fields():
                setattr(self, k, v)

    @staticmethod
    def _load_partitioning_method(method, payload):
        if not isinstance(method, PartitioningMethod):
            raise TypeError("method should inherit from PartitioningMethod")
        payload.update(method.collect_payload())

    @staticmethod
    def _load_advanced_options(opts, payload):
        if not isinstance(opts, AdvancedOptions):
            raise TypeError("opts should inherit from AdvancedOptions")
        payload.update(opts.collect_payload())

    @staticmethod
    def _validate_and_return_target_type(target_type):
        if target_type not in [
            TARGET_TYPE.BINARY,
            TARGET_TYPE.REGRESSION,
            TARGET_TYPE.MULTICLASS,
            TARGET_TYPE.MULTILABEL,
        ]:
            raise TypeError("{} is not a valid target_type".format(target_type))
        return target_type

    def __repr__(self):
        return encode_utf8_if_py2(
            u"{}({})".format(self.__class__.__name__, self.project_name or self.id)
        )

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    @classmethod
    def get(cls, project_id):
        """
        Gets information about a project.

        Parameters
        ----------
        project_id : str
            The identifier of the project you want to load.

        Returns
        -------
        project : Project
            The queried project

        Examples
        --------
        .. code-block:: python

            import datarobot as dr
            p = dr.Project.get(project_id='54e639a18bd88f08078ca831')
            p.id
            >>>'54e639a18bd88f08078ca831'
            p.project_name
            >>>'Some project name'
        """
        path = "{}{}/".format(cls._path, project_id)
        return cls.from_location(
            path,
            keep_attrs=[
                "advanced_options.default_monotonic_increasing_featurelist_id",
                "advanced_options.default_monotonic_decreasing_featurelist_id",
            ],
        )

    @classmethod
    def create(
        cls,
        sourcedata,
        project_name="Untitled Project",
        max_wait=DEFAULT_MAX_WAIT,
        read_timeout=DEFAULT_TIMEOUT.UPLOAD,
        dataset_filename=None,
    ):
        """
        Creates a project with provided data.

        Project creation is asynchronous process, which means that after
        initial request we will keep polling status of async process
        that is responsible for project creation until it's finished.
        For SDK users this only means that this method might raise
        exceptions related to it's async nature.

        Parameters
        ----------
        sourcedata : basestring, file, pathlib.Path or pandas.DataFrame
            Dataset to use for the project.
            If string can be either a path to a local file, url to publicly
            available file or raw file content. If using a file, the filename
            must consist of ASCII characters only.
        project_name : str, unicode, optional
            The name to assign to the empty project.
        max_wait : int, optional
            Time in seconds after which project creation is considered
            unsuccessful
        read_timeout: int
            The maximum number of seconds to wait for the server to respond indicating that the
            initial upload is complete
        dataset_filename : string or None, optional
            (New in version v2.14) File name to use for dataset.
            Ignored for url and file path sources.

        Returns
        -------
        project : Project
            Instance with initialized data.

        Raises
        ------
        InputNotUnderstoodError
            Raised if `sourcedata` isn't one of supported types.
        AsyncFailureError
            Polling for status of async process resulted in response
            with unsupported status code. Beginning in version 2.1, this
            will be ProjectAsyncFailureError, a subclass of AsyncFailureError
        AsyncProcessUnsuccessfulError
            Raised if project creation was unsuccessful
        AsyncTimeoutError
            Raised if project creation took more time, than specified
            by ``max_wait`` parameter

        Examples
        --------
        .. code-block:: python

            p = Project.create('/home/datasets/somedataset.csv',
                               project_name="New API project")
            p.id
            >>> '5921731dkqshda8yd28h'
            p.project_name
            >>> 'New API project'
        """
        form_data = cls._construct_create_form_data(project_name)
        return cls._create_project_with_form_data(
            sourcedata,
            form_data,
            max_wait=max_wait,
            read_timeout=read_timeout,
            dataset_filename=dataset_filename,
        )

    @classmethod
    def encrypted_string(cls, plaintext):
        """Sends a string to DataRobot to be encrypted

        This is used for passwords that DataRobot uses to access external data sources

        Parameters
        ----------
        plaintext : str
            The string to encrypt

        Returns
        -------
        ciphertext : str
            The encrypted string
        """
        endpoint = "stringEncryptions/"
        response = cls._client.post(endpoint, data={"plain_text": plaintext})
        return response.json()["cipherText"]

    @classmethod
    def create_from_hdfs(cls, url, port=None, project_name=None, max_wait=DEFAULT_MAX_WAIT):
        """
        Create a project from a datasource on a WebHDFS server.

        Parameters
        ----------
        url : str
            The location of the WebHDFS file, both server and full path. Per the DataRobot
            specification, must begin with `hdfs://`, e.g. `hdfs:///tmp/10kDiabetes.csv`
        port : int, optional
            The port to use. If not specified, will default to the server default (50070)
        project_name : str, optional
            A name to give to the project
        max_wait : int
            The maximum number of seconds to wait before giving up.

        Returns
        -------
        Project

        Examples
        --------
        .. code-block:: python

            p = Project.create_from_hdfs('hdfs:///tmp/somedataset.csv',
                                         project_name="New API project")
            p.id
            >>> '5921731dkqshda8yd28h'
            p.project_name
            >>> 'New API project'
        """
        hdfs_project_create_endpoint = "hdfsProjects/"
        payload = {"url": url}
        if port is not None:
            payload["port"] = port
        if project_name is not None:
            payload["project_name"] = project_name

        response = cls._client.post(hdfs_project_create_endpoint, data=payload)
        return cls.from_async(response.headers["Location"], max_wait=max_wait)

    @classmethod
    def create_from_data_source(
        cls, data_source_id, username, password, project_name=None, max_wait=DEFAULT_MAX_WAIT
    ):
        """
        Create a project from a data source. Either data_source or data_source_id
        should be specified.

        Parameters
        ----------
        data_source_id : str
            the identifier of the data source.
        username : str
            the username for database authentication.
        password : str
            the password for database authentication. The password is encrypted
            at server side and never saved / stored.
        project_name : str, optional
            optional, a name to give to the project.
        max_wait : int
            optional, the maximum number of seconds to wait before giving up.

        Returns
        -------
        Project

        """
        payload = {"data_source_id": data_source_id, "user": username, "password": password}
        if project_name is not None:
            payload["project_name"] = project_name

        response = cls._client.post(cls._path, data=payload)
        return cls.from_async(response.headers["Location"], max_wait=max_wait)

    @classmethod
    def create_from_dataset(
        cls,
        dataset_id,
        dataset_version_id=None,
        project_name=None,
        user=None,
        password=None,
        credential_id=None,
        use_kerberos=None,
        credential_data=None,
    ):
        """
        Create a Project from a :class:`datarobot.Dataset`

        Parameters
        ----------
        dataset_id: string
            The ID of the dataset entry to user for the project's Dataset
        dataset_version_id: string, optional
            The ID of the dataset version to use for the project dataset. If not specified - uses
            latest version associated with dataset_id
        project_name: string, optional
            The name of the project to be created.
            If not specified, will be "Untitled Project" for database connections, otherwise
            the project name will be based on the file used.
        user: string, optional
            The username for database authentication.
        password: string, optional
            The password (in cleartext) for database authentication. The password
            will be encrypted on the server side in scope of HTTP request and never saved or stored
        credential_id: string, optional
            The ID of the set of credentials to use instead of user and password.
        use_kerberos: bool, optional
            Server default is False.
            If true, use kerberos authentication for database authentication.
        credential_data: dict, optional
            The credentials to authenticate with the database, to use instead of user/password or
            credential ID.

        Returns
        -------
        Project
        """
        payload = {
            "dataset_id": dataset_id,
            "dataset_version_id": dataset_version_id,
            "project_name": project_name,
            "user": user,
            "password": password,
            "credential_id": credential_id,
            "use_kerberos": use_kerberos,
            "credential_data": credential_data,
        }
        new_payload = {k: v for k, v in payload.items() if v is not None}

        if "credential_data" in new_payload:
            new_payload["credential_data"] = CredentialDataSchema(new_payload["credential_data"])

        response = cls._client.post(cls._path, data=new_payload)
        return cls.from_async(response.headers["Location"])

    @classmethod
    def _construct_create_form_data(cls, project_name):
        """
        Constructs the payload to be POSTed with the request to create a new project.

        Note that this private method is relied upon for extensibility so that subclasses can
        inject additional payload data when creating new projects.

        Parameters
        ----------
        project_name : str
            Name of the project.
        Returns
        -------
        dict
        """
        return {"project_name": project_name}

    @classmethod
    def _create_project_with_form_data(
        cls,
        sourcedata,
        form_data,
        max_wait=DEFAULT_MAX_WAIT,
        read_timeout=DEFAULT_TIMEOUT.UPLOAD,
        dataset_filename=None,
    ):
        """
        This is a helper for Project.create that uses the constructed form_data as the payload
        to post when creating the project on the server.  See parameters and return for create.

        Note that this private method is relied upon for extensibility to hook into Project.create.
        """
        if is_urlsource(sourcedata):
            form_data["url"] = sourcedata
            initial_project_post_response = cls._client.post(cls._path, data=form_data)
        else:
            dataset_filename = dataset_filename or "data.csv"
            filesource_kwargs = recognize_sourcedata(sourcedata, dataset_filename)
            initial_project_post_response = cls._client.build_request_with_file(
                url=cls._path,
                form_data=form_data,
                method="post",
                read_timeout=read_timeout,
                **filesource_kwargs
            )

        async_location = initial_project_post_response.headers["Location"]
        return cls.from_async(async_location, max_wait)

    @classmethod
    def from_async(cls, async_location, max_wait=DEFAULT_MAX_WAIT):
        """
        Given a temporary async status location poll for no more than max_wait seconds
        until the async process (project creation or setting the target, for example)
        finishes successfully, then return the ready project

        Parameters
        ----------
        async_location : str
            The URL for the temporary async status resource. This is returned
            as a header in the response to a request that initiates an
            async process
        max_wait : int
            The maximum number of seconds to wait before giving up.

        Returns
        -------
        project : Project
            The project, now ready

        Raises
        ------
        ProjectAsyncFailureError
            If the server returned an unexpected response while polling for the
            asynchronous operation to resolve
        AsyncProcessUnsuccessfulError
            If the final result of the asynchronous operation was a failure
        AsyncTimeoutError
            If the asynchronous operation did not resolve within the time
            specified
        """
        try:
            finished_location = wait_for_async_resolution(
                cls._client, async_location, max_wait=max_wait
            )
            proj_id = get_id_from_location(finished_location)
            return cls.get(proj_id)
        except errors.AppPlatformError as e:
            raise errors.ProjectAsyncFailureError(repr(e), e.status_code, async_location)

    @classmethod
    def start(
        cls,
        sourcedata,
        target=None,
        project_name="Untitled Project",
        worker_count=None,
        metric=None,
        autopilot_on=True,
        blueprint_threshold=None,
        response_cap=None,
        partitioning_method=None,
        positive_class=None,
        target_type=None,
        unsupervised_mode=False,
        blend_best_models=None,
        prepare_model_for_deployment=None,
        consider_blenders_in_recommendation=None,
        scoring_code_only=None,
        min_secondary_validation_model_count=None,
        shap_only_mode=None,
        relationships_configuration_id=None,
        autopilot_with_feature_discovery=None,
        feature_discovery_supervised_feature_reduction=None,
        unsupervised_type=None,
        autopilot_cluster_list=None,
    ):
        """
        Chain together project creation, file upload, and target selection.

        .. note:: While this function provides a simple means to get started, it does not expose
            all possible parameters. For advanced usage, using ``create`` and ``set_target``
            directly is recommended.

        Parameters
        ----------
        sourcedata : str or pandas.DataFrame
            The path to the file to upload. Can be either a path to a
            local file or a publicly accessible URL (starting with ``http://``, ``https://``,
            ``file://``, or ``s3://``). If the source is a DataFrame, it will be serialized to a
            temporary buffer.
            If using a file, the filename must consist of ASCII
            characters only.
        target : str, optional
            The name of the target column in the uploaded file. Should not be provided if
            ``unsupervised_mode`` is ``True``.
        project_name : str
            The project name.

        Other Parameters
        ----------------
        worker_count : int, optional
            The number of workers that you want to allocate to this project.
        metric : str, optional
            The name of metric to use.
        autopilot_on : boolean, default ``True``
            Whether or not to begin modeling automatically.
        blueprint_threshold : int, optional
            Number of hours the model is permitted to run.
            Minimum 1
        response_cap : float, optional
            Quantile of the response distribution to use for response capping
            Must be in range 0.5 .. 1.0
        partitioning_method : PartitioningMethod object, optional
            Instance of one of the :ref:`Partition Classes <partitions_api>` defined in
            ``datarobot.helpers.partitioning_methods``.
        positive_class : str, float, or int; optional
            Specifies a level of the target column that should treated as the
            positive class for binary classification.  May only be specified
            for binary classification targets.
        target_type : str, optional
            Override the automaticially selected target_type. An example usage would be setting the
            target_type='Multiclass' when you want to preform a multiclass classification task on a
            numeric column that has a low cardinality.
            You can use ``TARGET_TYPE`` enum.
        unsupervised_mode : boolean, default ``False``
            Specifies whether to create an unsupervised project.
        blend_best_models: bool, optional
            blend best models during Autopilot run
        scoring_code_only: bool, optional
            Keep only models that can be converted to scorable java code during Autopilot run.
        shap_only_mode: bool, optional
            Keep only models that support SHAP values during Autopilot run. Use SHAP-based insights
            wherever possible. Defaults to False.
        prepare_model_for_deployment: bool, optional
            Prepare model for deployment during Autopilot run.
            The preparation includes creating reduced feature list models, retraining best model on
            higher sample size, computing insights and assigning "RECOMMENDED FOR DEPLOYMENT" label.
        consider_blenders_in_recommendation: bool, optional
            Include blenders when selecting a model to prepare for deployment in an Autopilot Run.
            Defaults to False.
        min_secondary_validation_model_count: int, optional
           Compute "All backtest" scores (datetime models) or cross validation scores
           for the specified number of highest ranking models on the Leaderboard,
           if over the Autopilot default.
        relationships_configuration_id : str, optional
            (New in version v2.23) id of the relationships configuration to use
        autopilot_with_feature_discovery: bool, optional.
            (New in version v2.23) If true, autopilot will run on a feature list that includes
            features found via search for interactions.
        feature_discovery_supervised_feature_reduction: bool, default ``True`` optional
            (New in version v2.23) Run supervised feature reduction for feature discovery projects.
        unsupervised_type : UnsupervisedTypeEnum, optional
            (New in version v2.27) Specifies whether an unsupervised project is anomaly detection
            or clustering.
        autopilot_cluster_list : list(int), optional
            (New in version v2.27) Specifies the list of clusters to build for each model during
            Autopilot. Specifying multiple values in a list will build models with each number
            of clusters for the Leaderboard.

        Returns
        -------
        project : Project
            The newly created and initialized project.

        Raises
        ------
        AsyncFailureError
            Polling for status of async process resulted in response
            with unsupported status code
        AsyncProcessUnsuccessfulError
            Raised if project creation or target setting was unsuccessful
        AsyncTimeoutError
            Raised if project creation or target setting timed out

        Examples
        --------

        .. code-block:: python

            Project.start("./tests/fixtures/file.csv",
                          "a_target",
                          project_name="test_name",
                          worker_count=4,
                          metric="a_metric")

        This is an example of using a URL to specify the datasource:

        .. code-block:: python

            Project.start("https://example.com/data/file.csv",
                          "a_target",
                          project_name="test_name",
                          worker_count=4,
                          metric="a_metric")

        """
        # Create project part
        create_data = {"project_name": project_name, "sourcedata": sourcedata}
        project = cls.create(**create_data)

        # Set target
        if autopilot_on:
            mode = AUTOPILOT_MODE.QUICK
            # unsupervised clustering supports autopilot only in comprehensive mode
            if unsupervised_mode and unsupervised_type == UnsupervisedTypeEnum.CLUSTERING:
                mode = AUTOPILOT_MODE.COMPREHENSIVE
        else:
            mode = AUTOPILOT_MODE.MANUAL

        sfd = feature_discovery_supervised_feature_reduction
        advanced_options = AdvancedOptions(
            blueprint_threshold=blueprint_threshold,
            response_cap=response_cap,
            blend_best_models=blend_best_models,
            scoring_code_only=scoring_code_only,
            shap_only_mode=shap_only_mode,
            prepare_model_for_deployment=prepare_model_for_deployment,
            consider_blenders_in_recommendation=consider_blenders_in_recommendation,
            min_secondary_validation_model_count=min_secondary_validation_model_count,
            autopilot_with_feature_discovery=autopilot_with_feature_discovery,
            feature_discovery_supervised_feature_reduction=sfd,
        )

        project.set_target(
            target=target,
            metric=metric,
            mode=mode,
            worker_count=worker_count,
            advanced_options=advanced_options,
            partitioning_method=partitioning_method,
            positive_class=positive_class,
            target_type=target_type,
            unsupervised_mode=unsupervised_mode,
            relationships_configuration_id=relationships_configuration_id,
            unsupervised_type=unsupervised_type,
            autopilot_cluster_list=autopilot_cluster_list,
        )
        return project

    @classmethod
    def list(cls, search_params=None):
        """
        Returns the projects associated with this account.

        Parameters
        ----------
        search_params : dict, optional.
            If not `None`, the returned projects are filtered by lookup.
            Currently you can query projects by:

            * ``project_name``

        Returns
        -------
        projects : list of Project instances
            Contains a list of projects associated with this user
            account.

        Raises
        ------
        TypeError
            Raised if ``search_params`` parameter is provided,
            but is not of supported type.

        Examples
        --------
        List all projects
        .. code-block:: python

            p_list = Project.list()
            p_list
            >>> [Project('Project One'), Project('Two')]

        Search for projects by name
        .. code-block:: python

            Project.list(search_params={'project_name': 'red'})
            >>> [Project('Predtime'), Project('Fred Project')]

        """
        get_params = {}
        if search_params is not None:
            if isinstance(search_params, dict):
                get_params.update(search_params)
            else:
                raise TypeError(
                    "Provided search_params argument {} is invalid type {}".format(
                        search_params, type(search_params)
                    )
                )
        r_data = cls._client.get(cls._path, params=get_params).json()
        return [cls.from_server_data(item) for item in r_data]

    def _update(self, **data):
        """
        Change the project properties.

        In the future, DataRobot API will provide endpoints to directly
        update the attributes currently handled by this one endpoint.

        Other Parameters
        ----------------
        project_name : str, optional
            The name to assign to this project.

        holdout_unlocked : bool, optional
            Can only have value of `True`. If
            passed, unlocks holdout for project.

        worker_count : int, optional
            Sets number of workers. This cannot be greater than the number available to the
            current user account. Setting this to the special value of -1 will update the number
            of workers to the maximum allowable to your account.

        Returns
        -------
        project : Project
            Instance with fields updated.
        """
        acceptable_keywords = {
            "project_name",
            "holdout_unlocked",
            "worker_count",
            "project_description",
        }
        for key in set(data) - acceptable_keywords:
            raise TypeError("update() got an unexpected keyword argument '{}'".format(key))
        url = "{}{}/".format(self._path, self.id)
        self._client.patch(url, data=data)

        if "project_name" in data:
            self.project_name = data["project_name"]
        if "holdout_unlocked" in data:
            self.holdout_unlocked = data["holdout_unlocked"]
        if "project_description" in data:
            self.project_description = data["project_description"]
        return self

    def refresh(self):
        """
        Fetches the latest state of the project, and updates this object
        with that information. This is an inplace update, not a new object.

        Returns
        -------
        self : Project
            the now-updated project
        """
        url = "{}{}/".format(self._path, self.id)
        data = self._server_data(url)
        self._set_values(data)

    def delete(self):
        """
        Removes this project from your account.
        """
        url = "{}{}/".format(self._path, self.id)
        self._client.delete(url)

    def _construct_aim_payload(self, target, mode, metric):
        """
        Constructs the AIM payload to POST when setting the target for the project.

        Note that this private method is relied upon for extensibility so that subclasses can
        inject additional payload data when setting the project target.

        See set_target for more extensive description of these parameters.

        Parameters
        ----------
        target : str
            Project target to specify for AIM.
        mode : str
            Project ``AUTOPILOT_MODE``
        metric : str
            Project metric to use.
        Returns
        -------
        dict
        """
        return {
            "target": target,
            "mode": mode,
            "metric": metric,
        }

    def set_target(
        self,
        target=None,
        mode=AUTOPILOT_MODE.QUICK,
        metric=None,
        quickrun=None,
        worker_count=None,
        positive_class=None,
        partitioning_method=None,
        featurelist_id=None,
        advanced_options=None,
        max_wait=DEFAULT_MAX_WAIT,
        target_type=None,
        credentials=None,
        feature_engineering_prediction_point=None,
        unsupervised_mode=False,
        relationships_configuration_id=None,
        class_mapping_aggregation_settings=None,
        segmentation_task_id=None,
        unsupervised_type=None,
        autopilot_cluster_list=None,
    ):
        """
        Set target variable of an existing project and begin the autopilot process (unless manual
        mode is specified).

        Target setting is asynchronous process, which means that after
        initial request we will keep polling status of async process
        that is responsible for target setting until it's finished.
        For SDK users this only means that this method might raise
        exceptions related to it's async nature.

        When execution returns to the caller, the autopilot process will already have commenced
        (again, unless manual mode is specified).

        Parameters
        ----------
        target : str, optional
            The name of the target column in the uploaded file. Should not be provided if
            ``unsupervised_mode`` is ``True``.
        mode : str, optional
            You can use ``AUTOPILOT_MODE`` enum to choose between

            * ``AUTOPILOT_MODE.FULL_AUTO``
            * ``AUTOPILOT_MODE.MANUAL``
            * ``AUTOPILOT_MODE.QUICK``
            * ``AUTOPILOT_MODE.COMPREHENSIVE``: Runs all blueprints in the repository (warning:
              this may be extremely slow).

            If unspecified, ``QUICK`` is used. If the ``MANUAL`` value is used, the model
            creation process will need to be started by executing the ``start_autopilot``
            function with the desired featurelist. It will start immediately otherwise.
        metric : str, optional
            Name of the metric to use for evaluating models. You can query
            the metrics available for the target by way of
            ``Project.get_metrics``. If none is specified, then the default
            recommended by DataRobot is used.
        quickrun : bool, optional
            Deprecated - pass ``AUTOPILOT_MODE.QUICK`` as mode instead.
            Sets whether project should be run in ``quick run`` mode. This
            setting causes DataRobot to recommend a more limited set of models
            in order to get a base set of models and insights more quickly.
        worker_count : int, optional
            The number of concurrent workers to request for this project. If
            `None`, then the default is used.
            (New in version v2.14) Setting this to -1 will request the maximum number
            available to your account.
        partitioning_method : PartitioningMethod object, optional
            Instance of one of the :ref:`Partition Classes <partitions_api>` defined in
            ``datarobot.helpers.partitioning_methods``.
        positive_class : str, float, or int; optional
            Specifies a level of the target column that should treated as the
            positive class for binary classification.  May only be specified
            for binary classification targets.
        featurelist_id : str, optional
            Specifies which feature list to use.
        advanced_options : AdvancedOptions, optional
            Used to set advanced options of project creation.
        max_wait : int, optional
            Time in seconds after which target setting is considered
            unsuccessful.
        target_type : str, optional
            Override the automatically selected target_type. An example usage would be setting the
            target_type='Mutliclass' when you want to preform a multiclass classification task on a
            numeric column that has a low cardinality. You can use ``TARGET_TYPE`` enum.
        credentials: list, optional,
             a list of credentials for the datasets used in relationship configuration
             (previously graphs).
        feature_engineering_prediction_point : str, optional
            additional aim parameter.
        unsupervised_mode : boolean, default ``False``
            (New in version v2.20) Specifies whether to create an unsupervised project. If ``True``,
            ``target`` may not be provided.
        relationships_configuration_id : str, optional
            (New in version v2.21) ID of the relationships configuration to use.
        segmentation_task_id : str or SegmentationTask, optional
            (New in version v2.28) The segmentation task that should be used to split the project
            for segmented modeling.
        unsupervised_type : UnsupervisedTypeEnum, optional
            (New in version v2.27) Specifies whether an unsupervised project is anomaly detection
            or clustering.
        autopilot_cluster_list : list(int), optional
            (New in version v2.27) Specifies the list of clusters to build for each model during
            Autopilot. Specifying multiple values in a list will build models with each number
            of clusters for the Leaderboard.

        Returns
        -------
        project : Project
            The instance with updated attributes.

        Raises
        ------
        AsyncFailureError
            Polling for status of async process resulted in response
            with unsupported status code
        AsyncProcessUnsuccessfulError
            Raised if target setting was unsuccessful
        AsyncTimeoutError
            Raised if target setting took more time, than specified
            by ``max_wait`` parameter
        TypeError
            Raised if ``advanced_options``, ``partitioning_method`` or
            ``target_type`` is provided, but is not of supported type

        See Also
        --------
        datarobot.models.Project.start : combines project creation, file upload, and target
            selection. Provides fewer options, but is useful for getting started quickly.
        """
        if quickrun:
            alternative = "Pass `AUTOPILOT_MODE.QUICK` as the mode instead."
            deprecation_warning(
                "quickrun parameter",
                deprecated_since_version="v2.4",
                will_remove_version="v3.0",
                message=alternative,
            )
        if mode == AUTOPILOT_MODE.QUICK or quickrun:
            mode = AUTOPILOT_MODE.FULL_AUTO
            quickrun = True
        elif mode == AUTOPILOT_MODE.FULL_AUTO and quickrun is None:
            quickrun = False

        if worker_count is not None:
            self.set_worker_count(worker_count)

        aim_payload = self._construct_aim_payload(target, mode, metric)

        if advanced_options is not None:
            self._load_advanced_options(advanced_options, aim_payload)
        if positive_class is not None:
            aim_payload["positive_class"] = positive_class
        if quickrun is not None:
            aim_payload["quickrun"] = quickrun
        if target_type is not None:
            aim_payload["target_type"] = self._validate_and_return_target_type(target_type)
        if featurelist_id is not None:
            aim_payload["featurelist_id"] = featurelist_id
        if credentials is not None:
            aim_payload["credentials"] = credentials
        if feature_engineering_prediction_point is not None:
            aim_payload[
                "feature_engineering_prediction_point"
            ] = feature_engineering_prediction_point
        if partitioning_method:
            self._load_partitioning_method(partitioning_method, aim_payload)
            partitioning_method.prep_payload(self.id, max_wait=max_wait)
        if unsupervised_mode:
            aim_payload["unsupervised_mode"] = unsupervised_mode
            if unsupervised_type:
                aim_payload["unsupervised_type"] = unsupervised_type
            if unsupervised_type == UnsupervisedTypeEnum.CLUSTERING:
                if autopilot_cluster_list:
                    if not isinstance(autopilot_cluster_list, list):
                        raise ValueError("autopilot_cluster_list must be a list of integers")
                    aim_payload["autopilot_cluster_list"] = autopilot_cluster_list
        if relationships_configuration_id is not None:
            aim_payload["relationships_configuration_id"] = relationships_configuration_id
        if (
            target_type in {TARGET_TYPE.MULTICLASS, TARGET_TYPE.MULTILABEL}
            and class_mapping_aggregation_settings is not None
        ):
            aim_payload[
                "class_mapping_aggregation_settings"
            ] = class_mapping_aggregation_settings.collect_payload()

        if segmentation_task_id is not None:
            if max_wait == DEFAULT_MAX_WAIT:
                max_wait = DEFAULT_MAX_WAIT * 2
            if isinstance(segmentation_task_id, SegmentationTask):
                aim_payload["segmentation_task_id"] = segmentation_task_id.id
            elif isinstance(segmentation_task_id, str):
                aim_payload["segmentation_task_id"] = segmentation_task_id
            else:
                raise ValueError(
                    "segmentation_task_id must be either a string id or a SegmentationTask object"
                )

        url = "{}{}/aim/".format(self._path, self.id)
        response = self._client.patch(url, data=aim_payload)
        async_location = response.headers["Location"]

        # Waits for project to be ready for modeling, but ignores the return value
        self.from_async(async_location, max_wait=max_wait)

        self.refresh()
        return self

    def get_models(self, order_by=None, search_params=None, with_metric=None):
        """
        List all completed, successful models in the leaderboard for the given project.

        Parameters
        ----------
        order_by : str or list of strings, optional
            If not `None`, the returned models are ordered by this
            attribute. If `None`, the default return is the order of
            default project metric.

            Allowed attributes to sort by are:

            * ``metric``
            * ``sample_pct``

            If the sort attribute is preceded by a hyphen, models will be sorted in descending
            order, otherwise in ascending order.

            Multiple sort attributes can be included as a comma-delimited string or in a list
            e.g. order_by=`sample_pct,-metric` or order_by=[`sample_pct`, `-metric`]

            Using `metric` to sort by will result in models being sorted according to their
            validation score by how well they did according to the project metric.
        search_params : dict, optional.
            If not `None`, the returned models are filtered by lookup.
            Currently you can query models by:

            * ``name``
            * ``sample_pct``
            * ``is_starred``

        with_metric : str, optional.
            If not `None`, the returned models will only have scores for this
            metric. Otherwise all the metrics are returned.

        Returns
        -------
        models : a list of Model instances.
            All of the models that have been trained in this project.

        Raises
        ------
        TypeError
            Raised if ``order_by`` or ``search_params`` parameter is provided,
            but is not of supported type.

        Examples
        --------

        .. code-block:: python

            Project.get('pid').get_models(order_by=['-sample_pct',
                                          'metric'])

            # Getting models that contain "Ridge" in name
            # and with sample_pct more than 64
            Project.get('pid').get_models(
                search_params={
                    'sample_pct__gt': 64,
                    'name': "Ridge"
                })

            # Filtering models based on 'starred' flag:
            Project.get('pid').get_models(search_params={'is_starred': True})
        """
        from . import Model

        url = "{}{}/models/".format(self._path, self.id)
        get_params = {}
        if order_by is not None:
            order_by = self._canonize_order_by(order_by)
            get_params.update({"order_by": order_by})
        else:
            get_params.update({"order_by": "-metric"})
        if search_params is not None:
            if isinstance(search_params, dict):
                get_params.update(search_params)
            else:
                raise TypeError("Provided search_params argument is invalid")
        if with_metric is not None:
            get_params.update({"with_metric": with_metric})
        if "is_starred" in get_params:
            get_params["is_starred"] = "true" if get_params["is_starred"] else "false"
        resp_data = self._client.get(url, params=get_params).json()
        init_data = [dict(Model._safe_data(item), project=self) for item in resp_data]
        return [Model(**data) for data in init_data]

    def recommended_model(self):
        """Returns the default recommended model, or None if there is no default recommended model.

        Returns
        -------
        recommended_model : Model or None
            The default recommended model.

        """
        from . import ModelRecommendation

        try:
            model_recommendation = ModelRecommendation.get(self.id)
            return model_recommendation.get_model() if model_recommendation else None
        except errors.ClientError:
            warnings.warn(
                "Could not retrieve recommended model, or the recommended model does not exist.",
                ProjectHasNoRecommendedModelWarning,
            )
        return None

    def _canonize_order_by(self, order_by):
        legal_keys = [
            LEADERBOARD_SORT_KEY.SAMPLE_PCT,
            LEADERBOARD_SORT_KEY.PROJECT_METRIC,
        ]
        processed_keys = []
        if order_by is None:
            return order_by
        if isinstance(order_by, str):
            order_by = order_by.split(",")
        if not isinstance(order_by, list):
            msg = "Provided order_by attribute {} is of an unsupported type".format(order_by)
            raise TypeError(msg)
        for key in order_by:
            key = key.strip()
            if key.startswith("-"):
                prefix = "-"
                key = key[1:]
            else:
                prefix = ""
            if key not in legal_keys:
                camel_key = camelize(key)
                if camel_key not in legal_keys:
                    msg = "Provided order_by attribute {}{} is invalid".format(prefix, key)
                    raise ValueError(msg)
                key = camel_key
            processed_keys.append("{}{}".format(prefix, key))
        return ",".join(processed_keys)

    def get_datetime_models(self):
        """List all models in the project as DatetimeModels

        Requires the project to be datetime partitioned.  If it is not, a ClientError will occur.

        Returns
        -------
        models : list of DatetimeModel
            the datetime models
        """
        from . import DatetimeModel

        url = "{}{}/datetimeModels/".format(self._path, self.id)
        data = unpaginate(url, None, self._client)
        return [DatetimeModel.from_server_data(item) for item in data]

    def get_prime_models(self):
        """List all DataRobot Prime models for the project
        Prime models were created to approximate a parent model, and have downloadable code.

        Returns
        -------
        models : list of PrimeModel
        """
        from . import PrimeModel

        models_response = self._client.get("{}{}/primeModels/".format(self._path, self.id)).json()
        model_data_list = models_response["data"]
        return [PrimeModel.from_server_data(data) for data in model_data_list]

    def get_prime_files(self, parent_model_id=None, model_id=None):
        """List all downloadable code files from DataRobot Prime for the project

        Parameters
        ----------
        parent_model_id : str, optional
            Filter for only those prime files approximating this parent model
        model_id : str, optional
            Filter for only those prime files with code for this prime model

        Returns
        -------
        files: list of PrimeFile
        """
        url = "{}{}/primeFiles/".format(self._path, self.id)
        params = {"parent_model_id": parent_model_id, "model_id": model_id}
        files = self._client.get(url, params=params).json()["data"]
        return [PrimeFile.from_server_data(file_data) for file_data in files]

    def get_datasets(self):
        """List all the datasets that have been uploaded for predictions

        Returns
        -------
        datasets : list of PredictionDataset instances
        """
        datasets = self._client.get("{}{}/predictionDatasets/".format(self._path, self.id)).json()
        return [PredictionDataset.from_server_data(data) for data in datasets["data"]]

    def upload_dataset(
        self,
        sourcedata,
        max_wait=DEFAULT_MAX_WAIT,
        read_timeout=DEFAULT_TIMEOUT.UPLOAD,
        forecast_point=None,
        predictions_start_date=None,
        predictions_end_date=None,
        dataset_filename=None,
        relax_known_in_advance_features_check=None,
        credentials=None,
        actual_value_column=None,
        secondary_datasets_config_id=None,
    ):
        """Upload a new dataset to make predictions against

        Parameters
        ----------
        sourcedata : str, file or pandas.DataFrame
            Data to be used for predictions. If string, can be either a path to a local file,
            a publicly accessible URL (starting with ``http://``, ``https://``, ``file://``), or
            raw file content. If using a file on disk, the filename must consist of ASCII
            characters only.
        max_wait : int, optional
            The maximum number of seconds to wait for the uploaded dataset to be processed before
            raising an error.
        read_timeout : int, optional
            The maximum number of seconds to wait for the server to respond indicating that the
            initial upload is complete
        forecast_point : datetime.datetime or None, optional
            (New in version v2.8) May only be specified for time series projects, otherwise the
            upload will be rejected. The time in the dataset relative to which predictions should be
            generated in a time series project.  See the :ref:`Time Series documentation
            <time_series_predict>` for more information. If not provided, will default to using the
            latest forecast point in the dataset.
        predictions_start_date : datetime.datetime or None, optional
            (New in version v2.11) May only be specified for time series projects. The start date
            for bulk predictions. Note that this parameter is for generating historical predictions
            using the training data. This parameter should be provided in conjunction with
            ``predictions_end_date``. Cannot be provided with the ``forecast_point`` parameter.
        predictions_end_date : datetime.datetime or None, optional
            (New in version v2.11) May only be specified for time series projects. The end date
            for bulk predictions, exclusive. Note that this parameter is for generating
            historical predictions using the training data. This parameter should be provided in
            conjunction with ``predictions_start_date``.
            Cannot be provided with the ``forecast_point`` parameter.
        actual_value_column : string, optional
            (New in version v2.21) Actual value column name, valid for the prediction
            files if the project is unsupervised and the dataset is considered as bulk predictions
            dataset. Cannot be provided with the ``forecast_point`` parameter.
        dataset_filename : string or None, optional
            (New in version v2.14) File name to use for the dataset.
            Ignored for url and file path sources.
        relax_known_in_advance_features_check : bool, optional
            (New in version v2.15) For time series projects only. If True, missing values in the
            known in advance features are allowed in the forecast window at the prediction time.
            If omitted or False, missing values are not allowed.
        credentials: list, optional, a list of credentials for the datasets used
            in Feature discovery project
        secondary_datasets_config_id: string or None, optional
            (New in version v2.23) The Id of the alternative secondary dataset config
            to use during prediction for Feature discovery project.
        Returns
        -------
        dataset : PredictionDataset
            The newly uploaded dataset.

        Raises
        ------
        InputNotUnderstoodError
            Raised if ``sourcedata`` isn't one of supported types.
        AsyncFailureError
            Raised if polling for the status of an async process resulted in a response with an
            unsupported status code.
        AsyncProcessUnsuccessfulError
            Raised if project creation was unsuccessful (i.e. the server reported an error in
            uploading the dataset).
        AsyncTimeoutError
            Raised if processing the uploaded dataset took more time than specified
            by the ``max_wait`` parameter.
        ValueError
            Raised if ``forecast_point`` or ``predictions_start_date`` and ``predictions_end_date``
            are provided, but are not of the supported type.
        """
        form_data = {}
        if forecast_point:
            if not isinstance(forecast_point, datetime):
                raise ValueError("forecast_point must be an instance of datetime.datetime")
            form_data["forecast_point"] = forecast_point

        if forecast_point and predictions_start_date or forecast_point and predictions_end_date:
            raise ValueError(
                "forecast_point can not be provided together with "
                "predictions_start_date or predictions_end_date"
            )

        if predictions_start_date and predictions_end_date:
            if not isinstance(predictions_start_date, datetime):
                raise ValueError("predictions_start_date must be an instance of datetime.datetime")
            if not isinstance(predictions_end_date, datetime):
                raise ValueError("predictions_end_date must be an instance of datetime.datetime")
            form_data["predictions_start_date"] = predictions_start_date
            form_data["predictions_end_date"] = predictions_end_date
        elif predictions_start_date or predictions_end_date:
            raise ValueError(
                "Both prediction_start_date and prediction_end_date "
                "must be provided at the same time"
            )

        if actual_value_column:
            form_data["actual_value_column"] = actual_value_column
        if relax_known_in_advance_features_check:
            form_data["relax_known_in_advance_features_check"] = str(
                relax_known_in_advance_features_check
            )

        if credentials:
            form_data["credentials"] = json.dumps(credentials)
        if secondary_datasets_config_id:
            form_data["secondary_datasets_config_id"] = secondary_datasets_config_id
        if is_urlsource(sourcedata):
            form_data["url"] = sourcedata
            upload_url = "{}{}/predictionDatasets/urlUploads/".format(self._path, self.id)
            initial_project_post_response = self._client.post(upload_url, data=form_data)
        else:
            dataset_filename = dataset_filename or "predict.csv"
            filesource_kwargs = recognize_sourcedata(sourcedata, dataset_filename)
            upload_url = "{}{}/predictionDatasets/fileUploads/".format(self._path, self.id)
            initial_project_post_response = self._client.build_request_with_file(
                url=upload_url,
                form_data=form_data,
                method="post",
                read_timeout=read_timeout,
                **filesource_kwargs
            )

        async_loc = initial_project_post_response.headers["Location"]
        dataset_loc = wait_for_async_resolution(self._client, async_loc, max_wait=max_wait)
        dataset_data = self._client.get(dataset_loc, join_endpoint=False).json()
        return PredictionDataset.from_server_data(dataset_data)

    def upload_dataset_from_data_source(
        self,
        data_source_id,
        username,
        password,
        max_wait=DEFAULT_MAX_WAIT,
        forecast_point=None,
        relax_known_in_advance_features_check=None,
        credentials=None,
        predictions_start_date=None,
        predictions_end_date=None,
        actual_value_column=None,
        secondary_datasets_config_id=None,
    ):
        """
        Upload a new dataset from a data source to make predictions against

        Parameters
        ----------
        data_source_id : str
            The identifier of the data source.
        username : str
            The username for database authentication.
        password : str
            The password for database authentication. The password is encrypted
            at server side and never saved / stored.
        max_wait : int, optional
            Optional, the maximum number of seconds to wait before giving up.
        forecast_point : datetime.datetime or None, optional
            (New in version v2.8) For time series projects only. This is the default point relative
            to which predictions will be generated, based on the forecast window of the project. See
            the time series :ref:`prediction documentation <time_series_predict>` for more
            information.
        relax_known_in_advance_features_check : bool, optional
            (New in version v2.15) For time series projects only. If True, missing values in the
            known in advance features are allowed in the forecast window at the prediction time.
            If omitted or False, missing values are not allowed.
        credentials: list, optional, a list of credentials for the datasets used
            in Feature discovery project
        predictions_start_date : datetime.datetime or None, optional
            (New in version v2.20) For time series projects only. The start date for bulk
            predictions. Note that this parameter is for generating historical predictions using the
            training data. This parameter should be provided in conjunction with
            ``predictions_end_date``. Can't be provided with the ``forecast_point`` parameter.
        predictions_end_date : datetime.datetime or None, optional
            (New in version v2.20) For time series projects only. The end date for bulk predictions,
            exclusive. Note that this parameter is for generating historical predictions using the
            training data. This parameter should be provided in conjunction with
            ``predictions_start_date``. Can't be provided with the ``forecast_point`` parameter.
        actual_value_column : string, optional
            (New in version v2.21) Actual value column name, valid for the prediction
            files if the project is unsupervised and the dataset is considered as bulk predictions
            dataset. Cannot be provided with the ``forecast_point`` parameter.
        secondary_datasets_config_id: string or None, optional
            (New in version v2.23) The Id of the alternative secondary dataset config
            to use during prediction for Feature discovery project.
        Returns
        -------
        dataset : PredictionDataset
            the newly uploaded dataset

        """
        form_data = {"dataSourceId": data_source_id, "user": username, "password": password}
        if forecast_point:
            if not isinstance(forecast_point, datetime):
                raise ValueError("forecast_point must be an instance of datetime.datetime")
            form_data["forecastPoint"] = datetime_to_string(forecast_point)
        if predictions_start_date:
            if not isinstance(predictions_start_date, datetime):
                raise ValueError("predictions_start_date must be an instance of datetime.datetime")
            form_data["predictions_start_date"] = datetime_to_string(predictions_start_date)
        if predictions_end_date:
            if not isinstance(predictions_end_date, datetime):
                raise ValueError("predictions_end_date must be an instance of datetime.datetime")
            form_data["predictions_end_date"] = datetime_to_string(predictions_end_date)

        if relax_known_in_advance_features_check:
            form_data["relaxKnownInAdvanceFeaturesCheck"] = relax_known_in_advance_features_check
        if credentials:
            form_data["credentials"] = json.dumps(credentials)
        if secondary_datasets_config_id:
            form_data["secondary_datasets_config_id"] = secondary_datasets_config_id
        if actual_value_column:
            form_data["actual_value_column"] = actual_value_column

        upload_url = "{}{}/predictionDatasets/dataSourceUploads/".format(self._path, self.id)
        initial_project_post_response = self._client.post(upload_url, json=form_data)
        async_loc = initial_project_post_response.headers["Location"]
        dataset_loc = wait_for_async_resolution(self._client, async_loc, max_wait=max_wait)
        dataset_data = self._client.get(dataset_loc, join_endpoint=False).json()
        return PredictionDataset.from_server_data(dataset_data)

    def upload_dataset_from_catalog(
        self,
        dataset_id,
        dataset_version_id=None,
        max_wait=DEFAULT_MAX_WAIT,
        forecast_point=None,
        relax_known_in_advance_features_check=None,
        credentials=None,
        predictions_start_date=None,
        predictions_end_date=None,
        actual_value_column=None,
        secondary_datasets_config_id=None,
    ):
        """Upload a new dataset from a catalog dataset to make predictions against

        Parameters
        ----------
        dataset_id : str
            The identifier of the dataset.
        dataset_version_id : str, optional
            The version id of the dataset to use.
        max_wait : int, optional
            Optional, the maximum number of seconds to wait before giving up.
        forecast_point : datetime.datetime or None, optional
            For time series projects only. This is the default point relative
            to which predictions will be generated, based on the forecast window of the project. See
            the time series :ref:`prediction documentation <time_series_predict>` for more
            information.
        relax_known_in_advance_features_check : bool, optional
            For time series projects only. If True, missing values in the
            known in advance features are allowed in the forecast window at the prediction time.
            If omitted or False, missing values are not allowed.
        credentials: list, optional, a list of credentials for the datasets used
            in Feature discovery project
        predictions_start_date : datetime.datetime or None, optional
            For time series projects only. The start date for bulk
            predictions. Note that this parameter is for generating historical predictions using the
            training data. This parameter should be provided in conjunction with
            ``predictions_end_date``. Can't be provided with the ``forecast_point`` parameter.
        predictions_end_date : datetime.datetime or None, optional
            For time series projects only. The end date for bulk predictions,
            exclusive. Note that this parameter is for generating historical predictions using the
            training data. This parameter should be provided in conjunction with
            ``predictions_start_date``. Can't be provided with the ``forecast_point`` parameter.
        actual_value_column : string, optional
            Actual value column name, valid for the prediction
            files if the project is unsupervised and the dataset is considered as bulk predictions
            dataset. Cannot be provided with the ``forecast_point`` parameter.
        secondary_datasets_config_id: string or None, optional
            The Id of the alternative secondary dataset config
            to use during prediction for Feature discovery project.

        Returns
        -------
        dataset : PredictionDataset
            the newly uploaded dataset
        """
        form_data = {"datasetId": dataset_id}
        if dataset_version_id:
            form_data["datasetVersionId"] = dataset_version_id
        if forecast_point:
            if not isinstance(forecast_point, datetime):
                raise ValueError("forecast_point must be an instance of datetime.datetime")
            form_data["forecastPoint"] = datetime_to_string(forecast_point)
        if predictions_start_date:
            if not isinstance(predictions_start_date, datetime):
                raise ValueError("predictions_start_date must be an instance of datetime.datetime")
            form_data["predictions_start_date"] = datetime_to_string(predictions_start_date)
        if predictions_end_date:
            if not isinstance(predictions_end_date, datetime):
                raise ValueError("predictions_end_date must be an instance of datetime.datetime")
            form_data["predictions_end_date"] = datetime_to_string(predictions_end_date)

        if relax_known_in_advance_features_check:
            form_data["relaxKnownInAdvanceFeaturesCheck"] = relax_known_in_advance_features_check
        if credentials:
            form_data["credentials"] = json.dumps(credentials)
        if secondary_datasets_config_id:
            form_data["secondary_datasets_config_id"] = secondary_datasets_config_id
        if actual_value_column:
            form_data["actual_value_column"] = actual_value_column

        upload_url = "{}{}/predictionDatasets/datasetUploads/".format(self._path, self.id)
        initial_project_post_response = self._client.post(upload_url, json=form_data)
        async_loc = initial_project_post_response.headers["Location"]
        dataset_loc = wait_for_async_resolution(self._client, async_loc, max_wait=max_wait)
        dataset_data = self._client.get(dataset_loc, join_endpoint=False).json()
        return PredictionDataset.from_server_data(dataset_data)

    def get_blueprints(self):
        """
        List all blueprints recommended for a project.

        Returns
        -------
        menu : list of Blueprint instances
            All the blueprints recommended by DataRobot for a project
        """
        from . import Blueprint

        url = "{}{}/blueprints/".format(self._path, self.id)
        resp_data = self._client.get(url).json()
        return [Blueprint.from_data(from_api(item)) for item in resp_data]

    def get_features(self):
        """
        List all features for this project

        Returns
        -------
        list of Feature
            all features for this project
        """
        url = "{}{}/features/".format(self._path, self.id)
        resp_data = self._client.get(url).json()
        return [Feature.from_server_data(item) for item in resp_data]

    def get_modeling_features(self, batch_size=None):
        """List all modeling features for this project

        Only available once the target and partitioning settings have been set.  For more
        information on the distinction between input and modeling features, see the
        :ref:`time series documentation<input_vs_modeling>`.

        Parameters
        ----------
        batch_size : int, optional
            The number of features to retrieve in a single API call.  If specified, the client may
            make multiple calls to retrieve the full list of features.  If not specified, an
            appropriate default will be chosen by the server.

        Returns
        -------
        list of ModelingFeature
            All modeling features in this project
        """
        url = "{}{}/modelingFeatures/".format(self._path, self.id)
        params = {}
        if batch_size is not None:
            params["limit"] = batch_size
        return [
            ModelingFeature.from_server_data(item) for item in unpaginate(url, params, self._client)
        ]

    def get_featurelists(self):
        """
        List all featurelists created for this project

        Returns
        -------
        list of Featurelist
            All featurelists created for this project
        """
        url = "{}{}/featurelists/".format(self._path, self.id)
        resp_data = self._client.get(url).json()
        return [Featurelist.from_data(from_api(item)) for item in resp_data]

    def get_associations(self, assoc_type, metric, featurelist_id=None):
        """Get the association statistics and metadata for a project's
        informative features

        .. versionadded:: v2.17

        Parameters
        ----------
        assoc_type : string or None
            The type of association, must be either 'association' or 'correlation'
        metric : string or None
            The specified association metric, belongs under either association
            or correlation umbrella
        featurelist_id : string or None
            The desired featurelist for which to get association statistics
            (New in version v2.19)

        Returns
        --------
        association_data : dict
            Pairwise metric strength data, feature clustering data,
            and ordering data for Feature Association Matrix visualization
        """
        from .feature_association_matrix import FeatureAssociationMatrix

        feature_association_matrix = FeatureAssociationMatrix.get(
            project_id=self.id,
            metric=metric,
            association_type=assoc_type,
            featurelist_id=featurelist_id,
        )
        return feature_association_matrix.to_dict()

    def get_association_featurelists(self):
        """List featurelists and get feature association status for each

        .. versionadded:: v2.19

        Returns
        --------
        feature_lists : dict
            Dict with 'featurelists' as key, with list of featurelists as values
        """
        from .feature_association_matrix import FeatureAssociationFeaturelists

        fam_featurelists = FeatureAssociationFeaturelists.get(project_id=self.id)
        return fam_featurelists.to_dict()

    def get_association_matrix_details(self, feature1, feature2):
        """Get a sample of the actual values used to measure the association
        between a pair of features

        .. versionadded:: v2.17

        Parameters
        ----------
        feature1 : str
            Feature name for the first feature of interest
        feature2 : str
            Feature name for the second feature of interest

        Returns
        --------
        dict
            This data has 3 keys: chart_type, features, values, and types
        chart_type : str
            Type of plotting the pair of features gets in the UI.
            e.g. 'HORIZONTAL_BOX', 'VERTICAL_BOX', 'SCATTER' or 'CONTINGENCY'
        values : list
            A list of triplet lists e.g.
            {"values": [[460.0, 428.5, 0.001], [1679.3, 259.0, 0.001], ...]
            The first entry of each list is a value of feature1, the second entry of
            each list is a value of feature2, and the third is the relative frequency of
            the pair of datapoints in the sample.
        features : list of str
            A list of the passed features, [feature1, feature2]
        types : list of str
            A list of the passed features' types inferred by DataRobot.
            e.g. ['NUMERIC', 'CATEGORICAL']
        """
        from .feature_association_matrix import FeatureAssociationMatrixDetails

        feature_association_matrix_details = FeatureAssociationMatrixDetails.get(
            project_id=self.id, feature1=feature1, feature2=feature2
        )
        return feature_association_matrix_details.to_dict()

    def get_modeling_featurelists(self, batch_size=None):
        """List all modeling featurelists created for this project

        Modeling featurelists can only be created after the target and partitioning options have
        been set for a project.  In time series projects, these are the featurelists that can be
        used for modeling; in other projects, they behave the same as regular featurelists.

        See the :ref:`time series documentation<input_vs_modeling>` for more information.

        Parameters
        ----------
        batch_size : int, optional
            The number of featurelists to retrieve in a single API call.  If specified, the client
            may make multiple calls to retrieve the full list of features.  If not specified, an
            appropriate default will be chosen by the server.

        Returns
        -------
        list of ModelingFeaturelist
            all modeling featurelists in this project
        """
        url = "{}{}/modelingFeaturelists/".format(self._path, self.id)
        params = {}
        if batch_size is not None:
            params["limit"] = batch_size
        return [
            ModelingFeaturelist.from_server_data(item)
            for item in unpaginate(url, params, self._client)
        ]

    def get_discarded_features(self):
        """ Retrieve discarded during feature generation features. Applicable for time
        series projects. Can be called at the modeling stage.

        Returns
        -------
        discarded_features_info: DiscardedFeaturesInfo
        """
        return DiscardedFeaturesInfo.retrieve(self.id)

    def restore_discarded_features(self, features, max_wait=DEFAULT_MAX_WAIT):
        """ Restore discarded during feature generation features. Applicable for time
        series projects. Can be called at the modeling stage.

        Returns
        -------
        status: FeatureRestorationStatus
            information about features requested to be restored.
        """
        return DiscardedFeaturesInfo.restore(self.id, features, max_wait=max_wait)

    def create_type_transform_feature(
        self, name, parent_name, variable_type, replacement=None, date_extraction=None, max_wait=600
    ):
        """
        Create a new feature by transforming the type of an existing feature in the project

        Note that only the following transformations are supported:

        1. Text to categorical or numeric
        2. Categorical to text or numeric
        3. Numeric to categorical
        4. Date to categorical or numeric

        .. _type_transform_considerations:
        .. note:: **Special considerations when casting numeric to categorical**

            There are two parameters which can be used for ``variableType`` to convert numeric
            data to categorical levels. These differ in the assumptions they make about the input
            data, and are very important when considering the data that will be used to make
            predictions. The assumptions that each makes are:

            * ``categorical`` : The data in the column is all integral, and there are no missing
              values. If either of these conditions do not hold in the training set, the
              transformation will be rejected. During predictions, if any of the values in the
              parent column are missing, the predictions will error. Note that ``CATEGORICAL``
              is deprecated in v2.21.

            * ``categoricalInt`` : **New in v2.6**
              All of the data in the column should be considered categorical in its string form when
              cast to an int by truncation. For example the value ``3`` will be cast as the string
              ``3`` and the value ``3.14`` will also be cast as the string ``3``. Further, the
              value ``-3.6`` will become the string ``-3``.
              Missing values will still be recognized as missing.

            For convenience these are represented in the enum ``VARIABLE_TYPE_TRANSFORM`` with the
            names ``CATEGORICAL`` and ``CATEGORICAL_INT``.

        Parameters
        ----------
        name : str
            The name to give to the new feature
        parent_name : str
            The name of the feature to transform
        variable_type : str
            The type the new column should have. See the values within
            ``datarobot.enums.VARIABLE_TYPE_TRANSFORM``. Note that ``CATEGORICAL``
            is deprecated in v2.21.
        replacement : str or float, optional
            The value that missing or unconverable data should have
        date_extraction : str, optional
            Must be specified when parent_name is a date column (and left None otherwise).
            Specifies which value from a date should be extracted. See the list of values in
            ``datarobot.enums.DATE_EXTRACTION``
        max_wait : int, optional
            The maximum amount of time to wait for DataRobot to finish processing the new column.
            This process can take more time with more data to process. If this operation times
            out, an AsyncTimeoutError will occur. DataRobot continues the processing and the
            new column may successfully be constructed.

        Returns
        -------
        Feature
            The data of the new Feature

        Raises
        ------
        AsyncFailureError
            If any of the responses from the server are unexpected
        AsyncProcessUnsuccessfulError
            If the job being waited for has failed or has been cancelled
        AsyncTimeoutError
            If the resource did not resolve in time
        """
        from .feature import Feature

        if variable_type == VARIABLE_TYPE_TRANSFORM.CATEGORICAL:
            msg = "Use datarobot.enums.VARIABLE_TYPE_TRANSFORM.CATEGORICAL_INT instead"
            deprecation_warning(
                "CATEGORICAL transform",
                deprecated_since_version="v2.21",
                will_remove_version="v2.22",
                message=msg,
            )

        transform_url = "{}{}/typeTransformFeatures/".format(self._path, self.id)
        payload = dict(name=name, parentName=parent_name, variableType=variable_type)

        if replacement is not None:
            payload["replacement"] = replacement
        if date_extraction is not None:
            payload["dateExtraction"] = date_extraction

        response = self._client.post(transform_url, json=payload)
        result = wait_for_async_resolution(
            self._client, response.headers["Location"], max_wait=max_wait
        )
        return Feature.from_location(result)

    def create_featurelist(self, name, features):
        """
        Creates a new featurelist

        Parameters
        ----------
        name : str
            The name to give to this new featurelist. Names must be unique, so
            an error will be returned from the server if this name has already
            been used in this project.
        features : list of str
            The names of the features. Each feature must exist in the project
            already.

        Returns
        -------
        Featurelist
            newly created featurelist

        Raises
        ------
        DuplicateFeaturesError
            Raised if `features` variable contains duplicate features

        Examples
        --------
        .. code-block:: python

            project = Project.get('5223deadbeefdeadbeef0101')
            flists = project.get_featurelists()

            # Create a new featurelist using a subset of features from an
            # existing featurelist
            flist = flists[0]
            features = flist.features[::2]  # Half of the features

            new_flist = project.create_featurelist(name='Feature Subset',
                                                   features=features)
        """
        url = "{}{}/featurelists/".format(self._path, self.id)

        duplicate_features = get_duplicate_features(features)
        if duplicate_features:
            err_msg = "Can't create featurelist with duplicate features - {}".format(
                duplicate_features
            )
            raise errors.DuplicateFeaturesError(err_msg)

        payload = {
            "name": name,
            "features": features,
        }
        response = self._client.post(url, data=payload)
        return Featurelist.from_server_data(response.json())

    def create_modeling_featurelist(self, name, features):
        """Create a new modeling featurelist

        Modeling featurelists can only be created after the target and partitioning options have
        been set for a project.  In time series projects, these are the featurelists that can be
        used for modeling; in other projects, they behave the same as regular featurelists.

        See the :ref:`time series documentation<input_vs_modeling>` for more information.

        Parameters
        ----------
        name : str
            the name of the modeling featurelist to create.  Names must be unique within the
            project, or the server will return an error.
        features : list of str
            the names of the features to include in the modeling featurelist.  Each feature must
            be a modeling feature.

        Returns
        -------
        featurelist : ModelingFeaturelist
            the newly created featurelist

        Examples
        --------
        .. code-block:: python

            project = Project.get('1234deadbeeffeeddead4321')
            modeling_features = project.get_modeling_features()
            selected_features = [feat.name for feat in modeling_features][:5]  # select first five
            new_flist = project.create_modeling_featurelist('Model This', selected_features)
        """
        url = "{}{}/modelingFeaturelists/".format(self._path, self.id)

        payload = {"name": name, "features": features}
        response = self._client.post(url, data=payload)
        return ModelingFeaturelist.from_server_data(response.json())

    def get_metrics(self, feature_name):
        """Get the metrics recommended for modeling on the given feature.

        Parameters
        ----------
        feature_name : str
            The name of the feature to query regarding which metrics are
            recommended for modeling.

        Returns
        -------
        feature_name: str
            The name of the feature that was looked up
        available_metrics: list of str
            An array of strings representing the appropriate metrics.  If the feature
            cannot be selected as the target, then this array will be empty.
        metric_details: list of dict
            The list of `metricDetails` objects

            metric_name: str
                Name of the metric
            supports_timeseries: boolean
                This metric is valid for timeseries
            supports_multiclass: boolean
                This metric is valid for mutliclass classifciaton
            supports_binary: boolean
                This metric is valid for binary classifciaton
            supports_regression: boolean
                This metric is valid for regression
            ascending: boolean
                Should the metric be sorted in ascending order
        """
        url = "{}{}/features/metrics/".format(self._path, self.id)
        params = {"feature_name": feature_name}
        return from_api(self._client.get(url, params=params).json())

    def get_status(self):
        """Query the server for project status.

        Returns
        -------
        status : dict
            Contains:

            * ``autopilot_done`` : a boolean.
            * ``stage`` : a short string indicating which stage the project
              is in.
            * ``stage_description`` : a description of what ``stage`` means.

        Examples
        --------

        .. code-block:: python

            {"autopilot_done": False,
             "stage": "modeling",
             "stage_description": "Ready for modeling"}
        """
        url = "{}{}/status/".format(self._path, self.id)
        return from_api(self._client.get(url).json())

    def pause_autopilot(self):
        """
        Pause autopilot, which stops processing the next jobs in the queue.

        Returns
        -------
        paused : boolean
            Whether the command was acknowledged
        """
        url = "{}{}/autopilot/".format(self._path, self.id)
        payload = {"command": "stop"}
        self._client.post(url, data=payload)

        return True

    def unpause_autopilot(self):
        """
        Unpause autopilot, which restarts processing the next jobs in the queue.

        Returns
        -------
        unpaused : boolean
            Whether the command was acknowledged.
        """
        url = "{}{}/autopilot/".format(self._path, self.id)
        payload = {
            "command": "start",
        }
        self._client.post(url, data=payload)
        return True

    def start_autopilot(
        self,
        featurelist_id,
        mode=AUTOPILOT_MODE.FULL_AUTO,
        blend_best_models=True,
        scoring_code_only=False,
        prepare_model_for_deployment=True,
        consider_blenders_in_recommendation=False,
        run_leakage_removed_feature_list=True,
        autopilot_cluster_list=None,
    ):
        """Starts Autopilot on provided featurelist with the specified Autopilot settings,
        halting the current Autopilot run.

        Only one autopilot can be running at the time.
        That's why any ongoing autopilot on a different featurelist will
        be halted - modeling jobs in queue would not
        be affected but new jobs would not be added to queue by
        the halted autopilot.

        Parameters
        ----------
        featurelist_id : str
            Identifier of featurelist that should be used for autopilot
        mode : str, optional
            The Autopilot mode to run. You can use ``AUTOPILOT_MODE`` enum to choose between

            * ``AUTOPILOT_MODE.FULL_AUTO``

            If unspecified, ``FULL_AUTO`` is used.
        blend_best_models : bool, optional
            Blend best models during Autopilot run. This option is not supported in SHAP-only '
            'mode.
        scoring_code_only : bool, optional
            Keep only models that can be converted to scorable java code during Autopilot run.
        prepare_model_for_deployment : bool, optional
            Prepare model for deployment during Autopilot run. The preparation includes creating
            reduced feature list models, retraining best model on higher sample size,
            computing insights and assigning "RECOMMENDED FOR DEPLOYMENT" label.
        consider_blenders_in_recommendation : bool, optional
            Include blenders when selecting a model to prepare for deployment in an Autopilot Run.
            This option is not supported in SHAP-only mode or for multilabel projects.
        run_leakage_removed_feature_list : bool, optional
            Run Autopilot on Leakage Removed feature list (if exists).
        autopilot_cluster_list : list of int, optional
            (New in v2.27) A list of integers, where each value will be used as the number of
            clusters in Autopilot model(s) for unsupervised clustering projects. Cannot be specified
            unless project unsupervisedMode is true and unsupervisedType is set to 'clustering'.

        Raises
        ------
        AppPlatformError
            Raised project's target was not selected or the settings for Autopilot are invalid
            for the project project.
        """
        url = "{}{}/autopilots/".format(self._path, self.id)
        payload = {
            "featurelistId": featurelist_id,
            "mode": mode,
            "blendBestModels": blend_best_models,
            "scoringCodeOnly": scoring_code_only,
            "prepareModelForDeployment": prepare_model_for_deployment,
            "considerBlendersInRecommendation": consider_blenders_in_recommendation,
            "runLeakageRemovedFeatureList": run_leakage_removed_feature_list,
        }
        if autopilot_cluster_list:
            payload["autopilot_cluster_list"] = autopilot_cluster_list
        self._client.post(url, data=payload)

    def train(
        self,
        trainable,
        sample_pct=None,
        featurelist_id=None,
        source_project_id=None,
        scoring_type=None,
        training_row_count=None,
        monotonic_increasing_featurelist_id=MONOTONICITY_FEATURELIST_DEFAULT,
        monotonic_decreasing_featurelist_id=MONOTONICITY_FEATURELIST_DEFAULT,
        n_clusters=None,
    ):
        """Submit a job to the queue to train a model.

        Either `sample_pct` or `training_row_count` can be used to specify the amount of data to
        use, but not both.  If neither are specified, a default of the maximum amount of data that
        can safely be used to train any blueprint without going into the validation data will be
        selected.

        In smart-sampled projects, `sample_pct` and `training_row_count` are assumed to be in terms
        of rows of the minority class.

        .. note:: If the project uses datetime partitioning, use
            :meth:`Project.train_datetime <datarobot.models.Project.train_datetime>` instead.

        Parameters
        ----------
        trainable : str or Blueprint
            For ``str``, this is assumed to be a blueprint_id. If no
            ``source_project_id`` is provided, the ``project_id`` will be assumed
            to be the project that this instance represents.

            Otherwise, for a ``Blueprint``, it contains the
            blueprint_id and source_project_id that we want
            to use. ``featurelist_id`` will assume the default for this project
            if not provided, and ``sample_pct`` will default to using the maximum
            training value allowed for this project's partition setup.
            ``source_project_id`` will be ignored if a
            ``Blueprint`` instance is used for this parameter
        sample_pct : float, optional
            The amount of data to use for training, as a percentage of the project dataset from 0
            to 100.
        featurelist_id : str, optional
            The identifier of the featurelist to use. If not defined, the
            default for this project is used.
        source_project_id : str, optional
            Which project created this blueprint_id. If ``None``, it defaults
            to looking in this project. Note that you must have read
            permissions in this project.
        scoring_type : str, optional
            Either ``SCORING_TYPE.validation`` or
            ``SCORING_TYPE.cross_validation``. ``SCORING_TYPE.validation``
            is available for every partitioning type, and indicates that
            the default model validation should be used for the project.
            If the project uses a form of cross-validation partitioning,
            ``SCORING_TYPE.cross_validation`` can also be used to indicate
            that all of the available training/validation combinations
            should be used to evaluate the model.
        training_row_count : int, optional
            The number of rows to use to train the requested model.
        monotonic_increasing_featurelist_id : str, optional
            (new in version 2.11) the id of the featurelist that defines the set of features with
            a monotonically increasing relationship to the target. Passing ``None`` disables
            increasing monotonicity constraint. Default
            (``dr.enums.MONOTONICITY_FEATURELIST_DEFAULT``) is the one specified by the blueprint.
        monotonic_decreasing_featurelist_id : str, optional
            (new in version 2.11) the id of the featurelist that defines the set of features with
            a monotonically decreasing relationship to the target. Passing ``None`` disables
            decreasing monotonicity constraint. Default
            (``dr.enums.MONOTONICITY_FEATURELIST_DEFAULT``) is the one specified by the blueprint.
        n_clusters: int, optional
            (new in version 2.27) Number of clusters to use in an unsupervised clustering model.
            This parameter is used only for unsupervised clustering models that don't automatically
            determine the number of clusters.

        Returns
        -------
        model_job_id : str
            id of created job, can be used as parameter to ``ModelJob.get``
            method or ``wait_for_async_model_creation`` function

        Examples
        --------
        Use a ``Blueprint`` instance:

        .. code-block:: python

            blueprint = project.get_blueprints()[0]
            model_job_id = project.train(blueprint, training_row_count=project.max_train_rows)

        Use a ``blueprint_id``, which is a string. In the first case, it is
        assumed that the blueprint was created by this project. If you are
        using a blueprint used by another project, you will need to pass the
        id of that other project as well.

        .. code-block:: python

            blueprint_id = 'e1c7fc29ba2e612a72272324b8a842af'
            project.train(blueprint, training_row_count=project.max_train_rows)

            another_project.train(blueprint, source_project_id=project.id)

        You can also easily use this interface to train a new model using the data from
        an existing model:

        .. code-block:: python

            model = project.get_models()[0]
            model_job_id = project.train(model.blueprint.id,
                                         sample_pct=100)

        """
        try:
            return self._train(
                trainable.id,
                featurelist_id=featurelist_id,
                source_project_id=trainable.project_id,
                sample_pct=sample_pct,
                scoring_type=scoring_type,
                training_row_count=training_row_count,
                monotonic_increasing_featurelist_id=monotonic_increasing_featurelist_id,
                monotonic_decreasing_featurelist_id=monotonic_decreasing_featurelist_id,
                n_clusters=n_clusters,
            )
        except AttributeError:
            return self._train(
                trainable,
                featurelist_id=featurelist_id,
                source_project_id=source_project_id,
                sample_pct=sample_pct,
                scoring_type=scoring_type,
                training_row_count=training_row_count,
                monotonic_increasing_featurelist_id=monotonic_increasing_featurelist_id,
                monotonic_decreasing_featurelist_id=monotonic_decreasing_featurelist_id,
                n_clusters=n_clusters,
            )

    def _train(
        self,
        blueprint_id,
        featurelist_id=None,
        source_project_id=None,
        sample_pct=None,
        scoring_type=None,
        training_row_count=None,
        monotonic_increasing_featurelist_id=None,
        monotonic_decreasing_featurelist_id=None,
        n_clusters=None,
    ):
        """
        Submit a modeling job to the queue. Upon success, the new job will
        be added to the end of the queue.

        Parameters
        ----------
        blueprint_id: str
            The id of the model. See ``Project.get_blueprints`` to get the list
            of all available blueprints for a project.
        featurelist_id: str, optional
            The dataset to use in training. If not specified, the default
            dataset for this project is used.
        source_project_id : str, optional
            Which project created this blueprint_id. If ``None``, it defaults
            to looking in this project. Note that you must have read
            permisisons in this project.
        sample_pct: float, optional
            The amount of training data to use.
        scoring_type: string, optional
            Whether to do cross-validation - see ``Project.train`` for further explanation
        training_row_count : int, optional
            The number of rows to use to train the requested model.
        monotonic_increasing_featurelist_id : str, optional
            the id of the featurelist that defines the set of features with
            a monotonically increasing relationship to the target.
        monotonic_decreasing_featurelist_id : str, optional
            the id of the featurelist that defines the set of features with
            a monotonically decreasing relationship to the target.
        n_clusters: int, optional
            Number of clusters used in an unsupervised clustering model. This parameter is used
            only for unsupervised clustering models that don't automatically determine the number
            of clusters.

        Returns
        -------
        model_job_id : str
            id of created job, can be used as parameter to ``ModelJob.get``
            method or ``wait_for_async_model_creation`` function
        """
        url = "{}{}/models/".format(self._path, self.id)
        if sample_pct is not None and training_row_count is not None:
            raise ValueError("sample_pct and training_row_count cannot both be specified")
        # keys with None values get stripped out in self._client.post
        payload = {
            "blueprint_id": blueprint_id,
            "sample_pct": sample_pct,
            "training_row_count": training_row_count,
            "featurelist_id": featurelist_id,
            "scoring_type": scoring_type,
            "source_project_id": source_project_id,
        }
        if monotonic_increasing_featurelist_id is not MONOTONICITY_FEATURELIST_DEFAULT:
            payload["monotonic_increasing_featurelist_id"] = monotonic_increasing_featurelist_id
        if monotonic_decreasing_featurelist_id is not MONOTONICITY_FEATURELIST_DEFAULT:
            payload["monotonic_decreasing_featurelist_id"] = monotonic_decreasing_featurelist_id
        if n_clusters:
            payload["n_clusters"] = n_clusters
        response = self._client.post(
            url,
            data=payload,
            keep_attrs=[
                "monotonic_increasing_featurelist_id",
                "monotonic_decreasing_featurelist_id",
            ],
        )
        return get_id_from_response(response)

    def train_datetime(
        self,
        blueprint_id,
        featurelist_id=None,
        training_row_count=None,
        training_duration=None,
        source_project_id=None,
        monotonic_increasing_featurelist_id=MONOTONICITY_FEATURELIST_DEFAULT,
        monotonic_decreasing_featurelist_id=MONOTONICITY_FEATURELIST_DEFAULT,
        use_project_settings=False,
        sampling_method=None,
    ):
        """Create a new model in a datetime partitioned project

        If the project is not datetime partitioned, an error will occur.

        All durations should be specified with a duration string such as those returned
        by the :meth:`partitioning_methods.construct_duration_string
        <datarobot.helpers.partitioning_methods.construct_duration_string>` helper method.
        Please see :ref:`datetime partitioned project documentation <date_dur_spec>`
        for more information on duration strings.

        Parameters
        ----------
        blueprint_id : str
            the blueprint to use to train the model
        featurelist_id : str, optional
            the featurelist to use to train the model.  If not specified, the project default will
            be used.
        training_row_count : int, optional
            the number of rows of data that should be used to train the model.  If specified,
            neither ``training_duration`` nor ``use_project_settings`` may be specified.
        training_duration : str, optional
            a duration string specifying what time range the data used to train the model should
            span.  If specified, neither ``training_row_count`` nor ``use_project_settings`` may be
            specified.
        sampling_method : str, optional
            (New in version v2.23) defines the way training data is selected. Can be either
            ``random`` or ``latest``.  In combination with ``training_row_count`` defines how rows
            are selected from backtest (``latest`` by default).  When training data is defined using
            time range (``training_duration`` or ``use_project_settings``) this setting changes the
            way ``time_window_sample_pct`` is applied (``random`` by default).  Applicable to OTV
            projects only.
        use_project_settings : bool, optional
            (New in version v2.20) defaults to ``False``. If ``True``, indicates that the custom
            backtest partitioning settings specified by the user will be used to train the model and
            evaluate backtest scores. If specified, neither ``training_row_count`` nor
            ``training_duration`` may be specified.
        source_project_id : str, optional
            the id of the project this blueprint comes from, if not this project.  If left
            unspecified, the blueprint must belong to this project.
        monotonic_increasing_featurelist_id : str, optional
            (New in version v2.18) optional, the id of the featurelist that defines
            the set of features with a monotonically increasing relationship to the target.
            Passing ``None`` disables increasing monotonicity constraint. Default
            (``dr.enums.MONOTONICITY_FEATURELIST_DEFAULT``) is the one specified by the blueprint.
        monotonic_decreasing_featurelist_id : str, optional
            (New in version v2.18) optional, the id of the featurelist that defines
            the set of features with a monotonically decreasing relationship to the target.
            Passing ``None`` disables decreasing monotonicity constraint. Default
            (``dr.enums.MONOTONICITY_FEATURELIST_DEFAULT``) is the one specified by the blueprint.

        Returns
        -------
        job : ModelJob
            the created job to build the model
        """
        url = "{}{}/datetimeModels/".format(self._path, self.id)
        payload = {"blueprint_id": blueprint_id}
        if featurelist_id is not None:
            payload["featurelist_id"] = featurelist_id
        if source_project_id is not None:
            payload["source_project_id"] = source_project_id
        if training_row_count is not None:
            payload["training_row_count"] = training_row_count
        if training_duration is not None:
            payload["training_duration"] = training_duration
        if sampling_method is not None:
            payload["sampling_method"] = sampling_method
        if monotonic_increasing_featurelist_id is not MONOTONICITY_FEATURELIST_DEFAULT:
            payload["monotonic_increasing_featurelist_id"] = monotonic_increasing_featurelist_id
        if monotonic_decreasing_featurelist_id is not MONOTONICITY_FEATURELIST_DEFAULT:
            payload["monotonic_decreasing_featurelist_id"] = monotonic_decreasing_featurelist_id
        if use_project_settings:
            payload["use_project_settings"] = use_project_settings
        response = self._client.post(
            url,
            data=payload,
            keep_attrs=[
                "monotonic_increasing_featurelist_id",
                "monotonic_decreasing_featurelist_id",
            ],
        )
        job_id = get_id_from_response(response)
        return ModelJob.from_id(self.id, job_id)

    def blend(self, model_ids, blender_method):
        """Submit a job for creating blender model. Upon success, the new job will
        be added to the end of the queue.

        Parameters
        ----------
        model_ids : list of str
            List of model ids that will be used to create blender. These models should have
            completed validation stage without errors, and can't be blenders, DataRobot Prime
            or scaleout models.

        blender_method : str
            Chosen blend method, one from ``datarobot.enums.BLENDER_METHOD``. If this is a time
            series project, only methods in ``datarobot.enums.TS_BLENDER_METHOD`` are allowed.

        Returns
        -------
        model_job : ModelJob
            New ``ModelJob`` instance for the blender creation job in queue.

        See Also
        --------
        datarobot.models.Project.check_blendable : to confirm if models can be blended
        """
        url = "{}{}/blenderModels/".format(self._path, self.id)
        payload = {"model_ids": model_ids, "blender_method": blender_method}
        response = self._client.post(url, data=payload)
        job_id = get_id_from_response(response)
        model_job = ModelJob.from_id(self.id, job_id)
        return model_job

    def check_blendable(self, model_ids, blender_method):
        """Check if the specified models can be successfully blended

        Parameters
        ----------
        model_ids : list of str
            List of model ids that will be used to create blender. These models should have
            completed validation stage without errors, and can't be blenders, DataRobot Prime
            or scaleout models.

        blender_method : str
            Chosen blend method, one from ``datarobot.enums.BLENDER_METHOD``. If this is a time
            series project, only methods in ``datarobot.enums.TS_BLENDER_METHOD`` are allowed.

        Returns
        -------
        :class:`EligibilityResult <datarobot.helpers.eligibility_result.EligibilityResult>`
        """
        url = "{}{}/blenderModels/blendCheck/".format(self._path, self.id)
        payload = {"model_ids": model_ids, "blender_method": blender_method}
        response = self._client.post(url, data=payload).json()
        return EligibilityResult(
            response["blendable"],
            reason=response["reason"],
            context="blendability of models {} with method {}".format(model_ids, blender_method),
        )

    def start_prepare_model_for_deployment(self, model_id):
        """Prepare a specific model for deployment.

        The requested model will be trained on the maximum autopilot size then go through the
        recommendation stages. For datetime partitioned projects, this includes the feature impact
        stage, retraining on a reduced feature list, and retraining the best of the reduced
        feature list model and the max autopilot original model on recent data. For non-datetime
        partitioned projects, this includes the feature impact stage, retraining on a reduced
        feature list, retraining the best of the reduced feature list model and the max autopilot
        original model up to the holdout size, then retraining the up-to-the holdout model on the
        full dataset.

        Parameters
        ----------
        model_id : str
            The model to prepare for deployment.
        """
        url = "{}{}/deploymentReadyModels/".format(self._path, self.id)
        payload = {"modelId": model_id}
        self._client.post(url, data=payload)

    def get_all_jobs(self, status=None):
        """Get a list of jobs

        This will give Jobs representing any type of job, including modeling or predict jobs.

        Parameters
        ----------
        status : QUEUE_STATUS enum, optional
            If called with QUEUE_STATUS.INPROGRESS, will return the jobs
            that are currently running.

            If called with QUEUE_STATUS.QUEUE, will return the jobs that
            are waiting to be run.

            If called with QUEUE_STATUS.ERROR, will return the jobs that
            have errored.

            If no value is provided, will return all jobs currently running
            or waiting to be run.

        Returns
        -------
        jobs : list
            Each is an instance of Job
        """
        url = "{}{}/jobs/".format(self._path, self.id)
        params = {"status": status}
        res = self._client.get(url, params=params).json()
        return [Job(item) for item in res["jobs"]]

    def get_blenders(self):
        """Get a list of blender models.

        Returns
        -------
        list of BlenderModel
            list of all blender models in project.
        """
        from . import BlenderModel

        url = "{}{}/blenderModels/".format(self._path, self.id)
        res = self._client.get(url).json()
        return [BlenderModel.from_server_data(model_data) for model_data in res["data"]]

    def get_frozen_models(self):
        """Get a list of frozen models

        Returns
        -------
        list of FrozenModel
            list of all frozen models in project.
        """
        from . import FrozenModel

        url = "{}{}/frozenModels/".format(self._path, self.id)
        res = self._client.get(url).json()
        return [FrozenModel.from_server_data(model_data) for model_data in res["data"]]

    def get_combined_models(self):
        models_response = self._client.get(
            "{}{}/combinedModels/".format(self._path, self.id)
        ).json()
        model_data_list = models_response["data"]
        return [CombinedModel.from_server_data(data) for data in model_data_list]

    def get_segments_models(self, combined_model_id=None):
        """Retrieve a list of all models belonging to the segments/child projects
        of the segmented project.

        Parameters
        ----------
        combined_model_id : str, optional
            Id of the combined model to get segments for. If there is only a single
            combined model it can be retrieved automatically, but this must be
            specified when there are > 1 combined models.
        use_project_id_keys : bool, optional

        Returns
        -------
        segments_models : list(dict)
            A list of dictionaries containing all of the segments/child projects,
            each with a list of their models ordered by metric from best to worst.

        """
        if combined_model_id is None:
            combined_model_list = self.get_combined_models()
            if len(combined_model_list) > 1:
                raise ValueError(
                    "More than 1 combined_model_id was found, please specify the id "
                    "that you wish to use."
                )
            combined_model = combined_model_list[0]
        else:
            combined_model = CombinedModel.get(
                project_id=self.id, combined_model_id=combined_model_id
            )

        segments = combined_model.get_segments_info()
        segments_models = []
        for segment in segments:
            project_id = segment.project_id
            project = Project.get(project_id)
            project_models = project.get_models()

            segments_models.append(
                {
                    "segment": segment.segment,
                    "project_id": project_id,
                    "parent_project_id": self.id,
                    "combined_model_id": combined_model.id,
                    "models": project_models,
                }
            )

        return segments_models

    def get_model_jobs(self, status=None):
        """Get a list of modeling jobs

        Parameters
        ----------
        status : QUEUE_STATUS enum, optional
            If called with QUEUE_STATUS.INPROGRESS, will return the modeling jobs
            that are currently running.

            If called with QUEUE_STATUS.QUEUE, will return the modeling jobs that
            are waiting to be run.

            If called with QUEUE_STATUS.ERROR, will return the modeling jobs that
            have errored.

            If no value is provided, will return all modeling jobs currently running
            or waiting to be run.

        Returns
        -------
        jobs : list
            Each is an instance of ModelJob
        """
        url = "{}{}/modelJobs/".format(self._path, self.id)
        params = {"status": status}
        res = self._client.get(url, params=params).json()
        return [ModelJob(item) for item in res]

    def get_predict_jobs(self, status=None):
        """Get a list of prediction jobs

        Parameters
        ----------
        status : QUEUE_STATUS enum, optional
            If called with QUEUE_STATUS.INPROGRESS, will return the prediction jobs
            that are currently running.

            If called with QUEUE_STATUS.QUEUE, will return the prediction jobs that
            are waiting to be run.

            If called with QUEUE_STATUS.ERROR, will return the prediction jobs that
            have errored.

            If called without a status, will return all prediction jobs currently running
            or waiting to be run.

        Returns
        -------
        jobs : list
            Each is an instance of PredictJob
        """
        url = "{}{}/predictJobs/".format(self._path, self.id)
        params = {"status": status}
        res = self._client.get(url, params=params).json()
        return [PredictJob(item) for item in res]

    def _get_job_status_counts(self):
        jobs = self.get_model_jobs()
        job_counts = collections.Counter(job.status for job in jobs)
        return job_counts[QUEUE_STATUS.INPROGRESS], job_counts[QUEUE_STATUS.QUEUE]

    def wait_for_autopilot(self, check_interval=20.0, timeout=24 * 60 * 60, verbosity=1):
        """
        Blocks until autopilot is finished. This will raise an exception if the autopilot
        mode is changed from AUTOPILOT_MODE.FULL_AUTO.

        It makes API calls to sync the project state with the server and to look at
        which jobs are enqueued.

        Parameters
        ----------
        check_interval : float or int
            The maximum time (in seconds) to wait between checks for whether autopilot is finished
        timeout : float or int or None
            After this long (in seconds), we give up. If None, never timeout.
        verbosity:
            This should be VERBOSITY_LEVEL.SILENT or VERBOSITY_LEVEL.VERBOSE.
            For VERBOSITY_LEVEL.SILENT, nothing will be displayed about progress.
            For VERBOSITY_LEVEL.VERBOSE, the number of jobs in progress or queued is shown.
            Note that new jobs are added to the queue along the way.

        Raises
        ------
        AsyncTimeoutError
            If autopilot does not finished in the amount of time specified
        RuntimeError
            If a condition is detected that indicates that autopilot will not complete
            on its own
        """
        for _, seconds_waited in retry.wait(timeout, maxdelay=check_interval):
            if verbosity > VERBOSITY_LEVEL.SILENT:
                num_inprogress, num_queued = self._get_job_status_counts()
                logger.info(
                    "In progress: {0}, queued: {1} (waited: {2:.0f}s)".format(
                        num_inprogress, num_queued, seconds_waited
                    )
                )
            status = self._autopilot_status_check()
            if status["autopilot_done"]:
                return
        raise errors.AsyncTimeoutError("Autopilot did not finish within timeout period")

    def _autopilot_status_check(self):
        """
        Checks that autopilot is in a state that can run.

        Returns
        -------
        status : dict
            The latest result of calling self.get_status

        Raises
        ------
        RuntimeError
            If any conditions are detected which mean autopilot may not complete on its own
        """
        status = self.get_status()
        if status["stage"] != PROJECT_STAGE.MODELING:
            raise RuntimeError("The target has not been set, there is no autopilot running")
        self.refresh()
        # Project modes are: 0=full, 1=semi, 2=manual, 3=quick, 4=comprehensive
        if self.mode not in {0, 3, 4}:
            raise RuntimeError(
                "Autopilot mode is not full auto, quick or comprehensive, autopilot will not "
                "complete on its own"
            )
        return status

    def rename(self, project_name):
        """Update the name of the project.

        Parameters
        ----------
        project_name : str
            The new name
        """
        self._update(project_name=project_name)

    def set_project_description(self, project_description):
        """Set or Update the project description.

        Parameters
        ----------
        project_description : str
            The new description for this project.
        """
        self._update(project_description=project_description)

    def unlock_holdout(self):
        """Unlock the holdout for this project.

        This will cause subsequent queries of the models of this project to
        contain the metric values for the holdout set, if it exists.

        Take care, as this cannot be undone. Remember that best practice is to
        select a model before analyzing the model performance on the holdout set
        """
        return self._update(holdout_unlocked=True)

    def set_worker_count(self, worker_count):
        """Sets the number of workers allocated to this project.

        Note that this value is limited to the number allowed by your account.
        Lowering the number will not stop currently running jobs, but will
        cause the queue to wait for the appropriate number of jobs to finish
        before attempting to run more jobs.

        Parameters
        ----------
        worker_count : int
            The number of concurrent workers to request from the pool of workers.
            (New in version v2.14) Setting this to -1 will update the number of workers to the
            maximum available to your account.
        """
        return self._update(worker_count=worker_count)

    def get_leaderboard_ui_permalink(self):
        """
        Returns
        -------
        url : str
            Permanent static hyperlink to a project leaderboard.
        """
        return "{}/{}{}/models".format(self._client.domain, self._path, self.id)

    def open_leaderboard_browser(self):
        """
        Opens project leaderboard in web browser.

        Note:
        If text-mode browsers are used, the calling process will block
        until the user exits the browser.
        """

        url = self.get_leaderboard_ui_permalink()
        return webbrowser.open(url)

    def get_rating_table_models(self):
        """Get a list of models with a rating table

        Returns
        -------
        list of RatingTableModel
            list of all models with a rating table in project.
        """
        from . import RatingTableModel

        url = "{}{}/ratingTableModels/".format(self._path, self.id)
        res = self._client.get(url).json()
        return [RatingTableModel.from_server_data(item) for item in res]

    def get_rating_tables(self):
        """Get a list of rating tables

        Returns
        -------
        list of RatingTable
            list of rating tables in project.
        """
        from . import RatingTable

        url = "{}{}/ratingTables/".format(self._path, self.id)
        res = self._client.get(url).json()["data"]
        return [RatingTable.from_server_data(item, should_warn=False) for item in res]

    def get_access_list(self):
        """Retrieve users who have access to this project and their access levels

        .. versionadded:: v2.15

        Returns
        -------
        list of :class:`SharingAccess <datarobot.SharingAccess>`
        """
        url = "{}{}/accessControl/".format(self._path, self.id)
        return [
            SharingAccess.from_server_data(datum) for datum in unpaginate(url, {}, self._client)
        ]

    def share(self, access_list, send_notification=None, include_feature_discovery_entities=None):
        """Modify the ability of users to access this project

        .. versionadded:: v2.15

        Parameters
        ----------
        access_list : list of :class:`SharingAccess <datarobot.SharingAccess>`
            the modifications to make.
        send_notification : boolean, default ``True``
            (New in version v2.21) optional, whether or not an email notification should be sent,
            default to True
        include_feature_discovery_entities : boolean, default ``False``
            (New in version v2.21) optional (default: False), whether or not to share all the
            related entities i.e., datasets for a project with Feature Discovery enabled

        Raises
        ------
        datarobot.ClientError :
            if you do not have permission to share this project, if the user you're sharing with
            doesn't exist, if the same user appears multiple times in the access_list, or if these
            changes would leave the project without an owner

        Examples
        --------
        Transfer access to the project from old_user@datarobot.com to new_user@datarobot.com

        .. code-block:: python

            import datarobot as dr

            new_access = dr.SharingAccess(new_user@datarobot.com,
                                          dr.enums.SHARING_ROLE.OWNER, can_share=True)
            access_list = [dr.SharingAccess(old_user@datarobot.com, None), new_access]

            dr.Project.get('my-project-id').share(access_list)
        """
        payload = {
            "data": [access.collect_payload() for access in access_list],
        }
        if send_notification is not None:
            payload["sendNotification"] = send_notification
        if include_feature_discovery_entities is not None:
            payload["includeFeatureDiscoveryEntities"] = include_feature_discovery_entities
        self._client.patch(
            "{}{}/accessControl/".format(self._path, self.id), data=payload, keep_attrs={"role"}
        )

    def batch_features_type_transform(
        self, parent_names, variable_type, prefix=None, suffix=None, max_wait=600
    ):
        """
        Create new features by transforming the type of existing ones.

        .. versionadded:: v2.17

        .. note::
            The following transformations are only supported in batch mode:

                1. Text to categorical or numeric
                2. Categorical to text or numeric
                3. Numeric to categorical

            See :ref:`here <type_transform_considerations>` for special considerations when casting
            numeric to categorical.
            Date to categorical or numeric transformations are not currently supported for batch
            mode but can be performed individually using :meth:`create_type_transform_feature
            <datarobot.models.Project.create_type_transform_feature>`. Note that ``CATEGORICAL``
            is deprecated in v2.21.


        Parameters
        ----------
        parent_names : list
            The list of variable names to be transformed.
        variable_type : str
            The type new columns should have. Can be one of 'categorical', 'categoricalInt',
            'numeric', and 'text' - supported values can be found in
            ``datarobot.enums.VARIABLE_TYPE_TRANSFORM``.
        prefix : str, optional
            .. note:: Either ``prefix``, ``suffix``, or both must be provided.

            The string that will preface all feature names. At least one of ``prefix`` and
            ``suffix`` must be specified.
        suffix : str, optional
            .. note:: Either ``prefix``, ``suffix``, or both must be provided.

            The string that will be appended at the end to all feature names. At least one of
            ``prefix`` and ``suffix`` must be specified.
        max_wait : int, optional
            The maximum amount of time to wait for DataRobot to finish processing the new column.
            This process can take more time with more data to process. If this operation times
            out, an AsyncTimeoutError will occur. DataRobot continues the processing and the
            new column may successfully be constructed.

        Returns
        -------
        list of Features
            all features for this project after transformation.

        Raises
        ------
        TypeError:
            If `parent_names` is not a list.
        ValueError
            If value of ``variable_type`` is not from ``datarobot.enums.VARIABLE_TYPE_TRANSFORM``.
        AsyncFailureError`
            If any of the responses from the server are unexpected.
        AsyncProcessUnsuccessfulError
            If the job being waited for has failed or has been cancelled.
        AsyncTimeoutError
            If the resource did not resolve in time.
        """
        if not isinstance(parent_names, list) or not len(parent_names):
            raise TypeError("List of existing feature names expected, got {}".format(parent_names))

        if not hasattr(VARIABLE_TYPE_TRANSFORM, underscorize(variable_type).upper()):
            raise ValueError("Unexpected feature type {}".format(variable_type))

        if variable_type == VARIABLE_TYPE_TRANSFORM.CATEGORICAL:
            msg = "Use datarobot.enums.VARIABLE_TYPE_TRANSFORM.CATEGORICAL_INT instead"
            deprecation_warning(
                "CATEGORICAL transform",
                deprecated_since_version="v2.21",
                will_remove_version="v2.22",
                message=msg,
            )

        payload = dict(parentNames=list(parent_names), variableType=variable_type)

        if prefix:
            payload["prefix"] = prefix

        if suffix:
            payload["suffix"] = suffix

        batch_transform_url = "{}{}/batchTypeTransformFeatures/".format(self._path, self.id)

        response = self._client.post(batch_transform_url, json=payload)
        wait_for_async_resolution(self._client, response.headers["Location"], max_wait=max_wait)

        return self.get_features()

    def clone_project(self, new_project_name=None, max_wait=DEFAULT_MAX_WAIT):
        """
        Create a fresh (post-EDA1) copy of this project that is ready for setting
        targets and modeling options.

        Parameters
        ----------
        new_project_name : str, optional
            The desired name of the new project. If omitted, the API will default to
            'Copy of <original project>'
        max_wait : int, optional
            Time in seconds after which project creation is considered
            unsuccessful

        """
        body = {
            "projectId": self.id,
            "projectName": new_project_name,
        }
        result = self._client.post(self._clone_path, data=body)
        async_location = result.headers["Location"]
        return self.__class__.from_async(async_location, max_wait)

    def create_interaction_feature(self, name, features, separator, max_wait=DEFAULT_MAX_WAIT):
        """
        Create a new interaction feature by combining two categorical ones.

        .. versionadded:: v2.21

        Parameters
        ----------
        name : str
            The name of final Interaction Feature
        features : list(str)
            List of two categorical feature names
        separator : str
            The character used to join the two data values, one of these ` + - / | & . _ , `
        max_wait : int, optional
            Time in seconds after which project creation is considered unsuccessful.

        Returns
        -------
        interactionFeature: datarobot.models.InteractionFeature
            The data of the new Interaction feature

        Raises
        ------
        ClientError
            If requested Interaction feature can not be created. Possible reasons for example are:

                * one of `features` either does not exist or is of unsupported type
                * feature with requested `name` already exists
                * invalid separator character submitted.

        AsyncFailureError
            If any of the responses from the server are unexpected
        AsyncProcessUnsuccessfulError
            If the job being waited for has failed or has been cancelled
        AsyncTimeoutError
            If the resource did not resolve in time
        """
        from .feature import InteractionFeature

        if not isinstance(features, list):
            msg = 'List of two existing categorical feature names expected, got "{}"'.format(
                features
            )
            raise TypeError(msg)

        if len(features) != 2:
            msg = "Exactly two categorical feature names required, got {}".format(len(features))
            raise ValueError(msg)

        interaction_url = "{}{}/interactionFeatures/".format(self._path, self.id)
        payload = {"featureName": name, "features": features, "separator": separator}

        response = self._client.post(interaction_url, json=payload)

        feature_location = wait_for_async_resolution(
            self._client, response.headers["Location"], max_wait=max_wait
        )

        return InteractionFeature.from_location(feature_location)

    def get_relationships_configuration(self):
        """
        Get the relationships configuration for a given project

        .. versionadded:: v2.21

        Returns
        -------
        relationships_configuration: RelationshipsConfiguration
            relationships configuration applied to project
        """
        from . import RelationshipsConfiguration

        url = "{}{}/relationshipsConfiguration/".format(self._path, self.id)
        response = self._client.get(url).json()
        return RelationshipsConfiguration.from_server_data(response)

    def download_feature_discovery_dataset(self, file_name, pred_dataset_id=None):
        """Download Feature discovery training or prediction dataset

        Parameters
        ----------
        file_name : str
            File path where dataset will be saved.
        pred_dataset_id : str, optional
            ID of the prediction dataset
        """
        url = "{}{}/featureDiscoveryDatasetDownload/".format(self._path, self.id)
        if pred_dataset_id:
            url = "{}?datasetId={}".format(url, pred_dataset_id)

        response = self._client.get(url, stream=True)
        with open(file_name, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)

    def download_feature_discovery_recipe_sqls(
        self, file_name, model_id=None, max_wait=DEFAULT_MAX_WAIT
    ):
        """Export and download Feature discovery recipe SQL statements
        .. versionadded:: v2.25

        Parameters
        ----------
        file_name : str
            File path where dataset will be saved.
        model_id : str, optional
            ID of the model to export SQL for.
            If specified, QL to generate only features used by the model will be exported.
            If not specified, SQL to generate all features will be exported.
        max_wait : int, optional
            Time in seconds after which export is considered unsuccessful.

        Returns
        -------
        interactionFeature: datarobot.models.InteractionFeature
            The data of the new Interaction feature

        Raises
        ------
        ClientError
            If requested SQL cannot be exported. Possible reason is the feature is not
            available to user.
        AsyncFailureError
            If any of the responses from the server are unexpected.
        AsyncProcessUnsuccessfulError
            If the job being waited for has failed or has been cancelled.
        AsyncTimeoutError
            If the resource did not resolve in time.
        """
        export_url = "{}{}/featureDiscoveryRecipeSqlExports/".format(self._path, self.id)
        payload = {}
        if model_id:
            payload["modelId"] = model_id

        response = self._client.post(export_url, json=payload)

        download_location = wait_for_async_resolution(
            self._client, response.headers["Location"], max_wait=max_wait
        )

        response = self._client.get(download_location, stream=True)
        with open(file_name, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)

    def validate_external_time_series_baseline(
        self, catalog_version_id, target, datetime_partitioning, max_wait=DEFAULT_MAX_WAIT,
    ):
        """
        Validate external baseline prediction catalog.

        The forecast windows settings, validation and holdout duration specified in the
        datetime specification must be consistent with project settings as these parameters
        are used to check whether the specified catalog version id has been validated or not.
        See :ref:`external baseline predictions documentation <external_baseline_predictions>`
        for example usage.

        Parameters
        ----------
        catalog_version_id: str
            Id of the catalog version for validating external baseline predictions.
        target: str
            The name of the target column.
        datetime_partitioning: DatetimePartitioning object
            Instance of the DatetimePartitioning defined in
            ``datarobot.helpers.partitioning_methods``.

            Attributes of the object used to check the validation are:

            * ``datetime_partition_column``
            * ``forecast_window_start``
            * ``forecast_window_end``
            * ``holdout_start_date``
            * ``holdout_end_date``
            * ``backtests``
            * ``multiseries_id_columns``

            If the above attributes are different from the project settings, the catalog version
            will not pass the validation check in the autopilot.
        max_wait: int, optional
            The maximum number of seconds to wait for the catalog version to be validated before
            raising an error.

        Returns
        -------
        external_baseline_validation_info: ExternalBaselineValidationInfo
            Validation result of the specified catalog version.

        Raises
        ------
        AsyncTimeoutError
            Raised if the catalog version validation took more time than specified
            by the ``max_wait`` parameter.
        """
        payload = {
            "catalog_version_id": catalog_version_id,
            "target": target,
            "datetime_partition_column": datetime_partitioning.datetime_partition_column,
            "forecast_window_start": datetime_partitioning.forecast_window_start,
            "forecast_window_end": datetime_partitioning.forecast_window_end,
            "holdout_start_date": datetime_partitioning.holdout_start_date,
            "holdout_end_date": datetime_partitioning.holdout_end_date,
            "backtests": [
                {
                    "validation_start_date": backtest.validation_start_date,
                    "validation_end_date": backtest.validation_end_date,
                }
                for backtest in datetime_partitioning.backtests
            ],
            "multiseries_id_columns": datetime_partitioning.multiseries_id_columns,
        }
        url = "projects/{pid}/externalTimeSeriesBaselineDataValidationJobs/".format(pid=self.id)
        response = self._client.post(url, data=payload)
        result_url = wait_for_async_resolution(
            self._client, response.headers["Location"], max_wait=max_wait
        )
        return ExternalBaselineValidationInfo.from_server_data(self._client.get(result_url).json())

    def download_multicategorical_data_format_errors(self, file_name):
        """Download multicategorical data format errors to the CSV file. If any format errors
        where detected in potentially multicategorical features the resulting file will contain
        at max 10 entries. CSV file content contains feature name, dataset index in which the
        error was detected, row value and type of error detected. In case that there were no
        errors or none of the features where potentially multicategorical the CSV file will be
        empty containing only the header.

        Parameters
        ----------
        file_name : str
            File path where CSV file will be saved.
        """
        url = "{}{}/multicategoricalInvalidFormat/file/".format(self._path, self.id)
        response = self._client.get(url, stream=True)
        with open(file_name, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
