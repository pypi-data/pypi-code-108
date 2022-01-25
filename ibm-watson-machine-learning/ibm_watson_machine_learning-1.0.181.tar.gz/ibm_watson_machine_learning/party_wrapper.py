#!/usr/bin/env python3

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
import sys
import importlib.util

import ibm_watson_machine_learning._wrappers.requests as requests
import json
import logging
from ibm_watson_machine_learning.wml_resource import WMLResource
from ibm_watson_machine_learning.wml_client_error import WMLClientError

logger = logging.getLogger(__name__)

def process_heartbeat(client, **kwargs):
    try:
        config_dict = kwargs.get('config_dict')
        agg_info = config_dict.get('aggregator')
        if client:
            wml_services_url = agg_info['ip']
        else:
            wml_services_url = agg_info['ip'].split('/')[0]

        hearbeat_resp = requests.get("https://" + wml_services_url + "/wml_services/training/heartbeat")
        hearbeat_resp_json = json.loads(hearbeat_resp.content.decode("utf-8"))
        service_version = hearbeat_resp_json.get("service_implementation")

        if service_version.startswith("4.0"):
            version_details = service_version.split('-')
            if version_details[1] >= "202110":
                return "general"
            elif version_details[1] >= "202108":
                return "cpd402"
            else:
                return "cpd401"
        if service_version.startswith("35"):
            return "cpd35"

        return "general"

    except Exception as ex:
        logger.info("unable to process heartbeat")
        logger.exception(ex)
        return "general"


def import_source(module_file_path):
    module_name = 'ibmfl'

    module_spec = importlib.util.spec_from_file_location(
        module_name, module_file_path)
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_name] = module
    module_spec.loader.exec_module(module)


fl_path = os.path.abspath('.')
if fl_path not in sys.path:
    sys.path.append(fl_path)


class Party(WMLResource):
    """
    Party Wrapper for determining required version of FL Party to invoke.
    """

    SUPPORTED_PLATFORMS_MAP = {
        'general': "/cloud/ibmfl/__init__.py",
        'cpd35': "/cpd35/ibmfl/__init__.py",
        'cpd401': "1.0.122",
        'cpd402': "1.0.165"
    }

    def __init__(self, client=None, **kwargs):

        libs_module = sys.modules['ibm_watson_machine_learning.libs']
        libs_location_list = libs_module.__path__

        # base location string, default to cloud location
        ibmfl_module_location = libs_location_list[0] + '/ibmfl'

        # get arg for platform
        calculated_platform_env = process_heartbeat(client=client, **kwargs)
        platform_env = kwargs.get('env', calculated_platform_env)
        # process location
        ibmfl_module_location = ibmfl_module_location + self.SUPPORTED_PLATFORMS_MAP.get(platform_env)
        if not ibmfl_module_location.endswith(".py"):
        	print("Please use ibm-watson-machine-learning " + self.SUPPORTED_PLATFORMS_MAP.get(platform_env) )
        	exit()

        self.module_location = ibmfl_module_location
        self.args = kwargs
        self.Party = None
        self.connection = None
        self.log_level = None
        self.metrics_output = None

        if 'ibmfl' in sys.modules:
            del sys.modules['ibmfl']
        if 'ibmfl.party' in sys.modules:
            del sys.modules['ibmfl.party']
        if 'ibmfl.party.party' in sys.modules:
            del sys.modules['ibmfl.party.party']
        if client:
            WMLResource.__init__(self, __name__, client)
            self._client = client
            self.auth_token = "Bearer " + self._client.wml_token
            self.project_id = self._client.project_id
            self.log_level = kwargs.get("log_level", "ERROR")
        else:
            self.log_level = kwargs.get("log_level", "INFO")
            import_source(self.module_location)
            from ibmfl.party.party import Party
            self.Party = Party(**self.args)
            self.connection = self.Party.connection

    def start(self):
        self.Party.start()

    def run(self, aggregator_id, asynchronous=True, verify=True):
        """
        Run the party with the specified aggregator_id

        **Parameters**

        .. important::
           #. **aggregator_id**:  aggregator identifier\n
              **type**: str\n
           #. **asynchronous**:\n
              * True  - party starts to run the job in the background and progress can be checked later.\n
              * False - method will wait until training is complete and then print the job status.\n
              **type**: bool\n
           #. **verify**:  verify certificate\n
              **type**: bool\n

        **Output**

        **Example**
         >>> party.run( aggregator_id , asynchronous = True, verify = True )

        """
        import_source(self.module_location)
        from ibmfl.party.party import Party

        config_dict = self.args.get('config_dict')
        metrics_config = {
            "name": "WMLMetricsRecorder",
            "path": "ibmfl.party.metrics.metrics_recorder",
            "output_file": self.metrics_output,
            "output_type": "json",
            'compute_pre_train_eval': False,
            'compute_post_train_eval': False
        }
        if 'metrics_recorder' not in config_dict:
            config_dict["metrics_recorder"] = metrics_config
        agg_info = config_dict.get('aggregator').get('ip') + "/ml/v4/trainings/" + aggregator_id
        config_dict['aggregator']['ip'] = agg_info
        self.args['config_dict'] = config_dict

        #check for aggregator state and start job
        import time
        from ibmfl.exceptions import FLException
        try:
            training_status = self._client.training.get_status(aggregator_id)
            state = training_status['state']
            if state == "pending":
                while state == "pending":
                    logger.info("Waiting for aggregator accepting parties state..")
                    training_status = self._client.training.get_status(aggregator_id)
                    state = training_status['state']
                    time.sleep(10)
                if state != "accepting_parties":
                    raise FLException("The current state of training is %s, so the party is not able to start a job." % state)
                self.Party = Party(**self.args, token=self.auth_token, self_signed_cert=not verify, log_level=self.log_level)
                self.connection = self.Party.connection
                self.start()
            elif state == "running" or state == "accepting_parties":
                self.Party = Party(**self.args, token=self.auth_token, self_signed_cert=not verify, log_level=self.log_level)
                self.connection = self.Party.connection
                self.start()
            else:
                raise FLException("The current state of training is %s, so the party is not able to start a job." % state)

            #wait for the job to finish if synchrounous
            if not asynchronous:
                while "completed" != state and "failed" != state and "canceled" != state and self.is_running():
                    training_status = self._client.training.get_status(aggregator_id)
                    state = training_status['state']
                    time.sleep(10)
                logger.info("The training finishes with %s status" % state)
        except FLException as ex:
            raise FLException(str(ex))
        except Exception as ex:
            logger.info("The party failed to start training")
            logger.exception(ex)

    def monitor_logs(self, log_level="INFO"):
        """
        This method should be called prior to the run() method to
        enable the logs of the training job in the standard output

        **Parameters**

        .. important::
           #. **log_level**:  log level specified by user\n
              **type**: str\n

        **Output**

        .. important::
            **returns**: This method only outputs the logs to stdout\n
            **return type**: None\n

        **Example**
         >>> party.monitor_logs()

        """
        self.log_level = log_level

    def monitor_metrics(self, metrics_file="-"):
        """
        Enable the metrics of the training job in the standard output

        **Parameters**

        .. important::
           #. **metrics_file**:  a filename specified by user for metrics output\n
              **type**: str\n

        **Output**

        .. important::
            **returns**: This method outputs the metrics to stdout if a filename is not specified\n
            **return type**: None\n

        **Example**
         >>> party.monitor_metrics()

        """
        self.metrics_output = metrics_file

    def is_running(self):
        """
        Check if the training job is running

        **Output**

        .. important::
             **returns**: If the job is running\n
             **return type**: bool\n

        **Example**
         >>> party.is_running()

        """
        return not self.connection.stopped

    def get_round(self):  

        """
        Get the current round number

        **Output**

        .. important::
             **returns**: The current round number\n
             **return type**: int\n

        **Example**
         >>> party.get_round()

        """
        return self.Party.proto_handler.metrics_recorder.get_round_no()

    def cancel(self):
        """
        Stop the local connection to the training on the party side

        **Example**
         >>> party.cancel()

        """
        self.Party.stop_connection()
