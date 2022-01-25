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

import logging
from ibm_watson_machine_learning.tests.Cloud.preparation_and_cleaning import *

class TestHwSpec(unittest.TestCase):

    logger = logging.getLogger(__name__)

    @classmethod
    def setUpClass(self):
        TestHwSpec.logger.info("Service Instance: setting up credentials")

        self.wml_credentials = get_wml_credentials()
        self.client = get_client()

    def test_01_list_hw_specs(self):

        hw_spec_details1 = self.client.hardware_specifications.list()
        print(hw_spec_details1)

        hw_spec_details2 = self.client.hardware_specifications.list(name='V100x2')
        print(hw_spec_details2)

    def test_02_get_details(self):

        hw_spec_id = self.client.hardware_specifications.get_uid_by_name('V100x2')

        details = self.client.hardware_specifications.get_details(hw_spec_id)
        print(details)
        self.assertTrue("V100x2" in str(details))

if __name__ == '__main__':
    unittest.main()
