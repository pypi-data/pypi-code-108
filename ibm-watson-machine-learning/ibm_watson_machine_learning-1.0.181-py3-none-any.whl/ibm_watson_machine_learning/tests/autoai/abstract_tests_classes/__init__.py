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

from .abstract_autoai_test import AbstractTestAutoAIAsync, AbstractTestAutoAISync
from .abstract_deployment_webservice import AbstractTestWebservice
from .abstract_deployment_batch import AbstractTestBatch
from .abstract_test_iris_wml_autoai_multiclass_connections import AbstractTestAutoAIRemote
from .abstract_test_iris_using_database_connection import AbstractTestAutoAIDatabaseConnection
from .abstract_test_iris_using_database_data_asset import AbstractTestAutoAIConnectedAsset
from .abstract_obm_autoai_test import AbstractTestOBM
from .abstract_timeseries_test import AbstractTestTSAsync
