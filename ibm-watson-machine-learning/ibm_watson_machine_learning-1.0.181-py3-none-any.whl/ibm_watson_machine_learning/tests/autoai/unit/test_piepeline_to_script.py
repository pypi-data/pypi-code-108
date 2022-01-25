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

try:
    from sklearn.externals import joblib
except ImportError:
    import joblib

from ibm_watson_machine_learning.helpers import pipeline_to_script


class TestPipelineToScript(unittest.TestCase):
    model_path = './autoai/artifacts/bank/bank_model_333.pickle'
    pipeline = None

    @classmethod
    def setUp(cls) -> None:
        cls.pipeline = joblib.load(cls.model_path)

    def test_01__create_python_script(self):
        pipeline_to_script(pipeline=self.pipeline)

        script = None
        try:
            with open("pipeline_script.py") as f:
                script = f.read()

        except FileNotFoundError:
            self.assertIsNone(script, msg="pipeline_script.py file not found!")

        print(script)


if __name__ == '__main__':
    unittest.main()
