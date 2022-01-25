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

import abc

from ibm_watson_machine_learning.tests.base.abstract.abstract_deployment_test import AbstractDeploymentTest



class AbstractOnlineDeploymentTest(AbstractDeploymentTest, abc.ABC):
    """
    Abstract class implementing scoring with online deployment.
    """
    def create_deployment_props(self):
        return {
            self.wml_client.deployments.ConfigurationMetaNames.NAME: self.deployment_name,
            self.wml_client.deployments.ConfigurationMetaNames.ONLINE: {}
        }

    def test_09_download_deployment(self):
        pass

    def test_10_score_deployments(self):
        scoring_payload = self.create_scoring_payload()
        predictions = self.wml_client.deployments.score(self.deployment_id, scoring_payload)

        self.assertIsNotNone(predictions)
        self.assertIn("predictions", predictions)
