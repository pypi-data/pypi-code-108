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
import os

import ibm_boto3
from ibm_watson_machine_learning.preprocessing import DataJoinGraph
from ibm_watson_machine_learning.helpers.connections import DataConnection, S3Location
from ibm_watson_machine_learning.tests.utils import create_connection_to_cos
from ibm_watson_machine_learning.tests.autoai.abstract_tests_classes import AbstractTestOBM

from ibm_watson_machine_learning.utils.autoai.enums import PredictionType, Metrics, ClassificationAlgorithms


class TestAutoAIRemote(AbstractTestOBM, unittest.TestCase):
    """
    The test can be run on CLOUD, and CPD
    """
    HISTORICAL_RUNS_CHECK = False
    cos_resource = None

    subnames = ['insurance', 'customer', 'claim']

    deployment_payload_filenames = [f'{name}.csv' for name in subnames]
    input_data_filenames = [f'binary_delimiter_colon_{name}.csv' for name in subnames]
    input_data_path = './autoai/data/insurance_dataset/'

    input_node_names = subnames

    cos_endpoint = "https://s3.us.cloud-object-storage.appdomain.cloud"
    data_cos_path = "obm_data/"

    SPACE_ONLY = True

    BATCH_DEPLOYMENT_WITH_DA = True
    BATCH_DEPLOYMENT_WITH_CDA = True
    BATCH_DEPLOYMENT_WITH_CA_DA = True
    BATCH_DEPLOYMENT_WITH_CA_CA = True

    OPTIMIZER_NAME = "Binary Insurance dataset with colon delimeter OBM test sdk"

    target_space_id: str = None

    fairness_info = {
        # "protected_attributes": [
        #     {"feature": " ",
        #      "monitored_group": []},
        # ],
        "favorable_labels": [1]
    }

    experiment_info = dict(
        name=OPTIMIZER_NAME,
        prediction_type=PredictionType.BINARY,
        prediction_column='valid',
        positive_label=1,
        scoring=Metrics.RECALL_SCORE,
        drop_duplicates=False,
        fairness_info=fairness_info,
        include_only_estimators=[ClassificationAlgorithms.SnapSVM, ClassificationAlgorithms.EX_TREES]
    )

    def test_00b_prepare_COS_instance_and_connection(self):
        TestAutoAIRemote.connection_id, TestAutoAIRemote.bucket_name = create_connection_to_cos(
            wml_client=self.wml_client,
            cos_credentials=self.cos_credentials,
            cos_endpoint=self.cos_endpoint,
            bucket_name=self.bucket_name,
            save_data=True,
            data_path=self.input_data_path,
            data_filenames=self.input_data_filenames,
            data_cos_path=self.data_cos_path)

        self.assertIsInstance(self.connection_id, str)

    def test_01_create_multiple_data_connections__connections_created(self):
        TestAutoAIRemote.data_connections = []
        for file, node_name in zip(self.input_data_filenames, self.input_node_names):
            conn = DataConnection(
                data_join_node_name=node_name,
                connection_asset_id=self.connection_id,
                location=S3Location(
                    bucket=self.bucket_name,
                    path=os.path.join(self.data_cos_path, file)
                )
            )
            TestAutoAIRemote.data_connections.append(conn)

        TestAutoAIRemote.results_connection = None

        self.assertIsNotNone(obj=TestAutoAIRemote.data_connections)
        self.assertEqual(len(TestAutoAIRemote.data_connections), len(self.input_data_filenames))
        self.assertIsNone(self.results_connection)

    def test_02_create_data_join_graph__graph_created(self):
        print("Defining DataJoinGraph...")
        data_join_graph = DataJoinGraph()
        data_join_graph.node(name="customer", csv_separator=":")
        data_join_graph.node(name="insurance", csv_separator=":", main=True)
        data_join_graph.node(name="claim", csv_separator=":")
        data_join_graph.edge(from_node="customer", to_node="insurance",
                             from_column=["customer_number"], to_column=["customer_id"])
        data_join_graph.edge(from_node="claim", to_node="insurance",
                             from_column=["claim_SN"], to_column=["claim_id"])

        TestAutoAIRemote.data_join_graph = data_join_graph

        print(f"data_join_graph: {data_join_graph}")

    def test_40b_deployment_input_files_setup(self):
        TestAutoAIRemote.input_data_filenames = self.deployment_payload_filenames


if __name__ == '__main__':
    unittest.main()
