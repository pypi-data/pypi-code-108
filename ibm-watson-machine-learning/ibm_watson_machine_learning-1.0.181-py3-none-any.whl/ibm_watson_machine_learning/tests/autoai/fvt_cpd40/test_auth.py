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

import unittest
import copy

from ibm_watson_machine_learning import APIClient

from ibm_watson_machine_learning.tests.utils import (get_wml_credentials, is_cp4d)
from ibm_watson_machine_learning.wml_client_error import WMLClientError, CannotAutogenerateBedrockUrl


@unittest.skipIf(not is_cp4d(), "Not supported on cloud")
class TestAutoAIRemote(unittest.TestCase):
    """
    The test can be run on CLOUD, WMLS and CPD (not tested)
    The test covers:
    - COS set-up (if run on Cloud): checking if bucket exists for the cos instance, if not new bucket is create
    - Saving data `/bank.cdv` to COS/data assets
    - downloading training data from cos/data assets
    - downloading all generated pipelines to lale pipeline
    - deployment with lale pipeline
    - deployment deletion
    """
    wml_credentials = None
    token = None

    @classmethod
    def setUpClass(cls) -> None:
        """
        Load WML credentials from config.ini file based on ENV variable.
        """
        cls.wml_credentials = get_wml_credentials()
        wml_client = APIClient(wml_credentials=cls.wml_credentials)
        cls.token = wml_client.wml_token

    def test_01_missing_version(self):
        wml_credentials = copy.copy(self.wml_credentials)
        del wml_credentials['version']

        with self.assertRaises(WMLClientError) as context:
            APIClient(wml_credentials=wml_credentials)

        self.assertTrue('Missing version in credentials for Cloud Pak for Data. Add key `version` to your credentials with a supported value, referring to your software version' in context.exception.error_msg)

    def test_02_missing_url(self):
        wml_credentials = copy.copy(self.wml_credentials)
        del wml_credentials['url']

        with self.assertRaises(WMLClientError) as context:
            APIClient(wml_credentials=wml_credentials)

        self.assertTrue('`url` is not provided' in context.exception.error_msg)

    def test_03_missing_instance_id(self):
        wml_credentials = copy.copy(self.wml_credentials)
        del wml_credentials['instance_id']

        with self.assertRaises(WMLClientError) as context:
            APIClient(wml_credentials=wml_credentials)

        self.assertTrue('The specified url is not valid. To authenticate with your Cloud Pak for Data installed software, add `"instance_id": "openshift"` to your credentials. To authenticate with your Cloud Pak for Data as a Service account, see https://dataplatform.cloud.ibm.com/docs/content/wsj/analyze-data/ml-authentication.html.' in context.exception.error_msg)

    def test_04_invalid_version(self):
        wml_credentials = copy.copy(self.wml_credentials)
        wml_credentials['version'] = 'banana'

        with self.assertRaises(WMLClientError) as context:
            APIClient(wml_credentials=wml_credentials)

        self.assertTrue('Invalid value for \'version\' provided in wml_credentials' in context.exception.error_msg)

    def test_05_invalid_url(self):
        wml_credentials = copy.copy(self.wml_credentials)
        wml_credentials['url'] = 'banana'

        with self.assertRaises(WMLClientError) as context:
            APIClient(wml_credentials=wml_credentials)

        self.assertTrue('`url` must start with `https://`.' in context.exception.error_msg)

    def test_06_invalid_instance_id(self):
        wml_credentials = copy.copy(self.wml_credentials)
        wml_credentials['instance_id'] = 'banana'

        with self.assertRaises(WMLClientError) as context:
            APIClient(wml_credentials=wml_credentials)

        self.assertTrue('Invalid instance_id for Cloud Pak for Data. Use `"instance_id": "openshift"` in your credentials. To authenticate with a different offering, refer to the product documentation for authentication details.' in context.exception.error_msg)

    def test_username_password_auth_scenario_01_correct(self):
        wml_credentials = {
            'instance_id': self.wml_credentials['instance_id'],
            'url': self.wml_credentials['url'],
            'version': self.wml_credentials['version'],
            'username': self.wml_credentials['username'],
            'password': self.wml_credentials['password']
        }
        APIClient(wml_credentials=wml_credentials)

    def test_username_password_auth_scenario_02_missing_password(self):
        wml_credentials = {
            'instance_id': self.wml_credentials['instance_id'],
            'url': self.wml_credentials['url'],
            'version': self.wml_credentials['version'],
            'username': self.wml_credentials['username']
        }

        with self.assertRaises(WMLClientError) as context:
            APIClient(wml_credentials=wml_credentials)

        self.assertTrue('`password` missing in wml_credentials.' in context.exception.error_msg)

    def test_username_password_auth_scenario_03_missing_username(self):
        wml_credentials = {
            'instance_id': self.wml_credentials['instance_id'],
            'url': self.wml_credentials['url'],
            'version': self.wml_credentials['version'],
            'password': self.wml_credentials['password']
        }

        with self.assertRaises(CannotAutogenerateBedrockUrl) as context:
            APIClient(wml_credentials=wml_credentials)

        self.assertTrue('`username` missing in wml_credentials.' in context.exception.args[0].error_msg)

    def test_username_apikey_auth_scenario_01_correct(self):
        if 'apikey' not in self.wml_credentials:
            self.skipTest("No apikey in creds")

        wml_credentials = {
            'instance_id': self.wml_credentials['instance_id'],
            'url': self.wml_credentials['url'],
            'version': self.wml_credentials['version'],
            'username': self.wml_credentials['username'],
            'apikey': self.wml_credentials['apikey']
        }
        APIClient(wml_credentials=wml_credentials)

    def test_username_apikey_auth_scenario_02_invalid_apikey_key(self):
        if 'apikey' not in self.wml_credentials:
            self.skipTest("No apikey in creds")

        wml_credentials = {
            'instance_id': self.wml_credentials['instance_id'],
            'url': self.wml_credentials['url'],
            'version': self.wml_credentials['version'],
            'username': self.wml_credentials['username'],
            'apikey': self.wml_credentials['apikey']
        }
        APIClient(wml_credentials=wml_credentials)

    def test_token_auth_scenario_01_correct(self):
        wml_credentials = {
            'instance_id': self.wml_credentials['instance_id'],
            'url': self.wml_credentials['url'],
            'version': self.wml_credentials['version'],
            'token': self.token
        }
        APIClient(wml_credentials=wml_credentials)

    # For CPD it cannot be determined at this stage
    # def test_token_auth_scenario_02_invalid_token(self):
    #     wml_credentials = {
    #         'instance_id': self.wml_credentials['instance_id'],
    #         'url': self.wml_credentials['url'],
    #         'version': self.wml_credentials['version'],
    #         'token': 'banana'
    #     }
    #     with self.assertRaises(WMLClientError) as context:
    #         APIClient(wml_credentials=wml_credentials)
    #
    #     self.assertTrue('invalid token' in context.exception.error_msg)

    def test_token_auth_scenario_03_missing_token(self):
        wml_credentials = {
            'instance_id': self.wml_credentials['instance_id'],
            'url': self.wml_credentials['url'],
            'version': self.wml_credentials['version']
        }

        with self.assertRaises(WMLClientError) as context:
            APIClient(wml_credentials=wml_credentials)

        self.assertTrue('`username` missing in wml_credentials.' in context.exception.error_msg)

if __name__ == '__main__':
    unittest.main()
