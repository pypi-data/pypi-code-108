# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

# coding=utf-8
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
from retry import retry
import time
from ibm_ai_openscale_cli.utility_classes.utils import jsonFileToDict
from ibm_watson_machine_learning import APIClient
from ibm_watson_machine_learning.wml_client_error import ApiRequestFailure
from ibm_ai_openscale_cli.utility_classes.constants import WML_CHALLENGER_SOFTWARE_SPEC_MAPPING

logger = FastpathLogger(__name__)


class WatsonMachineLearningEngine:

    def __init__(self, credentials, openscale_client, cos_credentials=None, is_v4=False, is_mrm=False, is_icp=False):
        start = time.time()
        self._credentials = credentials
        self._client = APIClient(dict(credentials))
        self._openscale_client = openscale_client
        self._is_v4 = is_v4
        self._is_icp = is_icp
        self.space_id = None
        self._cos_credentials = cos_credentials
        if is_v4:
            self._set_or_create_space_id(openscale_client.get_datamart_id(), is_mrm)
        elapsed = time.time() - start
        self._openscale_client.timer('WML connect to WatsonMachineLearningAPIClient',elapsed)
        logger.log_info('Using Watson Machine Learning Python Client version: {}'.format(self._client.version))

    def get_native_client(self):
        return self._client

    def set_model(self, model):
        self._model_metadata = model.metadata

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_create_space(self, space_name):
        logger.log_debug('Creating space {} ...'.format(space_name))
        start = time.time()
        space_props = None
        if not self._is_icp:
            space_props = {
                    self._client.spaces.ConfigurationMetaNames.NAME: space_name,
                    "storage": {
                        "type": "bmcos_object_storage",
                        "resource_crn": self._cos_credentials['resource_instance_id']
                    },
                    "compute": {
                        "name": self._credentials['instance_name'],
                        "crn": self._credentials['instance_crn'],
                        "type": "machine_learning"
                    }
                }
        else:
            space_props = {
                self._client.spaces.ConfigurationMetaNames.NAME: space_name
            }
        space_details = self._client.spaces.store(meta_props=space_props)
        logger.log_info('Waiting 15 seconds to complete space creation ...')
        time.sleep(15)
        space_id = space_details['metadata']['id']

        for i in range(10):
            details = self._client.spaces.get_details(space_id)

            if 'status' in 'entity':
                if 'state' in 'status':
                    state = details["entity"]["status"]["state"]
                    _msg = "Space creation status = {}".format(state)
                    if state == "active":
                        logger.log_info(_msg)
                    break
                    if state == "error":
                        logger.log_info(_msg)
                        raise Exception("Space creation failed.")
                    else:
                        _msg = _msg + ', rechecking in 5 seconds ...'
                        logger.log_info(_msg)
                        time.sleep(5)
        elapsed = time.time() - start
        self._openscale_client.timer('WML create space completed', elapsed)
        logger.log_debug('Succesfully created space {} (id: {})'.format(space_name, space_id))
        return space_id

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_set_space(self, space_id, space_name):
        start = time.time()
        rc = self._client.set.default_space(space_id)
        elapsed = time.time() - start
        if not rc == 'SUCCESS':
            error_msg = 'ERROR: WML set.default_space failed for space {} (id: {}) {}'.format(space_name, space_id, rc)
            logger.log_error(error_msg)
            raise Exception(error_msg)
        self.space_id = space_id
        logger.log_info('Succesfully set space to {} (id: {})'.format(space_name, space_id))
        self._openscale_client.timer('WML set space completed', elapsed)

    def _set_or_create_space_id(self, data_mart_id, is_mrm=False):
        space_name = 'openscale-express-path-'
        if is_mrm:
            space_name += 'preprod-'
        space_name += data_mart_id
        logger.log_info('Checking for existing space "{}" ...'.format(space_name))
        
        try:
            spaces = self._client.spaces.get_details()
        except ApiRequestFailure as api_req_fail:
            if self._is_icp and api_req_fail.error_msg is not None and "404" in api_req_fail.error_msg:
                raise Exception("There was an error getting details of space. The WML service might not have been installed. Please follow instructions to install WML service and OpenScale in the correct order.")
            else:
                raise api_req_fail
        
        space_id = None
        for space in spaces['resources']:
            if space_name == space['entity']['name']:
                space_id = space['metadata']['id']
                break
        if not space_id:
            space_id = self._reliable_create_space(space_name=space_name)
        self._reliable_set_space(space_id, space_name)

    def _create_pipeline(self, model_name, pipeline_metadata_file):
        logger.log_info('Creating pipeline for model {} ...'.format(self._model_metadata['model_name']))
        pipeline_metadata = jsonFileToDict(pipeline_metadata_file)
        pipeline_props = {
            self._client.repository.DefinitionMetaNames.AUTHOR_NAME: pipeline_metadata['author']['name'],
            self._client.repository.DefinitionMetaNames.NAME: pipeline_metadata['name'],
            self._client.repository.DefinitionMetaNames.FRAMEWORK_NAME: pipeline_metadata['framework']['name'],
            self._client.repository.DefinitionMetaNames.FRAMEWORK_VERSION: pipeline_metadata['framework']['version'],
            self._client.repository.DefinitionMetaNames.RUNTIME_NAME: pipeline_metadata['framework']['runtimes'][0]['name'],
            self._client.repository.DefinitionMetaNames.RUNTIME_VERSION: pipeline_metadata['framework']['runtimes'][0]['version'],
            self._client.repository.DefinitionMetaNames.DESCRIPTION: pipeline_metadata['description'],
            self._client.repository.DefinitionMetaNames.TRAINING_DATA_REFERENCES: pipeline_metadata['training_data_reference']
        }
        start = time.time()
        self._client.repository.store_definition(self._model_metadata['pipeline_file'], meta_props=pipeline_props)
        elapsed = time.time() - start
        self._openscale_client.timer('WML repository.store_definition(pipeline)',elapsed)
        logger.log_info('Pipeline created successfully')

    def _delete_models(self, model_name):
        models = self._client.repository.get_model_details()
        functions = self._client.repository.get_function_details()
        found_model = False
        for model in (models['resources'] + functions['resources']):
            if self._is_v4:
                model_guid = model['metadata']['id']
                artifact_name = model['metadata']['name']
            else:
                model_guid = model['metadata']['guid']
                artifact_name = model['entity']['name']
            if model_name == artifact_name:
                try:
                    found_model = True
                    # delete the model's deployments (if any) before the model
                    deployments = self._client.deployments.get_details()
                    for deployment in deployments['resources']:
                        if self._is_v4:
                            deployment_guid = deployment['metadata']['id']
                            deployment_name = deployment['metadata']['name']
                        else:
                            deployment_guid = deployment['metadata']['guid']
                            deployment_name = deployment['entity']['name']
                        if self._is_v4:
                            deployment_asset_id = deployment["entity"]["asset"]["id"]
                        else:
                            deployment_asset_id = deployment['entity']['deployable_asset']['guid']
                        if deployment_asset_id == model_guid:
                            logger.log_info('Deleting deployment {} for model {} ...'.format(deployment_name, model_name))
                            if not deployment_name.startswith('WOS-INTERNAL'):
                                self._reliable_delete_deployment(deployment_guid)
                                logger.log_info('Deployment deleted successfully'.format())

                    # delete the model
                    logger.log_info('Deleting model {} ...'.format(model_name))
                    self._reliable_delete_model(model_guid)
                    logger.log_info('Model deleted successfully')
                except Exception as e:
                    logger.log_warning('Error deleting WML deployment "{}": {}'.format(model_guid, str(e)))
        if not found_model:
            logger.log_info('No existing model found with name: {}'.format(model_name))

    @retry(tries=2, delay=2, backoff=2)
    def _reliable_delete_model(self, model_guid):
        all_models = self._client.repository.get_model_details()
        all_functions = self._client.repository.get_function_details()
        for model in (all_models['resources'] + all_functions['resources']):
            if self._is_v4:
                artifact_model_id = model['metadata']['id']
            else:
                artifact_model_id = model['metadata']['guid']
            if model_guid == artifact_model_id:
                start = time.time()
                rc = self._client.repository.delete(model_guid)
                if not rc == 'SUCCESS':
                    error_msg = 'ERROR: WML repository.delete(model) delete failed (id: {}) {}'.format(model_guid, rc)
                    logger.log_error(error_msg)
                    raise Exception(error_msg)
                elapsed = time.time() - start
                self._openscale_client.timer('WML repository.delete(model)',elapsed)
                return
        logger.log_debug('Model {} not found, nothing to delete'.format(model_guid))

    def _create_model(self, model_name, model_metadata_file):
        logger.log_info('Creating new model {} ...'.format(model_name))
        metadata = jsonFileToDict(model_metadata_file)
        model_props = {
            self._client.repository.ModelMetaNames.NAME: model_name
        }
        if self._is_v4:
            fw = metadata['framework']
            software_spec_uid = None
            if fw["name"] == "scikit-learn":
                runtime_id = WML_CHALLENGER_SOFTWARE_SPEC_MAPPING[self._openscale_client._args.environment]
                software_spec_uid = self._client.software_specifications.get_uid_by_name(runtime_id)
            else:
                fw_runtime_uid = '{}-{}_{}'.format(fw['runtimes'][0]['name'], fw['name'], fw['runtimes'][0]['version'])
                software_spec_uid = self._client.software_specifications.get_uid_by_name(fw_runtime_uid)

            model_props[self._client.repository.ModelMetaNames.SOFTWARE_SPEC_UID] = software_spec_uid
            fw_type = '{}_{}'.format(fw['name'], fw['version'])
            model_props[self._client.repository.ModelMetaNames.TYPE] = fw_type
            # if 'output_data_schema' in metadata:
            #     model_props[self._client.repository.ModelMetaNames.OUTPUT_DATA_SCHEMA] = metadata['output_data_schema']
            if 'training_data_references' in metadata:
                model_props[self._client.repository.ModelMetaNames.TRAINING_DATA_REFERENCES] = metadata['training_data_references']
        else:
            model_props[self._client.repository.ModelMetaNames.FRAMEWORK_NAME] = metadata['framework']['name']
            model_props[self._client.repository.ModelMetaNames.FRAMEWORK_VERSION] = metadata['framework']['version']
            if 'runtimes' in metadata['framework']:
                model_props[self._client.repository.ModelMetaNames.RUNTIME_NAME] = metadata['framework']['runtimes'][0]['name']
                model_props[self._client.repository.ModelMetaNames.RUNTIME_VERSION] = metadata['framework']['runtimes'][0]['version']
            if 'training_data_schema' in metadata:
                model_props[self._client.repository.ModelMetaNames.TRAINING_DATA_SCHEMA] = metadata['training_data_schema']
            if 'evaluation' in metadata:
                model_props[self._client.repository.ModelMetaNames.EVALUATION_METHOD] = metadata['evaluation']['method']
                model_props[self._client.repository.ModelMetaNames.EVALUATION_METRICS] = metadata['evaluation']['metrics']
            if 'training_data_reference' in metadata:
                model_props[self._client.repository.ModelMetaNames.TRAINING_DATA_REFERENCE] = metadata['training_data_reference'][0]
            if 'libraries' in metadata['framework']:
                model_props[self._client.repository.ModelMetaNames.FRAMEWORK_LIBRARIES] = metadata['framework']['libraries']
            if 'label_column' in metadata:
                model_props[self._client.repository.ModelMetaNames.LABEL_FIELD] = metadata['label_column']
            if 'input_data_schema' in metadata:
                model_props[self._client.repository.ModelMetaNames.INPUT_DATA_SCHEMA] = metadata['input_data_schema']
            # if 'output_data_schema' in metadata:
            #     model_props[self._client.repository.ModelMetaNames.OUTPUT_DATA_SCHEMA] = metadata['output_data_schema']
        
        model_details = self._reliable_create_model(self._model_metadata['model_file'], model_props)
        if "type" in model_props and model_props["type"] == "python":
            model_guid = self._client.repository.get_function_uid(model_details)
        else:
            model_guid = self._client.repository.get_model_uid(model_details)
        logger.log_info('Created new model {} successfully (guid: {})'.format(model_name, model_guid))
        model_url = '{}{}?space_id={}&version=2020-06-22'.format(self._credentials['url'],
                                                                 self._client._models.get_href(model_details),
                                                                 self.space_id)
        return metadata, model_guid, model_url

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_create_model(self, model_file, model_props):
        start = time.time()
        try:
            if "type" in model_props and model_props["type"] == "python":
                model_details = self._client.repository.store_function(model_file, model_props)
            else:
                model_details = self._client.repository.store_model(model_file, model_props)
        except ApiRequestFailure as arf:
            if arf.error_msg is not None and "Unsupported software specification" in arf.error_msg:
                software_spec_uid = self._client.software_specifications.get_uid_by_name("default_py3.7_opence")
                model_props[self._client.repository.ModelMetaNames.SOFTWARE_SPEC_UID] = software_spec_uid
                if "type" in model_props and model_props["type"] == "python":
                    model_details = self._client.repository.store_function(model_file, model_props)
                else:
                    model_details = self._client.repository.store_model(model_file, model_props)
            else:
                raise arf

        elapsed = time.time() - start
        self._openscale_client.timer('WML repository.store_model', elapsed)
        return model_details

    def _list_all_models(self):
        logger.log_info('Listing all models ...')
        start = time.time()
        self._client.repository.list_models()
        elapsed = time.time() - start
        self._openscale_client.timer('WML repository.list_models', elapsed)
        logger.log_info('Models listed successfully')

    def _deploy_model(self, model_guid, deployment_name, deployment_description):
        logger.log_info('Creating new deployment {} ...'.format(deployment_name))
        elapsed_time, deployment_details = self._reliable_deploy_model(model_guid, deployment_name, deployment_description)
        if self._is_v4:
            deployment_guid = deployment_details['metadata']['id']
        deployment_url = deployment_details["entity"]["status"]["serving_urls"][0] if "serving_urls" in deployment_details["entity"]["status"] else deployment_details["entity"]["status"]["online_url"]["url"]
        logger.log_info('Created new deployment {} (guid: {}) successfully in {} seconds'.format(deployment_name, deployment_guid, round(elapsed_time, 2)))
        return deployment_guid, deployment_url

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_deploy_model(self, model_guid, deployment_name, deployment_description):
        start = time.time()
        deployment_details = None
        if self._is_v4:
            meta_props = {
                self._client.deployments.ConfigurationMetaNames.NAME: deployment_name,
                self._client.deployments.ConfigurationMetaNames.DESCRIPTION: deployment_description,
                self._client.deployments.ConfigurationMetaNames.ONLINE: {},
            }
            deployment_details = self._client.deployments.create(artifact_uid=model_guid, meta_props=meta_props)
        else:
            deployment_details = self._client.deployments.create(artifact_uid=model_guid, name=deployment_name, description=deployment_description)
        elapsed = time.time() - start
        self._openscale_client.timer('WML deployments.create', elapsed)
        return elapsed, deployment_details

    @retry(tries=5, delay=4, backoff=2)
    def _reliable_delete_deployment(self, deployment_guid):
        all_deployments = self._client.deployments.get_details()
        for deployment in all_deployments['resources']:
            if self._is_v4:
                artifact_deployment_id = deployment['metadata']['id']
            else:
                artifact_deployment_id = deployment['metadata']['guid']
            if deployment_guid == artifact_deployment_id:
                if not deployment_guid.startswith("WOS-INTERNAL"):
                    start = time.time()
                    rc = self._client.deployments.delete(deployment_guid)
                    if not rc == 'SUCCESS':
                        error_msg = 'ERROR: WML deployments.delete failed (id: {}) {}'.format(deployment_guid, rc)
                        logger.log_error(error_msg)
                        raise Exception(error_msg)
                    elapsed = time.time() - start
                    self._openscale_client.timer('WML deployments.delete', elapsed)
                    return
        logger.log_debug('Deployment {} not found, nothing to delete'.format(deployment_guid))

    def _list_all_deployments(self):
        start = time.time()
        deployment_details = self._client.deployments.get_details()
        elapsed = time.time() - start
        self._openscale_client.timer('WML deployments.get_details',elapsed)
        for details in deployment_details['resources']:
            logger.log_info('Name: {}, GUID: {}'.format(details['entity']['name'], details['metadata']['guid']))

    def create_model_and_deploy(self):
        model_name = self._model_metadata['model_name']
        deployment_name = self._model_metadata['deployment_name']

        # delete existing model and its deployments
        try:
            logger.log_info('Checking for models with the name {}'.format(model_name))
            self._delete_models(model_name)
        except Exception as e:
            pass # ignore deletion failures as we create a new model with same name different uid

        # create new model and deployment
        # self._create_pipeline(model_name, self._model_metadata['pipeline_metadata_file'])
        model_metadata_dict, model_guid, model_url = self._create_model(model_name, self._model_metadata['model_metadata_file'])
        deployment_guid, deployment_url = self._deploy_model(model_guid, deployment_name, self._model_metadata['deployment_description'])

        model_deployment_dict = {
            'deployment_url': deployment_url,
            'model_url': model_url,
            'model_name': model_name,
            'source_uid': model_guid,
            'model_metadata_dict': model_metadata_dict,
            'deployment_name': deployment_name,
            'source_entry_metadata_guid': deployment_guid,
            # 'binding_uid': self._client.service_instance.get_instance_id()
        }

        return model_deployment_dict

    def model_cleanup(self):
        model_name = self._model_metadata['model_name']
        self._delete_models(model_name)

    # returns info for first-found deployment with the specified name, if there are multiple
    def get_existing_deployment(self, deployment_name):
        model_name = self._model_metadata['model_name']
        model_guid = None
        deployment_guid = None
        model_metadata_dict = None
        model_url = None
        deployment_url = None
        logger.log_info('Use existing model named: {}'.format(model_name))
        models = self._client.repository.get_model_details()
        for this_model in models['resources']:
            this_model_name = this_model['metadata']['name']
            guid = this_model['metadata']['id']
            mata_data = this_model['metadata']
            if model_name == this_model_name:
                model_url = '{}{}?space_id={}&version=2020-06-22'.format(
                    self._credentials['url'],
                    self._client._models.get_href(this_model),
                    self.space_id
                )
                model_guid = guid
                model_metadata_dict = mata_data
                model_metadata_dict['training_data_schema'] = this_model['entity']['training_data_references'][0]['schema']
                break
        depl_details = self._client.deployments.get_details()
        for details in depl_details['resources']:
            dep_guid = details['metadata']['id']
            dep_name = details['entity']['name']
            if dep_name == deployment_name:
                deployment_url = details["entity"]["status"]["serving_urls"][0] if "serving_urls" in details["entity"]["status"] else details["entity"]["status"]["online_url"]["url"]
                deployment_guid = dep_guid
                break

        logger.log_info('Model Name: {}  Model GUID: {}'.format(model_name, model_guid))
        logger.log_info('Deployment Name: {}  Deployment GUID: {}'.format(deployment_name, deployment_guid))

        model_deployment_dict = {
            "model_name": model_name,
            'deployment_name': dep_name,
            'deployment_url': deployment_url,
            'model_url': model_url,
            'model_metadata_dict': model_metadata_dict,
            'source_uid': model_guid,
            'source_entry_metadata_guid': deployment_guid,
            # 'binding_uid': self._client.service_instance.get_instance_id(),
        }

        return model_deployment_dict

    def score(self, deployment_uid, values, fields=None):
        if fields:
            scoring_input = {
                "fields": fields,
                "values": values
            }
        else:
            scoring_input = {
                "values": values
            }
        payload = {
            self._client.deployments.ScoringMetaNames.INPUT_DATA: [scoring_input]
        }
        record = self._client.deployments.score(deployment_uid, payload)
        return record
