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

logger = FastpathLogger(__name__)

class AzureMachineLearningStudioEngine:

    def setup_scoring_metadata(self, subscription_details):
        self._scoring_url = subscription_details['entity']['deployments'][0]['scoring_endpoint']['url']
        token = subscription_details['entity']['deployments'][0]['scoring_endpoint']['credentials']['token']
        self._headers = subscription_details['entity']['deployments'][0]['scoring_endpoint']['request_headers']
        self._headers['Authorization'] = ('Bearer ' + token)

    def score(self, data):
        body = str.encode(json.dumps(data))
        start_time = time.time()
        response = requests.post(url=self._scoring_url, data=body, headers=self._headers)
        response_time = time.time() - start_time
        if 'error' in str(response.json()):
           logger.log_warning('WARN: Found error in scoring response: {}'.format(str(response.json())))
        result = response.json()
        record = PayloadRecord(request=data, response=result, response_time=int(response_time))
        return record

class AzureMachineLearningServiceEngine:

    def setup_scoring_metadata(self, subscription_details):
        self._scoring_url = subscription_details['entity']['deployments'][0]['scoring_endpoint']['url']
        # token = subscription_details['entity']['deployments'][0]['scoring_endpoint']['credentials']['token']
        # self._headers = subscription_details['entity']['deployments'][0]['scoring_endpoint']['request_headers']
        # self._headers['Authorization'] = ('Bearer ' + token)
        self._headers = subscription_details['entity']['deployments'][0]['scoring_endpoint']['request_headers']

    def score(self, data):
        body = str.encode(json.dumps(data))
        start_time = time.time()
        response = requests.post(url=self._scoring_url, data=body, headers=self._headers)
        response_time = time.time() - start_time
        if 'error' in str(response.json()):
           logger.log_warning('WARN: Found error in scoring response: {}'.format(str(response.json())))
        result = response.json()
        record = PayloadRecord(request=data, response=result, response_time=int(response_time))
        return record
