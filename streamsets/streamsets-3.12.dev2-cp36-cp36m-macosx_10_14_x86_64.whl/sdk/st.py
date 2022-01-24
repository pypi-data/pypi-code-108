# Copyright 2019 StreamSets Inc.

"""Abstractions for interacting with StreamSets Transformer."""

import copy
import io
import json
import logging
import zipfile
from datetime import datetime
from functools import wraps
from urllib.parse import urlparse

from . import st_api, st_models
from .constants import ENGINE_AUTHENTICATION_METHOD_FORM
from .exceptions import ValidationError
from .utils import SeekableList

logger = logging.getLogger(__name__)

# The `#:` constructs at the end of assignments are part of Sphinx's autodoc functionality.
DEFAULT_ST_USERNAME = 'admin'  #:
DEFAULT_ST_PASSWORD = 'admin'  #:
DEFAULT_START_STATUSES_TO_WAIT_FOR = ['RUNNING', 'FINISHED']  #:
DEFAULT_START_TIMEOUT = 300  #:
DEFAULT_STOP_TIMEOUT = 300  #:

# the server side for a validate (i.e. when the runner will give up on waiting for the validate to finish)
DEFAULT_VALIDATE_SERVER_TIMEOUT_SEC = 120
# client side validate timeout
DEFAULT_VALIDATE_CLIENT_TIMEOUT_SEC = 500
DEFAULT_VALIDATE_TIME_BETWEEN_CHECKS = 2

# the server side for a preview (i.e. when the runner will give up on waiting for the preview to finish)
DEFAULT_PREVIEW_SERVER_TIMEOUT_MS = 120000
# for now, make the client side default timeout the same value as the server side
DEFAULT_PREVIEW_CLIENT_TIMEOUT_SEC = DEFAULT_PREVIEW_SERVER_TIMEOUT_MS/1000
DEFAULT_PREVIEW_TIME_BETWEEN_CHECKS = 2


class Transformer:
    """Class to interact with StreamSets Transformer.

    Args:
        server_url (:obj:`str`): URL of an existing ST deployment with which to interact.
        username (:obj:`str`, optional): ST username. Default: :py:const:`streamsets.sdk.st.DEFAULT_ST_USERNAME`.
        password (:obj:`str`, optional): ST password. Default: :py:const:`streamsets.sdk.st.DEFAULT_ST_PASSWORD`.
        authentication_method (:obj:`str`, optional): StreamSets Transformer authentication method.
            Default: :py:const:`streamsets.sdk.constants.ENGINE_AUTHENTICATION_METHOD_FORM`.
        accounts_authentication_token (:obj:`str`, optional): StreamSets Accounts authentication token. Default: ``None``
        accounts_server_url (:obj:`str`, optional): StreamSets Accounts server base URL. Default: ``None``
        control_hub (:py:class:`streamsets.sdk.ControlHub`, optional): A StreamSets Control Hub instance to use
            for SCH-registered Transformers. Default: ``None``.
        dump_log_on_error (:obj:`bool`): Whether to output Transformer logs when exceptions
            are raised by certain methods. Default: ``False``
    """
    VERIFY_SSL_CERTIFICATES = True
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
        self.username = username or DEFAULT_ST_USERNAME
        self.password = password or DEFAULT_ST_PASSWORD
        self.control_hub = control_hub
        self.dump_log_on_error = dump_log_on_error

        if self.server_url:
            sch_headers = {
                'X-SS-User-Auth-Token': self.control_hub.api_client.session.headers['X-SS-User-Auth-Token']
            } if self.control_hub else {}
            session_attributes = {'verify': self.VERIFY_SSL_CERTIFICATES}
            self.api_client = st_api.ApiClient(server_url=self.server_url,
                                               authentication_method=self.authentication_method,
                                               accounts_authentication_token=accounts_authentication_token,
                                               accounts_server_url=accounts_server_url,
                                               username=self.username,
                                               password=self.password,
                                               headers=sch_headers,
                                               dump_log_on_error=self.dump_log_on_error,
                                               session_attributes=session_attributes,
                                               **kwargs)

            # Keep track of the server host so that tests that may need it (e.g. to set configurations) can use it.
            self.server_host = urlparse(self.server_url).netloc.split(':')[0]
        else:
            self.server_host = None
            self.api_client = None

        # ST definitions should be an attribute of this class, but we use a property for
        # access to handle necessary setup and synchronization tasks, so indicate internal use for
        # the underlying attribute with a leading underscore.
        self._definitions = None

        # Instances of :py:class:`streamsets.sdk.st_models.PipelineBuilder` require a blank pipeline (i.e.
        # an empty pipeline JSON) from our particular Transformer version. We keep track of this with an
        # instance attribute to avoid repetitive API calls.
        self._pipeline = None

    def _dump_st_log_on_error(*dec_args, **dec_kwargs):
        """A Python decorator to log ST when errors happen.

        Args:
            *dec_args: Optional positional arguments to be passed.
            **dec_kwargs: Optional keyword arguments to be passed, such as ``all`. ``all`` will
                include complete ST logs.
        """
        def outer_func(func):
            @wraps(func)
            def wrapped(self, *args, **kwargs):
                log_time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')
                try:
                    return func(self, *args, **kwargs)
                except:
                    if self.dump_log_on_error:
                        st_log = (self.get_logs()
                                  if dec_kwargs.get('all') else self.get_logs().after_time(log_time_now))
                        if st_log:
                            logger.error('Error during `%s` call. ST log follows ...', func.__name__)
                            print('------------------------- ST log - Begins -----------------------')
                            print(st_log)
                            print('------------------------- ST log - Ends -------------------------')
                    raise
            return wrapped
        if len(dec_args) == 1 and not dec_kwargs and callable(dec_args[0]):  # called without args
            return outer_func(dec_args[0])
        else:
            return outer_func

    @property
    def version(self):
        """Return the version of the Transformer.

        Returns:
           :obj:`str`: The version string.
        """
        return self.api_client.get_st_info()['version']

    @_dump_st_log_on_error
    def add_pipeline(self, *pipelines):
        """Add one or more pipelines to the Transformer instance.

        Args:
            *pipelines: One or more instances of :py:class:`streamsets.sdk.st_models.Pipeline`.
        """
        for pipeline in set(pipelines):
            # Only do the REST call to add the pipeline if an API client is available.
            if self.api_client:
                logger.info('Importing pipeline %s...', pipeline.id)
                response = self.api_client.import_pipeline(pipeline_id=pipeline.id,
                                                           pipeline_json=pipeline._data,
                                                           auto_generate_pipeline_id=True)
                pipeline._data = response
                status_command = self.api_client.get_pipeline_status(pipeline_id=pipeline.id)
                status_command.wait_for_status(status='EDITED')

    @_dump_st_log_on_error
    def remove_pipeline(self, *pipelines):
        """Remove one or more pipelines from the Transformer instance.

        Args:
            *pipelines: One or more instances of :py:class:`streamsets.sdk.st_models.Pipeline`.
        """
        for pipeline in set(pipelines):
            if self.api_client:
                logger.info('Deleting pipeline %s...', pipeline.id)
                self.api_client.delete_pipeline(pipeline_id=pipeline.id)

    def reset_origin(self, pipeline):
        """Reset origin offset.

        Args:
            pipeline (:py:class:`streamsets.sdk.st_models.Pipeline`): Pipeline object.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.Command`.
        """
        return self.api_client.reset_origin_offset(pipeline.id)

    @property
    def pipelines(self):
        """Get all pipelines in the pipeline store.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of
                :py:class:`streamsets.sdk.st_models.Pipeline` instances.
        """
        pipeline_ids = [pipeline_configuration_info['pipelineId']
                        for pipeline_configuration_info
                        in self.api_client.get_all_pipeline_configuration_info().response.json()]
        pipelines_archive = zipfile.ZipFile(
            file=io.BytesIO(self.api_client.export_pipelines(body=pipeline_ids).response.content), mode='r'
        )
        pipelines = [json.loads(pipelines_archive.read(pipeline_filename).decode())
                     for pipeline_filename in pipelines_archive.namelist()]
        return SeekableList(self.get_pipeline_builder().import_pipeline(pipeline, regenerate_id=False)
                                .build(title=pipeline['pipelineConfig']['title'])
                            for pipeline in pipelines)

    def get_pipeline_builder(self, **kwargs):
        """Get a pipeline builder instance with which a pipeline can be created.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.PipelineBuilder`.
        """
        if not self.api_client:
            raise Exception('ST must be started to get a PipelineBuilder instance.')

        # A :py:class:`streamsets.sdk.st_models.PipelineBuilder` instance takes an empty pipeline and a
        # dictionary of definitions as arguments. To get the former, we generate a pipeline in ST, export it,
        # and then delete it. For the latter, we simply pass along `self.definitions`.
        if not self._pipeline:
            create_pipeline_response = self.api_client.create_pipeline(pipeline_title='Pipeline Builder',
                                                                       auto_generate_pipeline_id=True).response.json()
            try:
                pipeline_id = create_pipeline_response['info']['pipelineId']
            except KeyError:
                pipeline_id = create_pipeline_response['info']['name']

            self._pipeline = self.api_client.export_pipeline(pipeline_id)
            self.api_client.delete_pipeline(pipeline_id)

        return st_models.PipelineBuilder(pipeline=copy.deepcopy(self._pipeline),
                                         definitions=self.definitions)

    @_dump_st_log_on_error
    def set_user(self, username, password=None):
        """Set the user with which to interact with ST.

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
        """Get an ST instance's definitions.

        Will return a cached instance of the definitions if called more than once.

        Returns:
            An instance of :py:class:`json`.
        """
        if self._definitions:
            return self._definitions

        # Getting definitions from ST requires a running deployment.
        if not self.api_client:
            raise Exception('ST must be started to get definitions.')

        self._definitions = self.api_client.get_definitions()
        return self._definitions

    @_dump_st_log_on_error
    def validate_pipeline(self, pipeline, **kwargs):
        """Validate a pipeline.

        Args:
            pipeline (:py:class:`streamsets.sdk.st_models.Pipeline`): The pipeline instance.
            timeout (:obj:`int`, optional): Server side validate Timeout in seconds.
                Default: :py:const:`streamsets.sdk.st.DEFAULT_VALIDATE_SERVER_TIMEOUT_SEC`.
            timeout_sec (:obj:`int`, optional): Client side validate timeout, in seconds.
                Default: :py:const:`streamsets.sdk.st.DEFAULT_VALIDATE_CLIENT_TIMEOUT_SEC`.
            time_between_checks (:obj:`int`, optional): Time to sleep between validation checks.
                Default: :py:const:`streamsets.sdk.st.DEFAULT_VALIDATE_TIME_BETWEEN_CHECKS`.
            using_configured_cluster_manager (:obj:`bool`, optional): Validate pipeline using configured cluster
                manager. Default: ``True``.
        """
        logger.info('Validating pipeline %s ...', pipeline.id)
        server_timeout_ms = kwargs.get('timeout', DEFAULT_VALIDATE_SERVER_TIMEOUT_SEC) * 1000
        timeout_sec = kwargs.get('timeout_sec', DEFAULT_VALIDATE_CLIENT_TIMEOUT_SEC)
        time_between_checks = kwargs.get('time_between_checks', DEFAULT_VALIDATE_TIME_BETWEEN_CHECKS)
        using_configured_cluster_manager = kwargs.get('using_configured_cluster_manager', True)

        if time_between_checks > timeout_sec:
            raise ValueError('Time to sleep between validate status check cannot be greater than validate timeout')

        validate_command = self.api_client.validate_pipeline(pipeline_id=pipeline.id,
            timeout=server_timeout_ms, remote=using_configured_cluster_manager).wait_for_validate(
            timeout_sec=timeout_sec, time_between_checks=time_between_checks)
        response = validate_command.response.json()
        if response['status'] != 'VALID':
            if 'issues' in response and response['issues']:
                raise ValidationError(response['issues'])
            elif 'message' in response:
                raise ValidationError(response['message'])
            else:
                raise ValidationError('Unknown validation failure with status as {}'.format(response['status']))

    @_dump_st_log_on_error
    def start_pipeline(self, pipeline, runtime_parameters=None, **kwargs):
        """Start a pipeline.

        Args:
            pipeline (:py:class:`streamsets.sdk.st_models.Pipeline`): The pipeline instance.
            runtime_parameters (:obj:`dict`, optional): Collection of runtime parameters. Default: ``None``.
            wait (:obj:`bool`, optional): Wait for pipeline to start. Default: ``True``.
            wait_for_statuses (:obj:`list`, optional): Pipeline statuses to wait on.
                Default: ``['RUNNING', 'FINISHED']``.
            timeout_sec (:obj:`int`): Timeout to wait for pipeline statuses, in seconds.
                Default: :py:const:`streamsets.sdk.st.DEFAULT_START_TIMEOUT`.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.PipelineCommand`.
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

    @_dump_st_log_on_error
    def stop_pipeline(self, pipeline, **kwargs):
        """Stop a pipeline.

        Args:
            pipeline (:py:class:`streamsets.sdk.st_models.Pipeline`): The pipeline instance.
            force (:obj:`bool`, optional): Force pipeline to stop. Default: ``False``.
            wait (:obj:`bool`, optional): Wait for pipeline to stop. Default: ``True``.
            timeout_sec (:obj:`int`): Timeout to wait for pipeline stop, in seconds.
                Default: :py:const:`streamsets.sdk.st.DEFAULT_STOP_TIMEOUT`.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.StopPipelineCommand`.
        """
        logger.info('Stopping pipeline %s...', pipeline.id)
        stop_command = self.api_client.stop_pipeline(pipeline_id=pipeline.id)

        if kwargs.get('force', False):
            # Note: Pipeline force stop is applicable only after a pipeline stop.
            stop_command = self.api_client.force_stop_pipeline(pipeline_id=pipeline.id)

        if kwargs.get('wait', True):
            stop_command.wait_for_stopped(kwargs.get('timeout_sec', DEFAULT_STOP_TIMEOUT))

        return stop_command

    @_dump_st_log_on_error
    def run_pipeline_preview(self, pipeline, rev=0, batches=1, batch_size=10, skip_targets=True, end_stage=None,
                             timeout=DEFAULT_PREVIEW_SERVER_TIMEOUT_MS, stage_outputs_to_override_json=None, **kwargs):
        """Run pipeline preview.

        Args:
            pipeline (:obj:`streamsets.sdk.st_models.Pipeline`): The pipeline instance.
            rev (:obj:`int`, optional): Pipeline revision. Default: ``0``.
            batches (:obj:`int`, optional): Number of batches. Default: ``1``.
            batch_size (:obj:`int`, optional): Batch size. Default: ``10``.
            skip_targets (:obj:`bool`, optional): Skip targets. Default: ``True``.
            end_stage (:obj:`str`, optional): End stage. Default: ``None``.
            timeout (:obj:`int`, optional): Server side preview Timeout in milliseconds. Default: ``120000``.
            stage_outputs_to_override_json (:obj:`str`, optional): Stage outputs to override. Default: ``None``.
            remote (:obj:`bool`, optional): Remote preview (i.e. run on the cluster). Default: ``False``.
            timeout_sec (:obj:`int`, optional): Client side preview timeout, in seconds.
                Default: :py:const:`streamsets.sdk.st.DEFAULT_PREVIEW_CLIENT_TIMEOUT_SEC`.
            wait (:obj:`bool`, optional): Wait for pipeline preview to finish. Default: ``True``.
            time_between_checks (:obj:`int`, optional): Time to sleep between preview status checks. Applicable when
                ```wait``` is enabled, in seconds.
                Default: :py:const:`streamsets.sdk.st.DEFAULT_PREVIEW_TIME_BETWEEN_CHECKS`.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.PreviewCommand`.
        """
        logger.info('Running preview for %s...', pipeline.id)
        self.validate_pipeline(pipeline, timeout=timeout, **kwargs)
        preview_command = self.api_client.run_pipeline_preview(pipeline.id, rev, batches,
                                                               batch_size, skip_targets, end_stage,
                                                               timeout, stage_outputs_to_override_json,
                                                               kwargs.get('remote', False))
        if kwargs.get('wait', True):
            timeout_sec = kwargs.get('timeout_sec', DEFAULT_PREVIEW_CLIENT_TIMEOUT_SEC)
            time_between_checks = kwargs.get('time_between_checks', DEFAULT_PREVIEW_TIME_BETWEEN_CHECKS)

            if time_between_checks > timeout_sec:
                raise ValueError('Time to sleep between preview status check cannot be greater than preview timeout')

            preview_command.wait_for_finished(timeout_sec=timeout_sec, time_between_checks=time_between_checks)

        return preview_command

    @_dump_st_log_on_error
    def get_pipeline_acl(self, pipeline):
        """Get pipeline ACL.

        Args:
            pipeline (:py:class:`streamsets.sdk.st_models.Pipeline`): The pipeline instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.PipelineAcl`.
        """
        return st_models.PipelineAcl(self.api_client.get_pipeline_acl(pipeline_id=pipeline.id))

    @_dump_st_log_on_error
    def set_pipeline_acl(self, pipeline, pipeline_acl):
        """Update pipeline ACL.

        Args:
            pipeline (:py:class:`streamsets.sdk.st_models.Pipeline`): The pipeline instance.
            pipeline_acl (:py:class:`streamsets.sdk.st_models.PipelineAcl`): The pipeline ACL instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.Command`.
        """
        return self.api_client.set_pipeline_acl(pipeline_id=pipeline.id, pipeline_acl_json=pipeline_acl._data)

    @_dump_st_log_on_error
    def get_pipeline_permissions(self, pipeline):
        """Return pipeline permissions for a given pipeline.

        Args:
            pipeline (:obj:`streamsets.sdk.st_models.Pipeline`): The pipeline instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.PipelinePermissions`.
        """
        return st_models.PipelinePermissions(self.api_client.get_pipeline_permissions(pipeline_id=pipeline.id))

    @_dump_st_log_on_error
    def get_pipeline_status(self, pipeline):
        """Get status of a pipeline.

        Args:
            pipeline (:py:class:`streamsets.sdk.st_models.Pipeline`): The pipeline instance.
        """
        logger.info('Getting status of pipeline %s...', pipeline.id)
        return self.api_client.get_pipeline_status(pipeline_id=pipeline.id)

    @_dump_st_log_on_error
    def get_pipeline_history(self, pipeline):
        """Get a pipeline's history.

        Args:
            pipeline (:py:class:`streamsets.sdk.st_models.Pipeline`): The pipeline instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.History`.
        """
        logger.info('Getting pipeline history for %s...', pipeline.id)
        return st_models.History(self.api_client.get_pipeline_history(pipeline_id=pipeline.id))

    @_dump_st_log_on_error
    def get_pipeline(self, pipeline_id):
        """Get a pipeline.

        Args:
            pipeline_id (:obj:`str`): Id of pipeline.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.Pipeline`.
        """
        exported_pipeline = self.api_client.export_pipeline(pipeline_id=pipeline_id)
        builder = self.get_pipeline_builder()
        builder.import_pipeline(exported_pipeline)
        return builder.build(title=exported_pipeline['pipelineConfig']['title'])

    @property
    def transformer_configuration(self):
        """Return all configurations for StreamSets Transformer.
        Returns:
            A :obj:`dict` with property names as keys and property values as values.
        """
        return self.api_client.get_transformer_configuration().response.json()

    @property
    def id(self):
        """Return id for StreamSets Transformer.

        Returns:
            A :obj:`str` Transformer ID.
        """
        transformer_id_command = self.api_client.get_transformer_id()
        transformer_id_json = transformer_id_command.response.json() if transformer_id_command.response.content else {}
        return transformer_id_json['id'] if transformer_id_json else None

    @property
    def current_user(self):
        """Get currently logged-in user and its groups and roles.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.User`.
        """
        logger.info('Getting current user ...')
        return st_models.User(self.api_client.get_current_user())

    def change_password(self, old_password, new_password):
        """Change password for the current user.

        Args:
            old_password (:obj:`str`): old password.
            new_password (:obj:`str`): new password.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_api.Command`.
        """
        data = {'data': {'id':  self.current_user.name, 'oldPassword': old_password, 'newPassword': new_password},
                'envelopeVersion': "1"}
        return self.api_client.change_password(data)

    def get_logs(self, ending_offset=-1, extra_message=None, pipeline=None, severity=None):
        """Get logs.

        Args:
            ending_offset (:obj:`int`): ending_offset, Default: ``-1``.
            extra_message (:obj:`str`): extra_message, Default: ``None``.
            pipeline (:py:class:`streamsets.sdk.st_models.Pipeline`): The pipeline instance, Default: ``None``.
            severity (:obj:`str`): severity, Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.Log`.
        """
        pipeline_id = pipeline.id if pipeline is not None else None
        return st_models.Log(self.api_client.get_logs(ending_offset, extra_message,
                                                      pipeline_id, severity))

    def get_alerts(self):
        """Get pipeline alerts.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.Alerts`.
        """
        return st_models.Alerts(self.api_client.get_alerts())

    @_dump_st_log_on_error
    def get_bundle_generators(self):
        """Get available support bundle generators.

        Returns:
            An instance of :py:class:`streamsets.sdk.st_models.BundleGenerators`.
        """
        return st_models.BundleGenerators(self.api_client.get_bundle_generators())

    @_dump_st_log_on_error
    def get_bundle(self, generators=None):
        """Generate new support bundle.

        Returns:
            An instance of :py:class:`zipfile.ZipFile`.
        """
        return self.api_client.get_bundle(generators)
