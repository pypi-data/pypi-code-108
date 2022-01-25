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

import os
import abc
import shutil

import coremltools

from ibm_watson_machine_learning.utils import extract_mlmodel_from_archive
from ibm_watson_machine_learning.tests.base.abstract.abstract_deployment_test import AbstractDeploymentTest



class AbstractVirtualDeploymentTest(AbstractDeploymentTest, abc.ABC):
    """
    Abstract class implementing scoring with virtual deployment.
    """
    download_path = "deployed_model.tar.gz"
    converted_model_path = None
    coreml_model = None


    def create_deployment_props(self):
        return {
            self.wml_client.deployments.ConfigurationMetaNames.NAME: self.deployment_name,
            self.wml_client.deployments.ConfigurationMetaNames.VIRTUAL: {"export_format": "coreml"}
        }

    def test_09_download_deployment(self):
        deployment_content = self.wml_client.deployments.download(self.deployment_id, self.download_path)
        self.assertIsNotNone(deployment_content)
        self.assertTrue(os.path.exists(self.download_path))

    def test_09a_load_downloaded_model(self):
        AbstractVirtualDeploymentTest.converted_model_path = extract_mlmodel_from_archive(
            self.download_path,
            self.model_id
        )
        self.assertTrue(os.path.exists(self.converted_model_path))

        AbstractVirtualDeploymentTest.coreml_model = coremltools.models.MLModel(self.converted_model_path)
        self.assertIsNotNone(self.coreml_model)

    def test_10_score_deployments(self):
        scoring_payload = self.create_scoring_payload()
        predictions = self.coreml_model.predict(scoring_payload)
        self.assertIsNotNone(predictions)

    def test_17_delete_downloaded_files(self):
        shutil.rmtree(self.model_id)
