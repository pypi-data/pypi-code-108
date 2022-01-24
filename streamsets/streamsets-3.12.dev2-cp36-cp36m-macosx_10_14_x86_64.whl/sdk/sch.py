# Copyright 2019 StreamSets Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Abstractions for interacting with StreamSets Dataflow Performance Manager."""
import io
import json
import logging
import requests
import threading
import uuid
import warnings
import zipfile
from datetime import datetime
from time import time

import requests

from . import sch_api
from .exceptions import JobInactiveError, UnsupportedMethodError
from .sdc import DataCollector as DataCollectorInstance
from .sch_models import (ActionAudits, AdminTool, Alert, ClassificationRuleBuilder, Configuration, Connection,
                         ConnectionAudits, ConnectionBuilder, ConnectionTags, ConnectionVerificationResult, Connections,
                         DataCollector, DataSla, DataSlaBuilder, DeploymentBuilder, Deployments, GroupBuilder, Groups,
                         Job, JobBuilder, Jobs, LoginAudits, Organization, OrganizationBuilder, Organizations, Pipeline,
                         PipelineBuilder, PipelineLabels, Pipelines, ProtectionMethodBuilder, ProtectionMethod,
                         ProtectionPolicies, ProtectionPolicy, ProtectionPolicyBuilder, ProvisioningAgents,
                         ReportDefinition, ReportDefinitionBuilder, ReportDefinitions, ScheduledTaskBuilder,
                         ScheduledTasks, StPipelineBuilder, Subscription, SubscriptionAudit, SubscriptionBuilder,
                         Subscriptions, Topologies, Topology, TopologyBuilder, Transformer, User, UserBuilder, Users)
from .utils import (SDC_DEFAULT_EXECUTION_MODE, SeekableList, TRANSFORMER_EXECUTION_MODES, join_url_parts,
                    wait_for_condition, reversed_dict, Version)

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_SDC_ID = 'SYSTEM_SDC_ID'
DEFAULT_WAIT_FOR_STATUS_TIMEOUT = 200
DEFAULT_WAIT_FOR_METRIC_TIMEOUT = 200
SDC_EXECUTOR_TYPE = 'COLLECTOR'
TRANSFORMER_EXECUTOR_TYPE = 'TRANSFORMER'


class ControlHub:
    """Class to interact with StreamSets Control Hub.

    Args:
        server_url (:obj:`str`): SCH server base URL.
        username (:obj:`str`): SCH username.
        password (:obj:`str`): SCH password.
    """
    VERIFY_SSL_CERTIFICATES = True
    def __init__(self,
                 server_url,
                 username,
                 password):
        self.server_url = server_url
        self.username = username
        self.password = password

        self.organization = self.username.split('@')[1]

        session_attributes = {'verify': self.VERIFY_SSL_CERTIFICATES}
        self.api_client = sch_api.ApiClient(server_url=self.server_url,
                                            username=self.username,
                                            password=self.password,
                                            session_attributes=session_attributes)

        self.login_command = self.api_client.login()

        self._roles = {user_role['id']: user_role['label']
                       for user_role in self.api_client.get_all_user_roles()}

        self._data_protector_version = None

        # We keep the Swagger API definitions as attributes for later use by various
        # builders.
        self._connection_api = (self.api_client.get_connection_api()
                                if Version(self.version) >= Version('3.19') else None)
        self._job_api = self.api_client.get_job_api()
        self._pipelinestore_api = self.api_client.get_pipelinestore_api()
        self._security_api = self.api_client.get_security_api()
        self._topology_api = self.api_client.get_topology_api()
        self._scheduler_api = self.api_client.get_scheduler_api()
        self._notification_api = self.api_client.get_notification_api()
        self._report_api = self.api_client.get_report_api()
        self._sla_api = self.api_client.get_sla_api()

        self._en_translations = self.api_client.get_translations_json()

        self._data_collectors = {}
        self._system_data_collector = None
        self._transformers = {}
        thread = threading.Thread(target=self._call_data_collectors)
        thread.start()

    def _call_data_collectors(self):
        self.system_data_collector
        self.data_collectors
        self.transformers

    @property
    def version(self):
        # The version of the Control Hub server, determined
        # by making a URL call to the server
        server_info = self.api_client.get_server_info()
        return server_info.response.json()['version']

    @property
    def system_data_collector(self):
        if self._system_data_collector is None:
            self._system_data_collector = DataCollectorInstance(server_url=join_url_parts(self.server_url,
                                                                                          'pipelinestore'),
                                                                control_hub=self)
        return self._system_data_collector

    @property
    def ldap_enabled(self):
        """Indication if LDAP is enabled or not.

        Returns:
            An instance of :obj:`boolean`.
        """
        return self.api_client.is_ldap_enabled().response.json()

    @property
    def organization_global_configuration(self):
        organization_global_configuration = self.api_client.get_organization_global_configurations().response.json()

        # Some of the config names are a bit long, so shorten them slightly...
        ID_TO_REMAP = {'accountType': 'Organization account type',
                       'contractExpirationTime': 'Timestamp of the contract expiration',
                       'trialExpirationTime': 'Timestamp of the trial expiration'}
        return Configuration(configuration=organization_global_configuration,
                             update_callable=self.api_client.update_organization_global_configurations,
                             id_to_remap=ID_TO_REMAP)

    @organization_global_configuration.setter
    def organization_global_configuration(self, value):
        self.api_client.update_organization_global_configurations(value._data)

    def set_user(self, username, password):
        """Set the user by which subsequent actions will be run.

        Args:
            username (:obj:`str`): SCH username.
            password (:obj:`str`): SCH password.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        # Preserve the original credentials in case something goes wrong trying to set a new user
        original_creds = dict(username=self.username, password=self.password, organization=self.organization)
        self.api_client.username = username
        self.api_client.password = password
        try:
            response = self.api_client.login()
            self.username = username
            self.password = password
            self.organization = username.split('@')[1]
        except requests.exceptions.HTTPError as e:
            self.username = self.api_client.username = original_creds['username']
            self.password = self.api_client.password = original_creds['password']
            self.organization = original_creds['organization']
            raise Exception('Encountered error while trying to set user.') from e


    def get_pipeline_builder(self, data_collector=None, transformer=None, fragment=False):
        """Get a pipeline builder instance with which a pipeline can be created.

        Args:
            data_collector (:py:obj:`streamsets.sdk.sch_models.DataCollector`, optional): The Data Collector
                in which to author the pipeline. If omitted, Control Hub's system SDC will be used. Default: ``None``.
            transformer (:py:obj:`streamsets.sdk.sch_models.Transformer`, optional): The Transformer in which to
                author the pipeline.
            fragment (:obj:`boolean`, optional): Specify if a fragment builder. Default: ``False``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.PipelineBuilder` or
            :py:class:`streamsets.sdk.sch_models.StPipelineBuilder`.
        """
        if transformer and data_collector:
            raise ValueError("Both transformer and data_collector arguments cannot be specified at the same time.")
        if transformer:
            data_collector = transformer
        pipeline = {property: None
                    for property in self._pipelinestore_api['definitions']['PipelineJson']['properties']}

        if data_collector is not None:
            data_collector_instance = data_collector.instance
            if fragment:
                create_fragment_response = (data_collector_instance.api_client
                                                                   .create_fragment('Pipeline Builder',
                                                                                    draft=True).response.json())
                pipeline_definition = json.dumps(create_fragment_response['pipelineFragmentConfig'])
                library_definitions = (json.dumps(create_fragment_response['libraryDefinitions'])
                                                 if create_fragment_response['libraryDefinitions'] else None)
                commit_pipeline_json = {'name': 'Pipeline Builder',
                                        'sdcId': data_collector.id,
                                        'fragment': True,
                                        'pipelineDefinition': pipeline_definition,
                                        'rulesDefinition': json.dumps(create_fragment_response['pipelineRules']),
                                        'libraryDefinitions': library_definitions}
                commit_pipeline_response = self.api_client.commit_pipeline(new_pipeline=True,
                                                                           import_pipeline=False,
                                                                           body=commit_pipeline_json,
                                                                           fragment=fragment).response.json()
                pipeline['sdcId'] = commit_pipeline_response['sdcId']
                pipeline['sdcVersion'] = commit_pipeline_response['sdcVersion']

                commit_id = commit_pipeline_response['commitId']
                pipeline_id = commit_pipeline_response['pipelineId']

                pipeline_commit = self.api_client.get_pipeline_commit(commit_id).response.json()
                pipeline_json = dict(pipelineFragmentConfig=json.loads(pipeline_commit['pipelineDefinition']),
                                     pipelineRules=json.loads(pipeline_commit['currentRules']['rulesDefinition']),
                                     libraryDefinitions=pipeline_commit['libraryDefinitions'])
                data_collector_instance._pipeline = pipeline_json
                self.api_client.delete_pipeline(pipeline_id)
            pipeline['sdcId'] = data_collector.id
            pipeline['sdcVersion'] = data_collector.version
        else:
            # For the system Data Collector, we need to create a new pipeline (which we then delete) to populate
            # DataCollector._pipeline.
            data_collector_instance = self.system_data_collector
            commit_pipeline_json = {'name': 'Pipeline Builder',
                                    'sdcId': DEFAULT_SYSTEM_SDC_ID}
            commit_pipeline_response = self.api_client.commit_pipeline(new_pipeline=True,
                                                                       import_pipeline=False,
                                                                       body=commit_pipeline_json,
                                                                       fragment=fragment).response.json()
            pipeline['sdcId'] = commit_pipeline_response['sdcId']
            pipeline['sdcVersion'] = commit_pipeline_response['sdcVersion']

            commit_id = commit_pipeline_response['commitId']
            pipeline_id = commit_pipeline_response['pipelineId']

            pipeline_commit = self.api_client.get_pipeline_commit(commit_id).response.json()
            if fragment:
                pipeline_json = dict(pipelineFragmentConfig=json.loads(pipeline_commit['pipelineDefinition']),
                                     pipelineRules=json.loads(pipeline_commit['currentRules']['rulesDefinition']),
                                     libraryDefinitions=pipeline_commit['libraryDefinitions'])
            else:
                pipeline_json = dict(pipelineConfig=json.loads(pipeline_commit['pipelineDefinition']),
                                     pipelineRules=json.loads(pipeline_commit['currentRules']['rulesDefinition']),
                                     libraryDefinitions=pipeline_commit['libraryDefinitions'])
            data_collector_instance._pipeline = pipeline_json
            self.api_client.delete_pipeline(pipeline_id)

        executor_pipeline_builder = data_collector_instance.get_pipeline_builder(fragment=fragment)
        if transformer:
            pipeline['executorType'] = 'TRANSFORMER'
            return StPipelineBuilder(pipeline=pipeline,
                                     transformer_pipeline_builder=executor_pipeline_builder,
                                     control_hub=self,
                                     fragment=fragment)
        return PipelineBuilder(pipeline=pipeline,
                               data_collector_pipeline_builder=executor_pipeline_builder,
                               control_hub=self,
                               fragment=fragment)

    def publish_pipeline(self, pipeline, commit_message='New pipeline', draft=False):
        """Publish a pipeline.

        Args:
            pipeline (:py:obj:`streamsets.sdk.sch_models.Pipeline`): Pipeline object.
            commit_message (:obj:`str`, optional): Default: ``'New pipeline'``.
            draft (:obj:`boolean`, optional): Default: ``False``.
        """
        # Get the updated stage data and update it in the pipelineDefinition json string.
        pipeline_definition = pipeline._pipeline_definition
        pipeline_stages = pipeline.stages
        pipeline_definition['stages'] = []
        for stage in pipeline_stages:
            pipeline_definition['stages'].append(stage._data)
        pipeline._pipeline_definition = pipeline_definition
        pipeline._data['pipelineDefinition'] = pipeline_definition

        # A :py:class:`streamsets.sdk.sch_models.Pipeline` instance with no commit ID hasn't been
        # published to Control Hub before, so we do so first.
        if not pipeline.commit_id:
            commit_pipeline_json = {'name': pipeline._pipeline_definition['title'],
                                    'sdcId': pipeline.sdc_id}
            if pipeline.sdc_id != DEFAULT_SYSTEM_SDC_ID:
                commit_pipeline_json.update({'pipelineDefinition': json.dumps(pipeline._pipeline_definition),
                                             'rulesDefinition': json.dumps(pipeline._rules_definition)})
            # fragmentCommitIds property is not returned by :py:meth:`streamsets.sdk.sch_api.ApiClient.commit_pipeline
            # and hence have to store it and add it to pipeline data before publishing the pipeline.
            fragment_commit_ids = pipeline._data.get('fragmentCommitIds')
            execution_mode = pipeline.configuration.get('executionMode', SDC_DEFAULT_EXECUTION_MODE)

            if execution_mode in TRANSFORMER_EXECUTION_MODES:
                commit_pipeline_json.update({'executorType': 'TRANSFORMER'})
            pipeline._data = self.api_client.commit_pipeline(new_pipeline=True,
                                                             import_pipeline=False,
                                                             fragment=pipeline.fragment,
                                                             execution_mode=execution_mode,
                                                             body=commit_pipeline_json).response.json()
            if fragment_commit_ids and not pipeline.fragment:
                pipeline._data['fragmentCommitIds'] = fragment_commit_ids
        # If the pipeline does have a commit ID and is not a draft, we want to create a new draft and update the
        # existing one in the pipeline store instead of creating a new one.
        elif not getattr(pipeline, 'draft', False):
            pipeline._data = self.api_client.create_pipeline_draft(
                commit_id=pipeline.commit_id,
                authoring_sdc_id=pipeline.sdc_id,
                authoring_sdc_version=pipeline.sdc_version
            ).response.json()
            # The pipeline name is overwritten when drafts are created, so we account for it here.
            pipeline.name = pipeline._pipeline_definition['title']

        pipeline.commit_message = commit_message
        pipeline.current_rules['rulesDefinition'] = json.dumps(pipeline._rules_definition)
        pipeline._pipeline_definition['metadata'].update({'dpm.pipeline.rules.id': pipeline.current_rules['id'],
                                                          'dpm.pipeline.id': pipeline.pipeline_id,
                                                          'dpm.pipeline.version': pipeline.version,
                                                          'dpm.pipeline.commit.id': pipeline.commit_id})
        pipeline._data['pipelineDefinition'] = json.dumps(pipeline._pipeline_definition)

        # Translated js code from https://git.io/fj1kr.
        # Call sdc api to import pipeline and libraryDefinitions.
        validate = True
        if pipeline.sdc_id != DEFAULT_SYSTEM_SDC_ID:
            validate = False
            pipeline_definition = json.loads(pipeline._data['pipelineDefinition'])
            entity_id = 'fragmentId' if 'fragmentId' in pipeline_definition else 'pipelineId'
            sdc_pipeline_id = pipeline_definition[entity_id]

            config_key = 'pipelineFragmentConfig' if pipeline.fragment else 'pipelineConfig'
            pipeline_envelope = {config_key: pipeline._pipeline_definition,
                                 'pipelineRules': pipeline._rules_definition}

            execution_mode = pipeline.configuration.get('executionMode', SDC_DEFAULT_EXECUTION_MODE)
            executors = self.transformers if execution_mode in TRANSFORMER_EXECUTION_MODES else self.data_collectors
            if pipeline.fragment:
                response_envelope = (executors.get(id=pipeline.sdc_id)
                                         .instance.api_client
                                         .import_fragment(fragment_id=sdc_pipeline_id,
                                                          fragment_json=pipeline_envelope,
                                                          include_library_definitions=True,
                                                          draft=True))
            else:
                response_envelope = (executors.get(id=pipeline.sdc_id)
                                         .instance.api_client
                                         .import_pipeline(pipeline_id=sdc_pipeline_id,
                                                          pipeline_json=pipeline_envelope,
                                                          overwrite=True,
                                                          include_library_definitions=True,
                                                          auto_generate_pipeline_id=True,
                                                          draft=True))

            response_envelope[config_key]['pipelineId'] = sdc_pipeline_id
            if execution_mode in TRANSFORMER_EXECUTION_MODES:
                response_envelope[config_key].update({'executorType': 'TRANSFORMER'})
            pipeline._data['pipelineDefinition'] = json.dumps(response_envelope[config_key])

            if response_envelope['libraryDefinitions']:
                pipeline._data['libraryDefinitions'] = json.dumps(response_envelope['libraryDefinitions'])
            else:
                pipeline._data['libraryDefinitions'] = None
            pipeline._data['currentRules']['rulesDefinition'] = json.dumps(response_envelope['pipelineRules'])

        save_pipeline_commit_command = self.api_client.save_pipeline_commit(commit_id=pipeline.commit_id,
                                                                            validate=validate,
                                                                            include_library_definitions=True,
                                                                            body=pipeline._data)
        if not draft:
            publish_pipeline_commit_command = self.api_client.publish_pipeline_commit(commit_id=pipeline.commit_id,
                                                                                      commit_message=commit_message)
        # Due to DPM-4470, we need to do one more REST API call to get the correct pipeline data.
        pipeline_commit = self.api_client.get_pipeline_commit(commit_id=pipeline.commit_id).response.json()

        pipeline._data = pipeline_commit
        if pipeline._builder is not None:
            pipeline._builder._sch_pipeline = pipeline_commit
        return save_pipeline_commit_command if draft else publish_pipeline_commit_command

    def delete_pipeline(self, pipeline, only_selected_version=False):
        """Delete a pipeline.

        Args:
            pipeline (:py:obj:`streamsets.sdk.sch_models.Pipeline`): Pipeline object.
            only_selected_version (:obj:`boolean`): Delete only current commit.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        if only_selected_version:
            return self.api_client.delete_pipeline_commit(pipeline.commit_id)
        return self.api_client.delete_pipeline(pipeline.pipeline_id)

    def duplicate_pipeline(self, pipeline, name=None, description='New Pipeline', number_of_copies=1):
        """Duplicate an existing pipeline.

        Args:
            pipeline (:py:obj:`streamsets.sdk.sch_models.Pipeline`): Pipeline object.
            name (:obj:`str`, optional): Name of the new pipeline(s). Default: ``None``.
            description (:obj:`str`, optional): Description for new pipeline(s). Default: ``'New Pipeline'``.
            number_of_copies (:obj:`int`, optional): Number of copies. Default: ``1``.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.Pipeline`.
        """
        if name is None:
            name = '{} copy'.format(pipeline.name)
        # Add a unique name prefix to identify duplicated pipelines
        dummy_name_prefix = '{}:{}'.format(name, str(uuid.uuid4()))

        duplicated_pipelines = SeekableList()

        duplicate_body = {property: None
                          for property in self._pipelinestore_api['definitions']['DuplicatePipelineJson']['properties']}
        duplicate_body.update({'namePrefix': dummy_name_prefix,
                               'description': description,
                               'numberOfCopies': number_of_copies})
        self.api_client.duplicate_pipeline(pipeline.commit_id, duplicate_body)

        if number_of_copies == 1:
            dummy_names = [dummy_name_prefix]
        else:
            dummy_names = ['{}{}'.format(dummy_name_prefix, i) for i in range(1, number_of_copies+1)]
        # Update dummy names with actual names
        for i, dummy_name in enumerate(dummy_names):
            duplicated_pipeline = self.pipelines.get(only_published=False, name=dummy_name)
            if number_of_copies == 1:
                duplicated_pipeline.name = name
            else:
                duplicated_pipeline.name = '{}{}'.format(name, i+1)
            self.api_client.save_pipeline_commit(commit_id=duplicated_pipeline.commit_id,
                                                 include_library_definitions=True,
                                                 body=duplicated_pipeline._data)
            duplicated_pipelines.append(duplicated_pipeline)
        return duplicated_pipelines

    def update_pipelines_with_different_fragment_version(self, pipelines, from_fragment_version,
                                                         to_fragment_version):
        """Update pipelines with latest pipeline fragment commit version.

        Args:
            pipelines (:obj:`list`): List of :py:class:`streamsets.sdk.sch_models.Pipeline` instances.
            from_fragment_version (:py:obj:`streamsets.sdk.sch_models.PipelineCommit`): commit of fragment from which
                                                                                        the pipeline needs to be
                                                                                        updated.
            to_fragment_version (:py:obj:`streamsets.sdk.sch_models.PipelineCommit`): commit of fragment to which
                                                                                      the pipeline needs to be updated.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`
        """
        pipeline_commit_ids = [pipeline.commit_id for pipeline in pipelines]
        return self.api_client.update_pipelines_with_fragment_commit_version(pipeline_commit_ids,
                                                                             from_fragment_version.commit_id,
                                                                             to_fragment_version.commit_id)

    @property
    def pipeline_labels(self):
        """Pipeline labels.

        Returns:
            An instance of :py:obj:`streamsets.sdk.sch_models.PipelineLabels`.
        """
        return PipelineLabels(self, organization=self.organization)

    def delete_pipeline_labels(self, *pipeline_labels):
        """Delete pipeline labels.

        Args:
            *pipeline_labels: One or more instances of :py:class:`streamsets.sdk.sch_models.PipelineLabel`.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        pipeline_label_ids = [pipeline_label.id for pipeline_label in pipeline_labels]
        logger.info('Deleting pipeline labels %s ...', pipeline_label_ids)
        delete_pipeline_label_command = self.api_client.delete_pipeline_labels(body=pipeline_label_ids)
        return delete_pipeline_label_command

    def duplicate_job(self, job, name=None, description=None, number_of_copies=1):
        """Duplicate an existing job.

        Args:
            job (:py:obj:`streamsets.sdk.sch_models.Job`): Job object.
            name (:obj:`str`, optional): Name of the new job(s). Default: ``None``. If not specified, name of the job
                                         with ``' copy'`` appended to the end will be used.
            description (:obj:`str`, optional): Description for new job(s). Default: ``None``.
            number_of_copies (:obj:`int`, optional): Number of copies. Default: ``1``.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.Job`.
        """
        if name is None:
            name = '{} copy'.format(job.job_name)
        # Add a unique name prefix to identify duplicated job
        dummy_name_prefix = '{}:{}'.format(name, str(uuid.uuid4()))

        duplicated_jobs = SeekableList()

        duplicate_body = {property: None
                          for property in self._job_api['definitions']['DuplicateJobJson']['properties']}
        duplicate_body.update({'namePrefix': dummy_name_prefix,
                               'description': description,
                               'numberOfCopies': number_of_copies})
        self.api_client.duplicate_job(job.job_id, duplicate_body)

        if number_of_copies == 1:
            dummy_names = [dummy_name_prefix]
        else:
            dummy_names = ['{}{}'.format(dummy_name_prefix, i) for i in range(1, number_of_copies+1)]
        # Update dummy names with actual names
        for i, dummy_name in enumerate(dummy_names):
            duplicated_job = self.jobs.get(job_name=dummy_name)
            if number_of_copies == 1:
                duplicated_job.job_name = name
            else:
                duplicated_job.job_name = '{}{}'.format(name, i+1)
            self.update_job(duplicated_job)
            duplicated_jobs.append(duplicated_job)
        return duplicated_jobs

    def get_user_builder(self):
        """Get a user builder instance with which a user can be created.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.UserBuilder`.
        """
        user = {}
        # Update the UserJson with the API definitions from Swagger.
        user.update({property: None
                     for property in self._security_api['definitions']['UserJson']['properties']})

        # Set other properties based on defaults from the web UI.
        user_defaults = {'active': True,
                         'groups': ['all@{}'.format(self.organization)],
                         'organization': self.organization,
                         'passwordGenerated': True,
                         'roles': ['timeseries:reader',
                                   'datacollector:manager',
                                   'jobrunner:operator',
                                   'pipelinestore:pipelineEditor',
                                   'topology:editor',
                                   'org-user',
                                   'sla:editor',
                                   'provisioning:operator',
                                   'user',
                                   'datacollector:creator',
                                   'notification:user'],
                         'userDeleted': False}
        user.update(user_defaults)

        return UserBuilder(user=user, roles=self._roles, control_hub=self)

    def add_user(self, user):
        """Add a user. Some user attributes are updated by SCH such as
            created_by,
            created_on,
            last_modified_by,
            last_modified_on,
            password_expires_on,
            password_system_generated.

        Args:
            user (:py:class:`streamsets.sdk.sch_models.User`): User object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        logger.info('Adding a user %s ...', user)
        create_user_command = self.api_client.create_user(self.organization, user._data)
        # Update :py:class:`streamsets.sdk.sch_models.User` with updated User metadata.
        user._data = create_user_command.response.json()
        return create_user_command

    def update_user(self, user):
        """Update a user. Some user attributes are updated by SCH such as
            last_modified_by,
            last_modified_on.

        Args:
            user (:py:class:`streamsets.sdk.sch_models.User`): User object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        logger.info('Updating a user %s ...', user)
        update_user_command = self.api_client.update_user(body=user._data,
                                                          org_id=self.organization,
                                                          user_id=user.id)
        user._data = update_user_command.response.json()
        return update_user_command

    def deactivate_user(self, *users, organization=None):
        """Deactivate Users for all given User IDs.

        Args:
            *users: One or more instances of :py:class:`streamsets.sdk.sch_models.User`.
            organization (:obj:`str`, optional): Default: ``None``. If not specified, current organization will be used.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        user_ids = [user.id for user in users]
        logger.info('Deactivating users %s ...', user_ids)
        organization = self.organization if organization is None else organization
        deactivate_users_command = self.api_client.deactivate_users(body=user_ids,
                                                                    org_id=organization)
        return deactivate_users_command

    def delete_user(self, *users, deactivate=False):
        """Delete users. Deactivate users before deleting if configured.

        Args:
            *users: One or more instances of :py:class:`streamsets.sdk.sch_models.User`.
            deactivate (:obj:`bool`, optional): Default: ``False``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        if deactivate:
            self.deactivate_user(*users)

        delete_user_command = None
        if len(users) == 1:
            logger.info('Deleting a user %s ...', users[0])
            delete_user_command = self.api_client.delete_user(org_id=self.organization,
                                                              user_id=users[0].id)
        else:
            user_ids = [user.id for user in users]
            logger.info('Deleting users %s ...', user_ids)
            delete_user_command = self.api_client.delete_users(body=user_ids,
                                                               org_id=self.organization)
        return delete_user_command

    @property
    def users(self):
        """Users.

        Returns:
            An instance of :py:obj:`streamsets.sdk.sch_models.Users`.
        """
        return Users(self, self._roles, self.organization)

    @property
    def login_audits(self):
        """Login Audits.

        Returns:
            An instance of :py:obj:`streamsets.sdk.sch_models.LoginAudits`.
        """
        return LoginAudits(self, self.organization)

    @property
    def action_audits(self):
        """Action Audits.

        Returns:
            An instance of :py:obj:`streamsets.sdk.sch_models.ActionAudits`.
        """
        return ActionAudits(self, self.organization)

    @property
    def connection_audits(self):
        """Connection Audits.

        Returns:
            An instance of :py:obj:`streamsets.sdk.sch_models.ConnectionAudits`.
        """
        return ConnectionAudits(self, self.organization)

    def get_group_builder(self):
        """Get a group builder instance with which a group can be created.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.GroupBuilder`.
        """
        # Update the GroupJson with the API definitions from Swagger.
        group = {property: None
                 for property in self._security_api['definitions']['GroupJson']['properties']}

        # Set other properties based on defaults from the web UI.
        group_defaults = {'organization': self.organization,
                          'roles': ['timeseries:reader',
                                    'datacollector:manager',
                                    'jobrunner:operator',
                                    'pipelinestore:pipelineEditor',
                                    'topology:editor',
                                    'org-user',
                                    'sla:editor',
                                    'provisioning:operator',
                                    'user',
                                    'datacollector:creator',
                                    'notification:user'],
                          'users': []}
        group.update(group_defaults)

        return GroupBuilder(group=group, roles=self._roles)

    def add_group(self, group):
        """Add a group.

        Args:
            group (:py:class:`streamsets.sdk.sch_models.Group`): Group object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        logger.info('Adding a group %s ...', group)
        create_group_command = self.api_client.create_group(self.organization, group._data)
        # Update :py:class:`streamsets.sdk.sch_models.Group` with updated Group metadata.
        group._data = create_group_command.response.json()
        return create_group_command

    def update_group(self, group):
        """Update a group.

        Args:
            group (:py:class:`streamsets.sdk.sch_models.Group`): Group object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        logger.info('Updating a group %s ...', group)
        update_group_command = self.api_client.update_group(body=group._data,
                                                            org_id=self.organization,
                                                            group_id=group.id)
        group._data = update_group_command.response.json()
        return update_group_command

    def delete_group(self, *groups):
        """Delete groups.

        Args:
            *groups: One or more instances of :py:class:`streamsets.sdk.sch_models.Group`.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        if len(groups) == 1:
            logger.info('Deleting a group %s ...', groups[0])
            delete_group_command = self.api_client.delete_group(org_id=self.organization,
                                                                group_id=groups[0].id)
        else:
            group_ids = [group.id for group in groups]
            logger.info('Deleting groups %s ...', group_ids)
            delete_group_command = self.api_client.delete_groups(body=group_ids,
                                                                 org_id=self.organization)
        return delete_group_command

    @property
    def groups(self):
        """Groups.

        Returns:
            An instance of :py:obj:`streamsets.sdk.sch_models.Groups`.
        """
        return Groups(self, self._roles, self.organization)

    @property
    def data_collectors(self):
        """Data Collectors registered to the Control Hub instance.

        Returns:
            Returns a :py:class:`streamsets.sdk.utils.SeekableList` of
            :py:class:`streamsets.sdk.sch_models.DataCollector` instances.
        """
        self._get_update_executors_cache('COLLECTOR')
        return SeekableList(self._data_collectors.values())

    @property
    def transformers(self):
        """Transformers registered to the Control Hub instance.

        Returns:
            Returns a :py:class:`streamsets.sdk.utils.SeekableList` of
            :py:class:`streamsets.sdk.sch_models.Transformer` instances.
        """
        self._get_update_executors_cache('TRANSFORMER')
        return SeekableList(self._transformers.values())

    @property
    def provisioning_agents(self):
        """Provisioning Agents registered to the Control Hub instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ProvisioningAgents`.
        """
        return ProvisioningAgents(self, self.organization)

    def delete_provisioning_agent(self, provisioning_agent):
        """Delete provisioning agent.

        Args:
            provisioning_agent (:py:class:`streamets.sdk.sch_models.ProvisioningAgent`):

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        return self.api_client.delete_provisioning_agent(provisioning_agent.id)

    def deactivate_provisioning_agent(self, provisioning_agent):
        """Deactivate provisioning agent.

        Args:
            provisioning_agent (:py:class:`streamets.sdk.sch_models.ProvisioningAgent`):

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        return self.api_client.deactivate_components(org_id=self.organization,
                                                     components_json=[provisioning_agent.id])

    def activate_provisioning_agent(self, provisioning_agent):
        """Activate provisioning agent.

        Args:
            provisioning_agent (:py:class:`streamets.sdk.sch_models.ProvisioningAgent`):

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        return self.api_client.activate_components(org_id=self.organization,
                                                   components_json=[provisioning_agent.id])

    def delete_provisioning_agent_token(self, provisioning_agent):
        """Delete provisioning agent token.

        Args:
            provisioning_agent (:py:class:`streamets.sdk.sch_models.ProvisioningAgent`):

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        return self.api_client.delete_components(org_id=self.organization,
                                                 components_json=[provisioning_agent.id])

    @property
    def deployments(self):
        """Deployments.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Deployments`.
        """
        return Deployments(self, self.organization)

    def get_deployment_builder(self):
        """Get a deployment builder instance with which a deployment can be created.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.DeploymentBuilder`.
        """
        deployment = {'name': None, 'description': None, 'labels': None, 'numInstances': None, 'spec': None,
                      'agentId': None}
        return DeploymentBuilder(dict(deployment))

    def add_deployment(self, deployment):
        """Add a deployment.

        Args:
            deployment (:py:class:`streamsets.sdk.sch_models.Deployment`): Deployment object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        create_deployment_command = self.api_client.create_deployment(deployment._data)
        # Update :py:class:`streamsets.sdk.sch_models.Deployment` with updated Deployment metadata.
        deployment._data = create_deployment_command.response.json()
        deployment._control_hub = self
        return create_deployment_command

    def update_deployment(self, deployment):
        """Update a deployment.

        Args:
            deployment (:py:class:`streamsets.sdk.sch_models.Deployment`): Deployment object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        logger.info('Updating deployment %s ...', deployment)
        update_deployment_command = self.api_client.update_deployment(deployment_id=deployment.id,
                                                                      body=deployment._data)
        deployment._data = update_deployment_command.response.json()
        return update_deployment_command

    def scale_deployment(self, deployment, num_instances):
        """Scale up/down active deployment.

        Args:
            deployment (:py:class:`streamsets.sdk.sch_models.Deployment`): Deployment object.
            num_instances (:obj:`int`): Number of sdc instances.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        scale_deployment_command = self.api_client.scale_deployment(deployment_id=deployment.id,
                                                                    num_instances=num_instances)
        deployment._data = self.deployments.get(id=deployment.id)._data
        return scale_deployment_command

    def delete_deployment(self, *deployments):
        """Delete deployments.

        Args:
            *deployments: One or more instances of :py:class:`streamsets.sdk.sch_models.Deployment`.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        if len(deployments) == 1:
            logger.info('Deleting deployment %s ...', deployments[0])
            delete_deployment_command = self.api_client.delete_deployment(deployment_id=deployments[0].id)
        else:
            deployment_ids = [deployment.id for deployment in deployments]
            logger.info('Deleting deployments %s ...', deployment_ids)
            delete_deployment_command = self.api_client.delete_deployments(body=deployment_ids)
        return delete_deployment_command

    def start_deployment(self, deployment, **kwargs):
        """Start Deployment.

        Args:
            deployment (:py:class:`streamsets.sdk.sch_models.Deployment`): Deployment instance.
            wait (:obj:`bool`, optional): Wait for deployment to start. Default: ``True``.
            wait_for_statuses (:obj:`list`, optional): Deployment statuses to wait on. Default: ``['ACTIVE']``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.DeploymentStartStopCommand`.
        """
        provisioning_agent_id = deployment.provisioning_agent.id
        start_cmd = self.api_client.start_deployment(deployment.id, provisioning_agent_id)
        if kwargs.get('wait', True):
            start_cmd.wait_for_deployment_statuses(kwargs.get('wait_for_statuses', ['ACTIVE']))
        return start_cmd

    def stop_deployment(self, deployment, wait_for_statuses=['INACTIVE']):
        """Stop Deployment.

        Args:
            deployment (:py:class:`streamsets.sdk.sch_models.Deployment`): Deployment instance.
            wait_for_statuses (:obj:`list`, optional): List of statuses to wait for. Default: ``['INACTIVE']``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.DeploymentStartStopCommand`.
        """
        provisioning_agent_id = deployment.provisioning_agent.id
        stop_cmd = self.api_client.stop_deployment(deployment.id)
        if wait_for_statuses:
            stop_cmd.wait_for_deployment_statuses(wait_for_statuses)
        return stop_cmd

    def acknowledge_deployment_error(self, *deployments):
        """Acknowledge errors for one or more deployments.

        Args:
            *deployments: One or more instances of :py:class:`streamsets.sdk.sch_models.Deployment`.
        """
        deployment_ids = [deployment.id for deployment in deployments]
        logger.info('Acknowledging errors for deployment(s) %s ...', deployment_ids)
        self.api_client.deployments_acknowledge_errors(deployment_ids)

    def _get_update_executors_cache(self, executor_type):
        """Get or update the executors cache variables.

        Args:
            executor_type (:obj:`str`): Executor type.

        Returns:
            A :py:class:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.DataCollector` or
            :py:class:`streamsets.sdk.sch_models.Transformer` instances.
        """
        executors = self.api_client.get_all_registered_executors(organization=None,
                                                                 executor_type=executor_type,
                                                                 edge=None,
                                                                 label=None,
                                                                 version=None,
                                                                 offset=None,
                                                                 len_=None,
                                                                 order_by=None,
                                                                 order=None).response.json()
        executor_ids = {executor['id'] for executor in executors}

        if executor_type == 'COLLECTOR':
            local_executor_ids = set(self._data_collectors.keys())
        elif executor_type == 'TRANSFORMER':
            local_executor_ids = set(self._transformers.keys())
        if executor_ids - local_executor_ids:
            # Case where we have to add more DataCollector or Transformer instances
            ids_to_be_added = executor_ids - local_executor_ids
            # Doing an O(N^2) here because it is easy to do so and N is too small to consider time complexity.
            for executor in executors:
                for executor_id in ids_to_be_added:
                    if executor_id == executor['id']:
                        if executor_type == 'COLLECTOR':
                            self._data_collectors[executor_id] = DataCollector(executor, self)
                        elif executor_type == 'TRANSFORMER':
                            self._transformers[executor_id] = Transformer(executor, self)
        else:
            # This will handle both the cases when the set of ids are equal and local_executor_ids has more ids.
            ids_to_be_removed = local_executor_ids - executor_ids
            for executor_id in ids_to_be_removed:
                if executor_type == 'COLLECTOR':
                    del self._data_collectors[executor_id]
                elif executor_type == 'TRANSFORMER':
                    del self._transformers[executor_id]
        if executor_type == 'COLLECTOR':
            return SeekableList(self._data_collectors.values())
        elif executor_type == 'TRANSFORMER':
            return SeekableList(self._transformers.values())

    def deactivate_datacollector(self, data_collector):
        """Deactivate data collector.

         Args:
            data_collector (:py:class:`streamsets.sdk.sch_models.DataCollector`): Data Collector object.
        """
        logger.info('Deactivating data collector component from organization %s with component id %s ...',
                    self.organization, data_collector.id)
        self.api_client.deactivate_components(org_id=self.organization,
                                              components_json=[data_collector.id])

    def activate_datacollector(self, data_collector):
        """Activate data collector.

        Args:
            data_collector (:py:class:`streamsets.sdk.sch_models.DataCollector`): Data Collector object.
        """
        logger.info('Activating data collector component from organization %s with component id %s ...',
                    self.organization, data_collector.id)
        self.api_client.activate_components(org_id=self.organization,
                                            components_json=[data_collector.id])

    def delete_data_collector(self, data_collector):
        """Delete data collector.

        Args:
            data_collector (:py:class:`streamsets.sdk.sch_models.DataCollector`): Data Collector object.
        """
        logger.info('Deleting data dollector %s ...', data_collector.id)
        self.api_client.delete_sdc(data_collector_id=data_collector.id)

    def delete_and_unregister_data_collector(self, data_collector):
        """Delete and Unregister data collector.

        Args:
            data_collector (:py:class:`streamsets.sdk.sch_models.DataCollector`): Data Collector object.
        """
        logger.info('Deactivating data collector component from organization %s with component id %s ...',
                    data_collector.organization, data_collector.id)
        self.api_client.deactivate_components(org_id=self.organization,
                                              components_json=[data_collector.id])
        logger.info('Deleting data collector component from organization %s with component id %s ...',
                    data_collector.organization, data_collector.id)
        self.api_client.delete_components(org_id=self.organization,
                                          components_json=[data_collector.id])
        logger.info('Deleting data dollector from jobrunner %s ...', data_collector.id)
        self.api_client.delete_sdc(data_collector_id=data_collector.id)

    def update_data_collector_labels(self, data_collector):
        """Update data collector labels.

        Args:
            data_collector (:py:class:`streamsets.sdk.sch_models.DataCollector`): Data Collector object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.DataCollector`.
        """
        logger.info('Updating data collector %s with labels %s ...',
                    data_collector.id, data_collector.labels)
        return DataCollector(self.api_client.update_sdc_labels(
            data_collector_id=data_collector.id,
            data_collector_json=data_collector._data).response.json(), self)

    def get_data_collector_labels(self, data_collector):
        """Returns all labels assigned to data collector.

        Args:
            data_collector (:py:class:`streamsets.sdk.sch_models.DataCollector`): Data Collector object.

        Returns:
            A :obj:`list` of data collector assigned labels.
        """
        logger.info('Getting assigned labels for data collector %s ...', data_collector.id)
        return self.api_client.get_sdc_lables(data_collector_id=data_collector.id).response.json()

    def update_data_collector_resource_thresholds(self, data_collector, max_cpu_load=None, max_memory_used=None,
                                                  max_pipelines_running=None):
        """Updates data collector resource thresholds.

        Args:
            data_collector (:py:class:`streamsets.sdk.sch_models.DataCollector`): Data Collector object.
            max_cpu_load (:obj:`float`, optional): Max CPU load in percentage. Default: ``None``.
            max_memory_used (:obj:`int`, optional): Max memory used in MB. Default: ``None``.
            max_pipelines_running (:obj:`int`, optional): Max pipelines running. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        thresholds = {"maxMemoryUsed": max_memory_used,
                      "maxCpuLoad": max_cpu_load,
                      "maxPipelinesRunning": max_pipelines_running}
        thresholds_to_be_updated = {k: v for k, v in  thresholds.items() if v is not None}
        data_collector_json = data_collector._data
        data_collector_json.update(thresholds_to_be_updated)
        cmd = self.api_client.update_sdc_resource_thresholds(data_collector.id, data_collector_json)
        data_collector._refresh()
        return cmd

    def balance_data_collectors(self, *data_collectors):
        """Balance all jobs running on given Data Collectors.

        Args:
            *sdcs: One or more instances of :py:class:`streamsets.sdk.sch_models.DataCollector`.
        """
        data_collector_ids = [data_collector.id for data_collector in data_collectors]
        logger.info('Balancing all jobs on Data Collector(s) %s ...', data_collector_ids)
        self.api_client.balance_data_collectors(data_collector_ids)

    def get_job_builder(self):
        """Get a job builder instance with which a job can be created.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.JobBuilder`.
        """
        job = {property: None
               for property in self._job_api['definitions']['JobJson']['properties']}

        # Set other properties based on defaults from the web UI.
        JOB_DEFAULTS = {'forceStopTimeout': 120000,
                        'labels': ['all'],
                        'numInstances': 1,
                        'statsRefreshInterval': 60000,
                        'rawJobTags': []}
        job.update(JOB_DEFAULTS)
        return JobBuilder(job=job, control_hub=self)

    def get_components(self, component_type_id, offset=None, len_=None, order_by='LAST_VALIDATED_ON', order='ASC'):
        """Get components.

        Args:
            component_type_id (:obj:`str`): Component type id.
            offset (:obj:`str`, optional): Default: ``None``.
            len_ (:obj:`str`, optional): Default: ``None``.
            order_by (:obj:`str`, optional): Default: ``'LAST_VALIDATED_ON'``.
            order (:obj:`str`, optional): Default: ``'ASC'``.
        """
        return self.api_client.get_components(org_id=self.organization,
                                              component_type_id=component_type_id,
                                              offset=offset,
                                              len_=len_,
                                              order_by=order_by,
                                              order=order)

    def create_components(self, component_type, number_of_components=1, active=True):
        """Create components.

        Args:
            component_type (:obj:`str`): Component type.
            number_of_components (:obj:`int`, optional): Default: ``1``.
            active (:obj:`bool`, optional): Default: ``True``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.CreateComponentsCommand`.
        """
        return self.api_client.create_components(org_id=self.organization,
                                                 component_type=component_type,
                                                 number_of_components=number_of_components,
                                                 active=active)

    def get_organization_builder(self):
        """Get an organization builder instance with which an organization can be created.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.OrganizationBuilder`.
        """
        organization = {property: None
                        for property in self._security_api['definitions']['NewOrganizationJson']['properties']}

        # Set other properties based on defaults from the web UI.
        organization_defaults = {'active': True,
                                 'passwordExpiryTimeInMillis': 5184000000,  # 60 days
                                 'validDomains': '*'}
        organization_admin_user_defaults = {'active': True,
                                            'roles': ['user',
                                                      'org-admin',
                                                      'datacollector:admin',
                                                      'pipelinestore:pipelineEditor',
                                                      'jobrunner:operator',
                                                      'timeseries:reader',
                                                      'timeseries:writer',
                                                      'topology:editor',
                                                      'notification:user',
                                                      'sla:editor',
                                                      'provisioning:operator']}
        organization['organization'] = organization_defaults
        organization['organizationAdminUser'] = organization_admin_user_defaults

        return OrganizationBuilder(organization=organization['organization'],
                                   organization_admin_user=organization['organizationAdminUser'])

    def add_organization(self, organization):
        """Add an organization.

        Args:
            organization (:py:obj:`streamsets.sdk.sch_models.Organization`): Organization object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        logger.info('Adding organization %s ...', organization.name)
        body = {'organization': organization._data,
                'organizationAdminUser': organization._organization_admin_user}
        create_organization_command = self.api_client.create_organization(body)
        organization._data = create_organization_command.response.json()
        return create_organization_command

    def update_organization(self, organization):
        """Update an organization.

        Args:
            organization (:py:obj:`streamsets.sdk.sch_models.Organization`): Organization instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        logger.info('Updating organization %s ...', organization.name)
        update_organization_command = self.api_client.update_organization(org_id=organization.id,
                                                                          body=organization._data)
        organization._data = update_organization_command.response.json()
        return update_organization_command

    @property
    def organizations(self):
        """Organizations.

        Returns:
            An instance of :py:obj:`streamsets.sdk.sch_models.Organizations`.
        """
        return Organizations(self)

    @property
    def pipelines(self):
        """Pipelines.

        Returns:
            An instance of :py:obj:`streamsets.sdk.sch_models.Pipelines`.
        """
        return Pipelines(self, self.organization)

    def import_pipelines_from_archive(self, archive, commit_message, fragments=False):
        """Import pipelines from archived zip directory.

        Args:
            archive (:obj:`file`): file containing the pipelines.
            commit_message (:obj:`str`): Commit message.
            fragments (:obj:`bool`, optional): Indicates if pipeline contains fragments.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.Pipeline`.
        """
        return SeekableList([Pipeline(pipeline,
                                      builder=None,
                                      pipeline_definition=json.loads(pipeline['pipelineDefinition']),
                                      rules_definition=json.loads(pipeline['currentRules']['rulesDefinition']),
                                      control_hub=self)
                             for pipeline in self.api_client.import_pipelines(commit_message=commit_message,
                                                                              pipelines_file=archive,
                                                                              fragments=fragments).response.json()])

    def import_pipeline(self, pipeline, commit_message, name=None, data_collector_instance=None):
        """Import pipeline from json file.

        Args:
            pipeline (:obj:`dict`): A python dict representation of ControlHub Pipeline.
            commit_message (:obj:`str`): Commit message.
            name (:obj:`str`, optional): Name of the pipeline. If left out, pipeline name from JSON object will be
                                         used. Default ``None``.
            data_collector_instance (:py:class:`streamsets.sdk.sch_models.DataCollector`): If excluded, system sdc will
                                                                                           be used. Default ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Pipeline`.
        """
        if name is None: name = pipeline['pipelineConfig']['title']
        sdc_id = data_collector_instance.id if data_collector_instance is not None else DEFAULT_SYSTEM_SDC_ID
        pipeline['pipelineConfig']['info']['sdcId'] = sdc_id
        commit_pipeline_json = {'name': name,
                                'commitMessage': commit_message,
                                'pipelineDefinition': json.dumps(pipeline['pipelineConfig']),
                                'libraryDefinitions': json.dumps(pipeline['libraryDefinitions']),
                                'rulesDefinition': json.dumps(pipeline['pipelineRules']),
                                'sdcId': sdc_id}
        commit_pipeline_response = self.api_client.commit_pipeline(new_pipeline=False,
                                                                   import_pipeline=True,
                                                                   body=commit_pipeline_json).response.json()
        commit_id = commit_pipeline_response['commitId']
        return self.pipelines.get(commit_id=commit_id)

    def export_pipelines(self, pipelines, fragments=False, include_plain_text_credentials=False):
        """Export pipelines.

        Args:
            pipelines (:obj:`list`): A list of :py:class:`streamsets.sdk.sch_models.Pipeline` instances.
            fragments (:obj:`bool`): Indicates if exporting fragments is needed.
            include_plain_text_credentials (:obj:`bool`): Indicates if plain text credentials should be included.

        Returns:
            An instance of type :py:obj:`bytes` indicating the content of zip file with pipeline json files.
        """
        commit_ids = [pipeline.commit_id for pipeline in pipelines]
        return (self.api_client.export_pipelines(body=commit_ids,
                                                 fragments=fragments,
                                                 include_plain_text_credentials=include_plain_text_credentials)
                                                 .response.content)

    @property
    def jobs(self):
        """Jobs.

        Returns:
            An instance of :py:obj:`streamsets.sdk.sch_models.Jobs`.
        """
        return Jobs(self)

    @property
    def data_protector_enabled(self):
        """:obj:`bool`: Whether Data Protector is enabled for the current organization."""
        add_ons = self.api_client.get_available_add_ons().response.json()
        logger.debug('Add-ons: %s', add_ons)
        return all(app in add_ons['enabled'] for app in ['policy', 'sdp_classification'])

    @property
    def data_protector_version(self):
        """:obj:`str`: Returns the StreamSets Data Protector version string configured in the system data collector. If
        data protector is not enabled a None value is returned"""
        if self._data_protector_version is None:
            # The data protector version is determined by retriving the available stage definitions and then finding a
            #stage library for data protector, parsing its libraryLabel property.
            sdp_stage_lib = next(iter([stage for stage in self.system_data_collector.definitions['stages']
                                       if stage['library'] == ProtectionMethod.STAGE_LIBRARY]), None)
            self._data_protector_version = sdp_stage_lib['libraryLabel'].split(' ')[2] if sdp_stage_lib else None
        return self._data_protector_version


    @property
    def connection_tags(self):
        """Connection Tags.

        Returns:
            An instance of :py:obj:`streamsets.sdk.sch_models.ConnectionTags`.
        """
        return ConnectionTags(control_hub=self, organization=self.organization)


    @property
    def alerts(self):
        """Alerts.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.Alert`.
        """
        # The SCH API requires fetching active and acknowledged alerts separately. As such we make two calls for each
        # of the active/acknowledged endpoints, combine them and sort chronologically by 'triggeredOn'.
        active_alerts = self.api_client.get_all_alerts(alert_status='ACTIVE').response.json()
        acknowledged_alerts = self.api_client.get_all_alerts(alert_status='ACKNOWLEDGED').response.json()

        return SeekableList(Alert(alert, control_hub=self) for alert in sorted(active_alerts + acknowledged_alerts,
                                                                               key=lambda x: x['triggeredOn']))

    def add_job(self, job):
        """Add a job.

        Args:
            job (:py:class:`streamsets.sdk.sch_models.Job`): Job object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Job`.
        """
        new_job_json = {property_: value
                        for property_, value in job._data.items()
                        if property_ in self._job_api['definitions']['NewJobJson']['properties']}
        logger.info('Adding job %s ...', job.job_name)
        create_job_command = self.api_client.create_job(body=new_job_json)
        # Update :py:class:`streamsets.sdk.sch_models.Job` with updated Job metadata.
        job._data = create_job_command.response.json()

        if self.data_protector_enabled:
            policies = dict(jobId=job.job_id)
            if job.read_policy:
                policies['readPolicyId'] = job.read_policy._id
            else:
                read_protection_policies = self._get_protection_policies('Read')
                if len(read_protection_policies) == 1:
                    logger.warning('Read protection policy not set for job (%s). Setting to %s ...',
                                   job.job_name,
                                   read_protection_policies[0].name)
                    policies['readPolicyId'] = read_protection_policies[0]._id
                else:
                    raise Exception('Read policy not selected.')

            if job.write_policy:
                policies['writePolicyId'] = job.write_policy._id
            else:
                write_protection_policies = self._get_protection_policies('Write')
                if len(write_protection_policies) == 1:
                    logger.warning('Write protection policy not set for job (%s). Setting to %s ...',
                                   job.job_name,
                                   write_protection_policies[0].name)
                    policies['writePolicyId'] = write_protection_policies[0]._id
                else:
                    raise Exception('Write policy not selected.')
            self.api_client.update_job_policies(body=policies)
        return create_job_command

    def edit_job(self, job):
        """Edit a job.

        Args:
            job (:py:class:`streamsets.sdk.sch_models.Job`): Job object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Job`.
        """
        logger.warning('This method has been superseded by update_job and will be removed in a future release.')
        logger.info('Editing job %s with job id %s ...', job.job_name, job.job_id)
        return Job(self.api_client.update_job(job_id=job.job_id, job_json=job._data).response.json())

    def update_job(self, job):
        """Update a job.

        Args:
            job (:py:class:`streamsets.sdk.sch_models.Job`): Job object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Job`.
        """
        logger.info('Updating job %s with job id %s ...', job.job_name, job.job_id)
        return Job(self.api_client.update_job(job_id=job.job_id, job_json=job._data).response.json())

    def upgrade_job(self, *jobs):
        """Upgrade job(s) to latest pipeline version.

        Args:
            *jobs: One or more instances of :py:class:`streamsets.sdk.sch_models.Job`.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.Job`.
        """
        job_ids = [job.job_id for job in jobs]
        self.api_client.upgrade_jobs(job_ids)
        return SeekableList(self.jobs.get(id=job_id) for job_id in job_ids)

    def import_jobs(self, archive, pipeline=True, number_of_instances=False, labels=False, runtime_parameters=False,
                    **kwargs):
        # update_migrate_offsets is not configurable through UI and is supported through kwargs.
        """Import jobs from archived zip directory.

        Args:
            archive (:obj:`file`): file containing the jobs.
            pipeline (:obj:`boolean`, optional): Indicate if pipeline should be imported. Default: ``True``.
            number_of_instances (:obj:`boolean`, optional): Indicate if number of instances should be imported.
                                                            Default: ``False``.
            labels (:obj:`boolean`, optional): Indicate if labels should be imported. Default: ``False``.
            runtime_parameters (:obj:`boolean`, optional): Indicate if runtime parameters should be imported.
                                                           Default: ``False``.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.Job`.
        """
        return SeekableList([Job(job['minimalJobJson'], control_hub=self)
                             for job in self.api_client.import_jobs(jobs_file=archive,
                                                                    update_pipeline_refs=pipeline,
                                                                    update_num_instances=number_of_instances,
                                                                    update_labels=labels,
                                                                    update_runtime_parameters=runtime_parameters,
                                                                    **kwargs).response.json()])

    def export_jobs(self, jobs):
        """Export jobs to a compressed archive.

        Args:
            jobs (:obj:`list`): A list of :py:class:`streamsets.sdk.sch_models.Job` instances.

        Returns:
            An instance of type :py:obj:`bytes` indicating the content of zip file with job json files.
        """
        job_ids = [job.job_id for job in jobs]
        return self.api_client.export_jobs(body=job_ids).response.content

    def reset_origin(self, *jobs):
        # It is called reset_origin instead of reset_offset in the UI because that is how sdc calls it. If we change it
        # to reset_offset in sdc, it would affect a lot of people.
        """Reset all pipeline offsets for given jobs.

        Args:
            *jobs: One or more instances of :py:class:`streamsets.sdk.sch_models.Job`.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.Job`.
        """
        job_ids = [job.job_id for job in jobs]
        self.api_client.reset_jobs_offset(job_ids)
        return SeekableList(self.jobs.get(id=job_id) for job_id in job_ids)

    def upload_offset(self, job, offset_file=None, offset_json=None):
        """Upload offset for given job.

        Args:
            job (:py:class:`streamsets.sdk.sch_models.Job`): Job object.
            offset_file (:obj:`file`, optional): File containing the offsets. Default: ``None``. Exactly one of
                                                 ``offset_file``, ``offset_json`` should specified.
            offset_json (:obj:`dict`, optional): Contents of offset. Default: ``None``. Exactly one of ``offset_file``,
                                                 ``offset_json`` should specified.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.Job`.
        """
        # Comparing with None because, {} is also an accepted offset.
        if offset_file and offset_json is not None:
            raise ValueError("Cannot specify both the arguments offset_file and offset_json at the same time.")
        if not offset_file and offset_json is None:
            raise ValueError("Exactly one of the arguments offset_file and offset_json should be specified.")
        if offset_json is not None:
            job_json = self.api_client.upload_job_offset_as_json(job.job_id, offset_json).response.json()
        else:
            job_json = self.api_client.upload_job_offset(job.job_id, offset_file).response.json()
        return Job(job_json, self)

    def get_current_job_status(self, job):
        """Returns the current job status for given job id.

        Args:
            job (:py:class:`streamsets.sdk.sch_models.Job`): Job object.
        """
        logger.info('Fetching job status for job id %s ...', job.job_id)
        return self.api_client.get_current_job_status(job_id=job.job_id)

    def delete_job(self, *jobs):
        """Delete one or more jobs.

        Args:
            *jobs: One or more instances of :py:class:`streamsets.sdk.sch_models.Job`.
        """
        job_ids = [job.job_id for job in jobs]
        logger.info('Deleting job(s) %s ...', job_ids)
        if len(job_ids) == 1:
            try:
                api_version = 2 if '/v2/job/{jobId}' in self._job_api['paths'] else 1
            except:
                # Ignore any improper swagger setup and fall back to default version in case of any errors
                api_version = 1
            self.api_client.delete_job(job_ids[0], api_version=api_version)
        else:
            self.api_client.delete_jobs(job_ids)

    def start_job(self, *jobs, wait=True, **kwargs):
        """Start one or more jobs.

        Args:
            *jobs: One or more instances of :py:class:`streamsets.sdk.sch_models.Job`.
            wait (:obj:`bool`, optional): Wait for pipelines to reach RUNNING status before returning.
                Default: ``True``.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.StartJobsCommand`.
        """
        # Preserve compatibility with previous 'wait_for_data_collectors' argument
        wait_for_data_collectors = kwargs.get('wait_for_data_collectors')
        if wait_for_data_collectors is not None:
            warnings.warn('The wait_for_data_collectors argument to ControlHub.start_job will be removed in a '
                          'future release. Please use wait argument instead.',
                          DeprecationWarning)
            wait = wait_for_data_collectors

        job_names = [job.job_name for job in jobs]
        logger.info('Starting %s (%s) ...', 'jobs' if len(job_names) > 1 else 'job', ', '.join(job_names))

        job_ids = [job.job_id for job in jobs]
        start_jobs_command = self.api_client.start_jobs(job_ids)
        # The startJobs endpoint in SCH returns an OK with no other data in the body. As such, we add the list of
        # jobs passed to this method as an attribute to the StartJobsCommand returned by
        # :py:method:`streamsets.sdk.sch_api.ApiClient.start_jobs`.
        start_jobs_command.jobs = jobs

        if wait:
            start_jobs_command.wait_for_pipelines()
        return start_jobs_command

    def start_job_template(self, job_template, instance_name_suffix='COUNTER', parameter_name=None,
                           runtime_parameters=None, number_of_instances=1, wait_for_data_collectors=False):
        """Start Job instances from a Job Template.

        Args:
            job_template (:py:class:`streamsets.sdk.sch_models.Job`): A Job instance with the property job_template set
                                                                      to ``True``.
            instance_name_suffix (:obj:`str`, optional): Suffix to be used for Job names in
                                                         {'COUNTER', 'TIME_STAMP', 'PARAM_VALUE'}. Default: ``COUNTER``.
            parameter_name (:obj:`str`, optional): Specified when instance_name_suffix is 'PARAM_VALUE'.
                                                   Default: ``None``.
            runtime_parameters (:obj:`dict`) or (:obj:`list`): Runtime Parameters to be used in the jobs. If a dict is
                                                               specified, ``number_of_instances`` jobs will be started.
                                                               If a list is specified, ``number_of_instances`` is
                                                               ignored and job instances will be started using the
                                                               elements of the list as Runtime Parameters for each job.
                                                               If left out, Runtime Parameters from Job Template will be
                                                               used. Default: ``None``.
            number_of_instances (:obj:`int`, optional): Number of instances to be started using given parameters.
                                                        Default: ``1``.
            wait_for_data_collectors (:obj:`bool`, optional): Default: ``False``.

        Returns:
            A :py:class:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.Job` instances.
        """
        assert job_template.job_template, "Please specify a Job Template instance."
        if instance_name_suffix == 'PARAM_VALUE': assert parameter_name is not None, "Please specify a parameter name."

        start_job_template_json = {property: None
                                   for property in
                                   self._job_api['definitions']['JobTemplateCreationInfoJson']['properties']}

        if runtime_parameters is None: runtime_parameters = job_template.runtime_parameters._data
        if isinstance(runtime_parameters, dict):
            runtime_parameters = [runtime_parameters] * number_of_instances

        start_job_template_json.update({'namePostfixType': instance_name_suffix,
                                        'paramName': parameter_name,
                                        'runtimeParametersList': runtime_parameters})
        jobs_reponse = self.api_client.create_and_start_job_instances(job_template.job_id, start_job_template_json)

        jobs = SeekableList()
        for job_response in jobs_reponse.response.json():
            job = self.jobs.get(id=job_response['jobId'])
            self.api_client.wait_for_job_status(job_id=job.job_id, status='ACTIVE')
            if wait_for_data_collectors:
                def job_has_data_collector(job):
                    job.refresh()
                    job_data_collectors = job.data_collectors
                    logger.debug('Job Data Collectors: %s', job_data_collectors)
                    return len(job_data_collectors) > 0
                wait_for_condition(job_has_data_collector, [job], timeout=120)
            job.refresh()
            jobs.append(job)

        return jobs

    def stop_job(self, *jobs, force=False, timeout_sec=300):
        """Stop one or more jobs.

        Args:
            *jobs: One or more instances of :py:class:`streamsets.sdk.sch_models.Job`.
            force (:obj:`bool`, optional): Force job to stop. Default: ``False``.
            timeout_sec (:obj:`int`, optional): Timeout in secs. Default: ``300``.
        """
        jobs_ = {job.job_id: job for job in jobs}
        job_ids = list(jobs_.keys())
        logger.info('Stopping job(s) %s ...', job_ids)
        # At the end, we'll return the command from the job being stopped, so we hold onto it while we update
        # the underlying :py:class:`streamsets.sdk.sch_models.Job` instances.
        stop_jobs_command = self.api_client.force_stop_jobs(job_ids) if force else self.api_client.stop_jobs(job_ids)

        job_inactive_error = None
        for job_id in job_ids:
            try:
                self.api_client.wait_for_job_status(job_id=job_id, status='INACTIVE', timeout_sec=timeout_sec)
            except JobInactiveError as ex:
                job_inactive_error = ex
        updated_jobs = self.api_client.get_jobs(body=job_ids).response.json()
        for updated_job in updated_jobs:
            job_id = updated_job['id']
            jobs_[job_id]._data = updated_job
        if job_inactive_error:
            raise job_inactive_error
        return stop_jobs_command

    def get_protection_policy_builder(self):
        """Get a protection policy builder instance with which a protection policy can be created.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ProtectionPolicyBuilder`.
        """
        protection_policy = self.api_client.get_new_protection_policy().response.json()['response']['data']
        protection_policy.pop('messages', None)
        id_ = protection_policy['id']

        policy_procedure = self.api_client.get_new_policy_procedure(id_).response.json()['response']['data']
        policy_procedure.pop('messages', None)
        return ProtectionPolicyBuilder(self, protection_policy, policy_procedure)

    def get_protection_method_builder(self):
        """Get a protection method builder instance with which a protection method can be created.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ProtectionMethodBuilder`.
        """
        return ProtectionMethodBuilder(self.get_pipeline_builder())

    def get_classification_rule_builder(self):
        """Get a classification rule builder instance with which a classification rule can be created.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ClassificationRuleBuilder`.
        """
        classification_rule = self.api_client.get_new_classification_rule(
            self._classification_catalog_id
        ).response.json()['response']['data']
        # Remove 'messages' from the classification rule JSON.
        classification_rule.pop('messages', None)
        classifier = self.api_client.get_new_classification_classifier(
            self._classification_catalog_id
        ).response.json()['response']['data']
        # Remove 'messages' from the classifier JSON.
        classifier.pop('messages', None)
        return ClassificationRuleBuilder(classification_rule, classifier)

    @property
    def _classification_catalog_id(self):
        """Get the classification catalog id for the org.

        Returns:
            An instance of :obj:`str`:.
        """
        classification_catalog_list_response = self.api_client.get_classification_catalog_list().response.json()
        # We assume it's the first (and only) classification catalog id for the org
        return classification_catalog_list_response['response'][0]['data']['id']

    def add_protection_policy(self, protection_policy):
        """Add a protection policy.

        Args:
            protection_policy (:py:obj:`streamsets.sdk.sch_models.ProtectionPolicy`): Protection Policy object.
        """
        protection_policy._id = self.api_client.create_protection_policy(
            {'data': protection_policy._data}
        ).response.json()['response']['data']['id']
        for procedure in protection_policy.procedures:
            new_policy_procedure = self.api_client.get_new_policy_procedure(
                protection_policy._id
            ).response.json()['response']['data']
            procedure._id = new_policy_procedure['id']
            procedure._policy_id = protection_policy._id
            self.api_client.create_policy_procedure({'data': procedure._data})

    def set_default_write_protection_policy(self, protection_policy):
        """Set a default write protection policy.

        Args:
            protection_policy
            (:py:obj:`streamsets.sdk.sch_models.ProtectionPolicy`): Protection
            Policy object to be set as the default write policy.

        Returns:
            An updated instance of :py:obj:`streamsets.sdk.sch_models.ProtectionPolicy`.

        Raises:
            UnsupportedMethodError: Only supported on Control Hub version 3.14.0+.
        """
        if Version(self.version) < Version('3.14.0'):
            raise UnsupportedMethodError('Method not supported for Control Hub version below 3.14.0')

        policy_id = protection_policy._data['id']
        self.api_client.set_default_write_protection_policy(policy_id)
        # Once the policy is updated, the local copy needs to be refreshed.
        # The post call itself doesn't return the latest data, so need to do
        # another lookup.  This mimics the UI in its behavior.
        return self.protection_policies.get(_id=policy_id)

    def set_default_read_protection_policy(self, protection_policy):
        """Set a default read protection policy.

        Args:
            protection_policy
            (:py:obj:`streamsets.sdk.sch_models.ProtectionPolicy`): Protection
            Policy object to be set as the default read policy.

        Returns:
            An updated instance of :py:obj:`streamsets.sdk.sch_models.ProtectionPolicy`.

        Raises:
            UnsupportedMethodError: Only supported on Control Hub version 3.14.0+.
        """
        if Version(self.version) < Version('3.14.0'):
            raise UnsupportedMethodError('Method not supported for Control Hub version below 3.14.0')

        policy_id = protection_policy._data['id']
        self.api_client.set_default_read_protection_policy(policy_id)
        # Once the policy is updated, the local copy needs to be refreshed.
        # The post call itself doesn't return the latest data, so need to do
        # another lookup.  This mimics the UI in its behavior.
        return self.protection_policies.get(_id=policy_id)

    def export_protection_policies(self, protection_policies):
        """Export protection policies to a compressed archive.

        Args:
            protection_policies (:obj:`list`): A list of :py:class:`streamsets.sdk.sch_models.ProtectionPolicy`
            instances.

        Returns:
            An instance of type :py:obj:`bytes` indicating the content of zip file with protection policy json files.
        """
        policy_ids = [policy._id for policy in protection_policies]
        return self.api_client.export_protection_policies(policy_ids=policy_ids).response.content

    def import_protection_policies(self, policies_archive):
        """Import protection policies from a compressed archive.

        Args:
            policies_archive (:obj:`file`): file containing the protection policies.

        Returns:
            A py:class:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.ProtectionPolicy`.
        """
        policies = self.api_client.import_protection_policies(policies_archive).response.json()['response']
        return SeekableList([ProtectionPolicy(policy['data']) for policy in policies])

    @property
    def protection_policies(self):
        """Protection policies.

        Returns:
            An instance of :py:obj:`streamsets.sdk.sch_models.ProtectionPolicies`.
        """
        return ProtectionPolicies(self)

    def run_pipeline_preview(self, pipeline, batches=1, batch_size=10, skip_targets=True,
                             skip_lifecycle_events=True, timeout=120000, test_origin=False,
                             read_policy=None, write_policy=None, executor=None, **kwargs):
        """Run pipeline preview.

        Args:
            pipeline (:py:obj:`streamsets.sdk.sch_models.Pipeline`): Pipeline object.
            batches (:obj:`int`, optional): Number of batches. Default: ``1``.
            batch_size (:obj:`int`, optional): Batch size. Default: ``10``.
            skip_targets (:obj:`bool`, optional): Skip targets. Default: ``True``.
            skip_lifecycle_events (:obj:`bool`, optional): Skip life cycle events. Default: ``True``.
            timeout (:obj:`int`, optional): Timeout. Default: ``120000``.
            test_origin (:obj:`bool`, optional): Test origin. Default: ``False``.
            read_policy (:py:obj:`streamsets.sdk.sch_models.ProtectionPolicy`): Read Policy for preview.
                If not provided, uses default read policy if one available. Default: ``None``.
            write_policy (:py:obj:`streamsets.sdk.sch_models.ProtectionPolicy`): Write Policy for preview.
                If not provided, uses default write policy if one available. Default: ``None``.
            executor (:py:obj:`streamsets.sdk.sch_models.DataCollector`, optional): The Data Collector
                in which to preview the pipeline. If omitted, Control Hub's first executor SDC will be used.
                Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.PreviewCommand`.
        """
        # Note: We only support SDC executor for now
        # Note: system data collector cannot be used for pipeline preview
        if not executor and len(self.data_collectors) < 1:
            raise Exception('No executor found')
        else:
            if self.data_protector_enabled:
                executor_instance = (executor or self.data_collectors[0]).instance
                if not read_policy:
                    read_protection_policies = self._get_protection_policies('Read')
                    if len(read_protection_policies) == 1:
                        read_policy_id = read_protection_policies[0].id
                    else:
                        raise Exception('Read policy not selected.')
                else:
                    read_policy_id = read_policy.id

                if not write_policy:
                    write_protection_policies = self._get_protection_policies('Write')
                    if len(write_protection_policies) == 1:
                        write_policy_id = write_protection_policies[0].id
                    else:
                        raise Exception('Write policy not selected.')
                else:
                    write_policy_id = write_policy.id

                parameters = {
                    'pipelineCommitId': pipeline.commit_id,
                    'pipelineId': pipeline.pipeline_id,
                    'read.policy.id': read_policy_id,
                    'write.policy.id': write_policy_id,
                    'classification.catalogId': self._classification_catalog_id,
                }
                return executor_instance.run_dynamic_pipeline_preview(type='PROTECTION_POLICY',
                                                                      parameters=parameters,
                                                                      batches=batches,
                                                                      batch_size=batch_size,
                                                                      skip_targets=skip_targets,
                                                                      skip_lifecycle_events=skip_lifecycle_events,
                                                                      timeout=timeout,
                                                                      test_origin=test_origin)
            else:
                executor_instance, executor_pipeline = self._add_pipeline_to_executor_if_not_exists(pipeline)
                return executor_instance.run_pipeline_preview(pipeline=executor_pipeline,
                                                              batches=batches,
                                                              batch_size=batch_size,
                                                              skip_targets=skip_targets,
                                                              timeout=timeout,
                                                              test_origin=test_origin,
                                                              wait=kwargs.get('wait', True))

    def test_pipeline_run(self, pipeline, reset_origin=False, parameters=None):
        """Test run a pipeline.

        Args:
            pipeline (:py:obj:`streamsets.sdk.sch_models.Pipeline`): Pipeline object.
            reset_origin (:obj:`boolean`, optional): Default: ``False``.
            parameters (:obj:`dict`, optional): Pipeline parameters. Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.StartPipelineCommand`.
        """
        executor_instance, executor_pipeline = self._add_pipeline_to_executor_if_not_exists(pipeline=pipeline,
                                                                                            reset_origin=reset_origin,
                                                                                            parameters=parameters)
        # Update pipeline rules as seen at https://git.io/JURT4
        pipeline_rules_command = (executor_instance.api_client.get_pipeline_rules(pipeline_id=executor_pipeline.id))
        pipeline_rules = pipeline._rules_definition
        pipeline_rules['uuid'] = pipeline_rules_command.response.json()['uuid']
        update_rules_command = (executor_instance.api_client
                                    .update_pipeline_rules(pipeline_id=executor_pipeline.id,
                                                           pipeline=pipeline_rules))
        executor_pipeline = executor_instance.pipelines.get(id=executor_pipeline.id)
        start_pipeline_command = executor_instance.start_pipeline(executor_pipeline)
        start_pipeline_command.executor_pipeline = executor_pipeline
        start_pipeline_command.executor_instance = executor_instance
        return start_pipeline_command

    def _add_pipeline_to_executor_if_not_exists(self, pipeline, reset_origin=False, parameters=None):
        """Util function to add SCH pipeline to executor.

        Args:
            pipeline (:py:obj:`streamsets.sdk.sch_models.Pipeline`): Pipeline object.
            reset_origin (:obj:`boolean`, optional): Default: ``False``.
            parameters (:obj:`dict`, optional): Pipeline parameters. Default: ``None``.

        Returns:
            An instance of :obj:`tuple` of (:py:obj:`streamsets.sdk.DataCollector` or
                :py:obj:`streamsets.sdk.Transformer` and :py:obj:`streamsets.sdk.sdc_models.Pipeline`)
        """
        executor_type = getattr(pipeline, 'executor_type', 'COLLECTOR') or 'COLLECTOR'
        authoring_executor = (self.data_collectors.get(id=pipeline.sdc_id) if executor_type == 'COLLECTOR' else
                              self.transformers.get(id=pipeline.sdc_id))
        authoring_executor_instance = authoring_executor.instance
        executor_pipeline_id = 'testRun__{}__{}'.format(pipeline.pipeline_id.split(':')[0], self.organization)
        pipeline_status_command = (authoring_executor_instance.api_client
                                       .get_pipeline_status(pipeline_id=executor_pipeline_id,
                                                            only_if_exists=True))
        if not pipeline_status_command.response.text:
            create_pipeline_response = (authoring_executor_instance.api_client
                                            .create_pipeline(pipeline_title=executor_pipeline_id,
                                                             description="New Pipeline",
                                                             auto_generate_pipeline_id=False,
                                                             draft=False))
        elif reset_origin:
            reset_origin_command = authoring_executor_instance.api_client.reset_origin_offset(pipeline_id=executor_pipeline_id)
        pipeline_info = (authoring_executor_instance.api_client
                             .get_pipeline_configuration(pipeline_id=executor_pipeline_id,
                                                         get='info'))
        if parameters:
            pipeline.parameters = parameters
        executor_pipeline_json = pipeline._pipeline_definition
        executor_pipeline_json['uuid'] = pipeline_info['uuid']
        update_pipeline_response = (authoring_executor_instance.api_client
                                        .update_pipeline(pipeline_id=executor_pipeline_id,
                                                         pipeline=executor_pipeline_json))
        return authoring_executor_instance, authoring_executor_instance.pipelines.get(id=executor_pipeline_id)

    def stop_test_pipeline_run(self, start_pipeline_command):
        """Stop the test run of pipeline.

        Args:
            start_pipeline_command (:py:class:`streamsets.sdk.sdc_api.StartPipelineCommand`)

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.StopPipelineCommand`.
        """
        return start_pipeline_command.executor_instance.stop_pipeline(start_pipeline_command.executor_pipeline)

    def preview_classification_rule(self, classification_rule, parameter_data, data_collector=None):
        """Dynamic preview of a classification rule.

        Args:
            classification_rule (:py:obj:`streamsets.sdk.sch_models.ClassificationRule`): Classification Rule object.
            parameter_data (:obj:`dict`): A python dict representation of raw JSON parameters required for preview.
            data_collector (:py:obj:`streamsets.sdk.sch_models.DataCollector`, optional): The Data Collector
                in which to preview the pipeline. If omitted, Control Hub's first executor SDC will be used.
                Default: ``None``.

        Returns:
            An instance of :py:class:`streamsets.sdk.sdc_api.PreviewCommand`.
        """
        if self.data_protector_enabled:
            # Note: system data collector cannot be used for dynamic preview
            if not data_collector and len(self.data_collectors) < 1:
                raise Exception('No executor DataCollector found')
            else:
                data_collector_instance = (data_collector or self.data_collectors[0]).instance
                parameters = {
                    'classification.catalogId': classification_rule.catalog_uuid,
                    'rawJson': json.dumps(parameter_data)
                }
                return data_collector_instance.run_dynamic_pipeline_preview(type='CLASSIFICATION_CATALOG',
                                                                            parameters=parameters)

    def add_classification_rule(self, classification_rule, commit=False):
        """Add a classification rule.

        Args:
            classification_rule (:py:obj:`streamsets.sdk.sch_models.ClassificationRule`): Classification Rule object.
            commit (:obj:`bool`, optional): Whether to commit the rule after adding it. Default: ``False``.
        """
        self.api_client.create_classification_rule({'data': classification_rule._data})
        default_classifier_ids = [classifier['data']['id']
                                  for classifier
                                  in self.api_client.get_classification_classifier_list(
                                                                                        classification_rule._data['id']
                                                                                        ).response.json()['response']]
        for classifier_id in default_classifier_ids:
            self.api_client.delete_classification_classifier(classifier_id)

        for classifier in classification_rule.classifiers:
            self.api_client.create_classification_classifier({'data': classifier._data})

        if commit:
            self.api_client.commit_classification_rules(self._classification_catalog_id)

    def get_scheduled_task_builder(self):
        """Get a scheduled task builder instance with which a scheduled task can be created.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ScheduledTaskBuilder`.
        """
        job_selection_types = self.api_client.get_job_selection_types(api_version=2).response.json()['response']['data']
        return ScheduledTaskBuilder(job_selection_types, self)

    def publish_scheduled_task(self, task):
        """Send the scheduled task to Control Hub. DEPRECATED

        Args:
            task (:py:class:`streamsets.sdk.sch_models.ScheduledTask`): Scheduled task object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        warnings.warn('The publish_scheduled_task method has been deprecated and will be removed in a future release. '
                      'Please use the add_scheduled_task method instead.', DeprecationWarning)
        return self.add_scheduled_task(task)

    def add_scheduled_task(self, task):
        """Add the scheduled task to Control Hub.

        Args:
            task (:py:class:`streamsets.sdk.sch_models.ScheduledTask`): Scheduled task object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        create_task_command = self.api_client.create_scheduled_task(data={'data': task._data}, api_version=2)
        task._data = create_task_command.response.json()['response']['data']
        return create_task_command

    def update_scheduled_task(self, task):
        """Update an existing scheduled task in Control Hub.

        Args:
            task (:py:class:`streamsets.sdk.sch_models.ScheduleTask`): Scheduled task object.

        Returns:
            An instance of py:class:`streamsets.sdk.sch_api.Command`.
        """
        update_task_command = self.api_client.update_scheduled_task(data={'data': task._data},
                                                                    id=task.id,
                                                                    api_version=2)
        task._data = update_task_command.response.json()['response']['data']
        return update_task_command

    @property
    def scheduled_tasks(self):
        """Scheduled Tasks.

        Returns:
            An instance of :py:obj:`streamsets.sdk.sch_models.ScheduledTasks`.
        """
        return ScheduledTasks(self)

    @property
    def subscriptions(self):
        """Event Subscriptions.

        Returns:
            An instance of :py:obj:`streamsets.sdk.sch_models.Subscriptions`.
        """
        return Subscriptions(self)

    def get_subscription_builder(self):
        """Get Event Subscription Builder.

        Returns:
            An instance of :py:obj:`streamsets.sdk.sch_models.SubscriptionBuilder`.
        """
        subscription = {property: None
                        for property in self._notification_api['definitions']['EventSubscriptionJson']['properties']}
        subscription.update(dict(enabled=True, deleted=False, events=[]))
        return SubscriptionBuilder(subscription=subscription,
                                   control_hub=self)

    def add_subscription(self, subscription):
        """Add Subscription to Control Hub.

        Args:
            subscription (:py:obj:`streamsets.sdk.sch_models.Subscription`): A Subscription instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        event_types = self._en_translations['notifications']['subscriptions']['events']
        subscription._data['events'] = [{'eventType': reversed_dict(event_types)[event.event_type],
                                         'filter': event.filter} for event in subscription.events]
        action_config = subscription._data['externalActions'][0]['config']
        subscription._data['externalActions'][0]['config'] = (json.dumps(action_config)
                                                              if isinstance(action_config, dict) else action_config)
        create_subscription_command = self.api_client.create_event_subscription(body=subscription._data)
        subscription._data = create_subscription_command.response.json()
        return create_subscription_command

    def update_subscription(self, subscription):
        """Update an existing Subscription.

        Args:
            subscription (:py:obj:`streamsets.sdk.sch_models.Subscription`): A Subscription instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        event_types = self._en_translations['notifications']['subscriptions']['events']
        subscription._data['events'] = [{'eventType': reversed_dict(event_types)[event.event_type],
                                         'filter': event.filter} for event in subscription.events]
        action_config = subscription._data['externalActions'][0]['config']
        subscription._data['externalActions'][0]['config'] = (json.dumps(action_config)
                                                              if isinstance(action_config, dict) else action_config)
        update_subscription_command = self.api_client.update_event_subscription(body=subscription._data)
        subscription._data = update_subscription_command.response.json()
        return update_subscription_command

    def delete_subscription(self, subscription):
        """Delete an exisiting Subscription.

        Args:
            subscription (:py:obj:`streamsets.sdk.sch_models.Subscription`): A Subscription instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        return self.api_client.delete_event_subscription(subscription_id=subscription.id)

    def acknowledge_event_subscription_error(self, subscription):
        """Acknowledge an error on given Event Subscription.

        Args:
            subscription (:py:obj:`streamsets.sdk.sch_models.Subscription`): A Subscription instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        cmd = self.api_client.event_subscription_acknowledge_error(subscription.id)
        subscription._data = cmd.response.json()
        return cmd

    @property
    def subscription_audits(self):
        """Subscription audits.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.SubscriptionAudit`.
        """
        cmd = self.api_client.get_all_subscription_audits()
        return SeekableList([SubscriptionAudit(audit) for audit in cmd.response.json()])

    def acknowledge_job_error(self, *jobs):
        """Acknowledge errors for one or more jobs.

        Args:
            *jobs: One or more instances of :py:class:`streamsets.sdk.sch_models.Job`.
        """
        job_ids = [job.job_id for job in jobs]
        logger.info('Acknowledging errors for job(s) %s ...', job_ids)
        self.api_client.jobs_acknowledge_errors(job_ids)

    def sync_job(self, *jobs):
        """Sync one or more jobs.

        Args:
            *jobs: One or more instances of :py:class:`streamsets.sdk.sch_models.Job`.
        """
        job_ids = [job.job_id for job in jobs]
        logger.info('Synchronizing job(s) %s ...', job_ids)
        self.api_client.sync_jobs(job_ids)

    def balance_job(self, *jobs):
        """Balance one or more jobs.

        Args:
            *jobs: One or more instances of :py:class:`streamsets.sdk.sch_models.Job`.
        """
        job_ids = [job.job_id for job in jobs]
        logger.info('Balancing job(s) %s ...', job_ids)
        self.api_client.balance_jobs(job_ids)

    def get_topology_builder(self):
        """Get a topology builder instance with which a topology can be created.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.TopologyBuilder`.
        """
        topology_json = {}
        # Update the topology_json with the API definitions from Swagger.
        topology_json.update({property: None
                              for property in self._topology_api['definitions']['TopologyJson']['properties']})
        topology_json['organization'] = self.organization
        topology_json['topologyDefinition'] = {}
        topology_json['topologyDefinition']['schemaVersion'] = '1'
        topology_json['topologyDefinition']['topologyNodes'] = []
        topology_json['topologyDefinition']['stageIcons'] = {}
        topology_json['topologyDefinition']['valid'] = True

        return TopologyBuilder(topology=topology_json, control_hub=self)

    def get_data_sla_builder(self):
        """Get a Data SLA builder instance with which a Data SLA can be created.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.DataSlaBuilder`.
        """
        data_sla = {property: None
                    for property in self._sla_api['definitions']['DataSlaJson']['properties']}
        data_sla['organization'] = self.organization

        return DataSlaBuilder(data_sla, self)

    @property
    def topologies(self):
        """Topologies.

        Returns:
            An instance of :py:obj:`streamsets.sdk.sch_models.Topologies`.
        """
        return Topologies(self)

    def import_topologies(self, archive, import_number_of_instances=False, import_labels=False,
                          import_runtime_parameters=False, **kwargs):
        # update_migrate_offsets is not configurable through UI and is supported through kwargs.
        """Import topologies from archived zip directory.

        Args:
            archive (:obj:`file`): file containing the topologies.
            import_number_of_instances (:obj:`boolean`, optional): Indicate if number of instances should be imported.
                                                            Default: ``False``.
            import_labels (:obj:`boolean`, optional): Indicate if labels should be imported. Default: ``False``.
            import_runtime_parameters (:obj:`boolean`, optional): Indicate if runtime parameters should be imported.
                                                           Default: ``False``.

        Returns:
            A :py:obj:`streamsets.sdk.utils.SeekableList` of :py:class:`streamsets.sdk.sch_models.Topology`.
        """
        return SeekableList([Topology(topology, control_hub=self)
                             for topology in self.api_client
                                             .import_topologies(topologies_file=archive,
                                                                update_num_instances=import_number_of_instances,
                                                                update_labels=import_labels,
                                                                update_runtime_parameters=import_runtime_parameters,
                                                                **kwargs).response.json()])

    def export_topologies(self, topologies):
        """Export topologies.

        Args:
            topologies (:obj:`list`): A list of :py:class:`streamsets.sdk.sch_models.Topology` instances.

        Returns:
            An instance of type :py:obj:`bytes` indicating the content of zip file with pipeline json files.
        """
        commit_ids = [topology.commit_id for topology in topologies]
        return self.api_client.export_topologies(body=commit_ids).response.content

    def delete_topology(self, topology, only_selected_version=False):
        """Delete a topology.

        Args:
            topology (:py:class:`streamsets.sdk.sch_models.Topology`): Topology object.
            only_selected_version (:obj:`boolean`): Delete only current commit.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        if only_selected_version:
            logger.info('Deleting topology version %s for topology %s ...', topology.commit_id, topology.topology_name)
            return self.api_client.delete_topology_versions(commits_json=[topology.commit_id])
        logger.info('Deleting topology %s with topology id %s ...', topology.topology_name, topology.topology_id)
        return self.api_client.delete_topologies(topologies_json=[topology.topology_id])

    def publish_topology(self, topology, commit_message=None):
        """Publish a topology.

        Args:
            topology (:py:class:`streamsets.sdk.sch_models.Topology`): Topology object to publish.
            commit_message (:obj:`str`, optional): Commit message to supply with the Topology. Default: ``None``

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        # If the topology already has a commit_id but isn't in draft mode, we assume it exists and create a new draft
        # in order to update the existing instance before publishing
        if topology.commit_id and not topology.draft:
            try:
                draft_topology = self.api_client.create_topology_draft(commit_id=topology.commit_id).response.json()
            except requests.exceptions.HTTPError:
                raise
            draft_topology.update({'topologyDefinition': topology._data['topologyDefinition']})
            created_topology = self.api_client.update_topology(commit_id=draft_topology['commitId'],
                                                               topology_json=draft_topology).response.json()
            response = self.api_client.publish_topology(commit_id=created_topology['commitId'],
                                                        commit_message=commit_message)
        # This is a brand-new topology being created for the first time
        elif not topology.commit_id:
            created_topology = self.api_client.create_topology(topology_json=topology._data).response.json()
            response = self.api_client.publish_topology(commit_id=created_topology['commitId'],
                                                        commit_message=commit_message)
        # This is an existing topology that's already in draft mode
        else:
            response = self.api_client.publish_topology(commit_id=topology.commit_id,
                                                        commit_message=commit_message)
        # Refresh the in-memory representation of the topology
        topology.commit_id = response.response.json()['commitId']
        topology._refresh()

        return response

    @property
    def report_definitions(self):
        """Report Definitions.

        Returns:
            An instance of :py:obj:`streamsets.sdk.sch_models.ReportDefinitions`.
        """
        return ReportDefinitions(self)

    def get_report_definition_builder(self):
        """Get a Report Definition Builder instance with which a Report Definition can be created.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ReportDefinitionBuilder`.
        """
        report_definition = {property: None
                             for property in self._report_api['definitions']['ReportDefinitionJson']['properties']}
        return ReportDefinitionBuilder(report_definition, self)

    def add_report_definition(self, report_definition):
        """Add Report Definition to Control Hub.

        Args:
            report_definition (:py:class:`streamsets.sdk.sch_models.ReportDefinition`): Report Definition instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        create_report_definition_command = self.api_client.create_new_report_definition(report_definition._data)
        report_definition._data = create_report_definition_command.response.json()
        return create_report_definition_command

    def update_report_definition(self, report_definition):
        """Update an existing Report Definition.

        Args:
            report_definition (:py:class:`streamsets.sdk.sch_models.ReportDefinition`): Report Definition instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        update_report_definition_command = self.api_client.update_report_definition(report_definition.id,
                                                                                    report_definition._data)
        report_definition._data = update_report_definition_command.response.json()
        return update_report_definition_command

    def delete_report_definition(self, report_definition):
        """Delete an existing Report Definition.

        Args:
            report_definition (:py:class:`streamsets.sdk.sch_models.ReportDefinition`): Report Definition instance.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        return self.api_client.delete_report_definition(report_definition.id)

    def get_connection_builder(self):
        """Get a connection builder instance with which a connection can be created.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ConnectionBuilder`.
        """
        # Update the ConnectionJson with the API definitions from Swagger.
        connection = {property: None
                      for property in self._connection_api['definitions']['ConnectionJson']['properties']}
        connection['organization'] = self.organization

        return ConnectionBuilder(connection=connection, control_hub=self)

    def add_connection(self, connection):
        """Add a connection.

        Args:
            connection (:py:class:`streamsets.sdk.sch_models.Connection`): Connection object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        logger.info('Adding a connection %s ...', connection)
        # Update _data with any changes made to the connection definition
        connection._data.update({'connectionDefinition': json.dumps(connection._connection_definition._data)})
        create_connection_command = self.api_client.create_connection(connection._data)
        # Update :py:class:`streamsets.sdk.sch_models.Connection` with updated Connection metadata.
        connection._data = create_connection_command.response.json()
        return create_connection_command

    @property
    def connections(self):
        """Connections.

        Returns:
            An instance of :py:obj:`streamsets.sdk.sch_models.Connections`.
        """
        return Connections(self, self.organization)

    def update_connection(self, connection):
        """Update a connection.

        Args:
            connection (:py:class:`streamsets.sdk.sch_models.Connection`): Connection object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_api.Command`.
        """
        logger.info('Updating a connection %s ...', connection)
        # Update _data with any changes made to the connection definition
        connection._data.update({'connectionDefinition': json.dumps(connection._connection_definition._data)})
        update_connection_command = self.api_client.update_connection(connection_id=connection.id,
                                                                      body=connection._data)
        connection._data = update_connection_command.response.json()
        return update_connection_command

    def delete_connection(self, *connections):
        """Delete connections.

        Args:
            *connections: One or more instances of :py:class:`streamsets.sdk.sch_models.Connection`.
        """
        for connection in connections:
            logger.info('Deleting connection %s ...', connection)
            self.api_client.delete_connection(connection_id=connection.id)

    def verify_connection(self, connection):
        """Verify connection.

        Args:
            connection (:py:class:`streamsets.sdk.sch_models.Connection`): Connection object.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.ConnectionVerificationResult`.
        """
        logger.info('Running dynamic preview for %s type ...', type)
        library_definition = json.loads(connection.library_definition)
        # As configured by UI at https://git.io/JUkz8
        parameters = {'connection': {'configuration': connection.connection_definition.configuration,
                                     'connectionId': connection.id,
                                     'type': connection.connection_type,
                                     'verifierDefinition': library_definition['verifierDefinitions'][0],
                                     'version': library_definition['version']}}
        dynamic_preview_request = {'dynamicPreviewRequestJson': {'batches': 2,
                                                                 'batchSize': 100,
                                                                 'parameters': parameters,
                                                                 'skipLifecycleEvents': True,
                                                                 'skipTargets': False,
                                                                 'testOrigin': False,
                                                                 'timeout': 120*1000, # 120 seconds
                                                                 'type': 'CONNECTION_VERIFIER'},
                                   'stageOutputsToOverrideJson': []}
        sdc = self.data_collectors.get(id=connection.sdc_id).instance
        validate_command = sdc.api_client.run_dynamic_pipeline_preview_for_connection(dynamic_preview_request)
        return ConnectionVerificationResult(validate_command.wait_for_validate().response.json())

    def _get_protection_policies(self, policy_type):
        """An internal function that returns a list of protection policies

        Args:
            policy_type (str): The type of policies to return (Read, Write)

        Returns:
            A list of :py:class:`streamsets.sdk.utils.SeekableList`
        """
        if Version(self.version) >= Version('3.14.0'):
            return (self.protection_policies.get_all(default_setting=policy_type) +
                    self.protection_policies.get_all(default_setting='Both'))
        else:
            return self.protection_policies.get_all(enactment=policy_type)

    def get_admin_tool(self, base_url, username, password):
        """Get SCH admin tool.

        Returns:
            An instance of :py:class:`streamsets.sdk.sch_models.AdminTool`.
        """
        return AdminTool(base_url, username, password)

    def wait_for_job_status(self, job, status, timeout_sec=DEFAULT_WAIT_FOR_STATUS_TIMEOUT):
        """Block until a job reaches the desired status.

        Args:
            job (:py:class:`streamsets.sdk.sch_models.Job`): The job instance.
            status (:py:obj:`str`): The desired status to wait for.
            timeout_sec (:obj:`int`, optional): Timeout to wait for ``job`` to reach ``status``, in seconds.
                Default: :py:const:`streamsets.sdk.sch.DEFAULT_WAIT_FOR_STATUS_TIMEOUT`.

        Raises:
            TimeoutError: If ``timeout_sec`` passes without ``job`` reaching ``status``.
        """
        def condition():
            job.refresh()
            logger.debug('Job has current status %s ...', job.status)
            return job.status == status

        def failure(timeout_sec):
            raise TimeoutError('Timed out after `{}` seconds waiting for Job `{}` '.format(timeout_sec, job.job_name),
                               'to reach status {}'.format(status))

        wait_for_condition(condition=condition, timeout=timeout_sec, failure=failure)

    def wait_for_job_pipeline_metric(self, job, metric, value,
                                     timeout_sec=DEFAULT_WAIT_FOR_METRIC_TIMEOUT):
        """Block until a job's pipeline metric reaches the desired value.
        Note: Currently this method works only for job with DataCollector executor.

        Args:
            job (:py:class:`streamsets.sdk.sch_models.Job`): The job instance.
            metric (:py:obj:`str`): The desired metric (e.g. ``'output_record_count'`` or ``'data_batch_count'``).
            value (:obj:`int`): The desired value to wait for.
            timeout_sec (:obj:`int`, optional): Timeout to wait for ``metric`` to reach ``value``, in seconds.
                Default: :py:const:`streamsets.sdk.sch.DEFAULT_WAIT_FOR_METRIC_TIMEOUT`.

        Raises:
            TimeoutError: If ``timeout_sec`` passes without ``metric`` reaching ``value``.
        """
        logger.info('Waiting for job metric %s to reach at value %s ...', metric, value)

        def condition():
            # There are some instances where job.executor_type is not filled as it is assumed SDC_EXECUTOR_TYPE
            executor_type = job.executor_type if job.executor_type else SDC_EXECUTOR_TYPE
            if executor_type != SDC_EXECUTOR_TYPE:
                raise Exception('This method is not yet supported for job with executor type other than COLLECTOR')
            job_executor = job.data_collectors[0]
            metrics = job_executor.instance.get_pipeline_metrics(job_executor.pipeline)

            if not metrics:
                raise ValueError('Operation only supported for running pipelines')
            current_value = getattr(metrics.pipeline, metric)
            logger.debug('Job metric %s has current value %s ...', metric, current_value)
            return current_value >= value

        def failure(timeout):
            raise Exception('Metric {} did not reach value {} after {} s'.format(metric, value, timeout))

        wait_for_condition(condition=condition, timeout=timeout_sec, failure=failure)

    def wait_for_job_metrics_record_count(self, job, count, timeout_sec=DEFAULT_WAIT_FOR_METRIC_TIMEOUT):
        """Block until a job's metrics reaches the desired count.

        Args:
            job (:py:class:`streamsets.sdk.sch_models.Job`): The job instance.
            count (:obj:`int`): The desired value to wait for.
            timeout_sec (:obj:`int`, optional): Timeout to wait for ``metric`` to reach ``count``, in seconds.
                Default: :py:const:`streamsets.sdk.sch.DEFAULT_WAIT_FOR_METRIC_TIMEOUT`.

        Raises:
            TimeoutError: If ``timeout_sec`` passes without ``metric`` reaching ``value``.
        """
        def condition():
            job.refresh()
            current_value = job.metrics(metric_type='RECORD_COUNT', include_error_count=True).output_count['PIPELINE']
            logger.debug('Waiting for job metric `%s` status to become `%s`', current_value, count)
            return current_value == count

        def failure(timeout_sec):
            raise Exception('Timed out after `{}` seconds waiting for Job metric `{}` to become {}'.format(
                timeout_sec, job.metrics(metric_type='RECORD_COUNT', include_error_count=True).output_count['PIPELINE'],
                count))

        wait_for_condition(condition=condition, timeout=timeout_sec, failure=failure)
