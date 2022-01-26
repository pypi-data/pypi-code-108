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

class TasksAPI(object):

    def __init__(self, host, api_key, verify_ssl=True, timeout=30, user_agent=None, cert=None, debug=False):
        """
        Initialize a ThreadFix Pro Tasks API instance.
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

    def queue_scan(self, application_id, scanner_name, target_url = None, scan_config_id = None):
        """
        Queues up a scan with a given scanner for an application.
        Allows caller to optionally override a default application URL and to specify a specific scan configuration file.
        :param application_id Application identifier.
        :param scanner_name Name of the scanner to run
        :param target_url Alternate URL to scan versus the application's default URL
        :param scan_config_id Identifier of file stored in ThreadFix that contains the scanner configuration to use
        """
        params = {"applicationId": application_id, "scannerType": scanner_name}
        if target_url:
            params['targetURL'] = target_url
        if scan_config_id:
            params['scanConfigId'] = scan_config_id
        return self._request('POST', 'rest/tasks/queueScan', params)

    def set_task_config(self, application_id, scanner_type, file_path):
        """
        Uploads a Scan Agent configuration file to an application that will be used by default for tasks with the relevant scanner.
        :param application_id: The id for the app to upload the file to
        :param scanner_type: The scanner the file will be used as a base for
        :param file: The file to upload
        """
        params = {'appId' : application_id, 'scannerType' : scanner_type}
        files = {'file' : open(file_path, 'rb')}
        return self._request('POST', 'rest/tasks/setTaskConfig', params, files)

    def request_scan_agent_key(self):
        """
        Request a Secure Scan Agent Key.  This key is used to request scan agent tasks and prevent multiple scan agents from interacting with the same task.
        """
        return self._request('GET', 'rest/tasks/requestScanAgentKey')

    def request_task(self, scanners, agent_config_path, scan_agent_secure_key):
        """
        Requests the next available task off the queue.
        :param scanners: Use this to only select taskss from specified scanner types
        :param agent_config_path: The path to the scangent.properties file your scan agent generated
        :param scan_agent_secure_key: A Secure Scan Agent Key obtained from the “Request Scan Agent Key” call
        """
        params = {'scanners' : scanners, 'scanAgentSecureKey' : scan_agent_secure_key}
        files = {'files' : open(agent_config_path, 'rb')}
        return self._request('POST', 'rest/tasks/requestTask', params, files)

    def update_task_status(self, scan_queue_task_id, message, scan_agent_secure_key, secure_task_key):
        """
        Sends a status update to ThreadFix for the Scan Agent
        :param scan_queue_task_id: ID for the Scan Agent Task to update
        :param message: The status update message
        :param scan_agent_secure_key: A Secure Scan Agent Key obtained from the “Request Scan Agent Key” call
        :param secure_task_key: The Secure Task Key that was returned when the Task was assigned from the queue
        """
        params = {'scanQueueTaskId' : scan_queue_task_id,  'message' : message, 'scanAgentSecureKey' : scan_agent_secure_key, 'secureTaskKey' : secure_task_key}
        return self._request('POST', 'rest/tasks/taskStatusUpdate', params)

    def complete_task(self, scan_queue_task_id, file_path, scan_agent_secure_key, secure_task_key):
        """
        Marks a task as completed and uploads the scan file to the task’s application
        :param scan_queue_task_id: ID for the Scan Agent Task
        :param file_path: The path to the file to upload
        :param scan_agent_secure_key: A Secure Scan Agent Key obtained from the “Request Scan Agent Key” call
        :param secure_task_key: The Secure Task Key that was returned when the Task was assigned from the queue
        """
        params = {'scanQueueTaskId' : scan_queue_task_id, 'scanAgentSecureKey' : scan_agent_secure_key, 'secureTaskKey' : secure_task_key}
        files = {'file' : open(file_path, 'rb')}
        return self._request('POST', 'rest/tasks/completeTask', params, files)

    def fail_task(self, scan_queue_task_id, message, scan_agent_secure_key, secure_task_key):
        """
        Marks a task as failed, to complete it without a file upload.
        :param scan_queue_task_id: ID for the Scan Agent Task to mark as failed
        :param message: The message to provide reason for failure
        :param scan_agent_secure_key: A Secure Scan Agent Key obtained from the “Request Scan Agent Key” call
        :param secure_task_key: The Secure Task Key that was returned when the Task was assigned from the queue
        """
        params = {'scanQueueTaskId' : scan_queue_task_id,  'message' : message, 'scanAgentSecureKey' : scan_agent_secure_key, 'secureTaskKey' : secure_task_key}
        return self._request('POST', 'rest/tasks/failTask', params)

    def get_scan_agent_scanners(self):
        """
        Retrieves the list of scanners that can be configured with the Scan Agent
        """
        return self._request('GET', 'rest/tasks/scanners')

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