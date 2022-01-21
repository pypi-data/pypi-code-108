# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2021
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

# coding=utf-8
from ibm_ai_openscale_cli.utility_classes.fastpath_logger import FastpathLogger
import json
import time
import requests
from ibm_watson_openscale.supporting_classes.payload_record import PayloadRecord
from requests.auth import HTTPBasicAuth

logger = FastpathLogger(__name__)

class CustomMachineLearningEngine:

    def __init__(self, credentials):
        self._credentials = credentials
        self._auth = None
        if 'username' in self._credentials and 'password' in self._credentials:
            self._auth = HTTPBasicAuth(username=self._credentials['username'], password=self._credentials['password'] ) #pragma: allowlist secret

    def setup_scoring_metadata(self, subscription_details):
        self._scoring_url = subscription_details['entity']['deployments'][0]['scoring_endpoint']['url']

    def score(self, data):
        body = str.encode(json.dumps(data))
        headers = {'Content-Type': 'application/json'}
        start_time = time.time()
        response = requests.post(url=self._scoring_url, data=body, headers=headers, auth=self._auth)
        response_time = time.time() - start_time
        if 'error' in str(response.json()):
           logger.log_warning('WARN: Found error in scoring response: {}'.format(str(response.json())))
        record = PayloadRecord(request=data, response=response.json(), response_time=int(response_time))
        return record
