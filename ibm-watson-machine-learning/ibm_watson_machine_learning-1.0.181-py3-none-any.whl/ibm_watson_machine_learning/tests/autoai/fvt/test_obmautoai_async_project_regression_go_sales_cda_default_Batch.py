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
import  os
import ibm_boto3
from ibm_watson_machine_learning.preprocessing import DataJoinGraph
from ibm_watson_machine_learning.helpers.connections import DataConnection, ContainerLocation, FSLocation
from ibm_watson_machine_learning.tests.utils import is_cp4d, save_data_to_container, create_connection_to_cos
from ibm_watson_machine_learning.tests.autoai.abstract_tests_classes import AbstractTestOBM, \
    AbstractTestBatch

from ibm_watson_machine_learning.utils.autoai.errors import WrongDataJoinGraphNodeName

from ibm_watson_machine_learning.utils.autoai.enums import PredictionType, Metrics, RegressionAlgorithms


class TestAutoAIRemote(AbstractTestOBM, unittest.TestCase):
    """
    The test can be run on CLOUD, and CPD
    """
    HISTORICAL_RUNS_CHECK = False
    cos_resource = None

    input_data_filenames = ["go_1k.csv", "go_daily_sales.csv", "go_methods.csv",
                            "go_products.csv", "go_retailers.csv"]

    input_data_path = './autoai/data/go_sales_1k/'

    input_node_names = [name.replace('go_', 'node_').split('.')[0] for name in input_data_filenames]

    cos_endpoint = "https://s3.us.cloud-object-storage.appdomain.cloud"
    data_cos_path = "data/"

    SPACE_ONLY = False

    BATCH_DEPLOYMENT_WITH_DA = True
    BATCH_DEPLOYMENT_WITH_CDA = False
    BATCH_DEPLOYMENT_WITH_CA_DA = False
    BATCH_DEPLOYMENT_WITH_CA_CA = True

    OPTIMIZER_NAME = "Go Sales OBM test sdk"

    target_space_id: str = None

    experiment_info = dict(
        name=OPTIMIZER_NAME,
        desc='test description',
        prediction_type=PredictionType.REGRESSION,
        prediction_column='Quantity',
        scoring=Metrics.ROOT_MEAN_SQUARED_ERROR,
        # include_only_estimators=[RegressionAlgorithms.SnapDT, RegressionAlgorithms.RIDGE]
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
            asset_details = self.wml_client.data_assets.store({
                self.wml_client.data_assets.ConfigurationMetaNames.CONNECTION_ID: self.connection_id,
                self.wml_client.data_assets.ConfigurationMetaNames.NAME: f"{node_name} - training asset",
                self.wml_client.data_assets.ConfigurationMetaNames.DATA_CONTENT_NAME:
                    os.path.join(self.bucket_name, self.data_cos_path, file)
            })

            asset_id = self.wml_client.data_assets.get_id(asset_details)
            self.assertIsInstance(asset_id, str)

            conn = DataConnection(
                data_join_node_name=node_name,
                data_asset_id=asset_id
            )
            TestAutoAIRemote.data_connections.append(conn)

        TestAutoAIRemote.results_connection = None

        self.assertIsNotNone(obj=TestAutoAIRemote.data_connections)
        self.assertGreater(len(TestAutoAIRemote.data_connections), 0)
        self.assertIsNone(self.results_connection)


    def test_02_create_data_join_graph__graph_created(self):
        data_join_graph = DataJoinGraph()
        data_join_graph.node(name="node_daily_sales")
        data_join_graph.node(name="node_methods")
        data_join_graph.node(name="node_retailers")
        data_join_graph.node(name="node_products")
        data_join_graph.node(name="node_1k", main=True)

        data_join_graph.edge(from_node="node_products", to_node="node_1k",
                             from_column=["Product number"], to_column=["Product number"])
        data_join_graph.edge(from_node="node_retailers", to_node="node_1k",
                             from_column=["Retailer code"], to_column=["Retailer code"])
        data_join_graph.edge(from_node="node_methods", to_node="node_daily_sales",
                             from_column=["Order method code"], to_column=["Order method code"])

        TestAutoAIRemote.data_join_graph = data_join_graph

        print(f"data_join_graph: {data_join_graph}")




if __name__ == '__main__':
    unittest.main()
