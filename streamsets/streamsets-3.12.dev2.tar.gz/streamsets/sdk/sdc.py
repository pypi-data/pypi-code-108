# Copyright 2019 StreamSets Inc.

"""Abstractions for interacting with StreamSets Data Collector."""

import copy
import logging
import io
import json
import re
import time
import zipfile
from datetime import datetime
from functools import wraps
from urllib.parse import urlparse
from uuid import uuid4

import requests

from . import sdc_api, sdc_models
from .constants import ENGINE_AUTHENTICATION_METHOD_FORM
from .exceptions import ValidationError
from .utils import SeekableList

logger = logging.getLogger(__name__)

# The `#:` constructs at the end of assignments are part of Sphinx's autodoc functionality.
DEFAULT_SDC_USERNAME = 'admin'  #:
DEFAULT_SDC_PASSWORD = 'admin'  #:
DEFAULT_START_STATUSES_TO_WAIT_FOR = ['RUNNING', 'FINISHED']  #:
DEFAULT_SNAPSHOT_TIMEOUT = 30  #:
DEFAULT_START_TIMEOUT = 300  #:
DEFAULT_STOP_TIMEOUT = 300  #:
DEFAULT_WAIT_FOR_METRIC_TIMEOUT = 30 #:
DEFAULT_WAIT_FOR_STATUS_TIMEOUT = 30 #:
PIPELINE_FILENAME_FORMAT = 'sdc_pipelines_{}.zip'


class DataCollector:
    """Class to interact with StreamSets Data Collector.

    If connecting to an StreamSets Control Hub-registered instance of Data Collector, create an instance
    of :py:class:`streamsets.sdk.ControlHub` instead of instantiating with a ``username`` and ``password``.

    Args:
        server_url (:obj:`str`): URL of an existing SDC deployment with which to interact.
        username (:obj:`str`, optional): SDC username. Default: :py:const:`streamsets.sdk.sdc.DEFAULT_SDC_USERNAME`.
        password (:obj:`str`, optional): SDC password. Default: :py:const:`streamsets.sdk.sdc.DEFAULT_SDC_PASSWORD`.
        authentication_method (:obj:`str`, optional): StreamSets Data Collector authentication method.
            Default: :py:const:`streamsets.sdk.constants.ENGINE_AUTHENTICATION_METHOD_FORM`.
        accounts_authentication_token (:obj:`str`, optional): StreamSets Accounts authentication token.
            Default: ``None``
        accounts_server_url (:obj:`str`, optional): StreamSets Accounts server base URL. Default: ``None``
        control_hub (:py:class:`streamsets.sdk.ControlHub`, optional): A StreamSets Control Hub instance to use
            for SCH-registered Data Collectors. Default: ``None``.
        dump_log_on_error (:obj:`bool`): Whether to output Data Collector logs when exceptions
            are raised by certain methods. Default: ``False``
    """
    VERIFY_SSL_CERTIFICATES = True  #:

    def __init__(self,
                 server_url,
                 username=None,
                 password=None,
                 authentication_method=ENGINE_AUTHENTICATION_METHOD_FORM,
                 accounts_authentication_token=None,
                 accounts_server_url=None,
                 control_hub=None,
                 dump_log_on_error=False,
                 **kwargs):
        self.server_url = server_url
        self.authentication_method = authentication_method
        self.accounts_authentication_token = accounts_authentication_token
        self.accounts_server_url = accounts_server_url
        self.username = username or DEFAULT_SDC_USERNAME
        self.password = password or DEFAULT_SDC_PASSWORD
        self.control_hub = control_hub
        self.dump_log_on_error = dump_log_on_error

        # SDC definitions should be an attribute of this class, but we use a property for
        # access to handle necessary setup and synchronization tasks, so indicate internal use for
        # the underlying attribute with a leading underscore.
        self._definitions = None

        # Instances of :py:class:`streamsets.sdk.sdc_models.PipelineBuilder` require a blank pipeline (i.e.
        # an empty pipeline JSON) from our particular Data Collector version. We keep track of this with an
        # instance attribute to avoid repetitive API calls.
        self._pipeline = None

        if self.server_url:
            sch_headers = {
                'X-SS-User-Auth-Token': self.control_hub.api_client.session.headers['X-SS-User-Auth-Token']
            } if self.control_hub else {}
            session_attributes = {'verify': self.VERIFY_SSL_CERTIFICATES}
            self.api_client = sdc_api.ApiClient(server_url=self.server_url,
                                                authentication_method=self.authentication_method,
                                                accounts_authentication_token=accounts_authentication_token,
                                                accounts_server_url=accounts_server_url,
                                                username=self.username,
                                                password=self.password,
                                                headers=sch_headers,
                                                session_attributes=session_attributes,
                                                **kwargs)

            # Keep track of the server host so that tests that may need it (e.g. to set configurations) can use it.
            self.server_host = urlparse(self.server_url).netloc.split(':')[0]

        else:
            self.server_host = None
            self.api_client = None

    @property
    def version(self):
        """Return the version of the Data Collector.

        Returns:
           :obj:`str`: The version string.
        """
        return self.api_client.get_sdc_info()['version']

    @property
    def sdc_configuration(self):
        """Return all configurations for StreamSets Data Collector.

        Returns:
            A :obj:`dict` with property names as keys and property values as values.
        """
        sdc_configuration = self.api_client.get_sdc_configuration().response.json()
        sdc_configuration.update(self.api_client.get_sdc_ui_configuration().response.json())
        return sdc_configuration

    @property
    def id(self):
        """Return id for StreamSets Data Collector.

        Returns:
            A :obj:`str` SDC ID.
        """
        sdc_id_command = self.api_client.get_sdc_id()
        sdc_id_json = sdc_id_command.response.json() if sdc_id_command.response.content else {}
        return sdc_id_json['id'] if sdc_id_json else None

    def add_pipeline(self, *pipelines, **kwargs):
        """Add one or more pipelines to the DataCollector instance.

        Args:
            *pipelines: One or more instances of :py:class:`streamsets.sdk.sdc_models.Pipeline`.
        """
        for pipeline in set(pipelines):
            # Only do the REST call to add the pipeline if an API client is available.
            if self.api_client:
                logger.info('Importing pipeline %s...', pipeline.id)
                draft = kwargs.get('draft', False)
                response = self.api_client.import_pipeline(pipeline_id=pipeline.id,
                                                           pipeline_json=pipeline._data,
                                                           auto_generate_pipeline_id=True,
                                                           draft=draft)
                pipeline._data = response
                if not draft:
                    status_command = self.api_client.get_pipeline_status(pipeline_id=pipeline.id)
                    status_command.wait_for_status(status='EDITED')

    def update_pipeline(self, *pipelines):
        """Update one or more pipelines in the DataCollector instance.

        Args:
            *pipelines: One or more instances of :py:class:`streamsets.sdk.sdc_models.Pipeline`.
        """
        for pipeline in set(pipelines):
            if self.api_client:
                logger.info('Updating pipeline %s...', pipeline.id)
                update_pipeline_command = self.api_client.update_pipeline(pipeline_id=pipeline.id,
                                                                          pipeline=pipeline._data['pipelineConfig'])
                pipeline._data['pipelineConfig'] = update_pipeline_command.response.json()

    def remove_pipeline(self, *pipelines):
        """Remove one or more pipelines from the DataCollector instance.

        Args:
            *pipelines: One or more instances of :py:class:`streamsets.sdk.sdc_models.Pipeline`.
        """
        for pipeline in set(pipelines):
            if self.api_client:
                logger.info('Deleting pipeline %s...', pipeline.id)
                self.api_client.delete_pipeline(pipeline_id=pipeline.id)

    def get_stage_errors(self, pipeline, stage):
        """Get stage errors.

        Args:
            pipeline (:py:class:`streamsets.sdk.sdc_models.Pipeline`): Pipeline.
            stage (:py:class:`streamsets.sdk.sdc_models.Stage`): Stage.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sdc_models.StageError` instances.
        """
        error_messages = self.api_client.get_pipeline_error_messages(pipeline.id, stage.instance_name).response.json()
        return SeekableList([sdc_models.StageError(error_message)
                             for error_message
                             in error_messages])

    def reset_origin(self, pipeline):
        """Reset origin offset.

        Args:
            pipeline (:py:class:`streamsets.sdk.sdc_models.Pipeline`): Pipeline object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`.
        """
        return self.api_client.reset_origin_offset(pipeline.id)

    def get_pipeline_committed_offsets(self, pipeline):
        """Get a pipeline's committed offsets.

        Args:
            pipeline (:py:class:`streamsets.sdk.sdc_models.Pipeline`): Pipeline object.

        Returns:
            A :obj:`dict` containing committed offsets (or an empty :obj:`dict` if no offsets exist).
        """
        offsets_response = self.api_client.get_pipeline_committed_offsets(pipeline.id).response
        return offsets_response.json() if offsets_response.text else {}

    @property
    def pipelines(self):
        """Get all pipelines in the pipeline store.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of
                :py:class:`streamsets.sdk.sdc_models.Pipeline` instances.
        """
        pipeline_ids = [pipeline_configuration_info['pipelineId']
                        for pipeline_configuration_info
                        in self.api_client.get_all_pipeline_configuration_info().response.json()]
        if not pipeline_ids:
            return SeekableList()
        pipelines_archive = zipfile.ZipFile(
            file=io.BytesIO(self.api_client.export_pipelines(body=pipeline_ids).response.content), mode='r'
        )
        pipelines = [json.loads(pipelines_archive.read(pipeline_filename).decode())
                     for pipeline_filename in pipelines_archive.namelist()]
        return SeekableList(self.get_pipeline_builder().import_pipeline(pipeline, regenerate_id=False)
                                .build(title=pipeline['pipelineConfig']['title'], existing_pipeline=True)
                            for pipeline in pipelines)

    @property
    def sample_pipelines(self):
        """Get all sample pipelines in the pipeline store.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of
                :py:class:`streamsets.sdk.sdc_models.Pipeline` instances.
        """
        pipeline_ids = [pipeline_configuration_info['pipelineId']
                        for pipeline_configuration_info
                        in self.api_client.get_all_pipeline_configuration_info(
                            label='system:samplePipelines'
                        ).response.json()]
        if not pipeline_ids:
            return SeekableList()
        pipelines = [self.api_client.get_pipeline_configuration(pipeline_id, get='samplePipeline')
                     for pipeline_id in pipeline_ids]
        return SeekableList(self.get_pipeline_builder().import_pipeline(pipeline, regenerate_id=False)
                                .build(title=pipeline['pipelineConfig']['title'], existing_pipeline=True)
                            for pipeline in pipelines)

    def import_pipelines_from_archive(self, archive):
        """Import pipelines from archived zip directory.

        Args:
            archive (:obj:`file`): file containing the pipelines.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sdc_models.Pipeline`.
        """
        imported_pipelines = self.api_client.import_pipelines(pipelines_file=archive)['successEntities']
        return SeekableList(self.pipelines.get(id=pipeline['pipelineId'] if 'pipelineId' in pipeline
                                               else pipeline['pipelineConfig']['pipelineId'])
                            for pipeline in imported_pipelines)

    def import_pipeline(self, pipeline, title=None):
        """Import pipeline from json file.

        Args:
            pipeline (:obj:`dict`): JSON data loaded from file. Example usage: json.load(open(filename, 'r')).
            title (:obj:`str`, optional): Title of the pipeline. If left out, pipeline title from JSON object will be
                                         used. Default ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_models.Pipeline`.
        """
        old_name = pipeline['pipelineConfig']['title']
        pipeline['pipelineConfig']['title'] = title or pipeline['pipelineConfig']['title']
        pipeline_id = '{}{}'.format(re.sub(r'[\W]|_', r'', pipeline['pipelineConfig']['title']), uuid4())
        response = self.api_client.import_pipeline(pipeline_id=pipeline_id,
                                                   pipeline_json=pipeline,
                                                   auto_generate_pipeline_id=True)
        pipeline_id = response['pipelineConfig']['pipelineId']
        pipeline['pipelineConfig']['title'] = old_name
        return self.pipelines.get(id=pipeline_id)

    def export_pipelines(self, pipelines, include_library_definitions=False, include_plain_text_credentials=False):
        """Export pipelines.

        Args:
            pipelines (:obj:`list`): A list of :py:class:`streamsets.sdk.sdc_models.Pipeline` instances.
            include_library_definitions (:obj:`boolean`): Set to true to export for Control Hub. Default ``False``.
            include_plain_text_credentials (:obj:`boolean`): Default ``False``.

        Returns:
            An instance of type :py:obj:`bytes` indicating the content of zip file with pipeline json files.
        """
        pipeline_ids = [pipeline.id for pipeline in pipelines]
        return self.api_client.export_pipelines(
                                                body=pipeline_ids,
                                                include_library_definitions=include_library_definitions,
                                                include_plain_text_credentials=include_plain_text_credentials
                                                ).response.content

    def export_pipeline(self, pipeline, include_library_definitions=False, include_plain_text_credentials=False):
        """Export single pipeline to json file.

        Args:
            pipeline (:py:obj:`streamsets.sdk.sdc_models.Pipeline`): Pipeline instance.
            include_library_definitions (:obj:`boolean`): Set to true to export for Control Hub.
            include_plain_text_credentials (:obj:`boolean`): Default ``False``.

        Returns:
            A :py:obj:`dict` object containing the contents of pipeline.
        """
        return self.api_client.export_pipeline(pipeline.id,
                                               include_library_definitions=include_library_definitions,
                                               include_plain_text_credentials=include_plain_text_credentials)

    def get_pipeline_builder(self, **kwargs):
        """Get a pipeline builder instance with which a pipeline can be created.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_models.PipelineBuilder`.
        """
        if not self.api_client:
            raise Exception('SDC must be started to get a PipelineBuilder instance.')

        # A :py:class:`streamsets.sdk.sdc_models.PipelineBuilder` instance takes an empty pipeline and a
        # dictionary of definitions as arguments. To get the former, we generate a pipeline in SDC, export it,
        # and then delete it. For the latter, we simply pass along `self.definitions`.
        if not self._pipeline:
            draft = kwargs.get('draft', False)
            create_pipeline_response = self.api_client.create_pipeline(pipeline_title='Pipeline Builder',
                                                                       auto_generate_pipeline_id=True,
                                                                       draft=draft).response.json()
            if draft:
                # The response contains the pipeline envelope with draft flag.
                self._pipeline = create_pipeline_response
            else:
                try:
                    pipeline_id = create_pipeline_response['info']['pipelineId']
                except KeyError:
                    pipeline_id = create_pipeline_response['info']['name']

                self._pipeline = self.api_client.export_pipeline(pipeline_id)
                self.api_client.delete_pipeline(pipeline_id)

        return sdc_models.PipelineBuilder(pipeline=copy.deepcopy(self._pipeline),
                                          definitions=self.definitions,
                                          fragment=kwargs.get('fragment', False),
                                          data_collector=self)

    def set_user(self, username, password=None):
        """Set the user with which to interact with SDC.

        Args:
            username (:obj:`str`): Username of user.
            password (:obj:`str`, optional): Password for user. Default: same as ``username``.
        """
        self.username = username
        # If password isn't set, assume it's the same as the username to follow existing
        # conventions.
        self.password = password or username

        if self.api_client:
            self.api_client.set_user(self.username, self.password)

    @property
    def definitions(self):
        """Get an SDC instance's definitions.

        Will return a cached instance of the definitions if called more than once.

        Returns:
            An instance of :py:class:`json`.
        """
        if self._definitions:
            return self._definitions

        # Getting definitions from SDC requires a running deployment.
        if not self.api_client:
            raise Exception('SDC must be started to get definitions.')

        self._definitions = self.api_client.get_definitions()
        return self._definitions

    def validate_pipeline(self, pipeline):
        """Validate a pipeline.

        Args:
            pipeline (:py:class:`streamsets.sdk.sdc_models.Pipeline`): The pipeline instance.
        """
        logger.info('Validating pipeline %s ...', pipeline.id)
        validate_command = self.api_client.validate_pipeline(pipeline_id=pipeline.id).wait_for_validate()
        response = validate_command.response.json()
        if response['status'] != 'VALID':
            if 'issues' in response and response['issues']:
                raise ValidationError(response['issues'])
            elif 'message' in response:
                raise ValidationError(response['message'])
            else:
                raise ValidationError('Unknown validation failure with status as {}'.format(response['status']))

    def start_pipeline(self, pipeline, runtime_parameters=None, **kwargs):
        """Start a pipeline.

        Args:
            pipeline (:py:class:`streamsets.sdk.sdc_models.Pipeline`): The pipeline instance.
            runtime_parameters (:obj:`dict`, optional): Collection of runtime parameters. Default: ``None``.
            wait (:obj:`bool`, optional): Wait for pipeline to start. Default: ``True``.
            wait_for_statuses (:obj:`list`, optional): Pipeline statuses to wait on.
                Default: ``['RUNNING', 'FINISHED']``.
            timeout_sec (:obj:`int`): Timeout to wait for pipeline statuses, in seconds.
                Default: :py:const:`streamsets.sdk.sdc.DEFAULT_START_TIMEOUT`.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.PipelineCommand`.
        """
        issues = self.api_client.get_pipeline_configuration(pipeline_id=pipeline.id)['issues']
        if issues['issueCount']:
            raise ValidationError(issues)

        logger.info('Starting pipeline %s ...', pipeline.id)
        pipeline_command = self.api_client.start_pipeline(pipeline_id=pipeline.id,
                                                          runtime_parameters=runtime_parameters)
        if kwargs.get('wait', True):
            timeout_sec = kwargs.get('timeout_sec', DEFAULT_START_TIMEOUT)
            pipeline_command.wait_for_status(status=kwargs.get('wait_for_statuses', DEFAULT_START_STATUSES_TO_WAIT_FOR),
                                             timeout_sec=timeout_sec)

        return pipeline_command

    def stop_pipeline(self, pipeline, **kwargs):
        """Stop a pipeline.

        Args:
            pipeline (:py:class:`streamsets.sdk.sdc_models.Pipeline`): The pipeline instance.
            force (:obj:`bool`, optional): Force pipeline to stop. Default: ``False``.
            wait (:obj:`bool`, optional): Wait for pipeline to stop. Default: ``True``.
            timeout_sec (:obj:`int`): Timeout to wait for pipeline stop, in seconds.
                Default: :py:const:`streamsets.sdk.sdc.DEFAULT_STOP_TIMEOUT`.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.StopPipelineCommand`.
        """
        logger.info('Stopping pipeline %s...', pipeline.id)
        stop_command = self.api_client.stop_pipeline(pipeline_id=pipeline.id)

        if kwargs.get('force', False):
            # Note: Pipeline force stop is applicable only after a pipeline stop.
            stop_command = self.api_client.force_stop_pipeline(pipeline_id=pipeline.id)

        if kwargs.get('wait', True):
            stop_command.wait_for_stopped(kwargs.get('timeout_sec', DEFAULT_STOP_TIMEOUT))

        return stop_command

    def run_pipeline_preview(self, pipeline, rev=0, batches=1, batch_size=10, skip_targets=True, end_stage=None,
                             timeout=2000, test_origin=False, stage_outputs_to_override_json=None, **kwargs):
        """Run pipeline preview.

        Args:
            pipeline (:obj:`streamsets.sdk.sdc_models.Pipeline`): The pipeline instance.
            rev (:obj:`int`, optional): Pipeline revision. Default: ``0``.
            batches (:obj:`int`, optional): Number of batches. Default: ``1``.
            batch_size (:obj:`int`, optional): Batch size. Default: ``10``.
            skip_targets (:obj:`bool`, optional): Skip targets. Default: ``True``.
            end_stage (:obj:`str`, optional): End stage. Default: ``None``.
            timeout (:obj:`int`, optional): Timeout. Default: ``2000``.
            test_origin (:obj:`bool`, optional): Test origin. Default: ``False``
            stage_outputs_to_override_json (:obj:`str`, optional): Stage outputs to override. Default: ``None``.
            wait (:obj:`bool`, optional): Wait for pipeline preview to finish. Default: ``True``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.PreviewCommand`.
        """
        logger.info('Running preview for %s ...', pipeline.id)
        preview_command = self.api_client.run_pipeline_preview(pipeline.id, rev, batches,
                                                               batch_size, skip_targets, end_stage,
                                                               timeout, test_origin, stage_outputs_to_override_json)
        if kwargs.get('wait', True):
            preview_command.wait_for_finished()

        return preview_command

    def run_dynamic_pipeline_preview(self, type, parameters={}, batches=1, batch_size=1, skip_targets=True,
                                     skip_lifecycle_events=True, end_stage=None, timeout=10000,
                                     test_origin=False, stage_outputs_to_override_json_text=None,
                                     stage_outputs_to_override_json=[], **kwargs):
        """Run dynamic pipeline preview.

        Args:
            type (:obj:`str`): Dynamic preview request type. ``CLASSIFICATION_CATALOG`` or ``PROTECTION_POLICY``
            parameters (:obj:`dict`, optional): Dynamic preview request parameters. Default: ``{}``
            batches (:obj:`int`, optional): Number of batches. Default: ``1``.
            batch_size (:obj:`int`, optional): Batch size. Default: ``1``.
            skip_targets (:obj:`bool`, optional): Skip targets. Default: ``True``.
            skip_lifecycle_events (:obj:`bool`, optional): Skip life cycle events. Default: ``True``.
            end_stage (:obj:`str`, optional): End stage. Default: ``None``.
            timeout (:obj:`int`, optional): Timeout. Default: ``10000``.
            test_origin (:obj:`bool`, optional): Test origin. Default: ``False``.
            stage_outputs_to_override_json_text (:obj:`str`, optional): Stage outputs to override text.
                Default: ``None``.
            stage_outputs_to_override_json (:obj:`list`, optional): Stage outputs to override. Default: ``[]``.
            wait (:obj:`bool`, optional): Wait for pipeline preview to finish. Default: ``True``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.PreviewCommand`.
        """
        logger.info('Running dynamic preview for %s type ...', type)
        dynamic_preview_request = {'dynamicPreviewRequestJson': {'type': type,
                                                                 'parameters': parameters,
                                                                 'batches': batches,
                                                                 'batchSize': batch_size,
                                                                 'skipTargets': skip_targets,
                                                                 'skipLifecycleEvents': skip_lifecycle_events,
                                                                 'endStageInstanceName': end_stage,
                                                                 'timeout': timeout,
                                                                 'testOrigin': test_origin,
                                                                 'stageOutputsToOverrideJsonText':
                                                                    stage_outputs_to_override_json_text},
                                   'stageOutputsToOverrideJson': stage_outputs_to_override_json}
        preview_command = self.api_client.run_dynamic_pipeline_preview(dynamic_preview_request)
        if kwargs.get('wait', True):
            preview_command.wait_for_finished()

        return preview_command

    def get_snapshots(self, pipeline):
        """Get information about stored snapshots.

        Args:
            pipeline (:py:class:`streamsets.sdk.sdc_models.Pipeline`, optional): The pipeline instance.

        Returns:
            A list of :py:class:`streamsets.sdk.sdc_models.SnapshotInfo` instances.
        """
        return SeekableList(sdc_models.Snapshot(self.api_client, snapshot)
                            for snapshot in sorted(self.api_client.get_snapshots_by_pipeline(pipeline.id)
                                                   .response.json(), key=lambda x: x['timeStamp']))

    def capture_snapshot(self, pipeline, snapshot_name=None, start_pipeline=False,
                         runtime_parameters=None, batches=1, batch_size=10, **kwargs):
        """Capture a snapshot for given pipeline.

        Args:
            pipeline (:obj:`streamsets.sdk.sdc_models.Pipeline`): The pipeline instance.
            snapshot_name (:obj:`str`, optional): Name for the generated snapshot. If set to ``None``,
                an auto-generated UUID (which can be recovered from the returned ``SnapshotCommand``
                object's ``snapshot_name`` attribute) will be used when calling the REST API. Default: ``None``.
            start_pipeline (:obj:`bool`, optional): If set to true, then the pipeline will be
                started and its first batch will be captured. Otherwise, the pipeline must be
                running, in which case one of the next batches will be captured. Default: ``False``.
            runtime_parameters (:obj:`dict`, optional): Runtime parameters to override Pipeline Parameters value.
                Default: ``None``.
            wait (:obj:`bool`, optional): Wait for capture snapshot to finish. Default: ``True``.
            wait_for_statuses (:obj:`list`, optional): Pipeline statuses to wait on.
                Default: ``['RUNNING', 'FINISHED']``.
            timeout_sec (:obj:`int`): Timeout to wait for snapshot, in seconds.
                Default: :py:const:`streamsets.sdk.sdc.DEFAULT_SNAPSHOT_TIMEOUT`.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.SnapshotCommand`.
        """
        timeout_sec = kwargs.get('timeout_sec', DEFAULT_SNAPSHOT_TIMEOUT)
        logger.info('Capturing snapshot (%d batches of size %d, timeout %d seconds) for %s...', batches, batch_size,
                    timeout_sec, pipeline.id)
        snapshot_id = '{}{}'.format('snapshot', int(datetime.now().timestamp()*1000))
        snapshot_command = self.api_client.capture_snapshot(pipeline_id=pipeline.id,
                                                            snapshot_name=snapshot_id,
                                                            snapshot_label=snapshot_name or str(uuid4()),
                                                            start_pipeline=start_pipeline,
                                                            runtime_parameters=runtime_parameters,
                                                            batches=batches, batch_size=batch_size)
        if start_pipeline:
            status_command = self.api_client.get_pipeline_status(pipeline_id=pipeline.id)
            status_command.wait_for_status(status=kwargs.get('wait_for_statuses',
                                                             DEFAULT_START_STATUSES_TO_WAIT_FOR))

        if kwargs.get('wait', True):
            snapshot_command.wait_for_finished(timeout_sec)

        return snapshot_command

    def delete_snapshot(self, snapshot):
        """Delete a snapshot from the specified pipeline.

        Args:
            snapshot (:obj:`streamsets.sdk.sdc_models.Snapshot`): The Snapshot object to be deleted.
        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`.
        """
        delete_command = self.api_client.delete_snapshot(pipeline_id=snapshot._data['name'],
                                                         snapshot_id=snapshot._data['id'])
        return delete_command

    def get_pipeline_acl(self, pipeline):
        """Get pipeline ACL.

        Args:
            pipeline (:py:class:`streamsets.sdk.sdc_models.Pipeline`): The pipeline instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_models.PipelineAcl`.
        """
        return sdc_models.PipelineAcl(self.api_client.get_pipeline_acl(pipeline_id=pipeline.id))

    def set_pipeline_acl(self, pipeline, pipeline_acl):
        """Update pipeline ACL.

        Args:
            pipeline (:py:class:`streamsets.sdk.sdc_models.Pipeline`): The pipeline instance.
            pipeline_acl (:py:class:`streamsets.sdk.sdc_models.PipelineAcl`): The pipeline ACL instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`.
        """
        return self.api_client.set_pipeline_acl(pipeline_id=pipeline.id, pipeline_acl_json=pipeline_acl._data)

    def get_pipeline_permissions(self, pipeline):
        """Return pipeline permissions for a given pipeline.

        Args:
            pipeline (:obj:`streamsets.sdk.sdc_models.Pipeline`): The pipeline instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_models.PipelinePermissions`.
        """
        return sdc_models.PipelinePermissions(self.api_client.get_pipeline_permissions(pipeline_id=pipeline.id))

    def get_pipeline_status(self, pipeline):
        """Get status of a pipeline.

        Args:
            pipeline (:py:class:`streamsets.sdk.sdc_models.Pipeline`): The pipeline instance.
        """
        logger.info('Getting status of pipeline %s...', pipeline.id)
        return self.api_client.get_pipeline_status(pipeline_id=pipeline.id)

    def get_pipeline_history(self, pipeline):
        """Get a pipeline's history.

        Args:
            pipeline (:py:class:`streamsets.sdk.sdc_models.Pipeline`): The pipeline instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_models.History`.
        """
        logger.info('Getting pipeline history for %s...', pipeline.id)
        return sdc_models.History(self.api_client.get_pipeline_history(pipeline_id=pipeline.id))

    def get_pipeline_metrics(self, pipeline):
        """Get a pipeline's metrics.

        Args:
            pipeline (:py:class:`streamsets.sdk.sdc_models.Pipeline`): The pipeline instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_models.Metrics`.
        """
        logger.info('Getting metrics for pipeline %s ...', pipeline.id)
        # Mirror SDC error handling for pipeline metrics REST API (https://git.io/JfTBI). That is, the API client
        # will handle cases of non-existent pipeline IDs being passed through, but pipelines without metrics
        # (e.g. those are that stopped) will simply return None implicitly.
        command = self.api_client.get_pipeline_metrics(pipeline_id=pipeline.id)
        # Handle case of empty response with HTTP 200 (seen for pipelines while starting) and of HTTP 204.
        if command.response.text and command.response.status_code != requests.codes.no_content:
            return sdc_models.Metrics(command.response.json())

    def wait_for_pipeline_metric(self, pipeline, metric, value, timeout_sec=DEFAULT_WAIT_FOR_METRIC_TIMEOUT):
        """Block until a pipeline metric reaches the desired value.

        Args:
            pipeline (:py:class:`streamsets.sdk.sdc_models.Pipeline`): The pipeline instance.
            metric (:py:obj:`str`): The desired metric (e.g. ``'output_record_count'`` or ``'data_batch_count'``).
            value: The desired value to wait for.
            timeout_sec (:obj:`int`, optional): Timeout to wait for ``metric`` to reach ``value``, in seconds.
                Default: :py:const:`streamsets.sdk.sdc.DEFAULT_WAIT_FOR_METRIC_TIMEOUT`.

        Raises:
            TimeoutError: If ``timeout_sec`` passes without ``metric`` reaching ``value``.
        """
        logger.info('Waiting for pipeline metric %s to reach at value %s ...', metric, value)
        start_waiting_time = time.time()
        stop_waiting_time = start_waiting_time + timeout_sec

        while time.time() < stop_waiting_time:
            metrics = self.get_pipeline_metrics(pipeline)
            if not metrics:
                raise ValueError('Operation only supported for running pipelines')
            current_value = getattr(metrics.pipeline, metric)
            logger.debug('Pipeline metric %s has current value %s ...', metric, current_value)
            if current_value >= value:
                logger.info('Metric %s reached value %s for pipeline %s (took %.2f s).',
                            metric,
                            value,
                            pipeline.id,
                            time.time() - start_waiting_time)
                break

            time.sleep(1)
        else:
            # We got out of the loop and did not get the metric we were waiting for.
            raise TimeoutError('Metric {} did not reach value {} '
                               'after {} s (current value {})'.format(metric, value, timeout_sec, current_value))

    def wait_for_pipeline_status(self, pipeline, status, timeout_sec=DEFAULT_WAIT_FOR_STATUS_TIMEOUT):
        """Block until a pipeline reaches the desired status.

        Args:
            pipeline (:py:class:`streamsets.sdk.sdc_models.Pipeline`): The pipeline instance.
            status (:py:obj:`str`): The desired status to wait for.
            timeout_sec (:obj:`int`, optional): Timeout to wait for ``pipeline`` to reach ``status``, in seconds.
                Default: :py:const:`streamsets.sdk.sdc.DEFAULT_WAIT_FOR_STATUS_TIMEOUT`.

        Raises:
            TimeoutError: If ``timeout_sec`` passes without ``pipeline`` reaching ``status``.
        """
        logger.info('Waiting for pipeline to reach status %s ...', status)
        start_waiting_time = time.time()
        stop_waiting_time = start_waiting_time + timeout_sec

        while time.time() < stop_waiting_time:
            current_status = self.get_pipeline_status(pipeline).response.json()['status']
            logger.debug('Pipeline has current status %s ...', current_status)
            if current_status == status:
                logger.info('Pipeline (%s) reached status %s (took %.2f s).',
                            pipeline.id,
                            status,
                            time.time() - start_waiting_time)
                break
            time.sleep(1)
        else:
            # We got out of the loop and did not get the status we were waiting for.
            raise TimeoutError('Pipeline did not reach status {} '
                               'after {} s (current status {})'.format(status, timeout_sec, current_status))

    @property
    def current_user(self):
        """Get currently logged-in user and its groups and roles.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_models.User`.
        """
        logger.info('Getting current user ...')
        return sdc_models.User(self.api_client.get_current_user())

    def change_password(self, old_password, new_password):
        """Change password for the current user.

        Args:
            old_password (:obj:`str`): old password.
            new_password (:obj:`str`): new password.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.Command`.
        """
        data = {'data': {'id': self.current_user.name, 'oldPassword': old_password, 'newPassword': new_password},
                'envelopeVersion': "1"}
        return self.api_client.change_password(data)

    def get_logs(self, ending_offset=-1, extra_message=None, pipeline=None, severity=None):
        """Get logs.

        Args:
            ending_offset (:obj:`int`): ending_offset, Default: ``-1``.
            extra_message (:obj:`str`): extra_message, Default: ``None``.
            pipeline (:py:class:`streamsets.sdk.sdc_models.Pipeline`): The pipeline instance, Default: ``None``.
            severity (:obj:`str`): severity, Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_models.Log`.
        """
        pipeline_id = pipeline.id if pipeline is not None else None
        response = self.api_client.get_logs(ending_offset, extra_message, pipeline_id, severity).response
        return sdc_models.Log(response.json() if response.content else {})

    def get_alerts(self):
        """Get pipeline alerts.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_models.Alerts`.
        """
        return sdc_models.Alerts(self.api_client.get_alerts())

    @property
    def stage_libraries(self):
        """Get all stage libraries.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of
                :py:class:`streamsets.sdk.sdc_models.StageLibrary` instances.
        """
        stage_libraries = SeekableList()
        repositories = self.api_client.get_stage_libraries_list(repo_url=None, installed_only=False).response.json()
        for repository in repositories:
            repository_manifest = {key: value for key, value in repository.items() if key != 'stageLibraries'}
            for stage_library in repository['stageLibraries']:
                stage_libraries.append(sdc_models.StageLibrary(stage_library, repository_manifest))
        return stage_libraries

    def get_stage_library_version(self, stage):
        # This has been added to DataCollector instead of Stage class because of the api_client unavailability.
        """Get the stage library version.

        Args:
            stage (:py:obj:`streamsets.sdk.sdc_models.Stage`): stage object

        Returns:
            An instance of :obj:`str`
        """
        # This has to be parsed from stagelib manifest because that is the only reliable place.
        stage_libraries_list = self.api_client.get_stage_libraries_list(repo_url=None, installed_only=True)
        stage_library_manifest = next(iter([lib['stagelibManifest'] for lib in stage_libraries_list.response.json()[0]['stageLibraries']
                                       if lib['stageLibraryManifest']['stageLibId'] == stage.library]), None)
        # ([0-9]+\.[0-9]+\.[0-9]+(-.*)?) signifies 3.13.0-SNAPSHOT or 3.13.0 as an example.
        return re.match('.*-([0-9]+\.[0-9]+\.[0-9]+(-.*)?).tgz.*', stage_library_manifest).groups()[0]

    def get_bundle_generators(self):
        """Get available support bundle generators.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_models.BundleGenerators`.
        """
        return sdc_models.BundleGenerators(self.api_client.get_bundle_generators())

    def get_bundle(self, generators=None):
        """Generate new support bundle.

        Returns:
            An instance of :py:class:`zipfile.ZipFile`.
        """
        return self.api_client.get_bundle(generators)

    def get_jmx_metrics(self):
        """Get SDC JMX metrics

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_models.JmxMetrics`.
        """
        logger.info('Getting JMX metrics ...')
        return sdc_models.JmxMetrics(self.api_client.get_jmx_metrics().response.json())
