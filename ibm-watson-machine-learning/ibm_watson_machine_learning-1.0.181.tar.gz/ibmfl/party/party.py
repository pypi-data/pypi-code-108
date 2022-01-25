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


import logging

logger = logging.getLogger(__name__)

class Party:

    def __init__(self, **kwargs):
        logger.warning("The module ibmfl will be deprecated and become part of the Python client. Please use the latest Python client to access the party package.")
        from ibm_watson_machine_learning.party_wrapper import Party
        self.party = Party(**kwargs)
        self.connection = self.party.connection

    def start(self):
        self.party.start()

