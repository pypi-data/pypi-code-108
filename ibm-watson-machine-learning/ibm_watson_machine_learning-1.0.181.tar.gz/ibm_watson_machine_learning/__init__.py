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

pkg_name = "ibm-watson-machine-learning"

try:
    from importlib.metadata import version
    version = version(pkg_name)

except (ModuleNotFoundError, AttributeError):
    from importlib_metadata import version as imp_lib_ver
    version = imp_lib_ver(pkg_name)

from ibm_watson_machine_learning.client import APIClient
APIClient.version = version

from .utils import is_python_2
if is_python_2():
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Python 2 is not officially supported.")