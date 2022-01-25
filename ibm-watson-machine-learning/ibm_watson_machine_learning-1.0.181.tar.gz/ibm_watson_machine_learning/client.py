#  (C) Copyright IBM Corp. 2021.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import logging

from ibm_watson_machine_learning.messages.messages import Messages
from ibm_watson_machine_learning.utils import version

#from ibm_watson_machine_learning.learning_system import LearningSystem
from ibm_watson_machine_learning.experiments import Experiments
from ibm_watson_machine_learning.repository import Repository
from ibm_watson_machine_learning.model_definition import ModelDefinition
from ibm_watson_machine_learning.models import Models
from ibm_watson_machine_learning.pipelines import Pipelines
from ibm_watson_machine_learning.deployments import Deployments
from ibm_watson_machine_learning.factsheets import Factsheets
from ibm_watson_machine_learning.training import Training
from ibm_watson_machine_learning.functions import Functions
from ibm_watson_machine_learning.platform_spaces import PlatformSpaces
from ibm_watson_machine_learning.assets import Assets
from ibm_watson_machine_learning.connections import Connections
from ibm_watson_machine_learning.Set import Set
from ibm_watson_machine_learning.sw_spec import SwSpec
from ibm_watson_machine_learning.hw_spec import HwSpec
from ibm_watson_machine_learning.pkg_extn import PkgExtn
from ibm_watson_machine_learning.shiny import Shiny
from ibm_watson_machine_learning.script import Script
from ibm_watson_machine_learning.wml_client_error import NoWMLCredentialsProvided
from ibm_watson_machine_learning.wml_client_error import WMLClientError
from ibm_watson_machine_learning.instance_new_plan import ServiceInstanceNewPlan

from ibm_watson_machine_learning.remote_training_system import RemoteTrainingSystem
from ibm_watson_machine_learning.volumes import Volume

from ibm_watson_machine_learning.export_assets import Export
from ibm_watson_machine_learning.import_assets import Import

import copy
import os


'''
.. module:: APIClient
   :platform: Unix, Windows
   :synopsis: Watson Machine Learning API Client.

.. moduleauthor:: IBM
'''


class APIClient:
    version = None

    def __init__(self, wml_credentials, project_id=None, verify=None):
        self._logger = logging.getLogger(__name__)
        self.wml_credentials = copy.deepcopy(wml_credentials)
        self.CAMS = None
        self.WSD = None
        self.WSD_20 = None
        self.ICP_30 = None
        self.ICP = None
        self.default_space_id = None
        self.default_project_id = None
        self.project_type = None
        self.CLOUD_PLATFORM_SPACES = False
        self.PLATFORM_URL = None
        self.CAMS_URL = None
        self.CREATED_IN_V1_PLAN = False
        self.version_param = '2021-06-24'
        self.ICP_PLATFORM_SPACES = False # This will be applicable for 3.5 and later and specific to convergence functionalities
        self.ICP_35 = False # Use it for any 3.5 specific functionalities
        self.ICP_40 = False # Use it for any 4.0 specific functionalities
        self.CLOUD_BETA_FLOW = False

        self.PLATFORM_URLS_MAP = {
            'https://wml-dev.ml.test.cloud.ibm.com': 'https://api.dataplatform.dev.cloud.ibm.com',
            'https://wml-fvt.ml.test.cloud.ibm.com': 'https://api.dataplatform.dev.cloud.ibm.com',
            'https://us-south.ml.test.cloud.ibm.com': 'https://api.dataplatform.dev.cloud.ibm.com',
            'https://yp-qa.ml.cloud.ibm.com': 'https://api.dataplatform.test.cloud.ibm.com',
            'https://private.yp-qa.ml.cloud.ibm.com': 'https://api.dataplatform.test.cloud.ibm.com',
            'https://yp-cr.ml.cloud.ibm.com': 'https://api.dataplatform.test.cloud.ibm.com',
            'https://private.yp-cr.ml.cloud.ibm.com': 'https://api.dataplatform.test.cloud.ibm.com',
            'https://jp-tok.ml.cloud.ibm.com': 'https://api.jp-tok.dataplatform.cloud.ibm.com',
            'https://eu-gb.ml.cloud.ibm.com': 'https://api.eu-gb.dataplatform.cloud.ibm.com',
            'https://eu-de.ml.cloud.ibm.com': 'https://api.eu-de.dataplatform.cloud.ibm.com',
            'https://us-south.ml.cloud.ibm.com': 'https://api.dataplatform.cloud.ibm.com'
        }

        if verify:
            os.environ['WML_CLIENT_VERIFY_REQUESTS'] = 'True'

        elif isinstance(verify, str):
            os.environ['WML_CLIENT_VERIFY_REQUESTS'] = verify

        elif verify is None:
            pass

        else:
            os.environ['WML_CLIENT_VERIFY_REQUESTS'] = 'False'

        import ibm_watson_machine_learning._wrappers.requests as requests
        requests.packages.urllib3.disable_warnings()

        if "token" in wml_credentials:
            self.proceed = True
        else:
            self.proceed = False

        self.project_id = project_id
        self.wml_token = None
        self.__wml_local_supported_version_list = ['1.0', '1.1',
                                                   '2.0', '2.0.1', '2.0.2', '2.5.0',
                                                   '3.0.0', '3.0.1', '3.5', '4.0']
        self.__wsd_supported_version_list = ['1.0', '1.1', '2.0']
        self.__predefined_instance_type_list = ['icp', 'openshift', 'wml_local', 'wsd_local']
        os.environ['WSD_PLATFORM'] = 'False'
        if wml_credentials is None:
            raise NoWMLCredentialsProvided()
        if 'url' not in self.wml_credentials:
            raise WMLClientError(Messages.get_message(message_id="url_not_provided"))
        if not self.wml_credentials['url'].startswith('https://'):
            raise WMLClientError(Messages.get_message(message_id="invalid_url"))
        if self.wml_credentials['url'][-1] == "/":
            self.wml_credentials['url'] = self.wml_credentials['url'].rstrip('/')

        if 'instance_id' not in wml_credentials.keys():
            self.CLOUD_PLATFORM_SPACES = True
            self.wml_credentials[u'instance_id'] = 'invalid'  # This is applicable only via space instance_id
            self.ICP = False
            self.CAMS = False

            if wml_credentials[u'url'] in self.PLATFORM_URLS_MAP.keys():
                self.PLATFORM_URL = self.PLATFORM_URLS_MAP[wml_credentials[u'url']]
                self.CAMS_URL = self.PLATFORM_URLS_MAP[wml_credentials[u'url']]
            else:
                raise WMLClientError(Messages.get_message(message_id="invalid_cloud_scenario_url"))

            if not self._is_IAM():
                raise WMLClientError(Messages.get_message(message_id="apikey_not_provided"))
        else:
            if 'icp' == wml_credentials[u'instance_id'].lower() or 'openshift' == wml_credentials[
                u'instance_id'].lower() or 'wml_local' == wml_credentials[u'instance_id'].lower():
                self.ICP = True
                os.environ["DEPLOYMENT_PLATFORM"] = "private"
                ##Condition for CAMS related changes to take effect (Might change)
                if 'version' not in wml_credentials:
                    raise WMLClientError(Messages.get_message(self.__wml_local_supported_version_list, message_id="version_not_provided"))

                if 'version' in wml_credentials.keys() and (
                        '2.0.1' == wml_credentials[u'version'].lower() or '2.5.0' == wml_credentials[
                    u'version'].lower() or
                        '3.0.0' == wml_credentials[u'version'].lower() or '3.0.1' == wml_credentials[
                            u'version'].lower() or '3.5' == wml_credentials[u'version'].lower() or
                        '4.0' == wml_credentials[u'version'].lower() or
                        '1.1' == wml_credentials[u'version'].lower() or '2.0' == wml_credentials[u'version'].lower()):
                    self.CAMS = True
                    os.environ["DEPLOYMENT_PRIVATE"] = "icp4d"
                    if 'wml_local' == wml_credentials[u'instance_id'].lower() and \
                            ('1.1' == wml_credentials[u'version'].lower() or '2.0' == wml_credentials[
                                u'version'].lower()):
                        url_port = wml_credentials[u'url'].split(':')[-1]
                        if not url_port.isdigit():
                            raise WMLClientError(Messages.get_message(message_id="no_port_number_for_wml_local"))

                    if '3.0.0' == wml_credentials[u'version'].lower() or \
                            '3.0.1' == wml_credentials[u'version'].lower() or \
                            '2.0' == wml_credentials[u'version'].lower():
                        self.ICP_30 = True

                    # For Cloud convergence related functionalities brought into CP4D 3.5
                    if '3.5' == wml_credentials[u'version'].lower():
                        self.ICP_PLATFORM_SPACES = True
                        self.ICP_35 = True

                    if '4.0' == wml_credentials[u'version'].lower():
                        self.ICP_PLATFORM_SPACES = True
                        self.ICP_40 = True
                        if 'bedrock_url' not in wml_credentials:
                            self.wml_credentials['bedrock_url'] = '.'.join(['https://cp-console'] + wml_credentials['url'].split('.')[1:])
                            self._is_bedrock_url_autogenerated = True

                else:
                    if 'version' in wml_credentials.keys() and \
                            wml_credentials[u'version'].lower() not in self.__wml_local_supported_version_list:
                        raise WMLClientError(Messages.get_message(
                            ', '.join(self.__wml_local_supported_version_list),
                            message_id="invalid_version"))

                    self.CAMS = False
            else:
                if ('wsd_local' == wml_credentials[u'instance_id'].lower()) and \
                        ('1.1' == wml_credentials[u'version'].lower() or '2.0' == wml_credentials[u'version'].lower()):
                    self.WSD = True
                    os.environ['WSD_PLATFORM'] = 'True'
                    if '2.0' == wml_credentials[u'version'].lower():
                        self.WSD_20 = True
                else:
                    if ('wsd_local' == wml_credentials[u'instance_id'].lower()) and \
                            'version' in wml_credentials.keys() and \
                            wml_credentials[u'version'].lower() not in self.__wsd_supported_version_list:
                        raise WMLClientError(Messages.get_message(
                            ', '.join(self.__wsd_supported_version_list),
                            message_id="invalid_version"))

                    if 'instance_id' in wml_credentials.keys():
                        if wml_credentials['url'] in self.PLATFORM_URLS_MAP:
                            raise WMLClientError(Messages.get_message(message_id="instance_id_in_cloud_scenario"))
                        else:
                            raise WMLClientError(Messages.get_message(message_id="invalid_instance_id"))

                    self.ICP = False
                    self.CAMS = False

                    self.service_instance = ServiceInstanceNewPlan(self)

                    headers = self._get_headers()

                    del headers[u'X-WML-User-Client']
                    if 'ML-Instance-ID' in headers:
                        del headers[u'ML-Instance-ID']
                    del headers[u'x-wml-internal-switch-to-new-v4']

                    response_get_instance = requests.get(
                        u'{}/ml/v4/instances/{}'.format(self.wml_credentials['url'],
                                                  self.wml_credentials['instance_id']),
                        params={'version': self.version_param},
                        # params=self._client._params(),
                        headers=headers
                    )

                    if response_get_instance.status_code == 200:
                        if 'plan' in response_get_instance.json()[u'entity']:
                            tags = response_get_instance.json()[u'metadata']['tags']
                            if 'created_in_v1_plan' in tags:
                                self.CREATED_IN_V1_PLAN = True
                            if response_get_instance.json()[u'entity'][u'plan'][u'version'] == 2 and\
                                    not self.CREATED_IN_V1_PLAN and\
                                    response_get_instance.json()[u'entity'][u'plan']['name'] != 'lite':
                                self.CLOUD_PLATFORM_SPACES = True

                                # If v1 lite converted to v2 plan, tags : ["created_in_v1_plan"]

                                if not self._is_IAM():
                                    raise WMLClientError(Messages.get_message(message_id="apikey_not_provided"))

                                if wml_credentials[u'url'] in self.PLATFORM_URLS_MAP.keys():
                                    self.PLATFORM_URL = self.PLATFORM_URLS_MAP[wml_credentials[u'url']]
                                    self.CAMS_URL = self.PLATFORM_URLS_MAP[wml_credentials[u'url']]
                                else:
                                    raise WMLClientError(Messages.get_message(message_id="url_not_provided"))

                                if self.CLOUD_PLATFORM_SPACES:
                                    print(Messages.get_message(message_id="instance_id_is_not_required_for_v2_plans"))

                            if not self.CLOUD_PLATFORM_SPACES:
                                self.CLOUD_BETA_FLOW = True
                                print(Messages.get_message(message_id="creating_assets_using_v4_beta_flow_is_deprecated"))
                    elif response_get_instance.status_code == 404:
                        raise WMLClientError(Messages.get_message(message_id="instance_id_not_found"))
                    elif response_get_instance.status_code == 401:
                        raise WMLClientError(Messages.get_message(message_id="not_authorized_to_access_the_instance_id"))
                    else:
                        # if someone is using beta flow and using instance api key
                        response_get_instance_v1 = requests.get(
                            u'{}/v3/wml_instances/{}'.format(self.wml_credentials['url'],
                                                             self.wml_credentials['instance_id']),
                            headers=self._get_headers()
                        )

                        if response_get_instance_v1.status_code != 200:
                            raise WMLClientError(Messages.get_message(
                                response_get_instance.text,
                                message_id="failed_to_get_instance_details"))

                        self.CLOUD_BETA_FLOW = True
                        print(Messages.get_message(message_id="creating_assets_using_v4_beta_flow_is_deprecated"))
            if "token" in wml_credentials:
                self.proceed = True
            else:
                self.proceed = False

        if 'instance_id' in wml_credentials.keys() and \
                (wml_credentials['instance_id'].lower() not in self.__predefined_instance_type_list) and \
                'version' in wml_credentials.keys():
            raise WMLClientError(Messages.get_message(message_id="provided_credentials_are_invalid"))

        self.project_id = project_id
        self.wml_token = None

        if not self.CLOUD_PLATFORM_SPACES and not self.ICP_PLATFORM_SPACES and not self.CLOUD_BETA_FLOW:
            raise WMLClientError(Messages.get_message(message_id="client_is_not_supported_in_this_release"))

        # if not self.ICP and not self.ICP_30 and not self.WSD:
        if not self.WSD and not self.CLOUD_PLATFORM_SPACES and not self.ICP_PLATFORM_SPACES:
            from ibm_watson_machine_learning.instance import ServiceInstance
            self.service_instance = ServiceInstance(self)
            self.service_instance.details = self.service_instance.get_details()

        if self.CLOUD_PLATFORM_SPACES or self.ICP_PLATFORM_SPACES:
            # For cloud, service_instance.details will be set during space creation( if instance is associated ) or
            # while patching a space with an instance
            import sys
            if (3 == sys.version_info.major) and (6 == sys.version_info.minor):
                if self.CLOUD_PLATFORM_SPACES:
                    print(Messages.get_message(message_id="python_3_6_framework_is_deprecated"))
                elif self.ICP_PLATFORM_SPACES:
                    print(Messages.get_message(message_id="python_3_6_framework_is_deprecated_cp4d"))

            self.service_instance = ServiceInstanceNewPlan(self)
            self.volumes = Volume(self)

            if self.ICP_PLATFORM_SPACES:
                self.service_instance.details = self.service_instance.get_details()

            self.set = Set(self)

            self.spaces = PlatformSpaces(self)

            self.export_assets = Export(self)
            self.import_assets = Import(self)

            if self.ICP_PLATFORM_SPACES:
                self.shiny = Shiny(self)

            self.script = Script(self)
            self.model_definitions = ModelDefinition(self)

            self.package_extensions = PkgExtn(self)
            self.software_specifications = SwSpec(self)

            self.hardware_specifications = HwSpec(self)

            self.connections = Connections(self)
            self.training = Training(self)

            self.data_assets = Assets(self)

            self.deployments = Deployments(self)

            if self.CLOUD_PLATFORM_SPACES:
                from ibm_watson_machine_learning.migration_v4ga_cloud import Migrationv4GACloud
                self.v4ga_cloud_migration = Migrationv4GACloud(self)
                self.factsheets = Factsheets(self)

            self.remote_training_systems = RemoteTrainingSystem(self)

        ##Initialize Assets and Model_Definitions only for CAMS
        if (self.CAMS or self.WSD) and not self.ICP_PLATFORM_SPACES:
            self.set = Set(self)
            self.data_assets = Assets(self)
            self.model_definitions = ModelDefinition(self)
            if self.ICP_30:
                self.connections = Connections(self)
                self.software_specifications = SwSpec(self)
                self.hardware_specifications = HwSpec(self)
                self.package_extensions = PkgExtn(self)
                self.script = Script(self)
                if not '2.0' == wml_credentials[u'version'].lower():
                    self.shiny = Shiny(self)
            if self.WSD_20:
                self.software_specifications = SwSpec(self)

        #    self.learning_system = LearningSystem(self)
        self.repository = Repository(self)
        self._models = Models(self)
        self.pipelines = Pipelines(self)
        self.experiments = Experiments(self)
        self._functions = Functions(self)

        if not self.WSD and not self.CLOUD_PLATFORM_SPACES and not self.ICP_PLATFORM_SPACES:
            from ibm_watson_machine_learning.runtimes import Runtimes
            from ibm_watson_machine_learning.spaces import Spaces
            self.runtimes = Runtimes(self)
            self.deployments = Deployments(self)
            self.training = Training(self)
            self.spaces = Spaces(self)
            self.connections = Connections(self)

        self._logger.info(Messages.get_message(message_id="client_successfully_initialized"))
        self.version = version()

    def _check_if_either_is_set(self):
        if self.CAMS or self.CLOUD_PLATFORM_SPACES:
            if self.default_space_id is None and self.default_project_id is None:
                raise WMLClientError(Messages.get_message(message_id="it_is_mandatory_to_set_the_space_project_id"))

    def _check_if_space_is_set(self):
        if self.CAMS or self.CLOUD_PLATFORM_SPACES:
            if self.default_space_id is None:
                raise WMLClientError(Messages.get_message(message_id="it_is_mandatory_to_set_the_space_id"))

    def _params(self, skip_space_project_chk=False, skip_for_create=False):
        params = {}
        if self.CAMS or self.CLOUD_PLATFORM_SPACES:
            if self.CLOUD_PLATFORM_SPACES or self.ICP_PLATFORM_SPACES:
                params.update({'version': self.version_param})
            if not skip_for_create:
                if self.default_space_id is not None:
                    params.update({'space_id': self.default_space_id})
                elif self.default_project_id is not None:
                    params.update({'project_id': self.default_project_id})
                else:
                    # For system software/hardware specs
                    if skip_space_project_chk is False:
                        raise WMLClientError(Messages.get_message(message_id="it_is_mandatory_to_set_the_space_project_id"))

        if self.WSD:
            if self.default_project_id is not None:
                params.update({'project_id': self.default_project_id})
            else:
                raise WMLClientError(Messages.get_message(message_id="it_is_mandatory_to_set_the_project_id"))

        if self.project_type == 'local_git_storage':
            params.update({'userfs': 'true'})

        if self.project_type != 'local_git_storage' and 'userfs' in params:
            del params['userfs']

        return params

    def _get_headers(self, content_type='application/json', no_content_type=False, wsdconnection_api_req=False, zen=False):
        if self.WSD:
                headers = {'X-WML-User-Client': 'PythonClient'}
                if self.project_id is not None:
                    headers.update({'X-Watson-Project-ID': self.project_id})
                if not no_content_type:
                    headers.update({'Content-Type': content_type})
                if wsdconnection_api_req is True:
                    token = "desktop user token"
                else:
                    token = "desktop-token"
                headers.update({'Authorization':  "Bearer " + token})

        elif zen:
            headers= {'Content-Type': content_type}
            headers.update({'Authorization': "Bearer " + self.service_instance._create_token()})
        else:
            if self.proceed is True:
                token = "Bearer "+ self.wml_credentials["token"]
            else:
                token = "Bearer " + self.service_instance._get_token()
            headers = {
                'Authorization': token,
                'X-WML-User-Client': 'PythonClient'
            }
            # Cloud Convergence
            if self._is_IAM() or (self.service_instance._is_iam() is None and not self.CLOUD_PLATFORM_SPACES and not self.ICP_PLATFORM_SPACES):
                headers['ML-Instance-ID'] = self.wml_credentials['instance_id']

            headers.update({'x-wml-internal-switch-to-new-v4': "true"})
            if not self.ICP:
                #headers.update({'x-wml-internal-switch-to-new-v4': "true"})
                if self.project_id is not None:
                    headers.update({'X-Watson-Project-ID': self.project_id})

            if not no_content_type:
                headers.update({'Content-Type': content_type})

        return headers

    def _get_icptoken(self):
        return self.service_instance._create_token()

    def _is_default_space_set(self):
        if self.default_space_id is not None:
            return True
        return False

    def _is_IAM(self):
        if('apikey' in self.wml_credentials.keys()):
            if (self.wml_credentials['apikey'] != ''):
                return True
            else:
                raise WMLClientError(Messages.get_message(message_id="apikey_value_cannot_be_empty"))
        elif('token' in self.wml_credentials.keys()):
            if (self.wml_credentials['token'] != ''):
                return True
            else:
                raise WMLClientError(Messages.get_message(message_id="token_value_cannot_be_empty"))
        else:
            return False
