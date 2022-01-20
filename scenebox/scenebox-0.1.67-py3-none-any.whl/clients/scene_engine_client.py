#  Copyright (c) 2020 Caliber Data Labs.
#  All rights reserved.
#
import imghdr
import io
import json
import os
import re
import time
from collections import defaultdict, OrderedDict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple, Type, Union, Callable
from urllib.parse import quote

import requests

from ..clients.job_manager_client import Job, wait_for_jobs
from ..constants import (AUXILIARY_KEY, TIMESTAMP_FIELD,
                         AssetsConstants, COCOAnnotations, ConfigTypes,
                         EntityInfluenceTypes, EntityNames, EntityTypes,
                         JobConstants, MLModelConstants, SessionTypes,
                         SetsAssets, SetTags, ValidExtensions, AuxiliaryDataTypes, Sensors, AnnotationGroups)
from ..custom_exceptions import (AssetError, IndexingException,
                                 InvalidArgumentsError, InvalidAuthorization,
                                 InvalidTimeError, JobError, ResponseError,
                                 SetsError, ThumbnailNotAvailableError, SimilaritySearchError)
from ..models.annotation import (Annotation, BoundingBox,
                                 BoundingBoxAnnotation, Polygon,
                                 PolygonAnnotation)
from ..models.udf import Enricher, Script, Webhook, UDFError, UDF
from ..models.object_access import ObjectAccess
from ..tools.image_utils import get_image_attributes
from ..tools.logger import get_logger
from ..tools.misc import (get_guid, get_md5_from_json_object,
                          hash_string_into_positive_integer_reproducible,
                          parse_file_path, run_threaded, join)
from ..tools.naming import UriParser, get_similarity_index_name, standardize_name
from ..tools.time_utils import (datetime_or_str_to_iso_utc,
                                str_or_datetime_to_datetime,
                                string_to_datetime)
from ..tools.video_utils import get_video_attributes
from ..tools.connections import KVStoreTemplate
from .asset_manager_client import DEFAULT_SEARCH_SIZE, AssetManagerClient

DEFAULT_MAX_ASSETS = 250
VERSION_POSTFIX = "v1"
TIME_INDEX_FIELD = "time_index"

logger = get_logger(__name__)

try:
    import pandas as pd
except ImportError as e:
    logger.warning("Could not import package: {}".format(e))

try:
    import dill as pickle
except ImportError as e:
    logger.warning("Could not import package: {}".format(e))

try:
    from IPython.display import Javascript
except ImportError as e:
    logger.warning("Could not import package: {}".format(e))

try:
    import numpy as np
except ImportError as e:
    logger.warning("Could not import package: {}".format(e))

def no_set_provided_error():
    raise ValueError(
        "No set_id provided and no default set_id exists. Either provide or set with _use_set(<set_id>)")


def no_asset_provided_error():
    raise ValueError(
        "No asset_type provided and no default asset_type exists. Either provide or set with _set_asset_state("
        "<asset_type>, <metadata:only>)")


def invalid_set_asset_error(asset_type):
    raise ValueError(
        "The asset_type {} is not a valid set asset type. Valid set assets are: {}".format(
            asset_type, SetsAssets.VALID_ASSET_TYPES))


class SceneEngineClient(object):
    """Acts as the root client for all user-tasks on SceneBox."""

    def __init__(
            self,
            auth_token: Optional[str] = None,
            scene_engine_url: str = 'https://scene-engine.demo.scenebox.ai/',
            asset_manager_url: Optional[str] = None,
            environment: Optional[str] = None,
            artifacts_path: str = ".",
            kv_store: Optional[KVStoreTemplate] = None
    ):
        """Create a SceneEngineClient object. Used to interact with SceneBox's
           high-level REST APIs.

           Parameters
           ----------
           auth_token:
               Personal token associated with a valid SceneBox account. Find this token
               under user profile on the SceneBox web app.
           scene_engine_url:
               URL for the SceneEngine REST server.
           asset_manager_url:
               URL for the AssetManager associated with the SceneEngine server.
           environment:
               The environment that the client is going to use (dev, demo, etc). It will override
           artifacts_path:
               SceneBox's output directory.
           kv_store:
               key-value store to use in asset-manager-client to cache bytes.
        """

        self.environment = environment or os.environ.get("SCENEBOX_ENV")
        if not self.environment:
            self.scene_engine_url = scene_engine_url
            self._fix_scene_engine_url()
            self.front_end_url = self.scene_engine_url.replace(
                "scene-engine.",
                "").replace(
                VERSION_POSTFIX,
                "") if self.scene_engine_url else None
            self.requests = SceneEngineRequestHandler(
                self.scene_engine_url, auth_token)
            self.asset_manager_url = asset_manager_url or self._get_asset_manager_url()
        else:
            valid_environments = ["dev", "demo", "prod"]
            self.environment = self.environment.lower()
            if self.environment not in valid_environments:
                raise ValueError("{} is not a valid Scenebox environment.".format(self.environment))
            self._set_env_urls(env=self.environment)
            self.requests = SceneEngineRequestHandler(
                self.scene_engine_url, auth_token)
        self.set_id = None
        self.project_id = None

        self.amc_cache = {}

        self.auth_token = auth_token

        self.artifacts_path = artifacts_path

        if kv_store:
            self.kv_store = kv_store
        else:
            self.kv_store = None

    def _fix_scene_engine_url(self):
        """Get SceneEngine URL."""
        if not self.scene_engine_url:
            return
        if self.scene_engine_url.endswith("/{}".format(VERSION_POSTFIX)):
            pass
        elif self.scene_engine_url.endswith("/{}/".format(VERSION_POSTFIX)):
            self.scene_engine_url = self.scene_engine_url[:-1]
        elif self.scene_engine_url.endswith("/"):
            self.scene_engine_url += VERSION_POSTFIX
        else:
            self.scene_engine_url += "/{}".format(VERSION_POSTFIX)

    def _get_asset_manager_url(self) -> str:
        """Obtain the url of asset-manager."""

        resp = self.requests.get("status", remove_version=True)
        resp.raise_for_status()

        version = resp.json().get("asset_manager_url")
        if version is None:
            ValueError("cannot get asset_manager_url")
        return version

    def _set_env_urls(self, env: str):
        ENV_URL_TEMPLATE = "https://{}.{}.scenebox.ai/"
        self.scene_engine_url = ENV_URL_TEMPLATE.format("scene-engine", env) + VERSION_POSTFIX
        self._fix_scene_engine_url()
        self.asset_manager_url = ENV_URL_TEMPLATE.format("asset-manager", env) + VERSION_POSTFIX
        self.front_end_url = ENV_URL_TEMPLATE.replace(
            "{}.", "", 1).format(env)

    def __serialize_class(self, input_class: Type[UDF]):
        '''

        Args:
            input_class: UDF class (if a more general type is needed, one way is to define type as objcet,
            then check if type(input_class)=="type" and hasattr("__module__"), or use typing.Generic or typing.TypeVar
            and define all classes you want to use)

        checks if class module is not "__main__", raise error. see
        https://docs.python.org/3/library/pickle.html#what-can-be-pickled-and-unpickled

        the reason is to avoid pickle.load failure due to this issue
        https://github.com/CaliberDataLabs/scenebox/pull/1753#issue-1101033608
        '''
        if input_class.__module__ != "__main__":
            raise UDFError("pickled objects and UDFs should be defined on a top level")

        pickled_obj = pickle.dumps(input_class)
        return pickled_obj


    def whoami(self)->dict:
        '''
        Get logged-in user authentication details

        Returns
        -------
        dict
            A dictionary with the following keys: "version","build_host""token","username","role","organization"
        '''
        return self.requests.get("auth", remove_version=True).json()

    def with_auth(self,
                  auth_token: Optional[str] = None,
                  ):
        """Save auth_token into SceneEngineClient as an instance attribute. Authorizes the current SceneEngineClient
        object with the auth_token provided in this call or uses the auth_token the client was created with.

        Parameters
        ----------
        auth_token:
            Personal token associated with a valid SceneBox account. Find this token
            under user profile on the SceneBox web app.

        """
        if auth_token:
            self.auth_token = auth_token

        # Need to also call with_auth of AssetManagerClient in order
        # to update the asset cache

        self.requests.with_auth(
            auth_token=auth_token)

        return self

    def get_platform_version(self) -> str:
        """Get version of the SceneBox Client.

        Returns
        -------
        str
            SceneBox version number

        Raises
        ------
        ValueError
            If a valid version cannot be obtained from SceneBox.
        """
        resp = self.requests.get("status", remove_version=True)
        resp.raise_for_status()

        version = resp.json().get("version")
        if version is None:
            ValueError("cannot get version")

        return version

    def update_artifact_path(self, artifacts_path):
        """Updates the SceneEngineClient artifact path.

        Parameters
        ----------
        artifacts_path:
           Path that specifies the location to save output files.

        """
        self.artifacts_path = artifacts_path

    def get_job(self, job_id: str) -> Job:
        """Get the job_manager_client.Job object associated with the provided job ID.

        Can be a currently executing or finished Job.

        Parameters
        ----------
        job_id:
            The job ID associated with the Job of interest.

        Returns
        -------
        Job
            Job object with the job id ``job_id``.

        """
        metadata = self.get_asset_manager(
            AssetsConstants.JOBS_ASSET_ID).get_metadata(id=job_id)

        return Job(
            status=metadata.get("status"),
            id=job_id,
            progress=metadata.get("progress", 0.0),
            description=metadata.get("description"),
            stage=metadata.get("stage")
        )

    def _wait_for_job_completion(self,
                                 job_id: str,
                                 increments_sec: int = 10,
                                 enable_max_wait: bool = False,
                                 max_wait_sec: int = 300,
                                 progress_callback: Optional[Callable] = None
                                 ):
        """Wait for a job to complete.

        Input a max waiting time before an unfinished job throws an Exception.  Choose to either poll while a job is in
        progress, or enact a callable function ``progress_callback()`` with every increment set by ``increments_sec``.

        Parameters
        ----------
        job_id:
            The ID of the job in progress.
        increments_sec:
            The amount of time to poll in between checking job status and calling progress_callback().
        enable_max_wait:
            If True, immediately throws an Exception.  Intended for use when there is an external timing constraint.
            Otherwise, does nothing.
        max_wait_sec:
            The maximum amount of time to wait for a job to finish before throwing an exception.  Measured in seconds.
        progress_callback:
            Callback function to log the progress of the inference job. The callback should accept a parameter of type
            float for progress and str for progress message.

        Raises
        ------
        JobError
            If job encounters an error, and could not complete.
            If job does not finish after ``max_wait_sec`` seconds.

        """
        # progress callable should take progress as an input and do "something" with it

        elapsed_time = 0
        try:
            while not enable_max_wait or elapsed_time < max_wait_sec:
                elapsed_time += increments_sec
                job = self.get_job(job_id=job_id)
                if progress_callback:
                    progress_callback(job.progress, job.stage)
                logger.info(
                    "job_id {:40.40s}|Status:{:12.12s}|Progress:{:6.1f} Elapsed Time: {:5d} sec|Description: {} \r".format(
                        job_id,
                        job.status,
                        job.progress,
                        elapsed_time,
                        job.description))
                if job.status == JobConstants.STATUS_FINISHED:
                    logger.info(150 * "-" + "\r")
                    return
                elif job.status in {JobConstants.STATUS_ABORTED}:
                    job_metadata = self.get_asset_manager(
                        AssetsConstants.JOBS_ASSET_ID).get_metadata(job_id)
                    job_notes = job_metadata['notes']
                    raise JobError(
                        'Job {} encountered error with status {} with notes::: {}'.format(
                            job_id, job.status, job_notes))
                else:
                    time.sleep(increments_sec)
        except KeyboardInterrupt as e:
            resp = self.requests.put(
                "jobs/cancel/{}".format(job_id),
                trailing_slash=False)
            if not resp.ok:
                logger.error("Could not interrupt running job {} because {}".format(job_id,
                                                                                    resp.content))
            else:
                raise JobError("Job {} terminated by user".format(job_id))

        raise JobError(
            "Job {} is not finished after {} seconds".format(
                job_id, max_wait_sec))

    def _wait_for_operation_completion(self,
                                       operation_id: str,
                                       increments_sec: int = 10,
                                       enable_max_wait: bool = False,
                                       max_wait_sec: int = 300):

        """Wait for an operation to complete.

        Input a max waiting time before an unfinished operation throws an Exception.  Choose to either poll while a job is in
        progress, or enact a callable function ``progress_callback()`` with every increment set by ``increments_sec``.

        Parameters
        ----------
        operation_id:
            The ID of the job in progress.
        increments_sec:
            The amount of time to poll in between checking operation status.
        enable_max_wait:
            If True, immediately throws an Exception.  Intended for use when there is an external timing constraint.
            Otherwise, does nothing.
        max_wait_sec:
            The maximum amount of time to wait for a job to finish before throwing an exception.  Measured in seconds.

        Raises
        ------
        JobError
            If operation encounters an error, and could not complete.
            If operation does not finish after ``max_wait_sec`` seconds.

        """

        elapsed_time = 0
        try:
            while not enable_max_wait or elapsed_time < max_wait_sec:
                elapsed_time += increments_sec
                operation_status = self.get_operation_status(operation_id)
                status = operation_status.get("status")
                progress = operation_status.get("progress")
                logger.info(
                    "operation_id {:40.40s}|Status:{:12.12s}|Progress:{:6.1f} Elapsed Time: {:5d} sec\r".format(
                        operation_id, status, progress, elapsed_time))
                if status == JobConstants.STATUS_FINISHED:
                    logger.info(150 * "-" + "\r")
                    return
                elif status in {JobConstants.STATUS_ABORTED}:
                    raise JobError(
                        'Operation {} encountered error'.format(operation_id))
                else:
                    time.sleep(increments_sec)
        except KeyboardInterrupt as e:
            resp = self.requests.delete(
                "operations/control/{}".format(operation_id),
                trailing_slash=False)
            if not resp.ok:
                logger.error("Could not interrupt running operation {} because {}".format(operation_id,
                                                                                    resp.content))
            else:
                raise JobError("Operation {} terminated by user".format(operation_id))


        raise JobError(
            "Operation {} is not finished after {} seconds".format(
                operation_id, max_wait_sec))


    def create_project(
            self,
            name: str,
            description: Optional[str] = None) -> str:

        """Create a project.

            Projects are used to organize and create data workflows.  Once a project is made, users can add sets,
            and apply operations associated with object/embeddings/annotation extraction, and more.

            Parameters
            ----------
            name:
                Name for the created project.
            description:
                A brief description of the project.  Describes project purpose, what operations the project will
                contain, etc.

            Returns
            -------
            str
                The ID of the created project.

            Raises
            ------
            ResponseError
                If the project could not be created.

            """
        options = {
            "name": name,
            "description": description
        }
        resp = self.requests.post(
            "projects/add/",
            trailing_slash=True,
            json=options)
        if not resp.ok:
            raise ResponseError(
                "Could not create the project: {}".format(
                    resp.content))

        id = resp.json()["id"]
        return id

    def delete_project(
            self,
            project_id: str):
        """Delete a project.

            Delete a project.  Deleting a project will not delete any related sets (primary or curated) or annotation
            recipes.

            Parameters
            ----------
            project_id:
                The name of the project to delete.

            Raises
            ------
            ResponseError
                If the project could not be deleted.

            """
        resp = self.requests.delete(
            "projects/meta/{}".format(project_id),
            trailing_slash=False)
        if not resp.ok:
            raise ResponseError(
                "Could not delete the project: {}".format(
                    resp.content))

    def create_operation(self,
                         name: str,
                         operation_type: str,
                         project_id: str,
                         config: dict,
                         stage: int = 0,
                         description: Optional[str] = None) -> str:

        """Create an operation inside a project.

            Operations are the custom workflows that can be created inside projects.  Several operations can be added to
            a single project.  Choose from annotation, dataset similarity search, consensus, object extraction, and
            model inference operation types.

            Parameters
            ----------
            name:
                The name of the operation to be created.
            operation_type:
                The type of the operation to execute.  Must match a constant in
                scenebox.constants.OperationTypes.VALID_TYPES.
            project_id:
                The ID of the project to add the operation to.
            config:
                Configurations for the operation to be added.  If ``operation_type`` is ``"annotation"``, then config
                must contain a dict entry with a key named "annotation_instruction_id" with the value of the relevant
                annotation instruction details.
            stage:
                The stage of the operation to be added.  Represents the order of the operations to be executed inside a
                project.
            description:
                A brief description outlining the purpose of the operation, what the operation will accomplish, etc.

            Returns
            -------
            str
                The ID of the created operation.

            Raises
            ------
            ResponseError:
                If the project could not be created.
            OperationError:
                If the provided operation type is not a valid operation type.

            """
        options = {
            "name": name,
            "type": operation_type,
            "stage": stage,
            "project_id": project_id,
            "config": config,
            "description": description
        }

        resp = self.requests.post(
            "operations/add/",
            trailing_slash=True,
            json=options)
        if not resp.ok:
            raise ResponseError(
                "Could not create the operation: {}".format(
                    resp.content))

        id = resp.json()["id"]
        return id

    def delete_operation(self, operation_id: str):

        """Delete an operation.

        Delete an operation from a project. Deleting an operation will not delete any related sets (primary or
        curated) or annotation recipes used by or generated by the operation.

        Parameters
        ----------
        operation_id:
            The ID of the operation to delete.

        Raises
        ------
        ResponseError
            If the operation could not be deleted.

        """

        resp = self.requests.delete(
            "operations/{}".format(operation_id),
            trailing_slash=False)
        if not resp.ok:
            raise ResponseError(
                "Could not delete the operation: {}".format(
                    resp.content))

    def start_operation(
            self,
            operation_id: str,
            operation_step: Optional[str] = None,
            wait_for_completion: bool = False) -> str:

        """Start an operation.

        Parameters
        ----------
        operation_id:
            The ID of the operation to execute.
        operation_step:
            If the operation is a CVAT or SuperAnnotate operation, chooses whether to send data to the given annotator,
            or receive annotations.  To send data to the annotator, pass ``send_data``.  To receive, input
            ``receive_annotations``.
            Otherwise, has no effect.
        wait_for_completion:
            If True, polls until job is complete.
            Otherwise, continues execution and does not raise an error if the job does not complete.

        Returns
        -------
        str
            The job ID of the Job that starts the operation.
        """
        if operation_step:
            params = {"operation_step": operation_step}
        else:
            params = None

        resp = self.requests.put(
            "operations/control/{}".format(operation_id),
            params=params,
            trailing_slash=False)
        if not resp.ok:
            raise ResponseError(
                "Could not start the operation: {}".format(
                    resp.content))

        job_id = resp.json().get("job_id")

        if wait_for_completion:
            self._wait_for_operation_completion(operation_id)

        return job_id

    def get_operation_status(self, operation_id: str) -> dict:

        """Get the status of an operation.

        Parameters
        ----------
        operation_id:
            The ID of the operation to execute.

        Returns
        -------
        dict
            The full status of the operation.

        """
        resp = self.requests.get("operations/{}/status/".format(operation_id))
        resp.raise_for_status()
        return resp.json()

    def add_sets_to_project(
            self,
            project_id: str,
            sets: List[str],
            stage: int = 0):

        """Add sets to a project.

        Specify sets to add to a project.  To run a given operation (associated with some project) on a set,
        the set must be added to the same project as the desired operation.

        Parameters
        ----------
        project_id:
            The ID of the project to add the given sets to.
        sets:
            List of IDs of sets to add to the project.
        stage:
            The stage associated with the set.  Match this with the stage of the desired operation to run.

        """
        options = {
            "sets": sets,
            "stage": stage,
        }

        resp = self.requests.post(
            "projects/{}/add_sets/".format(project_id),
            trailing_slash=True,
            json=options)
        resp.raise_for_status()

    def remove_sets_from_project(
            self,
            project_id: str,
            sets: List[dict]):
        """Remove sets from a project.

        Parameters
        ----------
        project_id:
            ID of the project to remove sets from.
        sets:
            A list of dictionaries listing sets to be removed.
            Dict format:
                [{"set_id": id_of_the_set_tobe_removed, "stage": "project_stage_for_the_set"}]

        """

        options = {
            "sets": sets,
        }

        resp = self.requests.post(
            "projects/{}/remove_sets/".format(project_id),
            trailing_slash=True,
            json=options)
        resp.raise_for_status()

    def create_set(
            self,
            name: str,
            asset_type: str,
            origin: Optional[str] = None,
            description: Optional[str] = None,
            expected_count: Optional[int] = None,
            tags: Optional[List[str]] = None,
            id: Optional[str] = None,
            aux_metadata: Optional[dict] = None,
            is_primary: bool = False,
            raise_if_set_exists=False
    ) -> str:
        """Create a named dataset.

        Set creation is helpful for performing data operations on several assets at once (e.g. ingesting an
        entire set of images/videos/LIDARs/etc. into SceneBox). Each set can only contain one asset type.
        Can optionally raise a SetsError if a set by the given name already exists.

        Parameters
        ----------
        name:
            The name to give to the set.
        asset_type:
            The type of assets for the set to contain. e.g. images, videos, LIDARs, etc.
        description:
            Human-readable description of the set. Allows other users to read more details about the given set.
        expected_count:
            Estimated count of the number of assets this set is expected to contain.
        tags:
            Labels associated with the set.  Allows for easy set search.
        id:
            Optional unique id for set (needs to be a string)
        aux_metadata:
            Optional dictionary of key and values to be added to sets metadata
        is_primary:
            If true, Gives the set an additional "Primary" tag for easy set sorting.  Otherwise, does nothing.
        raise_if_set_exists:
            Raises a SetsError if the name parameter matches an existing set.

        Returns
        -------
        str
            The name of the successfully created set.

        Raises
        ------
        SetsError
            If raise_if_set_exists is True, then will raise an error if the given set name matches an
            existing set.

        """
        same_name_sets = self.get_asset_manager(
            asset_type=AssetsConstants.SETS_ASSET_ID).search_assets(
            query={
                "filters": [
                    {
                        "field": "name",
                        "values": [name]}]})

        if same_name_sets:
            if raise_if_set_exists:
                raise SetsError("set name {} already exists".format(name))
            else:
                return same_name_sets[0]

        tags = tags or []

        if is_primary:
            tags.append(SetTags.PRIMARY_SET_TAG)

        options = {
            "assets_type": asset_type,
            "name": name,
            "description": description,
            "origin": origin,
            "expected_count": expected_count,
            "tags": tags or []
        }
        if id:
            options["id"] = id
        if aux_metadata:
            options["auxiliary"] = aux_metadata

        resp = self.requests.post(
            "sets/add/",
            trailing_slash=True,
            json=options
        )

        if not resp.ok:
            raise ResponseError(
                "Could not create the set: {}".format(
                    resp.content))

        id = resp.json()["id"]

        if is_primary:
            self.create_config(
                name="{}_dataset".format(name),
                type=ConfigTypes.HEADER_FILTER_GROUP,
                config={
                    "name": "{}_dataset".format(name),
                    "params": [
                        {
                            "key": "sets",
                            "value": name,
                            "type": "text",
                            "text": name,
                            "fuzzy": False,
                            "filter_out": False,
                        }
                    ]
                })
        return id

    def create_annotation_instruction(
            self,
            name: str,
            key: str,
            annotator: str,
            annotation_type: str,
            payload: dict,
            media_type: str = AssetsConstants.IMAGES_ASSET_ID,
            description: Optional[str] = None) -> str:
        """Create an annotation instruction.

        Annotation instructions hold the configurations for annotating assets with external annotators.
        When executing an operation of type "annotation", the relevant annotation instruction card is parsed.

        Parameters
        ----------
        name:
            Name of the annotation instruction to create.
        key:
            Authentication key to send to Scale or SuperAnnotate.
        annotator:
            Name of the annotator to use.  Choose an option from
            scenebox.constants.AnnotationProviders.VALID_PROVIDERS.
        annotation_type:
            Name of the annotation type to use.  Choose an option from
            scenebox.constants.AnnotationTypes.VALID_TYPES.
        payload:
            Configuration for the given annotator.
        media_type:
            Media type to send to the annotator.  Choose an option from
            scenebox.constants.AssetConstants.VALID_TYPES.
        description:
            A brief description of the annotation instruction's purpose, what it aims to
            accomplish, etc.

        Returns
        -------
        str
            The ID of the created annotation instruction.

        Raises
        ------
        ResponseError:
            If the annotation instruction could not be created.

        """
        options = {
            "name": name,
            "key": key,
            "annotator": annotator,
            "type": ConfigTypes.ANNOTATION_INSTRUCTION,
            "annotation_type": annotation_type,
            "config": payload,
            "media_type": media_type,
            "description": description,
        }
        resp = self.requests.post(
            "configs/add/",
            trailing_slash=True,
            json=options)

        if not resp.ok:
            raise ResponseError(
                "Could not create the annotation_instruction: {}".format(
                    resp.content))

        id = resp.json()["id"]
        return id

    def delete_annotation_instruction(self, annotation_instruction_id: str):
        """Delete an existing annotation instruction.

        Parameters
        ----------
        annotation_instruction_id:
            The ID of the annotation instruction to delete.

        Raises
        ------
        ResponseError:
            If the annotation instruction could not be deleted.

        """
        resp = self.requests.delete(
            "configs/meta/{}".format(annotation_instruction_id),
            trailing_slash=False)
        if not resp.ok:
            raise ResponseError(
                "Could not delete the annotation_instruction: {}".format(
                    resp.content))

    def create_config(
            self,
            name: str,
            type: str,
            config: dict,
            description: Optional[str] = None,
            **kwarg) -> str:
        """Create a config.

        Parameters
        ----------
        name:
            Name of the configuration.
        type:
            Type of the config to create.  Choose an option from scenebox.constants.ConfigTypes.VALID_TYPES.
        config:
            Body of the config to create.  Form dependent on the configuration needs.
        description:
            A brief description of the config's purpose, settings, etc. Same as the payload argument for
            ``self.create_annotation_instruction``.
        **kwarg:
            Any other misc. kwargs to save into the config.

        Returns
        -------
        str
            The ID of the created config.

        """
        options = kwarg
        options.update({
            "name": name,
            "type": type,
            "config": config,
            "description": description,
        })
        resp = self.requests.post(
            "configs/add/",
            trailing_slash=True,
            json=options)

        if not resp.ok:
            raise ResponseError(
                "Could not create the config: {}".format(
                    resp.content))

        id = resp.json()["id"]
        return id

    def delete_config(self, config_id: str):
        """Delete a config.

        Parameters
        ----------
        config_id:
            The ID of the config to delete.

        Raises
        ------
        ResponseError:
            If the config could not be deleted.

        """

        resp = self.requests.delete(
            "configs/meta/{}".format(config_id),
            trailing_slash=False)
        if not resp.ok:
            raise ResponseError(
                "Could not delete the config_id: {}".format(
                    resp.content))

    def get_config(self, config_id: str, complete_info=False) -> dict:
        """Get config metadata.

        Parameters
        ----------
        config_id:
            The ID of the config to receive the metadata of.
        complete_info:
            If True, returns the the entire metadata of the config
            (with the config parameters contained inside).  Otherwise,
            only returns the config parameters.

        Returns
        -------
        dict
            The metadata and/or parameters of the desired config.

        Raises
        ------
        ResponseError:
            If the config metadata could not be obtained.
        """
        resp = self.requests.get(
            "configs/meta/{}".format(config_id),
            trailing_slash=False)
        if not resp.ok:
            raise ResponseError(
                "Could not get the config metadata: {}".format(
                    resp.content))

        if complete_info:
            return resp.json()
        else:
            return resp.json().get("config", {})

    def set_lock(self, set_id: str) -> bool:
        """Lock a set.

        Locks a set from changes. Useful for protecting a set (i.e. marks a set as "in use")
        when performing a data operation on a set's assets.

        Parameters
        ----------
        set_id:
            The ID of the set to lock.

        Returns
        -------
        bool
            Always returns True.

        Raises
        ------
        HTTPError:
            If a server or client error occurs.

        """

        resp = self.requests.put("sets/{}/lock".format(set_id))
        resp.raise_for_status()

        return True

    def set_unlock(self, set_id: str) -> bool:
        """Unlocks a set.

        Releases a set from protection/external changes.

        Parameters
        ----------
        set_id:
            The ID of the set to unlock.

        Returns
        -------
        bool
            Always returns True.

        Raises
        ------
        HTTPError:
            If a server or client error occurs.

        """
        resp = self.requests.delete("sets/{}/lock".format(set_id))
        resp.raise_for_status()

        return True

    def set_is_locked(self, set_id: str) -> bool:
        """Check the lock status of a set.

        Parameters
        ----------
        set_id:
            The ID of the set to check the lock status of.

        Returns
        -------
        bool
            Returns True if the set is locked.
            Otherwise, returns False if the set is not locked.

        Raises
        ------
        HTTPError:
            If a server or client error occurs.

        """
        resp = self.requests.get("sets/{}/lock".format(set_id))
        resp.raise_for_status()

        return resp.json().get("locked")

    def delete_set(
            self,
            set_id: str = None,
            wait_for_completion: bool = False) -> str:

        """Delete a set.

        Parameters
        ----------
        set_id:
            The ID of the set to delete.
        wait_for_completion:
            If True, polls until job is complete.
            Otherwise, continues execution and does not raise an error if the job does not complete.

        Returns
        -------
        str
            The ID of the Job that attempts to delete the set.

        """
        if not set_id and not self.set_id:
            no_set_provided_error()
        set_id = set_id or self.set_id
        resp = self.requests.delete("sets/{}".format(set_id))
        resp.raise_for_status()
        if wait_for_completion:
            job_id = resp.json()["job_id"]
            self._wait_for_job_completion(job_id)
        return resp.json().get("job_id")

    def get_set_status(self, set_id: str = None) -> dict:
        """Get the status of a set.

        Parameters
        ----------
        set_id:
            The ID of the set to get the status of.

        Returns
        -------
        dict
            The full status of the desired set.

        Raises
        ------
        HTTPError:
            If a server or client error occurs.

        """
        if not set_id and not self.set_id:
            no_set_provided_error()
        resp = self.requests.get("sets/{}/status/".format(set_id))
        resp.raise_for_status()
        return resp.json()

    def add_assets_to_set(
            self,
            search: Optional[dict] = None,
            ids: Optional[list] = None,
            set_id: Optional[str] = None,
            limit: Optional[int] = None,
            wait_for_availability: bool = True,
            timeout: int = 30,
            wait_for_completion: bool = False,
    ) -> str:
        """Add assets to a set.

        Add assets to a set either with a search query, or by IDs.  Utilize only one of

        Parameters
        ----------
        search:
            Query to locate the data subset of interest.  Filters through existing
            assets according to the dictionary passed.
        ids:
            IDs of the assets to add to the given set.
        set_id:
            The ID of the set to add assets to.
        limit:
            The limit of the number of additions.  If the limit is reached,
            randomly down-sample the list of assets to add.
        wait_for_availability:
            If True and the specified set is locked, waits until ``timeout`` for the set
            to unlock.  Otherwise, if False, raises a SetsError if the set is locked.
        timeout:
            If ``wait_for_availability`` is True, represents the maximum amount of time
            for a set to unlock.  Otherwise, has no effect.
        wait_for_completion:
            If True, polls until job is complete.
            Otherwise, continues execution and does not raise an error if the job does not complete.

        Returns
        -------
        str
            ID of the Job that runs/ran the add assets job.

        Raises
        ------
        SetsError
            If ``wait_for_availability`` is False, and the specified set is locked.
            If neither ``ids`` or ``search`` are passed.
        TimeoutError
            If ``wait_for_availability`` is True, and timeout is reached before the desired
            set is unlocked.
        ResponseError
            If assets could not be added to the desired set.
        """
        if not set_id and not self.set_id:
            no_set_provided_error()

        set_id = set_id or self.set_id
        if not set_id:
            raise ValueError("No default set available")

        if search is None and ids is None:
            raise ValueError(
                "Either a search query or a list of ids must be provided")

        if self.set_is_locked(set_id):
            if wait_for_availability:
                t_start = time.time()
                while True:
                    time.sleep(1)
                    if time.time() - t_start > timeout:
                        raise TimeoutError(
                            "Timeout waiting for set {} to unlock".format(set_id))
                    if not self.set_is_locked(set_id):
                        logger.info(
                            "Set {} is locked, waiting 1s to add assets".format(set_id))
                        break
            else:
                raise SetsError("Set {} is locked".format(set_id))

        if search is not None:
            if limit:
                params = {"limit": limit}
            else:
                params = None
            resp = self.requests.post(
                "sets/{}/add_assets_query/".format(set_id),
                trailing_slash=True,
                json=search,
                params=params)
        elif ids is not None:
            assets_payload = {"asset_list": ids}
            resp = self.requests.post(
                "sets/{}/add_assets_list/".format(set_id),
                trailing_slash=True,
                json=assets_payload)
        else:
            raise SetsError(
                "Either ids or search should be specified for sets addition")

        if not resp.ok:
            raise ResponseError(
                "Could not add assets to set: {}, {}".format(
                    resp.content, resp.reason))

        if wait_for_completion:
            job_id = resp.json()["job_id"]
            self._wait_for_job_completion(job_id)

        return resp.json().get("job_id")

    def remove_assets_from_set(
            self,
            search: Optional[dict] = None,
            ids: Optional[list] = None,
            set_id: Optional[str] = None,
            wait_for_availability: bool = True,
            timeout: int = 30,
            wait_for_completion: bool = False,
    ) -> str:
        """Remove assets from a set either by query or by IDs.

        Parameters
        ----------
        search:
            Query to locate the data subset of interest.  Filters through existing
            assets according to the dictionary passed.
        ids:
            IDs of the assets to add to the given set.
        set_id:
            The ID of the set to add assets to.
        wait_for_availability:
          If True and the specified set is locked, waits until ``timeout`` for the set
          to unlock.  Otherwise, if False, raises a SetsError if the set is locked.
        timeout:
            If ``wait_for_availability`` is True, represents the maximum amount of time
            for a set to unlock.  Otherwise, has no effect.
        wait_for_completion:
            If True, polls until job is complete.
            Otherwise, continues execution and does not raise an error if the job does not complete.

        Returns
        -------
        str
            The ID of the job that runs/ran the Job to remove assets from a set.
        """
        if not set_id and not self.set_id:
            no_set_provided_error()

        set_id = set_id or self.set_id
        if not set_id:
            raise ValueError("No default set available")

        if search is None and ids is None:
            raise ValueError(
                "Either a search query or a list of ids must be provided")

        if self.set_is_locked(set_id):
            if wait_for_availability:
                t_start = time.time()
                while True:
                    time.sleep(1)
                    if time.time() - t_start > timeout:
                        raise TimeoutError(
                            "Timeout waiting for set {} to unlock".format(set_id))
                    if not self.set_is_locked(set_id):
                        logger.info(
                            "Set {} is locked, waiting 1s to remove assets".format(set_id))
                        break
            else:
                raise SetsError("Set {} is locked".format(set_id))

        if search:
            resp = self.requests.post(
                "sets/{}/remove_assets_query/".format(set_id),
                trailing_slash=True,
                json=search)
        else:
            assets_payload = {"asset_list": ids}
            resp = self.requests.post(
                "sets/{}/remove_assets_list/".format(set_id),
                trailing_slash=True,
                json=assets_payload)

        if not resp.ok:
            raise ResponseError(
                "Could not remove assets from set: {}, {}".format(
                    resp.content, resp.reason))

        if wait_for_completion:
            job_id = resp.json()["job_id"]
            self._wait_for_job_completion(job_id)

        return resp.json().get("job_id")

    def assets_in_set(self, set_id: Optional[str] = None) -> List[str]:
        """List assets within a set.

        Parameters
        ----------
        set_id:
            The ID of the set to list assets from.

        Returns
        -------
        List[str]
            A list of the IDs of the assets contained in the specified set.
        """
        return self.search_within_set(set_id=set_id, show_meta=False)

    def search_within_set(
            self,
            search: Optional[dict] = None,
            set_id: Optional[str] = None,
            show_meta: bool = True) -> List:
        """Search for assets within a set.

        Parameters
        ----------
        search:
            Search query to send to the endpoint.  Filters through existing
            sets according to the dictionary passed.
        set_id:
            The ID of the set to search.
        show_meta:
            If True, returns the metadata of each asset in the set.
            Otherwise, simply lists the IDs of each asset in the set.

        Returns
        -------
        List
            Contains asset IDs and/or metadata for the assets in the given set.

        Raises
        ------
        ResponseError
            If the search could not be performed.
        """
        search = search or {}
        if not set_id and not self.set_id:
            no_set_provided_error()

        set_id = set_id or self.set_id
        if show_meta:
            resp = self.requests.post(
                "sets/{}/list_assets_meta/".format(set_id),
                trailing_slash=True,
                json=search)
        else:
            resp = self.requests.post(
                "sets/{}/list_assets/".format(set_id),
                trailing_slash=True,
                json=search)

        if not resp.ok:
            raise ResponseError(
                "Could not perform the search: {}".format(
                    resp.content))

        return resp.json()["results"]

    def zip_set(self, set_id: Optional[str] = None) -> (str, str):
        """Create a zipfile of a set.

        Parameters
        ----------
        set_id:
            The ID of the set to zip.

        Returns
        -------
        (str, str)
             The ID of the job that zipped the set,
             The zipfile ID of the zipped set).

        Raises
        -----
        ValueError
            If no set ID is provided.

        """
        if not set_id and not self.set_id:
            no_set_provided_error()
        set_id = set_id or self.set_id
        resp = self.requests.post(
            "sets/{}/zip_all_assets/".format(set_id),
            trailing_slash=True)
        resp.raise_for_status()
        return resp.json().get("job_id"), resp.json().get("zip_id")

    def compare_sets(self,
                     sets: List[str],
                     index_name: str,
                     metric_type: Optional[str] = None,
                     metric_params: Optional[Dict] = None,
                     wait_for_completion: bool = True
                     ) -> str:
        """Compare sets based on a given metric_type in an embedding space with given index_name.

        Parameters
        ----------
        sets:
            The IDs of the sets to compare with each other.

        index_name:
            The name of the embedding space.

        metric_type:
            The metric type that the comparison is based on; if not given, default value is wasserstein.

        metric_params:
            key-values of any parameters that are needed to calculate the metric;
            if not given, default values for num_projections and num_seeds are 25 and 50, respectively,
            for wasserstein distance calculation.

        wait_for_completion:
            If True, polls until job is complete.
            Otherwise, continues execution and does not raise an error if the job does not complete.

        Returns
        -------
        str
             The ID of the job that compared sets.

        Raises
        -----
        ValueError
            If sets is empty or contains only one set id.
            If index_name is not provided.

        """
        payload = {
            "sets": sets,
            "index_name": index_name
        }

        if metric_type:
            payload.update(
                {
                    "metric_type": metric_type
                }
            )
        if metric_params:
            payload.update(
                {
                    "metric_params": metric_params
                }
            )
        resp = self.requests.post(
            "sets_comparisons/compare_sets/",
            trailing_slash=True,
            json=payload)

        if not resp.ok:
            raise ResponseError(
                "{} ::: {} with token::: {}".format(
                    resp.reason, resp.content, self.auth_token))

        job_id = resp.json().get("job_id")

        if wait_for_completion:
            self._wait_for_job_completion(job_id)

        return job_id

    def get_comparison_matrix(self,
                              search: Optional[dict] = None,
                              index_name: Optional[str] = None,
                              ) -> List[dict]:
        """Gets the comparison matrix of an index.

        Parameters
        ----------
        search:
            Query to locate the data subset of interest.  Filters through existing
            assets according to the dictionary passed.
        index_name:
            index_name of the embeddings of interest.

        Returns
        -------
        List[dict]
            The requested comparison matrix.
        """
        payload = {
            "search": search,
            "index_name": index_name
        }

        resp = self.requests.post(
            "sets_comparisons/comparison_matrix/",
            trailing_slash=True,
            json=payload)

        if not resp.ok:
            raise ResponseError(
                "{} ::: {} with token::: {}".format(
                    resp.reason, resp.content, self.auth_token))

        return resp.json()

    def download_zipfile(self,
                         zip_id: str,
                         output_filename: Optional[str] = None) -> Union[str,
                                                                         io.BytesIO]:
        """Download a zipfile into either a bytesIO object or a file.

        Parameters
        ----------
        zip_id:
            The ID of the zipfile to download.
        output_filename:
            The filename to give the downloaded zipfile.

        Returns
        -------
        Union[str, io.BytesIO]
            If output_filename is provided, returns the path where the zipfile was locally saved as str.
            Otherwise, the zipfile is returned directly as a  io.BytesIO object.

        """
        data_bytes = self.get_asset_manager(
            asset_type=AssetsConstants.ZIPFILES_ASSET_ID).get_bytes(
            id=zip_id)
        if output_filename:
            if not output_filename.endswith(".zip"):
                output_filename += ".zip"
            fpath = os.path.join(self.artifacts_path, output_filename)
            with open(fpath, "wb") as f:
                f.write(data_bytes)
            return fpath
        else:
            bytes_file = io.BytesIO(data_bytes)
            return bytes_file

    def download_timeseries(self,
                            search_dic: Optional[Dict] = None,
                            fields: Optional[List[str]] = None) -> dict:
        """Download the timeseries using a search query.

        Parameters
        ----------
        search_dic:
            Query to locate the data subset of interest.  Filters through existing
            assets according to the dictionary passed.
        fields:
            Field names of fields to return from each session.

        Returns
        -------
        dict
            Mapping between session uids, and the returned timeseries data.
        """
        timeseries_data = defaultdict(list)
        json_payload = search_dic or {}
        resp = self.requests.post(
            "session_manager/search/",
            json=json_payload,
            trailing_slash=True)

        if not resp.ok:
            raise ResponseError(
                "{} ::: {} with token::: {}".format(
                    resp.reason, resp.content, self.auth_token))
        if fields and TIMESTAMP_FIELD not in fields:
            fields.append(TIMESTAMP_FIELD)
        session_interval_map = resp.json()
        for session_uid, v in session_interval_map.items():
            session_timeseries_data = {}
            intervals = v.get("intervals", [])
            for interval in intervals:
                session_timeseries_data["start_time"] = interval[0]
                session_timeseries_data["end_time"] = interval[1]
                search_dic["time_range"] = {
                    "start_time": interval[0],
                    "end_time": interval[1]
                }
                field_data = self.get_field_data(session_uid=session_uid,
                                                 search_dic=search_dic,
                                                 fields=fields)

                for field, data in field_data.items():
                    if field != TIME_INDEX_FIELD:
                        session_timeseries_data[field] = data
                timeseries_data[session_uid].append(session_timeseries_data)
        return dict(timeseries_data)

    def zip_set_and_download(self,
                             set_id: Optional[str] = None,
                             filename: Optional[str] = None) -> Union[str,
                                                                      io.BytesIO]:

        """Zip and download an existing set.

        The downloaded zip file contains several subfolders/files encapsulating the logged data on SceneBox.
        More specifically, this includes the following:
        -  Asset files with their original extension (images/videos/LIDARs, etc.)
        -  Asset metadata in .json format
        -  Annotation data in .json format (if available)

        Parameters
        ----------
        set_id:
            Set name of the set to zip and download
        filename:
            Name of the downloaded zip folder

        Returns
        -------
        Union[str, io.BytesIO]
            If filename is provided, returns the path where the zipfile was locally saved as str.
            Otherwise, the zipfile is returned directly as a  io.BytesIO object.

        Raises
        ------
        ValueError
            If no set_id is provided.
        """
        job_id, zip_id = self.zip_set(set_id)
        self._wait_for_job_completion(job_id)
        return self.download_zipfile(zip_id, output_filename=filename)

    def get_asset_manager(
            self,
            asset_type: str
    ) -> AssetManagerClient:
        """Set asset_manager state.

        Set the asset_manager state to access particular assets. This is often used in chaining:
        Eg. client.with_asset_state("images", True).search_files({})

        Parameters
        ----------
        asset_type:
            Desired AssetManagerClient asset type.

        Returns
        -------
        AssetManagerClient
            The AssetManagerClient associated with the specified asset.

        """
        key = asset_type + (self.auth_token or "")
        if key not in self.amc_cache:
            self.amc_cache[key] = AssetManagerClient(
                asset_type=asset_type,
                asset_manager_url=self.asset_manager_url,
                auth_token=self.auth_token,
                kv_store=self.kv_store
            )
        return self.amc_cache[key]

    def register_rosbag_session(
            self,
            session_name: str,
            session_directory_path: Optional[str] = None,
            rosbag_ids: Optional[List[str]] = None,
            config_name: Optional[str] = None,
            wait_for_completion: bool = True,
    ) -> Tuple[str, str]:
        """Register a rosbag session with the SceneEngine.

        Parameters
        ----------
        session_name:
            Name of the session.
        session_directory_path:
            Local path (on ros-extractor) to a session directory.
        rosbag_ids:
            List of rosbag IDs belonging to the session.
        config_name:
            Name of the session configuration file.
        wait_for_completion:
            If True, polls until job is complete.
            Otherwise, continues execution and does not raise an error if the job does not complete.

        Returns
        -------
        Tuple[str, str]
            the Job ID that carried out the indexing job, and the session UID of the created session.
        """
        if session_directory_path is None and rosbag_ids is None:
            # Insufficient arguments provided
            raise ValueError(
                "Must provide either session_directory_path or rosbag_ids")

        json_payload = {
            'session_name': session_name,
            'session_directory_path': session_directory_path,
            'source_data': rosbag_ids,
            'session_configuration': config_name,
        }

        resp = self.requests.post(
            "indexing/register_rosbag_session/",
            trailing_slash=True,
            json=json_payload)

        job_id = resp.json()["job_id"]

        if wait_for_completion:
            self._wait_for_job_completion(job_id)

        session_uid = resp.json()["session_uid"]

        return job_id, session_uid

    def get_session_resolution_status(self, session_uid: str) -> str:
        """Get the status of the session resolution task (if it exists).

        Parameters
        ----------
        session_uid:
            The session uid to get the session resolution status of.

        Returns
        -------
        str
            The session resolution status.
        """
        resp = self.requests.get(
            "session_manager/resolution_status/{}".format(session_uid),
            trailing_slash=False
        )
        return resp.json()['status']

    def _submit_rosbag_indexing_request(
            self,
            session_uid: str,
            session_directory_path: Optional[str] = None,
            rosbag_ids: Optional[List[str]] = None,
            config_name: Optional[str] = None,
            extraction_sensors: Optional[List[dict]] = None,
            extraction_types: Optional[List[dict]] = None,
            extraction_settings: Optional[dict] = None,
            enrichments: Optional[List[dict]] = None,
            re_resolve: bool = False,
    ) -> dict:
        """Submit indexing requests to the scene-engine.

        Index the rosbag session directory, extracting media-content and metadata and sending to the SceneEngine.

        Parameters
        ----------
        session_uid:
            UID of the session.
        session_directory_path:
            Local path (on ros-extractor) to a session directory.
        rosbag_ids:
            List of rosbag IDs belonging to the session.
        config_name:
            Name of the session configuration file
        extraction_sensors:
            List of sensor extractions of the following form:
            {
                "sensor_name": <sensor name>,
                "extraction_settings": <dict of extraction settings>,
                "extraction_types": <list of applicable extraction types>
            }
        extraction_types:
            List of type extractions of form:
            {
                "extraction_type": <Type of extraction>,
                "extraction_settings": <Extraction settings for this type>
            }
        extraction_settings:
            Fallback extraction settings.
        enrichments:
            The types of enrichments to add to the session.
        re_resolve:
            Re-resolve the session.

        Returns
        -------
        dict

        """
        if session_directory_path is None and rosbag_ids is None:
            # Insufficient arguments provided
            raise ValueError(
                "Must provide either session_directory_path or rosbag_ids")

        if extraction_types is None and extraction_sensors is None:
            raise ValueError(
                "Must provide one of extraction_types or extraction_sensors")

        json_payload = {
            'session_uid': session_uid,
            'session_directory_path': session_directory_path,
            'source_data': rosbag_ids,
            'session_configuration': config_name,
            'extraction_config': {
                'extraction_sensors': extraction_sensors or [],
                'extraction_types': extraction_types or [],
                'extraction_settings': extraction_settings or {},
            },
            'enrichments': enrichments or [],
            're_resolve': re_resolve
        }

        return self.requests.post(
            "indexing/index_rosbag_session/",
            trailing_slash=True,
            json=json_payload)

    def submit_video_indexing_request(
            self,
            session_name: str,
            video_session_data: Optional[dict] = None,
            video_filenames: Optional[List[str]] = None,
            raw_videos: Optional[dict] = None,
            session_formatting_strategy: Optional[str] = None,
            extraction_config: Optional[dict] = None,
            wait_for_completion: bool = True,
            retry: Optional[bool] = False,
            enrichments: Optional[List[dict]] = None,
            session_uid: Optional[str] = None

    ) -> dict:
        """Index a video session.

        Index the video session directory, extracting media-content and metadata and sending to the SceneEngine.

        Parameters
        ----------
        session_name:
            Name of the session to index.
        video_session_data:
            Video assets to include within the session.
            Expected to be of the following form:
            {
                'filename': TEST_SESSION_NAME,
                'metadata': {
                    'timestamp': '2020-08-01T12:46:15.700000+00:00'
                },
                'asset_ids': [<asset_id>, ...]
            }
        video_filenames:
            Video filenames to send to index.
        raw_videos:
            Mapping between video filenames and desired asset_ids
        session_formatting_strategy:
            Formatting strategy to use for the given data.
        extraction_config:
            Extraction settings for the video data.
        wait_for_completion:
        retry:
        enrichments:
            The types of enrichments to add to the video.
        session_uid:
            The session uid of the session to index.

        Returns
        -------
        dict
            A dictionary containing the job ID of the Job that carried out the video indexing request,
            and the session UID of the session that was indexed.
        """
        resp = self.requests.post(
            "indexing/index_video_session/",
            trailing_slash=True,
            json={
                'session_name': session_name,
                'video_session_data': video_session_data or [],
                'raw_videos': raw_videos or {},
                'extraction_config': extraction_config or {},
                'video_filenames': video_filenames,
                'session_formatting_strategy': session_formatting_strategy,
                'retry': retry,
                'enrichments': enrichments,
                'session_uid': session_uid,
            }
        )

        if not resp.ok:
            raise IndexingException(
                "Failed to index video session: {} -- {}".format(resp.reason, resp.content))

        if wait_for_completion:
            job_ids = [resp.json()["job_id"]]
            successful_jobs = 0
            failed_jobs = 0

            t1 = time.time()
            job_info = wait_for_jobs(
                job_ids=job_ids,
                asset_manager_url=self.asset_manager_url,
                auth_token=self.auth_token,
                timeout=None,
                raise_on_error=True)
            logger.info(
                "JOBS finished in {} seconds".format(
                    round(time.time() - t1), 2))
            successful_jobs += job_info['successful']
            failed_jobs += job_info['failed']

        return resp.json()

    def get_searchable_field_statistics(self, asset_type: str) -> dict:
        """Get the metadata searchable field statistics for a certain asset type.

        Parameters
        ----------
        asset_type:
            The asset type to receive the searchable field statistics of.

        Returns
        -------
        dict
            Dictionary with keys of the searchable statistics, and values of the
            min/max/count/defaults for that statistic.

        """
        return self.requests.get(
            route=join(
                asset_type,
                'meta',
                'searchable_field_statistics'),
            trailing_slash=True).json()

    def get_metadata(
            self,
            id: str,
            asset_type: str,
            with_session_metadata: bool = False) -> dict:
        """Get the metadata of an asset.

        Parameters
        ----------
        id:
            The ID of the asset to get metadata from.
        asset_type:
            The asset type of the asset to get metadata from.
        with_session_metadata:
            If True and the asset belongs to a session, also return session entities

        Returns
        -------
        dict
            The asset metadata.

        """
        if with_session_metadata is False:
            return self.get_asset_manager(
                asset_type=asset_type).get_metadata(id)
        else:
            resp = self.requests.get(
                route=join(
                    asset_type,
                    'meta',
                    id),
                trailing_slash=False,
                params={'with_session_metadata': True}
            )
            if not resp.ok:
                raise ResponseError(
                    "{} ::: {} with token::: {}".format(
                        resp.reason, resp.content, self.auth_token))
            return resp.json()

    def compress_images(self,
                        ids: List[str],
                        desired_shape: Optional[Tuple[int,
                                                      ...]] = None,
                        thumbnail_tag: Optional[str] = None,
                        use_preset: Optional[str] = None) -> Optional[str]:
        """Compress a list of images.

        Either specify desired_shape or use_preset to compress an image.

        Parameters
        ----------
        ids:
            The IDs of the images to compress.
        desired_shape:
            Specifies the desired output shape. Not used when use_preset is set.
        thumbnail_tag:
            Tag of the thumbnail to be created. Not used when use_preset is set.
        use_preset:
            Use a preset configuration for desired_shape & thumbnail tag.
            Must be included inside the config.

        Returns
        -------
        str
            The ID of the job that carries out the image compression.

        """
        resp = self.requests.post(
            "images/compress_images/",
            trailing_slash=True,
            json={
                "ids": ids,
                "desired_shape": desired_shape,  # h x w x ..
                "thumbnail_tag": thumbnail_tag,
                "use_preset": use_preset,
            }
        )

        job_id = resp.json().get("job_id")

        return job_id

    def compress_videos(self,
                        ids: List[str],
                        desired_shape: Optional[Tuple[int,
                                                      ...]] = None,
                        thumbnail_tag: Optional[str] = None,
                        use_preset: Optional[str] = None,
                        job_id: Optional[str] = None
                        ) -> dict:
        """Compress a list of videos.

            Either specify desired_shape or use_preset to compress a video.

            Parameters
            ----------
            ids:
                The IDs of the videos to compress.
            desired_shape:
                Specifies the desired output shape. Not used when use_preset is set.
            thumbnail_tag:
                Tag of the thumbnail to be created. Not used when use_preset is set.
            use_preset:
                Use a preset configuration for desired_shape & thumbnail tag.
                Must be included inside the config.

            Returns
            -------
            dict
                The full response of the job that carries out the video compression.

        """
        resp = self.requests.post(
            "videos/compress_videos/",
            trailing_slash=True,
            json={
                "ids": ids,
                "desired_shape": desired_shape,  # h x w x ..
                "thumbnail_tag": thumbnail_tag,
                "use_preset": use_preset,
                "job_id": job_id
            }
        )

        return resp.json()

    def compress_lidars(self,
                        ids: List[str],
                        skip_factors: Optional[List[int]] = None
                        ) -> dict:
        """Compress a list of videos.

        Either specify desired_shape or use_preset to compress a lidar.

        Parameters
        ----------
        ids:
            The IDs of the LIDARs to compress.
        skip_factors:
            Determines how many LIDAR points to skip.  Each point listed creates a new thumbnail.
            Defaults to [1, 10, 100].

        Returns
        -------
        dict
            The job ID of the Job that carries out the LIDAR compression.

        """
        skip_factors = skip_factors or [1, 10, 100]
        resp = self.requests.post(
            "lidars/compress_lidars/",
            trailing_slash=True,
            json={
                "ids": ids,
                "skip_factors": skip_factors
            }
        )

        return resp.json()

    def concatenate_videos(
            self,
            ids: List[str],
            output_video_id: str,
            video_metadata: dict,
            job_id: Optional[str] = None) -> dict:
        """Concatenate a list of videos into a single video.

        Parameters
        ----------
        ids:
            The IDs of the videos to concatenate.
        output_video_id:
            The ID of the concatenated video produced.
        video_metadata:
            Metadata of the concatenated video produced.
        job_id:
            If provided, creates a job with the given job_id.  Otherwise, automatically generates a job ID.

        Returns
        -------
        dict
            The job ID of the Job that carries out the video concatenation.

        """
        resp = self.requests.post(
            "videos/concatenate_videos/",
            trailing_slash=True,
            json={
                "ids": ids,
                "output_video_id": output_video_id,
                "video_metadata": video_metadata,
                "job_id": job_id
            }
        )

        return resp.json()

    def add_annotation(self,
                       annotation: Annotation,
                       raw_annotation: Optional[str] = None,
                       update_asset: bool = True,
                       buffered_write: bool = False,
                       replace_sets: bool = False,
                       add_to_cache: bool = False
                       ):

        """Add a single annotation.

        Add an annotation using a class from the ``scenebox.models.annotation`` module.

        Parameters
        ----------
        annotation:
            The formatted annotation to ingest.
        raw_annotation:
            The raw annotation file to ingest.  Gets uploaded as a raw file.
        update_asset:
            If True, updates the metadata of the previously uploaded asset associated with the ``annotation``
        buffered_write:
            If True, ingests annotation in a buffered fashion.
        replace_sets:
            If True and update_asset is False, appends to existing annotation metadata rather than replacing it.
            If False and update_asset is True, replaces existing annotation metadata with the inputted ``annotation``
            metadata.
        add_to_cache:
            If True, corresponding bytes will be added to cache for quick access.

        """

        metadata = annotation.to_dic()
        self.get_asset_manager(
            asset_type=AssetsConstants.ANNOTATIONS_ASSET_ID).put_asset(
            metadata=metadata,
            id=annotation.id,
            file_object=raw_annotation,
            wait_for_completion=buffered_write,
            add_to_redis_cache=add_to_cache
        )

        annotation.post_upload(annotations_amc=self.get_asset_manager(AssetsConstants.ANNOTATIONS_ASSET_ID))
        if update_asset:
            self.get_asset_manager(
                asset_type=annotation.media_type).update_metadata(
                id=annotation.asset_id,
                metadata={
                    "annotations": [
                        annotation.id],
                    "annotations_meta": [{
                        "provider": annotation.provider,
                        "id": annotation.id,
                        "type": annotation.annotation_type,
                        "version": annotation.version,}]},
                replace_sets=replace_sets)

    def add_annotations(self,
                        annotations: Iterable[Annotation],
                        buffered_write: bool = True,
                        update_asset: bool = True,
                        raw_annotations: List[Optional[str]] = None,
                        threading: bool = True,
                        disable_tqdm: bool = False,
                        replace_sets: bool = False,
                        cleanup_annotation_masks: bool = False,
                        session_uid: Optional[str] = None,
                        annotations_to_objects: bool = False,
                        add_to_cache: bool = False
                        ):
        """Add several annotations at once.

        Parameters
        ----------
        annotations:
            The annotations to ingest.
        buffered_write:
            If True, ingests annotations in a buffered fashion.
        update_asset:
             If True, updates the metadata of the asset associated with each of the items in ``annotations``.
             Otherwise, does not update the metadata of the associated asset.
        raw_annotations:
            A list of the raw annotation files to ingest.  Gets uploaded as raw files.
        threading:
            If True, uses multithreading to speed up annotations ingestion.  Otherwise, does not use multithreading.
        disable_tqdm:
            If False, uses a progressbar wrapper that calculates and shows the progress of the threading process.
            Otherwise, disables/silences the tqdm progressbar wrapper.
        replace_sets:
            If True and update_asset is False, appends to existing annotation metadata rather than replacing it.
            If False and update_asset is True, replaces existing annotation metadata with the inputted ``annotation``
            metadata.
        cleanup_annotation_masks:
            If True, runs the cleanup_annotation_masks async task after adding all annotations.
        session_uid:
            If provided and annotations_to_objects is set to True, objects entities are added to the session during
            the annotations_to_objects async task.
        annotations_to_objects:
            If True, runs the annotations_to_objects async task after adding the annotations.
        add_to_cache:
            If True, corresponding bytes will be added to cache for quick access.
        """

        annotation_metadata = []
        annotation_ids = []
        media_types = []
        asset_ids = []
        asset_metadata = []
        for annotation in annotations:
            annotation_metadata.append(annotation.to_dic())
            annotation_ids.append(annotation.id)
            if update_asset:
                media_types.append(annotation.media_type)
                asset_ids.append(annotation.asset_id)
                asset_metadatum = {
                    "annotations": [
                        annotation.id],
                    "annotations_meta": [{
                        "provider": annotation.provider,
                        "id": annotation.id,
                        "type": annotation.annotation_type,
                        "version": annotation.version}]}
                asset_metadata.append(asset_metadatum)

        self.get_asset_manager(
            asset_type=AssetsConstants.ANNOTATIONS_ASSET_ID).put_assets_batch(
            metadata=annotation_metadata,
            ids=annotation_ids,
            file_objects=raw_annotations,
            wait_for_completion=buffered_write,
            threading=threading,
            disable_tqdm=disable_tqdm
        )

        for annotation in annotations:
            annotation.post_upload(annotations_amc=self.get_asset_manager(AssetsConstants.ANNOTATIONS_ASSET_ID))

        if update_asset:
            unique_media_type_list = list(set(media_types))
            if len(unique_media_type_list) != 1:
                raise ValueError("Expected batch of annotations to have the same "
                                 "media type. Got {}".format(unique_media_type_list))

            self.get_asset_manager(
                asset_type=unique_media_type_list[0]).update_metadata_batch(
                ids=asset_ids,
                metadata=asset_metadata,
                replace_sets=replace_sets)

        annotation_ids = [annotation.id for annotation in annotations]
        if cleanup_annotation_masks:
            self.cleanup_annotation_masks(ids=annotation_ids)

        if annotations_to_objects:
            self.annotations_to_objects(ids=annotation_ids,
                                        create_objects=True,
                                        session_uid=session_uid,
                                        add_to_session=True)

    @staticmethod
    def is_coco_annotation_file_valid(
            file_path: str
    ) -> bool:
        """Tests if a COCO annotation file is valid.

        A valid COCO annotations file is a .json file that only contains keys listed in
        ``scenebox.constants.COCOAnnotations.KEYS``, and values that are all of type list.

        Parameters
        ----------
        file_path:
            Location of the COCO annotation file to validate.

        Returns
        -------
        bool
            Returns True if the COCO annotation file is valid (and can be ingested into SceneBox).
            Otherwise, returns False if the COCO annotation file is invalid.
        """

        if not file_path.split('.')[-1] == "json":
            return False
        else:
            with open(file_path, 'r') as f:
                data = json.load(f)
            for key in COCOAnnotations.KEYS:
                if key not in data.keys():
                    return False
            for value in data.values():
                if not isinstance(value, list):
                    return False
        return True

    def add_coco_annotations_from_folder(
            self,
            file_path: str,
            provider: str,
            folder_path: Optional[str] = None,
            version: Optional[str] = None,
            annotation_group: Optional[str] = AnnotationGroups.GROUND_TRUTH,
            session_uid: Optional[str] = None,
            images_set_id: Optional[str] = None,
            annotations_set_id: Optional[str] = None,
            use_image_id_as_annotation_id: Optional[bool] = False,
            preprocesses: Optional[List[str]] = None,
            thumbnailize_at_ingest: bool = False
    ):
        """Add several images and/or COCO annotations.

        Upload several images and/or COCO annotations at once with the same local folder path.  This method is best
        used with local images that are all located in the same folder. For images not located in the same folder,
        or images that are not located on your local machine, check out ``self.add_image``.

        Parameters
        ----------
        file_path:
        provider:
            Name of the provider that supplied the annotations.
        folder_path:
            The local path to the folder of images to upload.  If not provided, no new images are uploaded.
        version:
            The version of the model that supplied the annotations.
        annotation_group:
            The group that the annotation belongs to.
            It can be one of ground_truth, model_generated, or other
        session_uid:
            The session to associate with the images to upload.  If folder_path is not provided, has no effect.
        images_set_id:
            The set to add the images to.  If folder_path is not provided, has no effect.
        annotations_set_id:
            The set to add the COCO annotations to
        use_image_id_as_annotation_id:
            If True, appends each annotation's associated image_id onto the annotation's ID.
            Otherwise, makes the annotation IDs ``None``.
        preprocesses:
            Specifies which process to treat the image thumbnails with.
        thumbnailize_at_ingest:
            If True, create thumbnail at ingestion time.  Otherwise, create thumbnails "on the fly".
        """

        if not self.is_coco_annotation_file_valid(file_path=file_path):
            logger.info(
                "{} is not a valid coco annotations file".format(file_path))
            return

        polygon_annotations = []
        bbox_annotations = []

        with open(file_path, 'r') as file:
            data = json.load(file)

        category_id_name_map = {
            category["id"]: category["name"] for category in data["categories"]}
        file_name_image_id_map = {image["file_name"].split(
            '/')[-1]: str(image["id"]) for image in data["images"]}
        if folder_path:
            self.add_images_from_folder(
                folder_path=folder_path,
                session_uid=session_uid,
                set_id=images_set_id,
                filename_image_id_map=file_name_image_id_map,
                preprocesses=preprocesses,
                thumbnailize_at_ingest=thumbnailize_at_ingest
            )
        image_id_annotation_map = defaultdict(list)

        for annotation in data["annotations"]:
            annotation_json = {}
            image_id = str(annotation["image_id"])
            annotation_json["bbox"] = annotation["bbox"]
            annotation_json["category_id"] = annotation["category_id"]
            annotation_json["segmentation"] = annotation["segmentation"]
            image_id_annotation_map[image_id].append(annotation_json)

        for image_id, annotations in image_id_annotation_map.items():
            bboxes = []
            polygons = []
            for annotation in annotations:
                if annotation["bbox"]:
                    bboxes.append(
                        BoundingBox(x_min=annotation["bbox"][0],
                                    y_min=annotation["bbox"][1],
                                    x_max=annotation["bbox"][0] + annotation["bbox"][2],
                                    y_max=annotation["bbox"][1] + annotation["bbox"][3],
                                    label=category_id_name_map[annotation["category_id"]],
                                    category_id=annotation["category_id"]
                                    )
                    )
                if annotation["segmentation"][0]:
                    coordinates = []
                    for i in range(0, len(annotation["segmentation"][0]), 2):
                        coordinates.append(
                            (annotation["segmentation"][0][i], annotation["segmentation"][0][i + 1]))
                    polygons.append(
                        Polygon(
                            coordinates=coordinates,
                            label=category_id_name_map[annotation["category_id"]],
                            category_id=annotation["category_id"]
                        )
                    )
            bbox_annotations.append(
                BoundingBoxAnnotation(
                    provider="{}_bbox".format(provider),
                    version=version,
                    bounding_boxes=bboxes,
                    image_id=image_id,
                    annotation_group=annotation_group,
                    set_id=annotations_set_id,
                    id="{}_bbox.ann".format(image_id) if use_image_id_as_annotation_id else None))
            polygon_annotations.append(
                PolygonAnnotation(
                    provider="{}_polygon".format(provider),
                    version=version,
                    polygons=polygons,
                    image_id=image_id,
                    annotation_group=annotation_group,
                    set_id=annotations_set_id,
                    id="{}_polygon.ann".format(image_id) if use_image_id_as_annotation_id else None))

        self.add_annotations(annotations=polygon_annotations)
        logger.info(
            "{} polygon annotations are added".format(
                len(polygon_annotations)))
        self.add_annotations(annotations=bbox_annotations)
        logger.info(
            "{} bbox annotations are added".format(
                len(polygon_annotations)))

    def delete_annotations(self,
                           ids: Optional[List[str]] = None,
                           search: Optional[dict] = None,
                           wait_for_completion: bool = True
                           ) -> str:

        """Delete annotations using a list of ids or a search query, and updates metadata of corresponding assets.

        Parameters
        ----------
        ids:
            A list of annotation IDs to delete.
        search:
            Query to locate the data subset of interest.  Filters through existing
            assets according to the dictionary passed.
        wait_for_completion:
            If True, polls until job is complete.
            Otherwise, continues execution and does not raise an error if the job does not complete.
            Default is True.
        Returns
        -------
        job_id
            The job ID of the Job that carries out the deletion of annotations.
        """
        if ids:
            annotations_meta = self.get_asset_manager(
                asset_type=AssetsConstants.ANNOTATIONS_ASSET_ID).search_meta(
                query={
                    "filters": [{
                        "field": "id",
                        "values": ids,
                        "filter_out": False
                    }]
                }
            )
        elif search:
            annotations_meta = self.get_asset_manager(
                asset_type=AssetsConstants.ANNOTATIONS_ASSET_ID).search_meta(
                query=search
            )
        else:
            annotations_meta = []

        if not annotations_meta:
            return "No annotations to delete"

        asset_ann_id_map = defaultdict(list)
        media_types = [annotations_meta[0].get("media_type")] * len(annotations_meta)
        for _ in annotations_meta:
            asset_ann_id_map[_["asset_id"]].append(_["id"])

        assets_meta = self.get_asset_manager(
            asset_type=annotations_meta[0].get("media_type")).search_meta(
            query={
                    "filters": [{
                        "field": "id",
                        "values": list(asset_ann_id_map.keys()),
                        "filter_out": False
                    }]
                },
            scan=True
        )
        sorted_assets_meta = sorted(assets_meta, key=lambda d: d['id'])
        sorted_asset_ann_id_map = OrderedDict(sorted(asset_ann_id_map.items()))

        def update_asset_meta(asset_id, asset_meta, ann_ids, media_type):
            anns = asset_meta["annotations"]
            anns_meta = asset_meta["annotations_meta"]
            for ann_id in ann_ids:
                if ann_id in anns:
                    index = anns.index(ann_id)
                    anns.remove(ann_id)
                    anns_meta.pop(index)

            self.get_asset_manager(
                asset_type=media_type).update_metadata(
                id=asset_id,
                replace_sets=True,
                metadata={
                    "annotations": anns,
                    "annotations_meta": anns_meta
                }
            )
        iterable_ = zip(sorted_asset_ann_id_map.keys(), sorted_assets_meta, sorted_asset_ann_id_map.values(), media_types)
        run_threaded(
            func=update_asset_meta,
            iterable=iterable_,
            desc="update annotations keys in media meta",
            expand_iterable=True
        )

        if ids:
            job_id = self.get_asset_manager("annotations").delete_with_list(assets_list=ids, wait_for_completion=wait_for_completion)
        elif search:
            job_id = self.get_asset_manager("annotations").delete_with_query(query=search, wait_for_completion=wait_for_completion)
        else:
            return "No annotations to delete"

        return job_id

    def compare_annotation_pairs(self,
                                 asset_id: str,
                                 asset_type: str,
                                 base_annotation_id: Optional[str] = None,
                                 other_annotation_id: Optional[str] = None,
                                 base_mapping: Optional[Dict[str, str]] = None,
                                 other_mapping: Optional[Dict[str, str]] = None,
                                 iou_threshold: Optional[float] = None,
                                 match_labels: Optional[bool] = None,
                                 wait_for_completion: Optional[bool] = False) -> dict:
        """Compare a pair of annotations on a single asset.

        .. note:: This method currently only supports an ``asset_type`` of images.

        Compare two sets of annotation_entities for a given asset, and register the corresponding annotation
        comparisons.  Specify two annotations to compare, and optionally provide label mappings that transform
        existing labels into labels that are comparable.

        If matching labels is desired, consider providing label mappings if synonymous, yet differently named labels
        exist for the specified annotation pair.
        i.e. if  ``base_annotation_id`` has an annotation label called "vehicle" and ``other_annotation_id`` has an
        annotation label called "automobile", consider providing a ``base_mapping = {"vehicle": "car"}`` and
        ``other_mapping = {"automobile": "car"}``.

        Parameters
        ----------
        asset_id:
            ID of the asset to compare annotations on.
        asset_type:
            The asset type of the asset listed in ``asset_id``.  Currently, only images are supported.
        base_annotation_id:
            The ID of the first annotation source to compare with the second.
        other_annotation_id:
            The ID of the second annotation source to compare with the first.
        base_mapping:
            Label mapping for the ``base_annotation_id`` annotations.
        other_mapping:
            Label mapping for the ``other_annotation_id`` annotations.
        iou_threshold:
            The minimum value of IOU to call two bounding boxes a match.
        match_labels:
            If True, matches labels when matching prediction and ground truth.
            If False, just considers IOU.
        wait_for_completion:

        Returns
        -------
        dict
            The job ID of the Job that carries out the annotation comparison.

        """
        json_resquest = {
            "asset_id": asset_id,
            "asset_type": asset_type
        }
        if base_annotation_id:
            json_resquest.update(
                {
                    "base_annotation_id": base_annotation_id,
                }
            )
        if other_annotation_id:
            json_resquest.update(
                {
                    "other_annotation_id": other_annotation_id,
                }
            )
        if base_mapping:
            json_resquest.update(
                {
                    "base_mapping": base_mapping,
                }
            )
        if other_mapping:
            json_resquest.update(
                {
                    "other_mapping": other_mapping,
                }
            )
        if iou_threshold:
            json_resquest.update(
                {
                    "iou_threshold": iou_threshold,
                }
            )
        if match_labels is not None:
            json_resquest.update(
                {
                    "match_labels": match_labels,
                }
            )
        resp = self.requests.post(
            "annotations_comparisons/compare_annotation_pairs/",
            trailing_slash=True,
            json=json_resquest
        )

        if wait_for_completion:
            job_id = resp.json()["job_id"]
            self._wait_for_job_completion(job_id)
        return resp.json()

    def get_standardized_session_name(self, session_name: str) -> str:
        """Get a standardized session name.

        Converts all the special characters in the inputted session name into underscores, and all the
        text into lowercase.

        Parameters
        ----------
        session_name:
            The session name to standardize.

        Returns
        -------
        str
            The standardized session name.

        """
        resp = self.requests.post(
            "sessions/standardize_name/",
            trailing_slash=True,
            json={
                'session_name': session_name})

        if not resp.ok:
            raise ResponseError("{} ::: {}".format(resp.reason, resp.content))
        return resp.json()['session_name']

    def _get_asset_response_model(self, asset_type: str):
        if asset_type not in AssetsConstants.VALID_ASSETS:
            raise ValueError("Invalid asset type {}".format(asset_type))
        return self.requests.get(
            route=join(asset_type, 'meta', 'response_model'),
            trailing_slash=True
        ).json()

    def add_session(self,
                    session_name: str,
                    session_type: str = SessionTypes.GENERIC_SESSION_ID,
                    resolution: Optional[float] = None) -> str:
        """Add a session.

        Parameters
        ----------
        session_name:
            The name to give to the session.
        session_type:
            The session type to give to the session. Choose from ``scenebox.constants.SessionTypes``.
        resolution:
            The resolution at which to sample events on.  Measured in seconds.
            Ensure you choose a small enough resolution that none of your events get aliased to occur at a lower
            frequency than expected.

        Returns
        -------
        str
            The session UID of the added session.

        """
        payload = {
            "session_name": session_name,
            "session_type": session_type
        }
        if resolution:
            payload["resolution"] = resolution
        resp = self.requests.post(
            "sessions/add/",
            trailing_slash=True,
            json=payload)
        if not resp.ok:
            raise ResponseError("{} ::: {}".format(resp.reason, resp.content))
        return resp.json().get("session_uid")

    def update_time_span(
            self,
            session_uid: str,
            session_start_time: Union[datetime, str],
            session_end_time: Union[datetime, str]) -> dict:
        """Update the start/end times of a session.

        Parameters
        ----------
        session_uid:
            session uid of the session to change the start/end time for.
        session_start_time:
            The new session start time.
        session_end_time:
            The new session end time.

        Returns
        -------
        dict
            The updated metadata of the session after the timespan update.

        """
        logger.info(
            "session_start_time {} and session_end_time {}".format(
                session_start_time,
                session_end_time))
        resp = self.requests.post(
            "sessions/update_time_span/",
            trailing_slash=True,
            json={
                "session_uid": session_uid,
                "session_start_time": datetime_or_str_to_iso_utc(session_start_time),
                "session_end_time": datetime_or_str_to_iso_utc(session_end_time)})
        if not resp.ok:
            raise ResponseError("{} ::: {}".format(resp.reason, resp.content))
        return resp.json()

    def add_source_data(
            self,
            session_uid: str,
            source_data: List[dict],
            sensors: List[dict],
            replace: Optional[bool] = True) -> dict:
        """Add source data to session metadata.

        Parameters
        ----------
        session_uid:
            The session UID of the session metadata to update.
        source_data:
            The source data to add to the session metadata.
        sensors:
            The sensors to be added to session metadata.  Describes what sensors were used to capture the data.
        replace:
            If True, overwrites existing source metadata with the supplied source data.
            Otherwise, appends the supplied source data to the existing source metadata.

        Returns
        -------
        dict
            The updated metadata of the session after the source data update.
        """
        resp = self.requests.post(
            "sessions/add_source_data/",
            trailing_slash=True,
            json={
                "session_uid": session_uid,
                "source_data": source_data,
                "sensors": sensors,
                "replace": replace})
        if not resp.ok:
            raise ResponseError("{} ::: {}".format(resp.reason, resp.content))
        return resp.json()

    def add_auxiliary_session_data(
            self,
            session_uid: str,
            auxiliary_data: List[dict],
            replace: Optional[bool] = True) -> dict:
        """Add auxiliary data to session metadata.

        Parameters
        ----------
        session_uid:
            The session UID Of the session to add auxliliary data to.
        auxiliary_data:
            The auxiliary data to add to the session metadata.
        replace:
            If True, overwrites existing auxiliary metadata with the supplied auxiliary data.
            Otherwise, appends the supplied auxiliary data to the existing auxiliary metadata.

        Returns
        -------
        dict
            The updated metadata of the session after the auxiliary session data update.
        """
        resp = self.requests.post(
            "sessions/add_auxiliary_data/",
            trailing_slash=True,
            json={
                "session_uid": session_uid,
                "auxiliary_data": auxiliary_data,
                "replace": replace})
        if not resp.ok:
            raise ResponseError("{} ::: {}".format(resp.reason, resp.content))
        return resp.json()

    def add_enrichments_configs(
            self,
            session_uid: str,
            enrichments_configs: List[dict],
            replace: Optional[bool] = True) -> dict:
        """Add enrichment configurations to session metadata.

        Parameters
        ----------
        session_uid:
            The session UID of the session to add the enrichment configurations to.
        enrichments_configs:
            The enrichments configuration to add to the session metadata.
        replace:
            If True, overwrites existing enrichments config metadata with the supplied enrichments config.
            Otherwise, appends the supplied enrichments config to the existing enrichments config metadata.

        Returns
        -------
        dict
            The updated metadata of the session after adding the enrichments configs.

        """
        resp = self.requests.post(
            "sessions/add_enrichments_configs/",
            trailing_slash=True,
            json={
                "session_uid": session_uid,
                "enrichments_configs": enrichments_configs,
                "replace": replace})
        if not resp.ok:
            raise ResponseError("{} ::: {}".format(resp.reason, resp.content))
        return resp.json()

    def add_geolocation_entity(
            self,
            geolocation: dict,
            entity_value: List[str],
            timestamp: Union[str, datetime],
            session_uid: str) -> dict:
        """Add a geolocation entity to a session.

        Parameters
        ----------
        geolocation:
            The longitude and latitude of the geolocation.  Typically of the following form:
            geolocation = {"lat": lat, "lon": lon}
        entity_value:
            The value of the geolocation entity.  Typically of the form [lat, long].
        timestamp:
            The timestamp of the geolocation.
        session_uid:
            The session uid of the session to add the geolocation entity to.

        Returns
        -------
        dict
            A confirmation that the Job to add the entity was acknowledged.

        """
        entity_dict = {
            "session": session_uid,
            "timestamp": datetime_or_str_to_iso_utc(timestamp),
            "enrichments": ["visibility", "weather", "location"],
            "entity_id": get_guid(),
            "geolocation": geolocation,
            "entity_name": EntityNames.GEOLOCATION,
            "entity_value": entity_value,
            "entity_type": EntityTypes.GEO_ENTITY_TYPE,
            "influence": EntityInfluenceTypes.GEO_INTERPOLATION
        }
        response = self.add_entity(
            entity_dict=entity_dict)
        return response

    def add_entity(self,
                   entity_dict: dict,
                   urgent: bool = False) -> dict:
        """Add an entity to the specified session.

        Parameters
        ----------
        entity_dict:
            The entity data to add.  Typically, has the following form:
            {
                "session": session_uid,
                "start_time": datetime_or_str_to_iso_utc(start_time),
                "end_time": datetime_or_str_to_iso_utc(end_time),
                "timestamp": datetime_or_str_to_iso_utc(start_time),
                "entity_id": entity_id,
                "entity_name": event_name,
                "entity_value": event_value,
                "entity_type": Choose from scenebox.constants.EntityTypes,
                "influence": Choose from scenebox.constants.EntityInfluenceTypes
                "extend_session": bool whether to extend a session to cover the influence interval
            }

        urgent:
            If True, entity is ingested immediately.  However, a manual resolution is needed afterwards
            to make the entity searchable.

        Returns
        -------
        dict
            A confirmation that the Job to add the entity was acknowledged.

        """
        # urgent messages are ingested immediately but a manual resolution is
        # needed after that to make them searchable
        if not entity_dict.get("session"):
            raise InvalidArgumentsError(
                "session is not specified"
            )
        resp = self.requests.post(
            "session_manager/add_entity/",
            trailing_slash=True,
            json={"entity_dict": entity_dict},
            params={"urgent": urgent}
        )
        if not resp.ok:
            raise ResponseError("{} ::: {}".format(resp.reason, resp.content))
        return resp.json()

    def add_entities(self,
                     entity_dicts: List[dict]) -> dict:
        """Add a list of entities to the specified sessions.

        Parameters
        ----------
        entity_dicts:
            The entity data to add.  Typically, each list item has the following form:
            {
                "session": session_uid,
                "start_time": datetime_or_str_to_iso_utc(start_time),
                "end_time": datetime_or_str_to_iso_utc(end_time),
                "timestamp": datetime_or_str_to_iso_utc(start_time),
                "entity_id": entity_id,
                "entity_name": event_name,
                "entity_value": event_value,
                "entity_type": Choose from scenebox.constants.EntityTypes,
                "influence": Choose from scenebox.constants.EntityInfluenceTypes
                "extend_session": bool whether to extend a session to cover the influence interval
            }

        Returns
        -------
        dict
            A confirmation that the Job to add the entities was acknowledged.

        """

        resp = self.requests.post(
            "session_manager/add_entities/",
            trailing_slash=True,
            json={"entity_dicts": entity_dicts},
        )
        if not resp.ok:
            raise ResponseError("{} ::: {}".format(resp.reason, resp.content))
        return resp.json()

    def resolve_session(
            self,
            session_uid: str,
            resolution: Optional[float] = None,
            wait_for_completion: bool = False) -> dict:
        """Resolve a session.

        Project session events onto a single timeline. Events are sampled at the given ``resolution``.  A smaller
        resolution is recommended if events rapidly change in value.

        Parameters
        ----------
        session_uid:
            The session UID of the session to resolve.
        resolution:
            The resolution at which to sample session events.  Measured in seconds.
        wait_for_completion:
            If True, polls until job is complete.
            Otherwise, continues execution and does not raise an error if the job does not complete.

        Returns
        -------
        dict
            The ID of the Job that attempts to resolve the session.
        """
        if resolution:
            params = {"resolution": resolution}
        else:
            params = {}
        resp = self.requests.post(
            "session_manager/resolve_session/{}".format(session_uid),
            params=params)
        if not resp.ok:
            raise ResponseError("{} ::: {}".format(resp.reason, resp.content))
        if wait_for_completion:
            job_id = resp.json()["job_id"]
            self._wait_for_job_completion(job_id)
        return resp.json()

    def add_event_interval(self,
                           event_name: str,
                           event_value: Union[str, List[str]],
                           start_time: Union[str, datetime],
                           end_time: Union[str, datetime],
                           session_uid: str,
                           urgent: bool = False
                           ) -> str:
        """Add an event interval to a session.

        Adds a "state_set" entity to a specific session's timespan.

        Parameters
        ----------
        event_name:
            The name of the event interval to add to the session.
        event_value:
            The value(s) of the event over the timespan.
        start_time:
            The start time of the event.
        end_time:
            The end time of the event.
        session_uid:
            The session UID of the session to add the event to.
        urgent:
            If True, entity is ingested immediately.  However, a manual resolution is needed afterwards
            to make the entity searchable.

        Returns
        -------
        str
            The ID of the added entity.

        """
        if isinstance(start_time, datetime) and isinstance(end_time, datetime):
            if start_time > end_time:
                raise InvalidTimeError(
                    "start time cannot be after the end time")
        entity_id = get_guid()
        if isinstance(event_value, str):
            event_value = [event_value]
        elif not isinstance(event_value, list):
            raise TypeError("event value can be either str or a List[str]")
        entity_dict = {
            "session": session_uid,
            "start_time": datetime_or_str_to_iso_utc(start_time),
            "end_time": datetime_or_str_to_iso_utc(end_time),
            "timestamp": datetime_or_str_to_iso_utc(start_time),
            "entity_id": entity_id,
            "entity_name": event_name,
            "entity_value": event_value,
            "entity_type": EntityTypes.STATE_SET_ENTITY_TYPE,
            "influence": EntityInfluenceTypes.INTERVAL
        }

        self.add_entity(entity_dict=entity_dict, urgent=urgent)
        # self.resolve_session(session_uid=session_uid)

        return entity_id

    def add_comments(self,
                     comments: Union[str, List[str]],
                     start_time: Union[str, datetime],
                     end_time: Union[str, datetime],
                     session_uid: str,
                     wait_for_completion: bool = False) -> dict:

        """Add a comment to a time segment of a session.

        Parameters
        ----------
        comments:
            The comment(s) to add to the given timespan.
        start_time:
            The start time of the timespan to add the comment to.
        end_time:
            The end time of the timespan to add the comment to.
        session_uid:
            The session UID of the session to add the comment to.
        wait_for_completion:
             If True, polls until job is complete.
            Otherwise, continues execution and does not raise an error if the job does not complete.

        Returns
        -------
        dict
            The ID of the Job that attempts to add the comment.

        """

        if isinstance(comments, str):
            comments = [comments]

        comment_json = {
            "intervals": [
                {
                    "start_time": datetime_or_str_to_iso_utc(start_time),
                    "end_time": datetime_or_str_to_iso_utc(end_time)
                }
            ],
            "texts": comments,
        }
        resp = self.requests.post(
            "sessions/{}/comments".format(session_uid),
            trailing_slash=False,
            json=comment_json
        )
        if wait_for_completion:
            job_id = resp.json()["job_id"]
            self._wait_for_job_completion(job_id)
        return resp.json()

    def get_field_data(self,
                       session_uid: str,
                       search_dic: dict = None,
                       fields: Union[List[str],
                                     str] = 'all') -> Dict[str,
                                                           list]:
        if not search_dic:
            search_dic = {}

        if isinstance(fields, str):
            if fields == 'all':
                fields = ['*']
            else:
                raise ValueError(
                    'Field {} is not valid. Must be a list of field names or `all`'.format(fields))

        resp = self.requests.post(
            "session_manager/field_data/{}".format(session_uid),
            trailing_slash=False,
            json={
                'search_dic': search_dic,
                'session_fields': fields
            }
        )
        return resp.json()

    def get_searchable_fields(self, asset_type: str) -> dict:
        return self.requests.get(
            route=join(
                asset_type,
                'meta',
                'search_fields'),
            trailing_slash=True).json()

    def __adjust_time_interval(self,
                               start_time: Union[datetime, str],
                               end_time: Union[datetime, str],
                               epsilon: float) -> (datetime, datetime):

        if isinstance(start_time, str):
            start_time_output = string_to_datetime(
                start_time) + timedelta(seconds=epsilon)
        elif isinstance(start_time, datetime):
            start_time_output = start_time + timedelta(seconds=epsilon)
        else:
            raise TypeError("time should be either datetime or string")

        if isinstance(end_time, str):
            end_time_output = string_to_datetime(
                end_time) - timedelta(seconds=epsilon)
        elif isinstance(end_time, datetime):
            end_time_output = end_time - timedelta(seconds=epsilon)
        else:
            raise TypeError("time should be either datetime or string")

        if start_time_output > end_time_output:
            raise InvalidTimeError(
                "start time cannot be after or within {} second of the end time".format(epsilon))
        return start_time_output, end_time_output

    def add_event_intervals(self,
                            event_name: str,
                            event_values: List[str],
                            start_times: List[Union[str, datetime]],
                            end_times: List[Union[str, datetime]],
                            session_uid: str,
                            epsilon: float = 0) -> List[str]:
        """Add a list of several event intervals to a session.

        Adds several "state_set" entities to a specific session's timespan.

        Parameters
        ----------
        event_name:
            The name of the event interval to add to the session.
        event_values:
            The value(s) of the event over the timespan.
        start_times:
            The start time of each event.
        end_times:
            The end time of each event.
        session_uid:
            The session UID of the session to add the events to.
        epsilon:
            Constant to increase the time-delta of entity start time and endtime.  Measured in seconds.

        Returns
        -------
        List[str]
            A list of the added entity IDs

        """

        if len(event_values) != len(start_times) or \
                len(event_values) != len(end_times):
            raise IndexError(
                "size of event_values, start_times, and end_times should be same")

        entity_ids = []
        for start_time, end_time, event_value in zip(
                start_times, end_times, event_values):
            start_time, end_time = self.__adjust_time_interval(
                start_time, end_time, epsilon)

            entity_id = get_guid()
            if not isinstance(event_value, str):
                raise TypeError("event value should be str")

            entity_dict = {
                "session": session_uid,
                "start_time": datetime_or_str_to_iso_utc(start_time),
                "end_time": datetime_or_str_to_iso_utc(end_time),
                "timestamp": datetime_or_str_to_iso_utc(start_time),
                "enrichments": [],
                "entity_id": entity_id,
                "entity_name": event_name,
                "entity_value": [event_value],
                "entity_type": EntityTypes.STATE_SET_ENTITY_TYPE,
                "influence": EntityInfluenceTypes.AFFECT_FORWARD
            }

            self.add_entity(entity_dict=entity_dict)
            entity_ids.append(entity_id)

        # self.resolve_session(session_uid=session_uid)

        return entity_ids

    def add_scalar_intervals(self,
                             measurement_name: str,
                             measurement_values: List[float],
                             start_times: List[Union[str, datetime]],
                             end_times: List[Union[str, datetime]],
                             session_uid: str,
                             epsilon: float = 0.001) -> List[str]:

        if len(measurement_values) != len(start_times) or \
                len(measurement_values) != len(end_times):
            raise IndexError(
                "size of event_values, start_times, and end_times should be same")

        timestamps = []
        unpacked_measurements = []

        for start_time, end_time, measurement_value in zip(
                start_times, end_times, measurement_values):
            start_time, end_time = self.__adjust_time_interval(
                start_time, end_time, epsilon)

            timestamps += [start_time, end_time]
            unpacked_measurements += [measurement_value, measurement_value]

        return self.add_scalar_measurements(
            measurement_name=measurement_name,
            measurement_values=unpacked_measurements,
            timestamps=timestamps,
            session_uid=session_uid)

    def add_scalar_measurements(self,
                                measurement_name: str,
                                measurement_values: List[float],
                                timestamps: List[Union[datetime, str]],
                                session_uid: str) -> List[str]:

        entity_ids = []
        entity_dicts = []
        if len(timestamps) != len(measurement_values):
            raise IndexError(
                "measurement_values and timestamps should have same length")

        for timestamp, measurement_value in zip(
                timestamps, measurement_values):
            entity_id = get_guid()
            entity_dict = {
                "session": session_uid,
                "timestamp": datetime_or_str_to_iso_utc(timestamp),
                "enrichments": [],
                "entity_id": entity_id,
                "entity_name": measurement_name,
                "entity_value": measurement_value,
                "entity_type": EntityTypes.SCALAR_ENTITY_TYPE,
                "influence": EntityInfluenceTypes.LINEAR_INTERPOLATION
            }
            entity_dicts.append(entity_dict)
            entity_ids.append(entity_id)

        self.add_entities(entity_dicts=entity_dicts)
        return entity_ids

    def add_point_events(self,
                         measurement_name: str,
                         measurement_values: List[str],
                         timestamps: List[Union[datetime, str]],
                         session_uid: str) -> List[str]:

        if len(timestamps) != len(measurement_values):
            raise IndexError(
                "measurement_values and timestamps should have same length")

        entity_ids = []
        entity_dicts = []
        resolution = self.get_asset_manager(
            AssetsConstants.SESSIONS_ASSET_ID).get_metadata(
            id=session_uid).get("resolution")
        for timestamp, measurement_value in zip(
                timestamps, measurement_values):
            entity_id = get_guid()
            timestamp = str_or_datetime_to_datetime(timestamp)
            start_time = datetime_or_str_to_iso_utc(
                timestamp - timedelta(seconds=resolution))
            end_time = datetime_or_str_to_iso_utc(
                timestamp + timedelta(seconds=resolution))
            timestamp = datetime_or_str_to_iso_utc(timestamp)
            entity_dict = {
                "session": session_uid,
                "timestamp": timestamp,
                "start_time": start_time,
                "end_time": end_time,
                "enrichments": [],
                "entity_id": entity_id,
                "entity_name": measurement_name,
                "entity_value": measurement_value,
                "entity_type": EntityTypes.STATE_ENTITY_TYPE,
                "influence": EntityInfluenceTypes.INTERVAL
            }
            entity_dicts.append(entity_dict)
            entity_ids.append(entity_id)

        self.add_entities(entity_dicts=entity_dicts)

    def add_timeseries_csv(self,
                           session_uid: str,
                           csv_filepath: str,
                           df_labels: Optional[List[str]] = None,
                           ):
        """Add a timeseries from a CSV file.

        Add a measurement DataFrame to a session as scalar entities from a CSV. Creates a ``measurement_df`` Pandas
        DataFrame from the inputted CSV file, then passes this dataframe to ``self.add_df``.

        Parameters
        ----------
        session_uid:
            The session to add the timeseries to.
        csv_filepath:
            The filepath of the CSV to turn into a timeseries.
        df_labels:
            List of the CSV column names to use.
        """
        kwargs = {}
        if df_labels:
            kwargs["names"] = df_labels
        measurement_df = pd.read_csv(csv_filepath, **kwargs)

        self.add_df(
            measurement_df=measurement_df,
            session_uid=session_uid
        )

    def add_df(self,
               measurement_df,
               session_uid: str,
               timestamps: Optional[List[Union[datetime,
                                               str]]] = None):

        """Add a measurement DataFrame to a session as scalar entities.

        Add several measurements across time in a session by populating the ``measurement_df`` Pandas DataFrame
        argument. Can add an arbitrary number of named measurements, either numeric or non-numeric.  Timestamps must
        either be specified in the ``timestamps`` argument, or under a column named "timestamps" inside
        ``measurement_df``.

        Parameters
        ----------
        measurement_df:
            DataFrame holding the measurement(s) of interest.  Add an arbitrary number of named columns to represent
            different measurement types. If a column named "timestamps" specifiying the timestamps of the
            measurements does not exist, must be specified under the ``timestamps`` method argument.

            If latitude/longitude columns are included in under the names "lat" and "lon" respectively,
            will automatically be added as geolocation entities.
        session_uid:
            The session UID to add the measurement(s) to.
        timestamps:
            A list of timestamps corresponding to the data measurements in ``measurement_df`

        """

        def add_numeric_df(column: str,
                           measurement_df: pd.DataFrame,
                           timestamps: List[datetime]):

            measurement_values = [
                float(x) for x in measurement_df[column].values]
            self.add_scalar_measurements(
                measurement_name=column.lower(),
                measurement_values=measurement_values,
                timestamps=timestamps,
                session_uid=session_uid)

        if TIMESTAMP_FIELD not in measurement_df.columns and not timestamps:
            raise KeyError(
                "dataframe must include a timestamp column or timestamps must be passed separately")
        if not timestamps:
            timestamps = [str_or_datetime_to_datetime(
                _) for _ in measurement_df.timestamp]
        if "lat" in measurement_df.columns and "lon" in measurement_df.columns:
            for timestamp, lat, lon in zip(timestamps, measurement_df["lat"], measurement_df["lon"]):
                self.add_geolocation_entity(
                    entity_value=[lat, lon],
                    geolocation={"lat": lat, "lon": lon},
                    session_uid=session_uid,
                    timestamp=datetime_or_str_to_iso_utc(timestamp)
                )
            measurement_df.drop(['lon', 'lat'], axis='columns', inplace=True)

        numeric_df = measurement_df.select_dtypes(include=np.number)
        non_numeric_df = measurement_df.drop(labels=numeric_df.columns, axis=1)
        if TIMESTAMP_FIELD in non_numeric_df.columns:
            non_numeric_df.drop(labels=TIMESTAMP_FIELD, axis=1, inplace=True)

        if not numeric_df.empty:
            run_threaded(func=add_numeric_df,
                         iterable=numeric_df.columns,
                         desc="adding scalar measurements",
                         measurement_df=numeric_df,
                         timestamps=timestamps)
        if not non_numeric_df.empty:
            for column in non_numeric_df.columns:
                self.add_point_events(
                    measurement_name=column,
                    measurement_values=non_numeric_df[column],
                    session_uid=session_uid,
                    timestamps=timestamps)
        self.resolve_session(session_uid=session_uid)

    def delete_session(self,
                       session_uid: str,
                       delete_assets_contents: bool = True,
                       wait_for_completion: bool = False):
        """Delete an existing session.

        Optionally delete the assets inside the session, as well.

        Parameters
        ----------
        session_uid:
            The UID of the session to delete.
        delete_assets_contents:
            If True, deletes the assets contained inside the specified session.
            Otherwise, does not delete the assets in the session.
        wait_for_completion:
            If True, polls until job is complete.
            Otherwise, continues execution and does not raise an error if the job does not complete.

        Returns:

        """
        resp = self.requests.delete(
            "session_manager/delete_session/{}".format(session_uid),
            trailing_slash=False,
            params={'delete_assets_contents': delete_assets_contents})
        if not resp.ok:
            raise ResponseError("{} ::: {}".format(resp.reason, resp.content))

        if wait_for_completion:
            job_id = resp.json()["job_id"]
            self._wait_for_job_completion(job_id)
        return resp.json()

    def add_event_with_search(self,
                              event_title: str,
                              search: dict,
                              wait_for_completion: bool = False):

        resp = self.requests.post("session_manager/add_event_with_search/",
                                  trailing_slash=False,
                                  json={
                                      "search": search,
                                      "event_title": event_title}
                                  )
        if not resp.ok:
            raise ResponseError("{} ::: {}".format(resp.reason, resp.content))

        if wait_for_completion:
            job_id = resp.json()["job_id"]
            self._wait_for_job_completion(job_id)
        return resp.json()

    def delete_events(self,
                      session_uids: List[str],
                      event_names: List[str],
                      start_time: Optional[str] = None,
                      end_time: Optional[str] = None,
                      wait_for_completion: bool = False):
        params = {'session_uids': session_uids,
                  'event_names': event_names}
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time

        resp = self.requests.delete(
            "session_manager/delete_event/",
            trailing_slash=False,
            json=params)
        if not resp.ok:
            raise ResponseError("{} ::: {}".format(resp.reason, resp.content))

        if wait_for_completion:
            job_id = resp.json()["job_id"]
            self._wait_for_job_completion(job_id)
        return resp.json()

    def search_assets(
            self,
            asset_type,
            search: Optional[dict] = None,
            size: int = DEFAULT_SEARCH_SIZE,
            offset: int = 0,
            sort_field: Optional[str] = None,
            sort_order: Optional[str] = None,
            scan: bool = False) -> List[str]:
        """Retrieve asset IDs with a search query.

        Returns the top ``size`` matching hits.  If a return of more than 10000 hits is desired, please use
        AssetManagerClient.search_assets_large().

        Parameters
        ----------
        asset_type:
            Asset type to filter for in the asset search.
        search:
            Query to locate the data subset of interest.  Filters through existing
            assets according to the dictionary passed.
        size:
            Specifies the Elasticsearch search size.  The maximum number of hits to return.
            Has no effect if ``scan`` is False.
        offset:
            Specifies the Elasticsearch search offset.  The number of hits to skip.
            Has no effect if ``scan`` is False.
        sort_field:
            Sorts for the specified name.
        sort_order:
            Specifies the Elasticsearch string sorting order.
        scan:
            If True, uses the Elasticsearch scan capability.
            Otherwise, uses the Elasticsearch search API.

        Returns
        -------
        List[str]
            A list of the IDs of the assets fulfilling the search query.

        """

        search = search or {}
        params = {'size': size, 'offset': offset, 'scan': scan}
        if sort_field:
            params['sort_field'] = sort_field
        if sort_order:
            params['sort_order'] = sort_order

        resp = self.requests.post("{}/".format(asset_type),
                                  json=search,
                                  params=params,
                                  trailing_slash=False)
        if not resp.ok:
            raise AssetError(
                'Could not search the files ::: {} -- {} -- {}'.format(
                    asset_type, resp.reason, resp.content))
        return resp.json()

    def search_meta(
            self,
            asset_type,
            query: Optional[dict] = None,
            size: int = DEFAULT_SEARCH_SIZE,
            offset: int = 0,
            sort_field: Optional[str] = None,
            sort_order: Optional[str] = None,
            scan: bool = False) -> List[Dict]:
        """Retrieve asset metadata with a search query.

        Returns the top ``size`` matching hits.  If a return of more than 10000 hits is desired, please use
        AssetManagerClient.search_meta_large().

        Parameters
        ----------
        asset_type:
            Asset type to filter for in the asset metadata search.
        query:
            Query to locate the data subset of interest.  Filters through existing
            assets according to the dictionary passed.
        size:
            Specifies the Elasticsearch search size.  The maximum number of hits to return.
            Has no effect if ``scan`` is False.
        offset:
            Specifies the Elasticsearch search offset.  The number of hits to skip.
            Has no effect if ``scan`` is False.
        sort_field:
            Sorts for the specified name.
        sort_order:
            Specifies the Elasticsearch string sorting order.
        scan:
            If True, uses the Elasticsearch scan capability.
            Otherwise, uses the Elasticsearch search API.

        Returns
        -------
        List[Dict]
            A list of the metadata of the assets fulfilling the search query.

        """

        query = query or {}
        params = {'size': size, 'offset': offset, 'scan': scan}
        if sort_field:
            params['sort_field'] = sort_field
        if sort_order:
            params['sort_order'] = sort_order

        resp = self.requests.post("{}/meta/".format(asset_type),
                                  json=query,
                                  params=params,
                                  trailing_slash=False)
        if not resp.ok:
            raise AssetError(
                'Could not search the files ::: {} -- {} -- {}'.format(
                    asset_type, resp.reason, resp.content))
        return resp.json()

    def add_embeddings(
            self,
            media_asset_id_embedding_bytes_map: Dict,
            asset_type: str,
            ndim: int,
            model: str,
            version: str,
            layer: Optional[str] = None,
            set_id: Optional[str] = None,
            similarity_ingest: bool = True,
            update_umap: bool = True,
            wait_for_completion: bool = False,
            buffered_write: bool = False,
            threading: bool = False,
            add_to_cache: bool = False
    ) -> List[str]:
        """Add existing embeddings to an asset.

        Parameters
        ----------
        media_asset_id_embedding_bytes_map:
            Provides a mapping between asset IDs and the asset's respective embedding.
            Dict keys should be asset ID, and dict value should be the embedding.
        asset_type:
            Type of the assets to add the embeddings to.
        ndim:
            Number of dimensions contained in each embedding.
        model:
            The model that generated the embedding.
        version:
            The version of the model that generated the embedding.
        layer:
            The layer that the embedding was extracted from.
        set_id:
            The set ID associated with the embeddings.
        similarity_ingest:
            If True, enables similar image/object search by performing bulk indexing.  Otherwise, has no effect.
        wait_for_completion:
            If True, polls until job is complete.
            Otherwise, continues execution and does not raise an error if the job does not complete.
        buffered_write:
            If True, ingests embeddings in a buffered fashion.
        threading:
            If True, enables multithreading to speed up operation. Otherwise, disables threading.
        add_to_cache:
            If True, corresponding bytes will be added to cache for quick access.

        Returns
        -------
        List[str]
            The IDs of the successfully added embeddings
        """

        similarity_index_name = get_similarity_index_name(
            media_type=asset_type, model=model, version=version)

        media_asset_id_embedding_meta_map = {}
        media_asset_id_embedding_id_map = {}

        def add_embedding_threaded(iterable):
            media_asset_id, embedding_bytes = iterable
            timestamp = datetime.utcnow()
            json_object_for_embedding_id = {
                'model': model,
                'version': version,
                'asset_id': media_asset_id,
                'layer': layer,
                'ndim': ndim}

            embeddings_hash = get_md5_from_json_object(
                json_object=json_object_for_embedding_id)
            embedding_id = str(
                hash_string_into_positive_integer_reproducible(embeddings_hash))

            embedding_meta = {
                'id': embedding_id,
                'timestamp': timestamp,
                'ndim': ndim,
                'sets': [set_id] if set_id else [],
                'tags': [layer] if layer else [],
                'media_type': asset_type,
                'asset_id': media_asset_id,
                'model': model,
                'version': version,
                'index_name': get_similarity_index_name(
                    media_type=asset_type,
                    model=model,
                    version=version)}

            media_asset_id_embedding_id_map[media_asset_id] = embedding_id
            media_asset_id_embedding_meta_map[media_asset_id] = embedding_meta

        run_threaded(func=add_embedding_threaded,
                     iterable=media_asset_id_embedding_bytes_map.items(),
                     desc="adding embeddings",
                     disable_threading=not threading,
                     disable_tqdm=True)

        embedding_bytes_list = []
        embedding_ids_list = []
        embeddings_metadata_list = []
        media_asset_ids = list(media_asset_id_embedding_bytes_map.keys())
        asset_metadata_list = []

        for media_asset_id in media_asset_ids:
            embedding_bytes_list.append(media_asset_id_embedding_bytes_map[media_asset_id])
            embedding_ids_list.append(media_asset_id_embedding_id_map[media_asset_id])
            embeddings_metadata_list.append(media_asset_id_embedding_meta_map[media_asset_id])
            asset_metadata_list.append({"embeddings":
                    {similarity_index_name: media_asset_id_embedding_id_map[media_asset_id]}})

        self.get_asset_manager(
            AssetsConstants.EMBEDDINGS_ASSET_ID).put_assets_batch(
            file_objects=embedding_bytes_list,
            ids=embedding_ids_list,
            metadata=embeddings_metadata_list)

        self.get_asset_manager(
            asset_type=asset_type).update_metadata_batch(
            ids=media_asset_ids,
            metadata=asset_metadata_list)

        if similarity_ingest:

            resp = self.requests.post(
                "similarity_search/bulk_index/",
                trailing_slash=False,
                json={"embedding_ids": embedding_ids_list})
            if not resp.ok:
                raise ResponseError(
                    "Could not clean_up the annotations: {}".format(
                        resp.content))

            job_id = resp.json()["job_id"]
            if wait_for_completion or update_umap:
                self._wait_for_job_completion(
                    job_id, max_wait_sec=max(
                        10 * len(embedding_ids_list), 60))
            if update_umap:
                self.create_umap(asset_type=asset_type,
                                 index_name=similarity_index_name,
                                 search_dic={},
                                 wait_for_completion=wait_for_completion)

        return embedding_ids_list


    def add_image(
            self,
            image_path: Optional[str] = None,
            id: Optional[str] = None,
            image_url: Optional[str] = None,
            image_uri: Optional[str] = None,
            image_bytes: Optional[Union[io.BytesIO, bytes, str]] = None,
            sensor: Optional[str] = None,
            timestamp: Optional[Union[str, datetime]] = None,
            session_uid: Optional[str] = None,
            set_id: Optional[Union[str, List[str]]] = None,
            annotations: Optional[List[Annotation]] = None,
            preprocesses: Optional[List[str]] = None,
            aux_metadata: Optional[dict] = None,
            geo_field: Optional[str] = None,
            shape_group_field: Optional[str] = None,
            enrichments: Optional[List[str]] = None,
            add_to_session: bool = False,
            thumbnailize_at_ingest: bool = False,
            buffered_write: bool = False,
            add_provider_to_labels: bool = True,
            overwrite: bool = True,
            add_to_cache: bool = False
    ) -> str:

        """Upload an image onto SceneBox.

               Upload an image with a local file path, URL, URI, or image bytes.  This method is best used with
               singular images, or images that are not all located in the same folder. For several images all located
               in the same folder, check out ``self.add_images_from_folder``.

               Parameters
               ----------
               image_path:
                   The local path to the image to upload. If not None, image_url, image_uri, and image_bytes should all
                   be None.
               id:
                   A unique image ID.  A common choice is the image filename.
               image_url:
                   The URL of the image to upload. Images must be publicly available.  If not None, image_url,
                   image_uri, and image_path should all be None.
               image_uri:
                   The URI of the image to upload. Can be from a private source.  If not None, image_url, image_path,
                   and image_bytes should all be None.
               image_bytes:
                   The image bytes to upload.  If not None, image_path, image_url, and image_uri should all be None.
               sensor:
                    The sensor associated with the image.
               timestamp:
                    The time at which the image was taken.
               session_uid:
                    The session associated with the image.
               set_id:
                    The set (str) or sets (List[str]) to add the image to.
               annotations:
                    Annotations associated with the image.  Each item in the passed list must be of a class from
                    scenebox.models.annotation.
               preprocesses:
                    Specifies which process to treat the image thumbnails with.
               aux_metadata:
                    Auxiliary metadata associated with the image (partitioned from primary metadata)
               geo_field:
                    Geolocation metadata associated with the image.
               shape_group_field:
                    Shape group metadata associated with the image (example: UMAP).
               enrichments:
                    The types of enrichments to add to the image.
               thumbnailize_at_ingest:
                    If True, create thumbnail at ingestion time.  Otherwise, create thumbnails "on the fly".
               buffered_write:
                    If True, writes images in a buffered fashion.
               add_to_session:
                    If True and session_uid is not None, add to the existing session with the passed session_uid.
               add_provider_to_labels:
                    If True the labels of the annotations in aux.label will included the provider as well. If False
                    only the labels will be ingested
               overwrite:
                    If True and id is not None, updates the the metadata/annotations/etc. of a previously uploaded
                    image.
               add_to_cache:
                    If True, corresponding bytes will be added to cache for quick access.

               Returns
               -------
               str
                   The id of the added image.

               Raises
               ------
               SetsErrorInvalidArgumentsError:
                    If more than one of image_path, image_url, image_uri, and image_bytes is not None
               ValueError:
                    If image_path, image_bytes, image_uri, and image_url are all None

               """
        sets = []
        if set_id:
            if isinstance(set_id, str):
                sets = [set_id]
            elif isinstance(set_id, list):
                sets = set_id

        if not overwrite and id is not None:
            if self.get_asset_manager(
                    asset_type=AssetsConstants.IMAGES_ASSET_ID).exists(id=id):
                if aux_metadata or preprocesses or set_id or annotations:
                    updated_meta = {}
                    if set_id:
                        updated_meta['sets'] = sets
                    if aux_metadata:
                        updated_meta[AUXILIARY_KEY] = aux_metadata
                    if preprocesses:
                        updated_meta['preprocesses'] = preprocesses
                    if annotations:
                        updated_meta["annotations"] = [
                            _.id for _ in annotations
                        ]
                        updated_meta["annotations_meta"] = [
                            {
                                "provider": _.provider,
                                "id": _.id,
                                "version": _.version,
                                "type": _.annotation_type
                            } for _ in annotations]
                        for annotation in annotations:
                            image_meta = self.get_asset_manager(
                                asset_type=AssetsConstants.IMAGES_ASSET_ID).get_metadata(
                                id=id)
                            annotation.timestamp = image_meta["timestamp"]
                            annotation.sensor = image_meta["sensor"]
                            annotation.session_uid = image_meta["session_uid"]
                        self.add_annotations(
                            annotations=annotations, update_asset=False)

                    self.get_asset_manager(
                        asset_type=AssetsConstants.IMAGES_ASSET_ID).update_metadata(
                        id=id, metadata=updated_meta)
                return id

        if sum(
                1 for _ in [
                    image_path,
                    image_url,
                    image_uri,
                    image_bytes] if _ is not None) != 1:
            raise InvalidArgumentsError(
                "Exactly one of image_path, image_url, image_uri, and image_bytes should be specified")

        if image_bytes:
            image_attributes = get_image_attributes(image_bytes=image_bytes)
            filename = id
        elif image_path:
            filename, _, _, image_format = parse_file_path(image_path)
            image_attributes = get_image_attributes(image_path=image_path)
            with open(image_path, 'rb') as f:
                image_bytes = io.BytesIO(f.read())
        elif image_url:
            filename = image_url.split("/")[-1]
            image_attributes = get_image_attributes(image_url=image_url)
        elif image_uri:
            filename = UriParser(uri=image_uri).key.split("/")[-1]
            object_access = ObjectAccess(
                uri=image_uri
            )
            image_attributes = get_image_attributes(
                self.get_asset_manager(
                    AssetsConstants.IMAGES_ASSET_ID).get_url_from_object_access(
                    object_access=object_access))
        else:
            raise ValueError(
                "Either image file path, image bytes, uri or url must be provided")

        if timestamp is None:
            timestamp = datetime.utcnow()
        else:
            timestamp = datetime_or_str_to_iso_utc(timestamp)

        image_metadata = {
            "width": image_attributes.width,
            "height": image_attributes.height,
            "format": image_attributes.format,
            "sensor": sensor,
            "timestamp": timestamp,
            "sets": sets,
            "preprocesses": preprocesses or [],
        }
        if session_uid is not None:
            image_metadata["session_uid"] = session_uid

        if annotations:
            image_metadata["annotations"] = [
                _.id for _ in annotations
            ]
            image_metadata["annotations_meta"] = [
                {
                    "provider": _.provider,
                    "id": _.id,
                    "version": _.version,
                    "type": _.annotation_type
                } for _ in annotations]
            labels = set()
            if add_provider_to_labels:
                for annotation in annotations:
                    for ae in annotation.annotation_entities:
                        labels.add("{}_{}".format(ae.label, annotation.provider))
            else:
                for annotation in annotations:
                    for ae in annotation.annotation_entities:
                        labels.add(ae.label)

            labels = list(labels)

            if aux_metadata:
                aux_metadata["labels"] = labels
            else:
                aux_metadata = {"labels": labels}

        if aux_metadata:
            image_metadata[AUXILIARY_KEY] = aux_metadata
        if image_bytes:
            if "png" in image_attributes.format.lower():
                content_type = "image/png"
            elif "jpg" in image_attributes.format.lower() or "jpeg" in image_attributes.format.lower():
                content_type = "image/jpeg"
            else:
                content_type = None
            id = self.get_asset_manager(
                AssetsConstants.IMAGES_ASSET_ID).put_asset(
                file_object=image_bytes,
                filename=filename,
                id=id,
                metadata=image_metadata,
                geo_field=geo_field,
                shape_group_field=shape_group_field,
                wait_for_completion=not buffered_write,
                buffered_write=buffered_write,
                content_type=content_type,
                add_to_redis_cache=add_to_cache
            )
        else:
            id = self.get_asset_manager(
                AssetsConstants.IMAGES_ASSET_ID).put_asset(
                url=image_url,
                filename=filename,
                id=id,
                uri=image_uri,
                metadata=image_metadata,
                geo_field=geo_field,
                wait_for_completion=not buffered_write,
                buffered_write=buffered_write
            )

        # If session_uid does not exist skip creating and pushing the entity
        if session_uid and add_to_session:
            entity_dict = {
                "session": session_uid,
                "timestamp": timestamp,
                "enrichments": enrichments or [],
                "entity_name": EntityNames.IMAGE,
                "media_asset_id": id,
                "entity_value": id,
                "entity_id": get_guid(),
                "entity_type": EntityTypes.MEDIA,
                "influence": EntityInfluenceTypes.INTERVAL
            }
            self.add_entity(entity_dict=entity_dict)

        # create thumbnail at ingestion time. By default set to False to speed up ingestion. If false, it thumbnails
        # will be created on the fly
        if thumbnailize_at_ingest:

            for preset in ["small", "tiny", "full_size_png"]:
                self.compress_images(
                    ids=[id],
                    use_preset=preset
                )

        if annotations:
            for annotation in annotations:
                annotation.timestamp = timestamp
                annotation.sensor = sensor
                annotation.session_uid = session_uid

            self.add_annotations(
                annotations=annotations,
                update_asset=False,
                threading=False,
                disable_tqdm=True)
        return id

    def add_images_from_folder(
            self,
            folder_path: str,
            session_uid: Optional[str] = None,
            set_id: Optional[str] = None,
            filename_image_id_map: Optional[dict] = None,
            preprocesses: Optional[List[str]] = None,
            thumbnailize_at_ingest: bool = False
    ):
        """Upload images from a single local folder path onto SceneBox.

           Upload several images at once with the same local folder path.  This method is best used with local images
           that are all located in the same folder. For images not located in the same folder, or images that are not
           located on your local machine, check out ``self.add_image``.

           Parameters
           ----------
           folder_path:
               The local path to the folder of images to upload.
           session_uid:
                The session associated with the image.
           set_id:
                The set to add the images to.
           filename_image_id_map:
                Provides a mapping from the image filenames to the desired image IDs.  If not specified, Image IDs are
                automatically assigned to a randomized, unique string.
           preprocesses:
                Specifies which process to images thumbnails with.
           thumbnailize_at_ingest:
                If True, create thumbnail at ingestion time.  Otherwise, create thumbnails "on the fly".

           Raises
           ------
           ValueError:
            "If image_path, image_bytes, image_uri, and image_url are all None"

           """
        kwargs = {}
        folder_path_object = Path(folder_path)
        if session_uid:
            kwargs["session_uid"] = session_uid
        if set_id:
            kwargs["set_id"] = set_id
        if thumbnailize_at_ingest:
            kwargs["thumbnailize_at_ingest"] = thumbnailize_at_ingest
        if preprocesses:
            kwargs["preprocesses"] = preprocesses
        file_list = [str(fp) for fp in folder_path_object.glob("*")]
        if not file_list:
            logger.warning("Could not find any valid images under {}".format(folder_path))
            return
        valid_images = []
        image_ids = []
        for file_path in file_list:
            image_type = imghdr.what(file_path)
            if image_type in ValidExtensions.IMAGES:
                valid_images.append(file_path)
                if filename_image_id_map:
                    image_ids.append(
                        filename_image_id_map[file_path.split('/')[-1]])
        if not valid_images:
            logger.warning("Could not find any valid images under {}".format(folder_path))

        run_threaded(
            func=self.add_image,
            iterable=valid_images,
            second_iterable=image_ids if filename_image_id_map else None,
            desc="adding images",
            **kwargs)

    def add_images_uri_list(
            self,
            images: List[dict],
            set_id: Optional[str] = None,
            wait_for_completion: bool = False):
        payload = {}
        payload["images"] = images

        logger.debug("Add Images URI List")

        if set_id is not None:
            payload["set_id"] = set_id

        resp = self.requests.post(
            "images/add_images_list/",
            trailing_slash=False,
            json=payload)
        if not resp.ok:
            raise ResponseError(
                "Could not add the images: {}".format(
                    resp.content))

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(
                job_id)
        return job_id

    def add_video(
            self,
            video_path: Optional[str] = None,
            video_url: Optional[str] = None,
            video_uri: Optional[str] = None,
            sensor: Optional[str] = None,
            start_timestamp: Optional[Union[datetime, str]] = None,
            session_uid: Optional[str] = None,
            id: Optional[str] = None,
            set_id: Optional[str] = None,
            annotations: Optional[List[Annotation]] = None,
            aux_metadata: Optional[dict] = None,
            enrichments: Optional[List[str]] = None,
            tags: Optional[List[str]] = None,
            compress_video: bool = True,
            buffered_write: bool = False,
            add_to_session: bool = False,
            create_session: bool = False
    ) -> Union[str, Tuple[str, str]]:

        """Upload a video onto SceneBox.

           Upload a video with a local file path, URL, or URI.

           Parameters
           ----------
           video_path:
               The local path to the video to upload. If not None, video_uri and video_url should both be None.
           video_url:
               The URL of the video to upload. Video must be publicly available.  If not None, video_path and
               video_uri should both be None.
           video_uri:
               The URI of the video to upload. Can be from a private source.  If not None, video_path, and video_url,
               should both be None.
           sensor:
                The sensor associated with the image.
           start_timestamp:
                The time at which the video recording began.
           session_uid:
                The session associated with the video.
           id:
               A unique video ID.  A common choice is the video filename.
           set_id:
                The set to add the video to.
           annotations:
                    Annotations associated with the Video.  Each item in the passed list must be of a class from
                    scenebox.models.annotation.
           aux_metadata:
                    Auxiliary metadata associated with the image (partitioned from primary metadata)
           enrichments:
                The types of enrichments to add to the image.
           tags:
                Labels associated with the video.  Allows for easy video search.
           compress_video:
                If true, register compressed video thumbnails.
           buffered_write:
                If True, writes images in a buffered fashion.
           add_to_session:
                If True and session_uid is not None, add to the existing session with the passed session_uid.
           create_session:
               If True and session_uid is None, create a single video session from the video with the video naming and
               the video start time and duration. Session resolution would be default (1.0 second) and video will be
               added as an aux_metadata. In this case, if the sensor name is not specified, it will be "main"

           Returns
           -------
           str
               The ID of the added video.

           Raises
           ------
           ValueError:
                If video_path, video_url, and video_uri are all None

           """
        id = id or get_guid()
        if video_path:
            filename, _, _, _ = parse_file_path(video_path)
            video_attributes = get_video_attributes(video_path)
        elif video_url:
            filename = video_url.split("/")[-1]
            video_attributes = get_video_attributes(video_url)
        elif video_uri:
            filename = UriParser(uri=video_uri).key.split("/")[-1]
            object_access = ObjectAccess(
                uri=video_uri
            )
            video_attributes = get_video_attributes(
                self.get_asset_manager(
                    AssetsConstants.VIDEOS_ASSET_ID).get_url_from_object_access(
                    object_access=object_access))
        else:
            raise ValueError("Either video_path, video_url, or video_uri must be provided")

        if start_timestamp:
            start_timestamp_dt = str_or_datetime_to_datetime(start_timestamp)
        else:
            start_timestamp_dt = datetime.utcnow()

        if not session_uid and create_session:
            session_uid = self.add_session(session_name=standardize_name(filename) or id,
                                           session_type=SessionTypes.VIDEOS_SESSION_ID)
            add_to_session = True
            sensor = sensor or "main"

        video_metadata = {
            "timestamp": datetime_or_str_to_iso_utc(start_timestamp_dt),
            "width": video_attributes.width,
            "height": video_attributes.height,
            "sensor": sensor,
            "duration": float(video_attributes.duration),
            "fps": video_attributes.fps,
            "sets": [set_id] if set_id else [],
            "start_time": datetime_or_str_to_iso_utc(start_timestamp_dt),
            "end_time": datetime_or_str_to_iso_utc(
                start_timestamp_dt
                + timedelta(
                    seconds=float(video_attributes.duration))),
            "tags": tags or []
        }

        if session_uid is not None:
            video_metadata["session_uid"] = session_uid

        if annotations:
            video_metadata["annotations"] = [
                _.id for _ in annotations
            ]
            video_metadata["annotations_meta"] = [
                {
                    "provider": _.provider,
                    "id": _.id,
                    "version": _.version,
                    "type": _.annotation_type
                } for _ in annotations]
            labels = set()
            for annotation in annotations:
                for ae in annotation.annotation_entities:
                    labels.add("{}_{}".format(ae.label, annotation.provider))

            labels = list(labels)

            if aux_metadata:
                aux_metadata["labels"] = labels
            else:
                aux_metadata = {"labels": labels}

            if aux_metadata:
                video_metadata[AUXILIARY_KEY] = aux_metadata

        if video_path:
            id = self.get_asset_manager(
                AssetsConstants.VIDEOS_ASSET_ID).put_asset(
                file_path=video_path,
                filename=filename,
                metadata=video_metadata,
                id=id,
                wait_for_completion=not buffered_write,
                buffered_write=buffered_write
            )
        elif video_url or video_uri:
            id = self.get_asset_manager(
                AssetsConstants.VIDEOS_ASSET_ID).put_asset(
                url=video_url,
                uri=video_uri,
                metadata=video_metadata,
                id=id,
                wait_for_completion=not buffered_write,
                buffered_write=buffered_write
            )
        else:
            raise ValueError(
                "Either file path or url, or uri must be provided ")

        # If session_uid does not exist skip creating and pushing the entity
        if session_uid and add_to_session:
            entity_dict = {
                "session": video_metadata["session_uid"],
                "start_time": video_metadata["start_time"],
                "end_time": video_metadata["end_time"],
                "timestamp": video_metadata["timestamp"],
                "enrichments": enrichments or [],
                "entity_name": EntityNames.VIDEO,
                "entity_id": filename,
                "entity_type": EntityTypes.MEDIA,
                "entity_value": id,
                "media_asset_id": id,
                "influence": EntityInfluenceTypes.AFFECT_FORWARD,
                "extend_session": True
            }
            self.add_entity(entity_dict=entity_dict, urgent=True)
        if compress_video:
            for preset in ['small', 'tiny']:
                self.compress_videos(
                    ids=[id],
                    use_preset=preset,
                )
        if create_session:
            auxiliary_data = [{
                "id": id,
                "type": AuxiliaryDataTypes.CONCATENATED_VIDEO,
                "tags": [sensor]
            }]

            self.add_auxiliary_session_data(session_uid=session_uid,
                                            auxiliary_data=auxiliary_data)

            video_source_data = [{
                "id": id,
                "type": AssetsConstants.VIDEOS_ASSET_ID,
                "sensor": sensor
            }]
            self.add_source_data(
                session_uid=session_uid,
                source_data=video_source_data,
                sensors=[{
                    "name": sensor,
                    "type": Sensors.CAMERA
                }]
            )
            self.resolve_session(session_uid=session_uid, wait_for_completion=True)
            return id, session_uid
        else:
            return id

    def get_video_frame_thumbnail(
            self,
            video_id: str,
            frame: int,
            thumbnail_tag: str) -> str:

        """Get thumbnail png for requested frame fram a video.

            Parameters
            ----------
            video_id:
                ID of the video to fetch the frame from.
            frame:
                The number 'n' for the n-th frame from the beginning.
            thumbnail_tag:
                Tag of the thumbnail to be created.

            Returns
            -------
            str
                URL for the requested thumbnail
        """

        video_amc = self.get_asset_manager(asset_type=AssetsConstants.VIDEOS_ASSET_ID)
        metadata = video_amc.get_metadata(id=video_id)
        thumbnails = metadata.get("thumbnails", {})
        frame_thumbnail_tag = "{}_frame_{}".format(thumbnail_tag, frame)

        object_access_dict = thumbnails.get(
            frame_thumbnail_tag, {}).get("object_access")

        if object_access_dict:
            object_access = ObjectAccess.from_dict(object_access_dict)
            url = video_amc.get_url_from_object_access(object_access, corr_id=video_id)
            return url
        else:
            raise ThumbnailNotAvailableError("put a good error here")

    def extract_frame_thumbnails(
            self,
            ids: List[str],
            frames: List[int],
            thumbnail_tags: Optional[List[str]] = None,
            wait_for_completion: bool = False) -> str:
        """Extract thumbnails for a list of frames in a video.

            Parameters
            ----------
            ids:
                IDs of the videos to extract frame thumbnails from.
            frames:
                A list of frame numbers starting from the beginning of each video.
            thumbnail_tags:
                List of types of thumbnails tags to extract.

            Returns
            -------
            str
                The job ID of the Job that running the operation.
        """

        thumbnail_tags = thumbnail_tags or ["small", "full_size_png"]
        payload = {
            "ids": ids,
            "thumbnail_tags": thumbnail_tags,
            "frames": frames
        }

        resp = self.requests.post(
            "videos/extract_frame_thumbnails/",
            trailing_slash=False,
            json=payload)

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(job_id)
        return job_id

    def add_lidar(
            self,
            lidar_path: Optional[str] = None,
            lidar_url: Optional[str] = None,
            lidar_uri: Optional[str] = None,
            lidar_bytes: Optional[Union[io.BytesIO, bytes, str]] = None,
            sensor: Optional[str] = None,
            timestamp: Optional[Union[str, datetime]] = None,
            session_uid: Optional[str] = None,
            id: Optional[str] = None,
            format: Optional[str] = None,
            num_fields: Optional[int] = None,
            set_id: Optional[str] = None,
            enrichments: Optional[List[str]] = None,
            buffered_write: bool = False,
            add_to_session: bool = False,
            add_to_cache: bool = False
    ) -> str:

        """Upload a LIDAR onto SceneBox.

           Upload a LIDAR with a local file path, URL, or URI.

           Parameters
           ----------
           lidar_path:
               The local path to the LIDAR to upload. If not None, lidar_uri and lidar_url should both be None.
           lidar_url:
               The URL of the LIDAR to upload. LIDAR must be publicly available.  If not None, lidar_path and
               lidar_uri should both be None.
           lidar_uri:
               The URI of the LIDAR to upload. Can be from a private source.  If not None, lidar_path, and lidar_url,
               should both be None.
           sensor:
                The sensor associated with the LIDAR.
           timestamp:
                The time at which the LIDAR was taken.
           session_uid:
                The session associated with the LIDAR.
           id:
               A unique video ID.  A common choice is the video filename.
           format:
               The format in which the LIDAR was embedded.
           num_fields:
               The number of fields exists in LIDAR file to reshape numpy array for displaying
           set_id:
                The set to add the video to.
           enrichments:
                The types of enrichments to add to the image.
           buffered_write:
                If True, writes images in a buffered fashion.
           add_to_session:
                If True and session_uid is not None, add to the existing session with the passed session_uid.
           add_to_cache:
                If True, corresponding bytes will be added to cache for quick access.

           Returns
           -------
           str
               The ID of the added LIDAR.

           Raises
           ------
           ValueError:
                If lidar_path, lidar_url, and lidar_uri are all None.

           """

        if lidar_path:
            filename, _, _, lidar_format = parse_file_path(lidar_path)
        elif lidar_url:
            filename = lidar_url.split("/")[-1]
        elif lidar_uri:
            filename = UriParser(uri=lidar_uri).key.split("/")[-1]
        elif lidar_bytes is not None:
            filename = get_guid()
        else:
            raise ValueError("Either LIDAR file path, uri or url must be provided")

        if timestamp is None:
            timestamp = datetime.utcnow()
        else:
            timestamp = datetime_or_str_to_iso_utc(timestamp)

        lidar_metadata = {"format": format,
                          "sensor": sensor,
                          "timestamp": timestamp,
                          "sets": [set_id] if set_id else []}

        if session_uid is not None:
            lidar_metadata["session_uid"] = session_uid

        if num_fields:
            lidar_metadata.update({"num_fields": num_fields})

        if lidar_path:
            id = self.get_asset_manager(
                AssetsConstants.LIDARS_ASSET_ID).put_asset(
                file_path=lidar_path,
                filename=filename,
                metadata=lidar_metadata,
                id=id,
                wait_for_completion=not buffered_write,
                buffered_write=buffered_write
            )
        elif lidar_url or lidar_uri:
            id = self.get_asset_manager(
                AssetsConstants.LIDARS_ASSET_ID).put_asset(
                url=lidar_url,
                uri=lidar_uri,
                metadata=lidar_metadata,
                id=id,
                wait_for_completion=not buffered_write,
                buffered_write=buffered_write
            )
        elif lidar_bytes is not None:
            id = self.get_asset_manager(
                AssetsConstants.LIDARS_ASSET_ID).put_asset(
                file_object=lidar_bytes,
                metadata=lidar_metadata,
                id=id,
                wait_for_completion=not buffered_write,
                buffered_write=buffered_write,
                add_to_redis_cache=add_to_cache
            )
        else:
            raise ValueError(
                "Either file path or url, or uri must be provided ")

        # If session_uid does not exist skip creating and pushing the entity
        if session_uid and add_to_session:
            entity_dict = {
                "session": session_uid,
                "timestamp": timestamp,
                "enrichments": enrichments or [],
                "entity_name": EntityNames.LIDAR,
                "media_asset_id": id,
                "entity_id": get_guid(),
                "entity_value": id,
                "entity_type": EntityTypes.MEDIA,
                "influence": EntityInfluenceTypes.INTERVAL
            }
            self.add_entity(entity_dict=entity_dict)

        self.compress_lidars(
            ids=[id],
            skip_factors=[1, 10, 100]
        )
        return id

    def extract_lidars_from_s8(
            self,
            folder_uri: str,
            sensor: Optional[str] = None,
            session_uid: Optional[str] = None,
            fps: Optional[float] = None,
            extract_start_time: Optional[Union[datetime, str]] = None,
            extract_end_time: Optional[Union[datetime, str]] = None,
            set_id: Optional[str] = None,
            wait_for_completion: bool = False
    ) -> str:

        payload = {"folder_uri": folder_uri, "sensor": sensor or folder_uri.split("/")[-1]}

        if session_uid:
            payload["session_uid"] = session_uid
        if extract_start_time:
            payload["extract_start_time"] = datetime_or_str_to_iso_utc(
                extract_start_time)
        if extract_end_time:
            payload["extract_end_time"] = datetime_or_str_to_iso_utc(
                extract_end_time)
        if fps:
            payload["fps"] = fps
        if set_id:
            payload["set_id"] = set_id
        resp = self.requests.post(
            "lidars/extract_lidars_s8/",
            trailing_slash=False,
            json=payload)

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(job_id)
        return job_id

    def cleanup_annotation_masks(self,
                                 ids: Optional[List[str]] = None,
                                 search: Optional[dict] = None,
                                 force_reclean: bool = False,
                                 wait_for_completion: bool = True) -> str:
        payload = {
            "force_reclean": force_reclean
        }
        if ids is not None:
            payload["ids"] = ids
        if search is not None:
            payload["search"] = search

        resp = self.requests.post(
            "annotations/cleanup_annotation_masks/",
            trailing_slash=False,
            json=payload)
        if not resp.ok:
            raise ResponseError(
                "Could not clean_up the annotations: {}".format(
                    resp.content))

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(
                job_id, max_wait_sec=max(
                    10 * len(ids), 60))
        return job_id

    def annotations_to_objects(self,
                               ids: Optional[List[str]] = None,
                               search: Optional[dict] = None,
                               create_objects: bool = False,
                               margin_ratio: float = 0.1,
                               output_set_id: str = None,
                               session_uid: Optional[str] = None,
                               add_to_session: bool = True,
                               wait_for_completion: bool = True,
                               progress_callback: Optional[Callable] = None) -> str:

        """Extracts objects from annotations.

        Converts annotations to objects from annotations that have been previously ingested into
        SceneBox.  Gets labels from the asset's auxiliary metadata.

        Parameters
        ----------
        ids:
            IDs of the previously ingested annotations.
        search:
            Query to locate the data subset of interest.  Filters through existing
            assets according to the dictionary passed.
        create_objects:
            If False and if mask annotations are available for the given asset id, adds the area of each annotation
            to the asset's auxiliary metadata.  Else, additionally creates object entities from the existing
            annotation data associated with the passed ID.
        margin_ratio:
            Widens/shrinks the object's area of interest.  A larger number increases the object's margin.
            Minimum value 0.
        output_set_id:
            The name of the set to add the created objects to, if create_objects is True.  Otherwise, has no effect.
        session_uid:
            The session associated with the objects.  Adds an event interval (and thus, an entity) to the existing
            session.
        add_to_session:
            Whether to add the object to the session with session_uid for session search
        wait_for_completion:
            If True, polls until job is complete.  Raises an error if job fails to finish after (2 * #ids) seconds
            if IDs are supplied.  Otherwise, continues execution and does not raise an error if the job does not
            complete.
        progress_callback:
        Callback function to log the progress of the inference job. The callback should accept a parameter of type
        float for progress.

        Returns
        -------
        str
            ID of the Job that runs/ran the object extraction job.

        Raises
        ------
        ResponseError
             If endpoint call does not get a valid response
        """
        payload = {'create_objects': create_objects,
                   'margin_ratio': margin_ratio,
                   'output_set_id': output_set_id
                   }

        if ids is not None:
            payload["ids"] = ids
        if search is not None:
            payload["search"] = search

        if session_uid:
            payload["session_uid"] = session_uid
            payload["add_to_session"] = add_to_session

        resp = self.requests.post(
            "annotations/annotations_to_objects/",
            trailing_slash=False,
            json=payload)
        if not resp.ok:
            raise ResponseError(
                "Could not create objects from annotations: {}".format(
                    resp.content))

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            if ids is not None:
                self._wait_for_job_completion(
                    job_id, max_wait_sec=2 * len(ids),
                    progress_callback=progress_callback)
            else:
                self._wait_for_job_completion(job_id, progress_callback=progress_callback,
                                              increments_sec=5)
        return job_id

    def compress_masks_batch(
            self,
            thumbnail_tag: str,
            ids: Optional[List[str]] = None,
            search: Optional[dict] = None,
            wait_for_completion: bool = True) -> str:

        payload = {}
        if ids is not None:
            payload["ids"] = ids
        if search is not None:
            payload["search"] = search

        payload["thumbnail_tag"] = thumbnail_tag

        resp = self.requests.post(
            "annotations/compress_masks_batch/",
            trailing_slash=False,
            json=payload)
        if not resp.ok:
            raise ResponseError(
                "Could not create objects from annotations: {}".format(
                    resp.content))

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(job_id)
        return job_id

    def get_annotation_sources(self,
                               search: Optional[dict] = None) -> List[Optional[dict]]:

        """Returns all sources of annotation for all images or images that satisfy a search query

        Parameters
        ----------
        search:
            Query to locate the data subset of interest.  Filters through existing
            assets according to the dictionary passed.

        Returns
        -------
        List
            a list of dictionaries that include provider, version, annotation_group,
            and annotation_type information for existing annotation sources

        """
        payload = search if search is not None else {}

        resp = self.requests.post(
            "annotations/annotation_sources/",
            trailing_slash=False,
            json=payload)
        if not resp.ok:
            raise ResponseError(
                "Could not fetch annotation sources: {}".format(
                    resp.content))

        return resp.json()

    def model_inference(self,
                        asset_type: str = AssetsConstants.IMAGES_ASSET_ID,
                        ids: Optional[List[str]] = None,
                        search: Optional[dict] = None,
                        model: str = MLModelConstants.MASK_RCNN_MODEL,
                        obtain_mask: bool = False,
                        obtain_bbox: bool = False,
                        obtain_object_entities: bool = False,
                        obtain_embeddings: bool = False,
                        threshold: Optional[float] = None,
                        classes_of_interest: Optional[List[str]] = None,
                        wait_for_completion: bool = False,
                        progress_callback: Optional[Callable] = None,
                        additional_params: Optional[Dict] = None
                        ):

        """Perform inference from a list of supported models. See for supported models.

        Extracts inferences such as masks, bounding boxes, objects, and/or embeddings on an asset of choice using a
        model of choice.  Select from Mask RCNN, StarDist, or Image Intensity Histogram.

        Parameters
        ----------
        asset_type:
            The type of assets to perform model inference on.
        ids:
            IDs of the previously uploaded assets on which to perform a model inference.
        search:
            Query to locate the data subset of interest.  Filters through existing
            assets according to the dictionary passed.
        model:
            The model to perform the inference with.  Select from Mask RCNN ('mrcnn'), StarDist ('stardist'), or Image
            Intensity Histogram ('histogram')
        obtain_mask:
            If True and model is Mask RCNN or StarDist, infer segmentations and add masks as a
            scenebox.models.annotation.SegmentationAnnotation.
            Otherwise, do nothing but log an error if the model chosen is Image Intensity Histogram.
        obtain_bbox:
            If True and model is Mask RCNN or StarDist, infer bounding boxes from masks add the masks as a
            scenebox.models.annotation.BoundingBoxAnnotation.
            Otherwise, do nothing but log an error if the model chosen is Image Intensity Histogram.
        obtain_object_entities:
            If True and model is Mask RCNN, obtains and adds object entities.
            Otherwise, do nothing but log an error if the model chosen is Image Intensity Histogram or StarDist.
        obtain_embeddings:
            If True, extract asset embeddings with the chosen model.
        image_size:
            If not None, resizes the input images to the provided size
            before performing inference(s).
            Otherwise, do nothing.
        wait_for_completion:
            If True, polls until job is complete.
            Otherwise, continues execution and does not raise an error if the job does not complete.
        progress_callback:
            Callback function to log the progress of the inference job. The callback should accept a parameter of type
            float for progress.
        additional_params:
            A JSON formatted key-value pair structure for additional parameters such as threshold and
            classes of interest supported by the chosen model.
        """

        payload = {
            "model": model,
            "obtain_mask": obtain_mask,
            "obtain_bbox": obtain_bbox,
            "obtain_object_entities": obtain_object_entities,
            "obtain_embeddings": obtain_embeddings,
            "asset_type": asset_type,
            "ids": ids or []
        }
        if threshold is not None:
            payload["threshold"] = threshold

        if classes_of_interest is not None:
            payload["classes_of_interest"] = classes_of_interest

        if search is not None:
            payload["search"] = search

        if additional_params is not None:
            # Combine params dictionaries
            payload = {**payload, **additional_params}

        resp = self.requests.post(
            "models/model_inference/",
            trailing_slash=False,
            json=payload)

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(job_id, progress_callback=progress_callback,
                                          increments_sec=5)
        return job_id

    def image_properties_enrichment(self,
                                    asset_type: str = AssetsConstants.IMAGES_ASSET_ID,
                                    properties: List[str] = None,
                                    ids: Optional[List[str]] = None,
                                    search: Optional[dict] = None,
                                    wait_for_completion: bool = False,
                                    progress_callback: Optional[Callable] = None,
                                    additional_params: Optional[Dict] = None
                                    ):

        """Enrich images or objects with classical image processing features.

        Enrich image or object assets with classical image properties/features such as brightness or contrast
        and add this as auxiliary metadata for the asset.

        Parameters
        ----------
        asset_type:
            The type of assets to perform model inference on.
        ids:
            IDs of the previously uploaded assets on which to perform a model inference.
        search:
            Query to locate the data subset of interest.  Filters through existing
            assets according to the dictionary passed.
        properties:
            A list of strings for each property to be added to the metadata of the asset.
            Choose from ['mean_brightness', 'rms_contrast', 'variance_of_laplacian'].
        wait_for_completion:
            If True, polls until job is complete.
            Otherwise, continues execution and does not raise an error if the job does not complete.
        progress_callback:
            Callback function to log the progress of the inference job. The callback should accept a parameter of type
            float for progress.
        additional_params:
            A JSON formatted key-value pair structure for additional parameters such as batch_size for the task.
        """

        payload = {
            "ids": ids or [],
            "properties": properties,
            "asset_type": asset_type,
        }

        if search is not None:
            payload["search"] = search

        if additional_params is not None:
            # Combine params dictionaries
            payload = {**payload, **additional_params}

        resp = self.requests.post(
            "images/image_properties_enrichment/",
            trailing_slash=False,
            json=payload)

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(job_id, progress_callback=progress_callback,
                                          increments_sec=5)
        return job_id

    def submit_enricher(self,
                        enricher_class: Type[Enricher]) -> str:
        if not issubclass(enricher_class, Enricher):
            raise AssetError("Problem with Enricher class")

        metadata = {
            "version": enricher_class.version,
            "type": "enricher",
            TIMESTAMP_FIELD: datetime.utcnow()
        }

        id = "{}_{}".format(enricher_class.__name__, enricher_class.version)

        return self.get_asset_manager(asset_type=AssetsConstants.UDFS_ASSET_ID).put_asset(
            metadata=metadata,
            file_object=self.__serialize_class(enricher_class),
            id=id
        )

    def enricher_dry_run(self,
                         enricher_class: Type[Enricher],
                         metadata: dict
                         ):

        enricher_id = self.submit_enricher(enricher_class=enricher_class)

        payload = {
            "udf_ids": [enricher_id],
            "metadata": metadata
        }

        resp = self.requests.post(
            "udfs/enricher_dry_run/",
            trailing_slash=False,
            json=payload)

        return resp.json()

    def enricher_batch(
            self,
            enricher_class: Type[Enricher],
            assets_type: str,
            ids: Optional[List[str]] = None,
            search: Optional[dict] = None,
            wait_for_completion: bool = False
    ) -> str:

        payload = {
            "ids": ids or []
        }

        if search is not None:
            payload["search"] = search

        enricher_id = self.submit_enricher(enricher_class=enricher_class)

        payload["udf_ids"] = [enricher_id]
        payload["assets_type"] = assets_type

        resp = self.requests.post(
            "udfs/batch/",
            trailing_slash=False,
            json=payload)

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(job_id)
        return job_id

    def register_webhook(self,
                         webhook_class: Type[Webhook]) -> str:
        if not issubclass(webhook_class, Webhook):
            raise AssetError("Input is not a webhook class")

        metadata = {
            "version": webhook_class.version,
            "type": "webhook",
            TIMESTAMP_FIELD: datetime.utcnow()
        }
        webhook_id = self.get_asset_manager(asset_type=AssetsConstants.UDFS_ASSET_ID).put_asset(
            metadata=metadata,
            file_object=self.__serialize_class(webhook_class),
            id="{}_{}".format(webhook_class.__name__, webhook_class.version)
        )

        return webhook_id

    def run_script(self,
                   script_class: Type[Script],
                   wait_for_completion: bool = True,
                   **kwargs
                   ) -> str:
        if not issubclass(script_class, Script):
            raise AssetError("Input is not a script class")

        metadata = {
            "version": script_class.version,
            "type": "script",
            TIMESTAMP_FIELD: datetime.utcnow()
        }
        script_id = self.get_asset_manager(asset_type=AssetsConstants.UDFS_ASSET_ID).put_asset(
            metadata=metadata,
            file_object=self.__serialize_class(script_class),
            id="{}_{}".format(script_class.__name__, script_class.version)
        )

        resp = self.requests.put(
            "udfs/run_script/{}".format(script_id),
            trailing_slash=False,
            json=kwargs)

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(job_id)
        return job_id

    def extract_images_from_videos(
            self,
            video_id: str,
            extract_start_time: Optional[Union[datetime, str]] = None,
            extract_end_time: Optional[Union[datetime, str]] = None,
            fps: Optional[float] = None,
            set_id: Optional[id] = None,
            wait_for_completion: bool = False
    ) -> str:

        payload = {
            "id": video_id
        }
        if extract_start_time:
            payload["extract_start_time"] = datetime_or_str_to_iso_utc(
                extract_start_time)

        if extract_end_time:
            payload["extract_end_time"] = datetime_or_str_to_iso_utc(
                extract_end_time)

        if fps:
            payload["fps"] = fps

        if set_id:
            payload["set_id"] = set_id

        resp = self.requests.post(
            "videos/extract_images/",
            trailing_slash=False,
            json=payload)

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(job_id)
        return job_id

    def extract_images_s8(
            self,
            folder_uri: Optional[str] = None,
            sensor: Optional[str] = None,
            session_uid: Optional[str] = None,
            fps: Optional[float] = None,
            extract_start_time: Optional[Union[datetime, str]] = None,
            extract_end_time: Optional[Union[datetime, str]] = None,
            set_id: Optional[str] = None,
            wait_for_completion: bool = False
    ) -> str:

        payload = {}
        if extract_start_time:
            payload["extract_start_time"] = datetime_or_str_to_iso_utc(
                extract_start_time)

        if extract_end_time:
            payload["extract_end_time"] = datetime_or_str_to_iso_utc(
                extract_end_time)

        if folder_uri:
            payload["folder_uri"] = folder_uri

        if sensor:
            payload["sensor"] = sensor

        if session_uid:
            payload["session_uid"] = session_uid

        if fps:
            payload["fps"] = fps

        if set_id:
            payload["set_id"] = set_id

        resp = self.requests.post(
            "videos/extract_images_s8/",
            trailing_slash=False,
            json=payload)

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(job_id)
        return job_id

    def extract_subclip_from_videos(
            self,
            video_id: str,
            subclip_id: Optional[str] = None,
            extract_start_time: Optional[Union[datetime, str]] = None,
            extract_end_time: Optional[Union[datetime, str]] = None,
            set_id: Optional[str] = None,
            wait_for_completion: bool = False
    ) -> str:

        payload = {
            "id": video_id
        }
        if extract_start_time:
            payload["extract_start_time"] = datetime_or_str_to_iso_utc(
                extract_start_time)

        if extract_end_time:
            payload["extract_end_time"] = datetime_or_str_to_iso_utc(
                extract_end_time)

        if subclip_id:
            payload["subclip_id"] = subclip_id

        if set_id:
            payload["set_id"] = set_id

        resp = self.requests.post(
            "videos/extract_subclip_video/",
            trailing_slash=False,
            json=payload)

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(job_id)
        return job_id

    def extract_video_from_s8(
            self,
            folder_uri: str,
            sensor: Optional[str] = None,
            session_uid: Optional[str] = None,
            video_id: Optional[str] = None,
            extract_start_time: Optional[Union[datetime, str]] = None,
            extract_end_time: Optional[Union[datetime, str]] = None,
            tags: Optional[List[str]] = None,
            set_id: Optional[str] = None,
            skip_frame: int = 0,
            wait_for_completion: bool = False
    ) -> str:

        payload = {"folder_uri": folder_uri,
                   "sensor": sensor or folder_uri.split("/")[-1],
                   "skip_frame": skip_frame}

        if session_uid:
            payload["session_uid"] = session_uid
        if tags:
            payload["tags"] = tags
        if extract_start_time:
            payload["extract_start_time"] = datetime_or_str_to_iso_utc(
                extract_start_time)
        if extract_end_time:
            payload["extract_end_time"] = datetime_or_str_to_iso_utc(
                extract_end_time)
        if video_id:
            payload["video_id"] = video_id
        if set_id:
            payload["set_id"] = set_id
        resp = self.requests.post(
            "videos/extract_video_s8/",
            trailing_slash=False,
            json=payload)

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(job_id)
        return job_id

    def images_to_video(self,
                        session_uid: str,
                        sensor: str,
                        fps: Optional[int] = None,
                        search: Optional[dict] = None,
                        image_format: Optional[str] = None,
                        video_id: Optional[str] = None,
                        wait_for_completion: bool = False) -> str:

        payload = {
            "id": video_id,
            "sensor": sensor,
            "search": search,
            "image_format": image_format,
            "session_uid": session_uid,
            "video_id": video_id or get_guid(),
            "fps": fps
        }
        resp = self.requests.post(
            "videos/images_to_video/",
            trailing_slash=False,
            json=payload)
        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(job_id)
        return job_id

    def similarity_search_bulk_index(
            self,
            embedding_ids: Optional[List[str]] = None,
            search_dic: Optional[dict] = None,
            wait_for_completion: bool = False) -> str:
        """Bulk indexes embeddings to allow for similarity search.

        Existing embeddings are mapped to a high-dimensional vector space. Then a distance measure is applied to find
        which assets are the most similar. After running this method, similarity search is available for the assets
        associated with the inputted embeddings.

        Parameters
        ----------
        embedding_ids:
            The IDs of the embeddings to bulk index.
        search_dic:
            Query to locate the data subset of interest.  Filters through existing
            assets according to the dictionary passed.
        wait_for_completion:
            If True, polls until job is complete.  Raises an error if job fails to finish after (2 * #ids) seconds
            if IDs are supplied.  Otherwise, continues execution and does not raise an error if the job does not
            complete.

        Returns
        -------
        str
            The ID of the Job that attempts to perform bulk indexing.
        """

        payload = {}
        if embedding_ids is not None:
            payload["embedding_ids"] = embedding_ids
        if search_dic is not None:
            payload["search_dic"] = search_dic

        # logger.debug("Bulk index payload: {}".format(payload))

        resp = self.requests.post(
            "similarity_search/bulk_index/",
            trailing_slash=False,
            json=payload)

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(job_id)

        return job_id

    def create_umap(
            self,
            asset_type: str,
            index_name: str,
            search_dic: Optional[dict] = None,
            n_neighbors: int = 20,
            min_dist: float = 0.3,
            progress_callback: Optional[Callable] = None,
            wait_for_completion: bool = False) -> str:

        """Applies UMAP onto existing asset indices.

        Applies UMAP (Uniform Manifold Approximation and Projection) to existing asset embeddings, and outputs a visual
        representation of the embeddings space.  Can be viewed from the "Embeddings" view on the SceneBox web app.

        .. note:: Embeddings must be indexed before this function can be used.

        Parameters
        ----------
        asset_type:
            The type of asset to apply UMAP on.
        index_name:
            index_name of the embeddings.  Used to filter through the embeddings metadata.
        search_dic:
            Query to locate the data subset of interest.  Filters through existing
            assets according to the dictionary passed.
        n_neighbors:
            Controls how UMAP balances local vs. global structure in data.  Low values of ``n_neighbours`` forces UMAP
            to concentrate on local structure, while high values push UMAP to look at larger neighbourhoods of each
            point.
        min_dist:
            Controls how tightly UMAP is allowed to pack points together.
        progress_callback:
            Callback function to log the progress of the inference job. The callback should accept a parameter of type
            float for progress.
        wait_for_completion:
            If True, polls until job is complete.
            Otherwise, continues execution and does not raise an error if the job does not complete.

        Returns
        -------
        str
            The job_id of the Job that applies UMAP.
        """

        payload = {
            "search": search_dic or {},
            "n_neighbors": n_neighbors,
            "min_dist": min_dist,
            "index_name": index_name,
            "asset_type": asset_type,
        }

        resp = self.requests.post(
            "embeddings/create_umap_from_assets/",
            trailing_slash=False,
            json=payload)

        job_id = resp.json()["job_id"]
        if wait_for_completion:
            self._wait_for_job_completion(job_id,
                                          progress_callback=progress_callback,
                                          increments_sec=5)

        return job_id

    def search_similar_assets(self,
                              id: str,
                              similar_asset_count: int = 10,
                              asset_type: str = AssetsConstants.IMAGES_ASSET_ID,
                              embedding_space: Optional[str] = None
                              ) -> List[str]:
        """Find top k similar assets to an existing asset with embeddings.

       Parameters
       ----------
       id:
           asset id.
       similar_asset_count:
           count of similar assets (10 by default)
       asset_type:
           type of assets (Images by default)
       embedding_space:
           embedding space in which similarity is performed on. Ineffective/optional if there is only one embedding
           space

       Returns
       -------
       list
           list of asset ids similar to the asset sorted by most to least similar.
       """

        metadata = self.get_asset_manager(asset_type=asset_type).get_metadata(id=id)
        embeddings = metadata.get("embeddings", {})

        if len(embeddings) == 1:
            embedding_space = list(embeddings.keys())[0]

        elif len(embeddings) > 1:
            if not embedding_space:
                raise SimilaritySearchError("embedding space should be specified")
            elif embedding_space not in embeddings:
                raise SimilaritySearchError("{} is not in the embeddings of asset".format(embedding_space))
        else:
            # len(embeddings) == 0:
            raise SimilaritySearchError("{} with id={} does not have embeddings".format(asset_type, id))

        payload = {
            "ids": [id],
            "similar_asset_count": similar_asset_count,
            "index_name": embedding_space,
            "asset_type": asset_type,
        }

        resp = self.requests.post(
            "similarity_search/similarity_search/",
            trailing_slash=False,
            json=payload)

        if not resp.ok:
            raise SimilaritySearchError(
                "finding {} assets similar to {} failed: {}".format(asset_type, id, resp.content))

        return resp.json()[0]

    def add_user(self,
                 email: str,
                 username: str,
                 role: str,
                 organization: str) -> Dict:
        """Add a new SceneBox user account to your organization.

        Parameters
        ----------
        email:
            E-mail of the user to add.
        username:
            Username of the user to add.
        role:
            Role of the user to add. Choose from admin, tester, health_checker, data_provider, data_user, or
            public_user. See the SceneBox user guides for more information.
        organization:
            Organization to add the user to.

        Returns
        -------
        dict
            The successfully created user ``username``, ``email``, ``role``, and ``organization``.

        """
        req = self.requests.post(
            "identity_manager/user",
            json={
                "username": username,
                "email": email,
                "role": role,
                "organization": organization},
            remove_version=True
        )
        if not req.ok:
            raise InvalidAuthorization(
                "cannot add user {}-{}".format(username, req.text))
        doc = req.json()

        user_dict = {
            "username": username,
            "organization_name": doc.get("organization"),
            "token": doc.get("token"),
            "role": doc.get("role"),
            "email": doc.get("email")
        }

        return user_dict

    def modify_user(
            self,
            username: str,
            email: Optional[str] = None,
            role: Optional[str] = None,
            organization: Optional[str] = None):
        """Modify an existing user account.

        Please note that an existing user's username cannot be changed.

        Parameters
        ----------
        username:
            The user username to modify.
        email:
            The new user email.
        role:
            The new user role. Choose from admin, tester, health_checker, data_provider, data_user, or
            public_user. See the SceneBox user guides for more information.
        organization:
            The new user organization.
        """
        payload = {}

        if email:
            payload.update({"email": email})
        if role:
            payload.update({"role": role})
        if organization:
            payload.update({"organization": organization})

        req = self.requests.put(
            "identity_manager/user/{}".format(username),
            json=payload,
            remove_version=True
        )
        if not req.ok:
            raise InvalidAuthorization(
                "cannot modify user {}-{}".format(username, req.text))

    def delete_user(self, username: str):
        req = self.requests.delete(
            "identity_manager/user/{}".format(username),
            remove_version=True
        )
        if not req.ok:
            raise InvalidAuthorization(
                "cannot delete user {}-{}".format(username, req.text))

    def list_users(self) -> List[Dict]:
        """Returns a list of all users.

        Returns
        -------
        List[Dict]:
            Returns a dictionary of username, organization name, role, email, and token for each user.
        """
        req = self.requests.get("identity_manager/user", remove_version=True)
        return req.json()

    def add_ownership(self, owner: str, access: str):
        req = self.requests.post(
            "identity_manager/ownership",
            json={
                "owner": owner,
                "access": access
            },
            remove_version=True
        )
        if not req.ok:
            raise InvalidAuthorization(
                "cannot add ownership for owner {} have access to {}-{}".format(owner, access, req.text))

    def revoke_ownership(self, owner: str, access: str):
        self.requests.delete("identity_manager/ownership",
                             json={
                                 "owner": owner,
                                 "access": access
                             },
                             remove_version=True)

    def list_ownerships(self) -> List[Dict]:
        """Returns a list of all ownerships.

        Returns
        -------
        List[Dict]
            A list of what ownerships the user associated with

        """
        req = self.requests.get(
            "identity_manager/ownership",
            remove_version=True)
        return req.json()

    def delete_all_data(self):
        self.requests.post(
            "maintenance/cleanup/",
            remove_version=True)

    def __display_url(self,
                      url: str):
        try:
            safe_url = quote(url, safe="/:?=&")
            full_url = "{}{}".format(self.front_end_url, safe_url)
            display(Javascript('window.open("{url}");'.format(url=full_url)))
        except NameError:
            logger.error(
                "Cannot display in this environment- Please use Colab or Jupyter")

    def display_image(self, image_id: str):
        """Display a given image on the SceneBox web app.

        Note
        ----
        This method will only run properly from a Google Colab or Jupyter notebook.  Please also make sure
        that you are logged into the SceneBox web app, and that pop-ups are allowed in your browser.

        Parameters
        ----------
        image_id:
            The ID of the image to display on the SceneBox web app.
        """
        self.__display_url(url="images?image={}".format(image_id))

    def display_video(self, video_id: str):
        """Display a given image on the SceneBox web app.

        Note
        ----
        This method will only run properly from a Google Colab or Jupyter notebook.  Please also make sure
        that you are logged into the SceneBox web app, and that pop-ups are allowed in your browser.

        Parameters
        ----------
        video_id:
            The ID of the video to display on the SceneBox web app.
        """
        self.__display_url(url="videos?video={}".format(video_id))

    def display_object(self, object_id: str):
        """Display a given object on the SceneBox web app.

        Note
        ----
        This method will only run properly from a Google Colab or Jupyter notebook.  Please also make sure
        that you are logged into the SceneBox web app, and that pop-ups are allowed in your browser.

        Parameters
        ----------
        object_id:
            The ID of the object to display on the SceneBox web app.
        """
        self.__display_url(url="objects?object={}".format(object_id))

    def display_lidar(self, lidar_id: str):
        """Display a given Lidar on the SceneBox web app.

        Note
        ----
        This method will only run properly from a Google Colab or Jupyter notebook.  Please also make sure
        that you are logged into the SceneBox web app, and that pop-ups are allowed in your browser.

        Parameters
        ----------
        lidar_id:
            The ID of the Lidar to display on the SceneBox web app.
        """
        self.__display_url(url="lidars?lidar={}".format(lidar_id))

    def display_session(self, session_uid: str):
        """Display a given session on the SceneBox web app.

        Note
        ----
        This method will only run properly from a Google Colab or Jupyter notebook.  Please also make sure
        that you are logged into the SceneBox web app, and that pop-ups are allowed in your browser.

        Parameters
        ----------
        session_uid:
            The ID of the session to display on the SceneBox web app.
        """
        self.__display_url(url="sessions?session_uid={}".format(session_uid))

    def display_set(self, set_id: str):
        """Display a given set on the SceneBox web app.

        Note
        ----
        This method will only run properly from a Google Colab or Jupyter notebook.  Please also make sure
        that you are logged into the SceneBox web app, and that pop-ups are allowed in your browser.

        Parameters
        ----------
        set_id:
            The ID of the set to display on the SceneBox web app.
        """
        self.__display_url(url="sets?set={}".format(set_id))

    def display_projects(self, project_id: str):
        """Display a given project on the SceneBox web app.

        Note
        ----
        This method will only run properly from a Google Colab or Jupyter notebook.  Please also make sure
        that you are logged into the SceneBox web app, and that pop-ups are allowed in your browser.

        Parameters
        ----------
        project_id:
            The ID of the project to display on the SceneBox web app.
        """
        self.__display_url(url="projects?project={}".format(project_id))

    def display_dashboard(self, dashboard_name: str):
        """Display a given dashboard on the SceneBox web app.

        Note
        ----
        This method will only run properly from a Google Colab or Jupyter notebook.  Please also make sure
        that you are logged into the SceneBox web app, and that pop-ups are allowed in your browser.

        Parameters
        ----------
        dashboard_name:
            The Name of the dashboard to display on the SceneBox web app.
        """
        self.__display_url(url="dashboard?dashboard={}".format(dashboard_name))

    def clear_cache(self, all_organizations: bool = False, partitions: Optional[List[str]]=None):
        '''
        Clears scene engine's Redis cache by organization
        Args:
            all_organizations: if True, Redis cache for all organization is cleared. Requires Admin privilege
            partitions: list of partitions (like images, sets, annotations) to clear their cache, if not set, all is cleared

        Returns:
            ACK_OK_RESPONSE on success
        '''
        payload = {"partitions": partitions} if partitions else {}
        return self.requests.post("clear_cache", params={"all_organizations": all_organizations}, remove_version=True,
                                  json=payload).json()


class SceneEngineRequestHandler:
    """Helper for making authenticated requests to the scene engine."""

    def __init__(
            self,
            scene_engine_url,
            auth_token=None):
        self.scene_engine_url = scene_engine_url
        self.auth_token = auth_token

    def with_auth(self,
                  auth_token: Optional[str] = None,
                  ):
        if auth_token:
            self.auth_token = auth_token

        return self

    def get(self,
            route,
            trailing_slash=False,
            params=None,
            headers=None,
            remove_version=False):
        return self.__make_scene_engine_request(
            method="get",
            route=route,
            trailing_slash=trailing_slash,
            params=params,
            headers=headers,
            remove_version=remove_version)

    def post(
            self,
            route,
            trailing_slash=False,
            params=None,
            json=None,
            headers=None,
            remove_version=False):
        return self.__make_scene_engine_request(
            method="post",
            route=route,
            trailing_slash=trailing_slash,
            params=params,
            json=json,
            headers=headers,
            remove_version=remove_version)

    def put(
            self,
            route,
            trailing_slash=False,
            params=None,
            json=None,
            headers=None,
            remove_version=False):
        return self.__make_scene_engine_request(
            method="put",
            route=route,
            trailing_slash=trailing_slash,
            params=params,
            json=json,
            headers=headers,
            remove_version=remove_version)

    def delete(
            self,
            route,
            trailing_slash=False,
            params=None,
            json=None,
            headers=None,
            remove_version=False):
        return self.__make_scene_engine_request(
            method="delete",
            route=route,
            trailing_slash=trailing_slash,
            params=params,
            json=json,
            headers=headers,
            remove_version=remove_version)

    def __make_scene_engine_request(
            self,
            method: str,
            route: str = "",
            trailing_slash: bool = False,
            params: Optional[dict] = None,
            json: Optional[dict] = None,
            headers: Optional[dict] = None,
            remove_version: bool = False):
        assert method in {"get", "post", "put", "delete"}
        url = self.__get_scene_engine_url(
            route, trailing_slash, remove_version)
        request_ = getattr(requests, method)
        if self.auth_token:
            if not params:
                params = {}
            params["token"] = self.auth_token
        resp = request_(
            url,
            params=params,
            json=json,
            headers=headers)
        if not resp.ok:
            raise ResponseError(
                "{} ::: {} with token::: {}".format(
                    resp.reason, resp.content, self.auth_token))
        return resp

    def __get_scene_engine_url(self, route, trailing_slash, remove_version):

        if remove_version:
            scene_engine_url_ = re.sub(
                "{}".format(VERSION_POSTFIX), "", self.scene_engine_url)
        else:
            scene_engine_url_ = self.scene_engine_url

        url = join(scene_engine_url_, route)
        if trailing_slash and not url.endswith("/"):
            url += "/"
        if not trailing_slash and url.endswith("/"):
            url = url[:-1]
        return url
