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

import pandas as pd
from ibm_watson_machine_learning.experiment import AutoAI
from ibm_watson_machine_learning.helpers.connections import DataConnection, DatabaseLocation
from ibm_watson_machine_learning.tests.autoai.abstract_tests_classes.abstract_test_iris_wml_autoai_multiclass_connections import (
    AbstractTestAutoAIRemote)
from ibm_watson_machine_learning.tests.utils import get_db_credentials
from ibm_watson_machine_learning.utils.autoai.errors import WMLClientError


class AbstractTestAutoAIDatabaseConnection(AbstractTestAutoAIRemote, abc.ABC):
    """
    The test can be run on CLOUD, and CPD
    The test covers:
    - DataBase connection set-up.
    - Saving data to a database.
    - downloading training data using created connection.
    - downloading all generated pipelines to lale pipeline.
    - deployment with lale pipeline.
    - deployment deletion.
    Connection used in test:
    - input: Connection to database.
    """
    database_name = "db_name"
    schema_name = "tests_sdk"
    table_name = "iris"

    def test_00c_prepare_connection_to_DATABASE(self):
        AbstractTestAutoAIDatabaseConnection.db_credentials = get_db_credentials(self.database_name)
        connection_details = self.wml_client.connections.create({
            'datasource_type': self.wml_client.connections.get_datasource_type_uid_by_name(self.database_name),
            'name': 'Connection to DB for python API tests',
            'properties': self.db_credentials
        })

        AbstractTestAutoAIDatabaseConnection.connection_id = self.wml_client.connections.get_uid(connection_details)
        self.assertIsInstance(self.connection_id, str)

    def test_01_initialize_AutoAI_experiment__pass_credentials__object_initialized(self):
        AbstractTestAutoAIDatabaseConnection.experiment = AutoAI(wml_credentials=self.wml_credentials.copy(),
                                                                 project_id=self.project_id,
                                                                 space_id=self.space_id)

        self.assertIsInstance(self.experiment, AutoAI, msg="Experiment is not of type AutoAI.")

    def test_02_DataConnection_setup(self):
        AbstractTestAutoAIDatabaseConnection.data_connection = DataConnection(
            connection_asset_id=self.connection_id,
            location=DatabaseLocation(
                schema_name=self.schema_name,
                table_name=self.table_name
            )
        )
        AbstractTestAutoAIDatabaseConnection.results_connection = None

        self.assertIsNotNone(obj=AbstractTestAutoAIDatabaseConnection.data_connection)

        self.data_connection._wml_client = self.wml_client
        self.data_connection.write(pd.read_csv(self.data_location))

    def test_02a_read_saved_remote_data_before_fit(self):
        AbstractTestAutoAIDatabaseConnection.data = self.data_connection.read()
        print("Data sample:")
        print(self.data.head())
        self.assertGreater(len(self.data), 0)

    def test_29_delete_connection_and_connected_data_asset(self):
        self.wml_client.connections.delete(self.connection_id)

        with self.assertRaises(WMLClientError):
            self.wml_client.connections.get_details(self.connection_id)
