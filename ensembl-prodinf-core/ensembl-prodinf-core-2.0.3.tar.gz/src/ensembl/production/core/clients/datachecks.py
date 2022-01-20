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

from ensembl.production.core.rest import RestClient
from ensembl.production.core.server_utils import assert_mysql_uri
import re
import json
import logging


class DatacheckClient(RestClient):
    """Client for checking databases using the datacheck service"""

    def submit_job(self, server_url, dbname, species, division, db_type,
                   datacheck_names, datacheck_groups, datacheck_types,
                   email, tag, target_url):
        #FIXME Make signature identical to parent
        """
    Run datachecks on a given server, for one or more species.
    Parameter requirements are complicated, because only the server_url is absolutely required,
    for lots of other parameters you need one from a set, but it doesn't matter which one...
    Arguments:
      server_url - location of server, in URI format
      dbname - name of a database to check
      species - name of a species to check
      division - name of a division to check
      db_type - type of database to check, defaults to 'core'

      datacheck_names - names of datacheck(s) to run, multiple values must be comma-separated
      datacheck_groups - datacheck group(s) to run, multiple values must be comma-separated
      datacheck_types - optional filter on type, 'critical' or 'advisory'

      email - optional address for an email on job completion
      tag - optional text for grouping datacheck submissions
      target_url - optional location of 'ancillary' server, for related databases
    """
        assert_mysql_uri(server_url)

        payload = {
            'server_url': server_url,
            'dbname': dbname,
            'species': species,
            'division': division,
            'db_type': db_type,
            'datacheck_names': [],
            'datacheck_groups': [],
            'datacheck_types': [],
            'email': email,
            'tag': tag,
        }

        if target_url is not None:
            payload['target_url'] = target_url
        if datacheck_names is not None:
            payload['datacheck_names'] = datacheck_names.split(',')
        if datacheck_groups is not None:
            payload['datacheck_groups'] = datacheck_groups.split(',')
        if datacheck_types is not None:
            payload['datacheck_types'] = datacheck_types.split(',')

        return RestClient.submit_job(self, payload)

    def list_jobs(self, output_file, pattern, failure_only=False):
        """
    Find jobs and print results
    Arguments:
      output_file - optional file to write report
      pattern - optional pattern to filter jobs by
      failure_only - only report failed jobs
    """
        jobs = super(DatacheckClient, self).list_jobs()
        if pattern is None:
            pattern = '.*'
        tag_pattern = re.compile(pattern)
        output = []
        for job in jobs:
            if 'tag' in job['input']:
                tag = job['input']['tag']
            else:
                tag = ''
            if tag_pattern.search(tag):
                if 'output' in job:
                    if failure_only is True:
                        if job['output']['failed_total'] > 0:
                            output.append(job)
                    else:
                        output.append(job)
                else:
                    output.append(job)

        if output_file is None:
            print(json.dumps(output, indent=2))
        else:
            output_file.write(json.dumps(output))

    def print_job(self, job, print_results=False, print_input=False):
        """
    Render a job to logging
    Arguments:
      job :  job to print
      print_results : set to True to print detailed results
      print_input : set to True to print input for job
    """
        logging.info("Job %s - %s" % (job['id'], job['status']))
        if print_input is True:
            self.print_inputs(job['input'])
        if job['status'] == 'complete':
            if print_results is True:
                logging.info("Submission status: " + str(job['status']))
                logging.info("Database passed: " + str(job['output']['passed_total']))
                logging.info("Database failed: " + str(job['output']['failed_total']))
                logging.info("Output directory: " + str(job['output']['output_dir']))
                logging.info("Per database results: ")
                logging.info(json.dumps(job['output']['databases'], indent=2))
        elif job['status'] == 'incomplete':
            if print_results is True:
                logging.info("Submission status: " + str(job['status']))
        elif job['status'] == 'failed':
            logging.info("Submission status: " + str(job['status']))
            # failures = self.retrieve_job_failure(job['id'])
            # logging.info("Error: " + str(failures))
        else:
            raise ValueError("Unknown status {}".format(job['status']))

    def print_inputs(self, i):
        """Utility to render a job input dict to logging"""
        logging.info("Registry file: " + i['registry_file'])
        if 'dbname' in i:
            for dbname in i['dbname']:
                logging.info("Database name: " + dbname)
        if 'species' in i:
            for species in i['species']:
                logging.info("Species name: " + species)
        if 'division' in i:
            for division in i['division']:
                logging.info("Division name: " + division)
        if 'db_type' in i:
            logging.info("Database type: " + i['db_type'])
        if 'datacheck_names' in i:
            for name in i['datacheck_names']:
                logging.info("Datacheck: " + name)
        if 'datacheck_groups' in i:
            for group in i['datacheck_groups']:
                logging.info("Datacheck group: " + group)
        if 'datacheck_types' in i:
            for datacheck_type in i['datacheck_types']:
                logging.info("Datacheck type: " + datacheck_type)
        if 'email' in i:
            logging.info("Email: " + i['email'])
        if 'tag' in i:
            logging.info("Tag: " + i['tag'])
