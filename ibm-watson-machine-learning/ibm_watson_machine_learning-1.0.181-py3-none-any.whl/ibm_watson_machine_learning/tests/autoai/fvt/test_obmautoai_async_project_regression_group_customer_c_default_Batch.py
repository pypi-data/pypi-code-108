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

import ibm_boto3
from ibm_watson_machine_learning.preprocessing import DataJoinGraph
from ibm_watson_machine_learning.helpers.connections import DataConnection, ContainerLocation, FSLocation
from ibm_watson_machine_learning.tests.utils import is_cp4d, save_data_to_container
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

    input_data_filenames = ['group_customer_main.csv', 'group_customer_customers.csv',
                            'group_customer_transactions.csv',
                            'group_customer_purchase.csv', 'group_customer_products.csv']
    input_data_path = './autoai/data/group_customer'

    input_node_names = [name.replace('group_customer_', '').split('.')[0] for name in input_data_filenames]

    cos_endpoint = "https://s3.us.cloud-object-storage.appdomain.cloud"
    data_cos_path = "data/"

    SPACE_ONLY = False

    BATCH_DEPLOYMENT_WITH_DA = False
    BATCH_DEPLOYMENT_WITH_CDA = False
    BATCH_DEPLOYMENT_WITH_CA_DA = True
    BATCH_DEPLOYMENT_WITH_CA_CA = True

    OPTIMIZER_NAME = "Group Customer OBM test sdk"

    target_space_id: str = None

    fairness_info = {
        "protected_attributes": [
            {"feature": "gender",
             "monitored_group": ["F"]},
        ],
        "favorable_labels": [[13, 28]],
        "unfavorable_labels": [[0, 12], [29, 62]]
    }

    experiment_info = dict(
        name=OPTIMIZER_NAME,
        desc='test description',
        prediction_type=PredictionType.REGRESSION,
        prediction_column='next_purchase',
        scoring=Metrics.R2_AND_DISPARATE_IMPACT_SCORE,
        holdout_size=0.2,
        fairness_info=fairness_info,
        include_only_estimators=[RegressionAlgorithms.LGBM, RegressionAlgorithms.XGB]
    )

    def test_00b_write_data_to_container(self):
        if self.SPACE_ONLY:
            self.wml_client.set.default_space(self.space_id)
        else:
            self.wml_client.set.default_project(self.project_id)

        save_data_to_container(data_path=self.input_data_path,
                               data_cos_path=self.data_cos_path,
                               data_filenames=self.input_data_filenames,
                               wml_client=self.wml_client)

    def test_01_create_multiple_data_connections__connections_created(self):
        TestAutoAIRemote.data_connections = []
        for file, node_name in zip(self.input_data_filenames, self.input_node_names):
            conn = DataConnection(
                data_join_node_name=node_name,
                location=ContainerLocation(path=file))
            TestAutoAIRemote.data_connections.append(conn)

        TestAutoAIRemote.results_connection = None

        self.assertIsNotNone(obj=TestAutoAIRemote.data_connections)
        self.assertGreater(len(TestAutoAIRemote.data_connections), 0)
        self.assertIsNone(self.results_connection)

    def test_02_create_data_join_graph__graph_created(self):
        data_join_graph = DataJoinGraph()
        data_join_graph.node(name="main")
        data_join_graph.node(name="customers")
        data_join_graph.node(name="transactions")
        data_join_graph.node(name="purchase")
        data_join_graph.node(name="products")
        data_join_graph.edge(from_node="main", to_node="customers",
                             from_column=["group_customer_id"], to_column=["group_customer_id"])
        data_join_graph.edge(from_node="main", to_node="transactions",
                             from_column=["transaction_id"], to_column=["transaction_id"])
        data_join_graph.edge(from_node="main", to_node="purchase",
                             from_column=["group_id"], to_column=["group_id"])
        data_join_graph.edge(from_node="transactions", to_node="products",
                             from_column=["product_id"], to_column=["product_id"])

        TestAutoAIRemote.data_join_graph = data_join_graph

        print(f"data_join_graph: {data_join_graph}")

    def test_07a_check_data_join_node_names(self):
        data_connections = []
        if self.wml_client.ICP:
            for file in self.input_data_filenames:
                conn = DataConnection(
                    location=FSLocation(path=self.data_location + file))
                data_connections.append(conn)
        else:
            for file in self.input_data_filenames:
                conn = DataConnection(
                    location=ContainerLocation(path=file))
                data_connections.append(conn)

        self.assertGreater(len(data_connections), 0)

        with self.assertRaises(WrongDataJoinGraphNodeName, msg="Training started with wrong data join node names"):
            self.remote_auto_pipelines.fit(
                training_data_reference=data_connections,
                training_results_reference=self.results_connection,
                background_mode=False)

    # def test_08_fit_run_training_of_auto_ai_in_wml(self):
    #
    #     AbstractTestOBM.remote_auto_pipelines = self.experiment.runs.get_optimizer("d7ed9b03-0577-42d4-938c-14ff5f1ad528")
    #     AbstractTestOBM.trained_pipeline_details = self.remote_auto_pipelines.get_run_details()
    #     AbstractTestOBM.run_id = self.trained_pipeline_details['metadata']['id']
    #
    #     status = self.remote_auto_pipelines.get_run_status()
    #     run_details = self.remote_auto_pipelines.get_run_details().get('entity')
    #     self.assertNotIn(status, ['failed', 'canceled'], msg=f"Training finished with status {status}. \n"
    #                                                          f"Details: {run_details.get('status')}")


if __name__ == '__main__':
    unittest.main()
