#   See the NOTICE file distributed with this work for additional information
#   regarding copyright ownership.
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#       http://www.apache.org/licenses/LICENSE-2.0
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import logging

import requests

from ensembl.production.core.rest import RestClient


class EventClient(RestClient):
    """
    Simple client for submitting an event to the event service and checking on progress
    This uses the base RestClient, but all endpoint URIs for checking on submited events
    have process as a path element, so this client combines the job_id and process together
    """
    def __init__(self, uri):
        super(EventClient, self).__init__(uri)

    def submit_job(self, payload):
        """
        Submit a job using the supplied dict as payload. No checking is carried out on the payload
        Arguments:
          payload : job input as dict
        """
        logging.info("Submitting job")
        logging.debug(payload)
        with self._session() as session:
            r = session.post(f'{self.uri}/submit' , json=payload)
        if r.status_code != 201:
            logging.error("failed to submit workflow because: %s", r.text)
        r.raise_for_status()
        return r.json()

    def list_workflows(self, handover_token=None):
        """List all Workflows"""
        logging.info("Listing")
        url = f'{self.uri}/{handover_token}' if handover_token else self.uri
        r = requests.get(self.uri)
        r.raise_for_status()
        return r.json()

    def stop_workflow(self, payload):
        """
        Stop Running Workflow
        Arguments:
          payload : {
                        "handover_token": "3729-jhshs-12929-1mssn",
                        "job_id": "string",
                        "pipeline_name": "string"
                    }
        """        
        logging.info("Stop Workflow")
        logging.debug(payload)
        with self._session() as session:
            r = session.post(f'{self.uri}/stop', json=payload)
        if r.status_code != 201:
            logging.error("failed to stop workflow because: %s", r.text)
        r.raise_for_status()
        return r.json()

    def restart_workflow(self, payload):
        """
        Restart Stopped Workflow
        Arguments:
          payload : {
                        "handover_token": "3729-jhshs-12929-1mssn",
                        "restart_type": "BEEKEEPER"
                    }
        """   
        logging.info("Stop Workflow")
        logging.debug(payload)
        with self._session() as session:
            r = session.post(f'{self.uri}/restart', json=payload)
        if r.status_code != 201:
            logging.error("failed to restart workflow because: %s", r.text)
        r.raise_for_status()
        return r.json() 


