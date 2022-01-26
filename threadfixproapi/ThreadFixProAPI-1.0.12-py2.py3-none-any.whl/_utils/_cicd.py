#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Evan Schlesinger"
__copyright__ = "(C) 2019 Denim group"
__contributors__ = ["Evan Schlesinger"]
__status__ = "Production"
__license__ = "MIT"

import requests
import urllib3
import requests.exceptions
import requests.packages.urllib3

from ._utilities import ThreadFixProResponse

class CICDAPI(object):

    def __init__(self, host, api_key, verify_ssl=True, timeout=30, user_agent=None, cert=None, debug=False):
        """
        Initialize a ThreadFix Pro CI/CD API instance.
        :param host: The URL for the ThreadFix Pro server. (e.g., http://localhost:8080/threadfix/) NOTE: must include http:// TODO: make it so that it is required or implicitly added if forgotten
        :param api_key: The API key generated on the ThreadFix Pro API Key page.
        :param verify_ssl: Specify if API requests will verify the host's SSL certificate, defaults to true.
        :param timeout: HTTP timeout in seconds, default is 30.
        :param user_agent: HTTP user agent string, default is "threadfix_pro_api/[version]".
        :param cert: You can also specify a local cert to use as client side certificate, as a single file (containing
        the private key and the certificate) or as a tuple of both file’s path
        :param debug: Prints requests and responses, useful for debugging.
        """

        self.host = host
        self.api_key = api_key
        self.verify_ssl = verify_ssl
        self.timeout = timeout

        if not user_agent:
            self.user_agent = 'threadfix_pro_api/2.7.5' 
        else:
            self.user_agent = user_agent

        self.cert = cert
        self.debug = debug  # Prints request and response information.

        if not self.verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) # Disabling SSL warning messages if verification is disabled.

    def create_cicd_pass_criteria(self, severity, max_allowed=None, max_introduced=None):
        """
        Creates a new CI/CD pass criteria
        :param severity: Name of severity
        :param max_allowed: The maximum number of vulnerabilities allowed for the Pass Criteria.  If no value is specified there is no limit.
        :param max_introduced: The maximum number of new vulnerabilities in a scan for the Pass Criteria.  If no value is specified there is no limit.
        """
        params = {'severity' : severity}
        if max_allowed:
            params['maxAllowed'] = max_allowed
        if max_introduced:
            params['maxIntroduced'] = max_introduced
        return self._request('POST', 'rest/cicd/passCriteria/create', params)

    def update_ci_cd_pass_criteria(self, cicd_id, severity, max_allowed=None, max_introduced=None):
        """
        Update CI/CD pass criteria
        :param cicd_id: CI/CD identifier
        :param severity: Name of severity
        :param max_allowed: The maximum number of vulnerabilities allowed for the Pass Criteria.  If no value is specified there is no limit.
        :param max_introduced: The maximum number of new vulnerabilities in a scan for the Pass Criteria.  If no value is specified there is no limit.
        """
        params = {'severity' : severity}
        if max_allowed:
            params['maxAllowed'] = max_allowed
        if max_introduced:
            params['maxIntroduced'] = max_introduced
        return self._request('POST', 'rest/cicd/passCriteria/' + str(cicd_id) + '/update', params)

    def list_cicd_pass_criteria(self):
        """
        Lists CI/CD pass criteria
        """
        return self._request('GET', 'rest/cicd/passCriteria')

    def get_cicd_pass_criteria_details(self, cicd_id):
        """
        Returns detailed information about the specified CI/CD pass criteria
        :param cicd_id: CI/CD identifier
        """
        return self._request('GET', 'rest/cicd/passCriteria/' + str(cicd_id) + '/detail')

    def delete_cicd_pass_criteria(self, cicd_id):
        """
        Deletes the specified CI/CD pass criteria
        :param cicd_id: CI/CD identifier
        """
        return self._request('DELETE', 'rest/cicd/passCriteria/' + str(cicd_id) + '/delete')

    def add_application_to_cicd_pass_criteria(self, pass_criteria_id, application_id):
        """
        Attaches the specified application to the specified pass criteria
        :param pass_criteria_id: Pass Criteria identifier
        :param application_id: Application identifier
        """
        return self._request('PUT', 'rest/cicd/passCriteria/' + str(pass_criteria_id) + '/addApplication/' + str(application_id))

    def remove_application_from_cicd_pass_criteria(self, pass_criteria_id, application_id):
        """
        Removes the specified application to the specified pass criteria
        :param pass_criteria_id: Pass Criteria identifier
        :param application_id: Application identifier
        """
        return self._request('DELETE', 'rest/cicd/passCriteria/' + str(pass_criteria_id) + '/removeApplication/' + str(application_id))

    def evaluate_cicd_pass_criteria(self, application_id, from_date=None, to_date=None):
        """
        Checks the specified application against all of the CI/CD pass criteria attached to it
        :param application_id: Application identifier
        :param from_date: Evaluate against any new open vulnerabilities from this date.  If no date is specified, the start date will be December 31, 1969.  
                        The time will be the start of day, 00:00:00. Format as yyyy-MM-dd
        :param to_date: Evaluate against any new open vulnerabilities until this date.  If no start date is specified, the end date will be the current date.  
                        The time will be the end of day, 23:59:59. Format as yyyy-MM-dd
        """
        params = {}
        if from_date:
            params['fromDate'] = from_date
        if to_date:
            parms['toDate'] = to_date
        return self._request('GET', 'rest/policy/status/application/' + str(application_id) + '/evaluate', params)

    def create_cicd_defect_reporter(self, severity, minimum=None, group_by=None):
        """
        Creates a new CI/CD defect reporter
        :param severity: Name of severity
        :param minimum: If true, includes all severities greater than the specified one as well.  Default value is false.  
        :param group_by: How to group vulnerabilities for defects
        """
        params = {'severity' : severity}
        if minimum:
            params['minimum'] = minimum
        if group_by:
            params['groupBy'] = group_by
        return self._request('POST', 'rest/cicd/defectReporting/create', params)

    def update_cicd_defect_reporter(self, cicd_id, severity, minimum=None, group_by=None):
        """
        Creates a new CI/CD defect reporter
        :param cicd_id: CI/CD identifier
        :param severity: Name of severity
        :param minimum: If true, includes all severities greater than the specified one as well.  Default value is false.  
        :param group_by: How to group vulnerabilities for defects
        """
        params = {'severity' : severity}
        if minimum:
            params['minimum'] = minimum
        if group_by:
            params['groupBy'] = group_by
        return self._request('PUT', 'rest/cicd/defectReporting/' + str(cicd_id) + '/update', params)

    def list_cicd_defect_reporters(self):
        """
        Lists CI/CD defect reporters
        """
        return self._request('GET', 'rest/cicd/defectReporting')

    def get_cicd_defect_reporter_details(self, cicd_id):
        """
        Returns CI/CD defect reporter details
        :param cicd_id: CI/CD identifier
        """
        return self._request('GET', 'rest/cicd/defectReporting/' + str(cicd_id) + '/detail')

    def delete_cicd_defect_reporter(self, cicd_id):
        """
        Deletes the CI/CD defect reporter
        :param cicd_id: CI/CD identifier
        """
        return self._request('DELETE', 'rest/cicd/defectReporting/' + str(cicd_id) + '/delete')

    def add_application_defect_tracker_to_cicd_defect_reporter(self, defect_reporter_id, app_defect_tracker_id):
        """
        Attaches the specified Application Defect Tracker to the specified CI/CD Defect Reporter
        :param defect_reporter_id: Defect Reporter identifier
        :param app_defect_tracker_id: App Defect Tracker identifier
        """
        return self._request('PUT', 'rest/cicd/defectReporting/' + str(defect_reporter_id) + '/addApplicationDefectTracker/' + str(app_defect_tracker_id))

    def remove_application_defect_tracker_to_cicd_defect_reporter(self, defect_reporter_id, app_defect_tracker_id):
        """
        Attaches the specified Application Defect Tracker to the specified CI/CD Defect Reporter
        :param defect_reporter_id: Defect Reporter identifier
        :param app_defect_tracker_id: App Defect Tracker identifier
        """
        return self._request('PUT', 'rest/cicd/defectReporting/' + str(defect_reporter_id) + '/removeApplicationDefectTracker/' + str(app_defect_tracker_id))
    
    # Utility

    def _request(self, method, url, params=None, files=None):
        """Common handler for all HTTP requests."""
        if not params:
            params = {}

        headers = {
            'Accept': 'application/json',
            'Authorization': 'APIKEY ' + self.api_key
        }

        try:
            if self.debug:
                print(method + ' ' + self.host + url)
                print(params)

            response = requests.request(method=method, url=self.host + url, params=params, files=files, headers=headers,
                                        timeout=self.timeout, verify=self.verify_ssl, cert=self.cert)

            if self.debug:
                print(response.status_code)
                print(response.text)

            try:
                json_response = response.json()

                message = json_response['message']
                success = json_response['success']
                response_code = json_response['responseCode']
                data = json_response['object']

                return ThreadFixProResponse(message=message, success=success, response_code=response_code, data=data)
            except ValueError:
                return ThreadFixProResponse(message='JSON response could not be decoded.', success=False)
        except requests.exceptions.SSLError:
            return ThreadFixProResponse(message='An SSL error occurred.', success=False)
        except requests.exceptions.ConnectionError:
            return ThreadFixProResponse(message='A connection error occurred.', success=False)
        except requests.exceptions.Timeout:
            return ThreadFixProResponse(message='The request timed out after ' + str(self.timeout) + ' seconds.',
                                     success=False)
        except requests.exceptions.RequestException:
            return ThreadFixProResponse(message='There was an error while handling the request.', success=False)