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
import uuid

from ibm_watson_machine_learning.helpers.connections import DataConnection, S3Location
from ibm_watson_machine_learning.utils.autoai.errors import WMLClientError
from ibm_watson_machine_learning.tests.utils import bucket_exists, create_bucket, is_cp4d, create_connection_to_cos
from ibm_watson_machine_learning.tests.autoai.abstract_tests_classes import AbstractTestAutoAIAsync, \
    AbstractTestWebservice, AbstractTestBatch

from ibm_watson_machine_learning.utils.autoai.enums import PredictionType, Metrics, ClassificationAlgorithms


class TestAutoAIRemote(AbstractTestAutoAIAsync, AbstractTestWebservice, AbstractTestBatch, unittest.TestCase):
    """
    The test can be run on CPD
    """

    cos_resource = None
    data_location = './autoai/data/credit_risk_training_500.parquet'

    data_cos_path = 'data/credit_risk_training_500.parquet'

    batch_payload_location = './autoai/data/credit_risk_scoring_payload.csv'
    batch_payload_cos_location = 'scoring_payload/credit_risk_scoring_payload.csv'

    SPACE_ONLY = False

    OPTIMIZER_NAME = "Credit Risk test sdk"

    BATCH_DEPLOYMENT_WITH_DF = True
    BATCH_DEPLOYMENT_WITH_DA = False

    target_space_id = None

    experiment_info = dict(
        name=OPTIMIZER_NAME,
        desc='test description',
        prediction_type=PredictionType.BINARY,
        prediction_column='Risk',
        scoring=Metrics.PRECISION_SCORE_MACRO,
        positive_label='No Risk',
        include_only_estimators=[ClassificationAlgorithms.SnapDT,
                                 ClassificationAlgorithms.SnapRF,
                                 ClassificationAlgorithms.SnapSVM,
                                 ClassificationAlgorithms.SnapLR],
        max_number_of_estimators=4,
        text_processing=False
    )

    def test_00b_prepare_COS_instance_and_connection(self):
        TestAutoAIRemote.connection_id, TestAutoAIRemote.bucket_name = create_connection_to_cos(
            wml_client=self.wml_client,
            cos_credentials=self.cos_credentials,
            cos_endpoint=self.cos_endpoint,
            bucket_name=self.bucket_name,
            save_data=True,
            data_path=self.data_location,
            data_cos_path=self.data_cos_path)

        self.assertIsInstance(self.connection_id, str)

    def test_02_data_reference_setup(self):
        TestAutoAIRemote.data_connection = DataConnection(
            connection_asset_id=self.connection_id,
            location=S3Location(
                bucket=self.bucket_name,
                path=self.data_cos_path
            )
        )
        self.assertIsNotNone(obj=TestAutoAIRemote.data_connection)

        TestAutoAIRemote.results_connection = None

        self.assertIsNone(obj=TestAutoAIRemote.results_connection)

    def test_11b_check_snap(self):
        pipeline_params = self.remote_auto_pipelines.get_pipeline_details()
        print(pipeline_params)

        pipeline_nodes = pipeline_params.get('pipeline_nodes')
        self.assertIn('Snap', str(pipeline_nodes), msg=f"{pipeline_nodes}")

    def test_99_delete_connection_and_connected_data_asset(self):
        self.wml_client.connections.delete(self.connection_id)

        with self.assertRaises(WMLClientError):
            self.wml_client.connections.get_details(self.connection_id)


if __name__ == '__main__':
    unittest.main()
