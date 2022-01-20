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
import re
from datetime import datetime

import requests
from sqlalchemy.engine import make_url

from ensembl.production.core.server_utils import assert_http_uri, assert_mysql_db_uri, assert_email


class HandoverClient(object):
    """
    Client for submitting databases for handover
    """

    handovers = '{}jobs'
    handover_token = '{}jobs/{}'

    def __init__(self, uri):
        assert_http_uri(uri)
        self.uri = uri

    def submit_handover(self, spec):
        """
        Arguments:
          spec : dict containing keys `src_uri`, `comment` and `contact`
        #TODO move this onto submit_job standard from parent class
        """
        assert_mysql_db_uri(spec['src_uri'])
        assert_email(spec['contact'])
        logging.info("Submitting {} for handover".format(spec['src_uri']))
        logging.debug(spec)
        r = requests.post(self.handovers.format(self.uri), json=spec)
        r.raise_for_status()
        return r.json()

    def list_handovers(self):
        """
        Retrieve full list of handover databases
        """
        logging.info("Listing from %s", self.handovers.format(self.uri))
        r = requests.get(self.handovers.format(self.uri))
        r.raise_for_status()
        return r.json()

    def print_handover_detail(self, handover):
        """
        Print out details of a handover
        Arguments:
          handover : Handover dict
        """
        handover_api_link = self.handover_token.format(self.uri, str(handover['handover_token']))
        report_time = datetime.strptime(handover['report_time'], "%Y-%m-%dT%H:%M:%S.%f")
        if 'current_message' in handover:
            logging.info("Handover %s (%s) submitted by (%s) - %s on %s" % (
                handover_api_link, handover['src_uri'], handover['contact'], handover['current_message'],
                report_time.strftime('%d-%m-%Y %H:%M')))
        elif 'message' in handover:
            logging.info("Handover %s (%s) submitted by (%s) - %s on %s." % (
                handover_api_link, handover['src_uri'], handover['contact'], handover['message'],
                report_time.strftime('%d-%m-%Y %H:%M'), ))

    def retrieve_handover(self, handover_token):
        """
        Retrieve a handover using an handover_token
        Arguments:
          handover_token: handover token, e.g: 56bf1f7e-ebdf-11e8-8afa-005056ab4d6f
        """
        logging.info("Retrieving details for handover " + str(handover_token))
        r = requests.get(self.handover_token.format(self.uri, str(handover_token)))
        r.raise_for_status()
        return r.json()

    def handover_summary_email(self, handovers, email):
        """
        Retrieve all the handovers associated with a given email
        Generate a unique list of handed over databases
        If a database was handed over multiple times, the latest one will be displayed.
        Print everything
        """
        fail_pattern = re.compile(".*(failed|problems).*")
        successful_pattern = re.compile(".*successful.*")
        summary = {}
        logging.info("Retrieving handovers for %s", str(email) )
        for handover in handovers:
            if handover['contact'] == email:
                src_uri = make_url(handover['src_uri'])
                if src_uri.database not in summary:
                    summary[src_uri.database] = handover
        for sum in summary:
            handover_result = "in progress"
            if fail_pattern.match(summary[sum]['current_message']):
                handover_result = "failed"
            elif successful_pattern.match(summary[sum]['current_message']):
                handover_result = "success"
            logging.info("Handover %s - %s : %s" % (summary[sum]['handover_token'], sum, handover_result))
