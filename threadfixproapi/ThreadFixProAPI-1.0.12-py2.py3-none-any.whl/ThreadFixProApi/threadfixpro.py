#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Brandon Spruth (bspruth@gmail.com), Jim Nelson (jim.nelson2@target.com),"
__copyright__ = "(C) 2018 Target Brands, Inc."
__contributors__ = ["Brandon Spruth", "Jim Nelson", "Evan Schlesinger"]
__status__ = "Production"
__license__ = "MIT"

import json
import requests
import urllib3
import requests.exceptions
import requests.packages.urllib3

from _utils import *

class ThreadFixProAPI(object):
    """An API wrapper to facilitate interactions to and from ThreadFix."""

    def __init__(self, host, api_key, verify_ssl=True, timeout=30, user_agent=None, cert=None, debug=False):
        """
        Initialize a ThreadFix Pro API instance.
        :param host: The URL for the ThreadFix Pro server. (e.g., http://localhost:8080/threadfix/) NOTE: must include http:// TODO: make it so that it is required or implicitly added if forgotten
        :param api_key: The API key generated on the ThreadFix Pro API Key page.
        :param verify_ssl: Specify if API requests will verify the host's SSL certificate, defaults to true.
        :param timeout: HTTP timeout in seconds, default is 30.
        :param user_agent: HTTP user agent string, default is "threadfix_pro_api/[version]".
        :param cert: You can also specify a local cert to use as client side certificate, as a single file (containing
        the private key and the certificate) or as a tuple of both file’s path
        :param debug: Prints requests and responses, useful for debugging.
        """
        self.TeamsAPI = TeamsAPI(host, api_key, verify_ssl, timeout, user_agent, cert, debug)
        self.ApplicationsAPI = ApplicationsAPI(host, api_key, verify_ssl, timeout, user_agent, cert, debug)
        self.DefectTrackersAPI = DefectTrackersAPI(host, api_key, verify_ssl, timeout, user_agent, cert, debug)
        self.PoliciesAPI = PoliciesAPI(host, api_key, verify_ssl, timeout, user_agent, cert, debug)
        self.ScansAPI = ScansAPI(host, api_key, verify_ssl, timeout, user_agent, cert, debug)
        self.TagsAPI = TagsAPI(host, api_key, verify_ssl, timeout, user_agent, cert, debug)
        self.TasksAPI = TasksAPI(host, api_key, verify_ssl, timeout, user_agent, cert, debug)
        self.VulnerabilitiesAPI = VulnerabilitiesAPI(host, api_key, verify_ssl, timeout, user_agent, cert, debug)
        self.WafsAPI = WafsAPI(host, api_key, verify_ssl, timeout, user_agent, cert, debug)
        self.CICDAPI = CICDAPI(host, api_key, verify_ssl, timeout, user_agent, cert, debug)
        self.RemoteProvidersAPI = RemoteProvidersAPI(host, api_key, verify_ssl, timeout, user_agent, cert, debug)
        self.UsersRolesAndGroupsAPI = UsersRolesAndGroupsAPI(host, api_key, verify_ssl, timeout, user_agent, cert, debug)
        self.EmailReportingAPI = EmailReportingAPI(host, api_key, verify_ssl, timeout, user_agent, cert, debug)
        self.MiscellaneousAPI = MiscellaneousAPI(host, api_key, verify_ssl, timeout, user_agent, cert, debug)
