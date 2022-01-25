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
import unittest

from ibm_watson_machine_learning.tests.base.abstract.abstract_deep_learning_test import \
    AbstractDeepLearningTest


class TestTensorflowTraining(AbstractDeepLearningTest, unittest.TestCase):
    """
    Test case checking the scenario of training an tensorflow model
    using model_definition only.
    """

    model_definition_name = "tensorflow_model_definition"
    training_name = "test_tensorflow_training"
    training_description = "TF-test-experiment"
    software_specification_name = "tensorflow_2.4-py3.8"
    execution_command = "python3 mnist_mlp.py"

    data_location = os.path.join(os.getcwd(), "base", "datasets", "tensorflow", "mnist.npz")
    data_cos_path = "mnist.npz"
    model_paths = [
        os.path.join(os.getcwd(), "base", "artifacts", "tensorflow", "tf-model-definition.zip")
    ]
    model_definition_ids = []
