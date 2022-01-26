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

class EmailReportingAPI(object):

    def __init__(self, host, api_key, verify_ssl=True, timeout=30, user_agent=None, cert=None, debug=False):
        """
        Initialize a ThreadFix Pro Email Reporting API instance.
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

    def list_scheduled_email_reports(self):
        """
        Retrives all scheduled email reports
        """
        return self._request('GET', 'rest/scheduledEmailReport/list')

    def create_scheduled_email_report(self, team_id, severity, frequency, day, hour, minute, period, cron_expression, scheduling_method=None):
        """
        Creates a new scheduled email report
        :param team_id: The ID for the team to attach to the report
        :param severity: The name of the severity for the report's severity threshold
        :param frequency: Must be "Weekly" or "Daily" Determines if the schedule will be everyday or only on a specified day of the week. "SELECT" method requires this
        :param day: Only used if it is on Weekly frequency. The day on which the report will execute. "SELECT" method requires this
        :param hour: The hour 1-12 for the time the report will execute. "SELECT" method requires this
        :param minute: 0, 15, 30, 45 - The minute the report will execute. "SELECT" method requires this
        :param period: "AM" or "PM" for the time the report will execute. "SELECT" method requires this
        :param cron_expression: Only if using "CRON" scheduling method. Cron expression for when it will execure
        :param scheduling_method: "CRON" or "SELECT", but will default to "SELECT"
        """
        params = {'teamIds' : team_id, 'severity' : severity, 'frequency' : frequency, 'day' : day, 'hour' : hour, 'minute' : minute, 'period' : period, 'cronExpression' : cron_expression}
        if scheduling_method:
            params['schedulingMethod'] = scheduling_method
        return self._request('POST', 'rest/scheduledEmailReport/add', params)

    def create_scheduled_email_report(self, scheduled_email_report_id, team_id, severity, frequency, day, hour, minute, period, cron_expression, scheduling_method=None):
        """
        Creates a new scheduled email report
        :param scheduled_email_report_id: Scheduled Email Report identifier
        :param team_id: The ID for the team to attach to the report
        :param severity: The name of the severity for the report's severity threshold
        :param frequency: Must be "Weekly" or "Daily" Determines if the schedule will be everyday or only on a specified day of the week. "SELECT" method requires this
        :param day: Only used if it is on Weekly frequency. The day on which the report will execute. "SELECT" method requires this
        :param hour: The hour 1-12 for the time the report will execute. "SELECT" method requires this
        :param minute: 0, 15, 30, 45 - The minute the report will execute. "SELECT" method requires this
        :param period: "AM" or "PM" for the time the report will execute. "SELECT" method requires this
        :param cron_expression: Only if using "CRON" scheduling method. Cron expression for when it will execure
        :param scheduling_method: "CRON" or "SELECT", but will default to "SELECT"
        """
        params = {'teamIds' : team_id, 'severity' : severity, 'frequency' : frequency, 'day' : day, 'hour' : hour, 'minute' : minute, 'period' : period, 'cronExpression' : cron_expression}
        if scheduling_method:
            params['schedulingMethod'] = scheduling_method
        return self._request('PUT', 'rest/scheduledEmailReport/' + str(scheduled_email_report_id) + '/edit', params)

    def delete_scheduled_email_report(self, scheduled_email_report_id):
        """
        Deletes a scheduled email report
        :param scheduled_email_report_id: Scheduled Email Report identifier
        """
        return self._request('DELETE', 'rest/scheduledEmailReport/' + str(scheduled_email_report_id))

    def set_emails_for_scheduled_email_report(self, scheduled_email_report_id, emails=None):
        """
        Sets the emails attached to an existing scheduled email report
        :param scheduled_email_report_id: Scheduled Email Report identifier
        :param emails: 	The emails to attach to the Schedule Email Report.  See the example for how to attach multiple.  
                        To remove all emails from a report, make this call without providing any 'emails' parameters.
        """
        params = {}
        if emails:
            params['emails'] = emails
        return self._request('PUT', 'rest/scheduledEmailReport/' + str(scheduled_email_report_id) + '/emails', params)

    def add_email_list_to_scheduled_email_report(self, scheduled_email_report_id, email_list_id):
        """
        Attaches an email list to a scheduled email report
        :param scheduled_email_report_id: Scheduled Email Report identifier
        :param email_list_id: Email List identifier
        """
        return self._request('POST', 'rest/scheduledEmailReport/' + str(scheduled_email_report_id) + '/emailList/' + str(email_list_id))

    def remove_email_list_to_scheduled_email_report(self, scheduled_email_report_id, email_list_id):
        """
        Removes an email list to a scheduled email report
        :param scheduled_email_report_id: Scheduled Email Report identifier
        :param email_list_id: Email List identifier
        """
        return self._request('DELETE', 'rest/scheduledEmailReport/' + str(scheduled_email_report_id) + '/emailList/' + str(email_list_id))

    def list_email_lists(self):
        """
        Retrieves all email lists
        """
        return self._request('GET', 'rest/emailList/list')

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