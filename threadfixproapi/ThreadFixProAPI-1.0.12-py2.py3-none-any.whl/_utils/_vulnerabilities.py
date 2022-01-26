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

class VulnerabilitiesAPI(object):

    def __init__(self, host, api_key, verify_ssl=True, timeout=30, user_agent=None, cert=None, debug=False):
        """
        Initialize a ThreadFix Pro Vulnerabilities API instance.
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

    def vulnerability_search(self, generic_vulnerabilities=None, teams=None, applications=None, channel_types=None, generic_severities=None, number_vulnerabilities=None,
                            page=None, parameter=None, path=None, start_date=None, end_date=None, show_open=None, show_closed=None, show_false_positive=None, 
                            show_not_false_positive=None, show_hidden=None, show_not_hidden=None, show_exploitable=None, show_not_exploitable=None, show_contested=None, 
                            show_not_contested=None, show_verified=None, show_not_verified=None, number_merged=None, show_defect_present=None, show_defect_not_present=None, 
                            show_defect_open=None, show_defect_closed=None, show_inconsistent_closed_defect_needs_scan=None, show_inconsistent_closed_defect_open_in_scan=None,
                            show_inconsistent_open_defect=None, include_custom_text=None, show_comment_present=None, comment_tags=None, days_old_modifier=None,
                            days_old=None, days_old_comments_modifier=None, days_old_comments=None, hours_old_comments_modifier=None, hours_old_comments=None, 
                            commented_by_user=None, vulnerabilities=None, cves_list=None, export_type=None, tags=None, vuln_tags=None, defect_id=None,
                            native_id=None, assign_to_user=None, show_shared_vuln_found=None, show_shared_vuln_not_found=None):
        """
        Returns a filtered list of vulnerabilities
        :param generic_vulnerabilities: Serialized list of generic vulnerability IDs to narrow results to
        :param teams: Serialized list of team IDs to narrow search to
        :param applications: Serialized list of application IDs to narrow search to
        :param channel_types: Serialized list of scanner names to narrow search to
        :param generic_severities: Serialized list of generic severity values to narrow search to
        :param number_vulnerabilities: Number of vulnerabilities to return defaults to 10
        :param page: Which page of vulnerabilities to return with each page containing {number_vulnerabilities} to return
        :param parameter: Filter to only return vulnerabilities containing this string in their parameters
        :param path: Filter to only return vulnerabilities containing this String in their path
        :param start_date: Lower bound on scan dates. Format: yyyy-MM-dd or Epoch time (in milliseconds)
        :param end_date: Upper bound on scan dates. Format: yyyy-MM-dd or Epoch time (in milliseconds)
        :param show_open: Flag to show only open vulnerabilites
        :param show_closed: Flag to show only close vulnerabilities
        :param show_false_positive: Flag to show only vulnerabilities that are false positives
        :param show_not_false_positive: Flag to show only vulnerabilities that are not false positives
        :param show_hidden: Flag to show hidden vulnerabilities
        :param show_not_hidden: Flag to show only vulnerabilities that are not hidden
        :param show_exploitable: Flag to show only vulnerabilities that are exploitable
        :param show_not_exploitable: Flag to show only vulnerabilities that are not exploitable
        :param show_contested: Flag to show only vulnerabilities that are contested
        :param show_not_contested: Flag to show only vulnerabilities that are not contested
        :param show_verified: Flag to show only verified vulnerabilities
        :param show_not_verified: Flag to show only not verified vulnerabilities
        :param number_merged: Number of vulnerabilities merged from different scans to narrow search to
        :param show_defect_present: Flag to show vulnerabilities with defects
        :param show_defect_not_present: Flag to show vulnerabilities without defects
        :param show_defect_open: Flag to show vulnerabilities with open defects
        :param show_defect_closed: Flag to show vulnerabilities with closed defects
        :param show_inconsistent_closed_defect_needs_scan: Flag to show vulnerabilities that have closed defects but have not yet been closed by a scan
        :param show_inconsistent_closed_defect_open_in_scan: Flag to show vulnerabilities that have closed defects but were found open in a scan since the defect was closed
        :param show_inconsistent_open_defect: Flag to show vulnerabilities that have open defects but have been closed by scans
        :param include_custom_text: Set to true to include Custom CWE Text in the response for each vulnerability
        :param show_comment_present: Flag to show vulnerabilities with comments
        :param comment_tags: Serialized list of comment tags. Example: commentTags[0].id=1
        :param days_old_modifier: Should only be value of "less" or "more". Used in conjunction with daysOld parameter
        :param days_old: Number of days in age of the vulnerability. Valid values are "10", "30", etc
        :param days_old_comments_modifier: Should only be value of "less" or "more". Used in conjunction with daysOldComments parameter
        :param days_old_comments: Number of days in age of the comment. Valid values are "10", "30", etc
        :param hours_old_comments_modifier: Should only be value of "less" or "more". Used in conjunction with hoursOldComments parameter
        :param hours_old_comments: Number of hours since comment was added to vulnerability. Valid values are "1", "10", etc
        :param commented_by_user: Filter vulnerabilities by ID of user that added comments to it
        :param vulnerabilities: Serialized list of vulnerability IDs
        :param cves_list: Serialized list of CVE IDs
        :param export_type: Type of export being performed (not case sensitive)
        :param tags: Filters to show vulnerabilities from Applications that are tagged with these application tags
        :param vuln_tags: lters to show vulnerabilities tagged with these vulnerability tags
        :param defect_id: Filters to show vulnerabilities with this defect attached
        :param native_id: Filters to show vulnerabilities with findings that have this native ID
        :param assign_to_user: Filters to show vulnerabilities that have a finding with this value in their assignToUser column
        :param show_shared_vuln_found: Filters to show only vulnerabilities that have been identified as Shared Vulnerabilities
        :param show_shared_vuln_not_found: Filters to show only vulnerabilities that have not been identified as Shared Vulnerabilities
        """
        params = {}
        if generic_vulnerabilities:
            for i in range(len(generic_vulnerabilities)):
                params['genericVulnerabilities[{}].id'.format(i)] = generic_vulnerabilities[i]
        if teams:
            for i in range(len(teams)):
                params['teams[{}].id'.format(i)] = teams[i]
        if applications:
            for i in range(len(applications)):
                params['applications[{}].id'.format(i)] = applications[i]
        if channel_types:
            for i in range(len(channel_types)):
                params['channelTypes[{}].name'.format(i)] = channel_types[i]
        if generic_severities:
            for i in range(len(generic_severities)):
                params['genericSeverities[{}].intValue'.format(i)] = generic_severities[i]
        if number_vulnerabilities:
            params['numberVulnerabilities'] = number_vulnerabilities
        if page:
            params['page'] = page
        if parameter:
            params['parameter'] = parameter
        if path:
            params['path'] = path
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if show_open:
            params['showOpen'] = show_open
        if show_closed:
            params['showClosed'] = show_closed
        if show_false_positive:
            params['showFalsePositive'] = show_false_positive
        if show_not_false_positive:
            params['showNotFalsePositive'] = show_not_false_positive
        if show_hidden:
            params['showHidden'] = show_hidden
        if show_not_hidden:
            params['showNotHidden'] = show_not_hidden
        if show_exploitable:
            params['showExploitable'] = show_exploitable
        if show_not_exploitable:
            params['showNotExploitable'] = show_not_exploitable
        if show_contested:
            params['showContested'] = show_contested
        if show_not_contested:
            params['showNotContested'] = show_not_contested
        if show_verified:
            params['showVerified'] = show_verified
        if show_not_verified:
            params['showNotVerified'] = show_not_verified
        if number_merged:
            params['numberMerged'] = number_merged
        if show_defect_present:
            params['showDefectPresent'] = show_defect_present
        if show_defect_not_present:
            params['showDefectNotPresent'] = show_defect_not_present
        if show_defect_open:
            params['showDefectOpen'] = show_defect_open
        if show_defect_closed:
            params['showDefectClosed'] = show_defect_closed
        if show_inconsistent_closed_defect_needs_scan:
            params['showInconsistentClosedDefectNeedsScan'] = show_inconsistent_closed_defect_needs_scan
        if show_inconsistent_closed_defect_open_in_scan:
            params['showInconsistentClosedDefectOpenInScan'] = show_inconsistent_closed_defect_open_in_scan
        if show_inconsistent_open_defect:
            params['showInconsistentOpenDefect'] = show_inconsistent_open_defect
        if include_custom_text:
            params['includeCustomText'] = include_custom_text
        if show_comment_present:
            params['showCommentPresent'] = show_comment_present
        if comment_tags:
            for i in range(len(comment_tags)):
                params['commentTags[{}].id'.format(i)] = comment_tags[i]
        if days_old_modifier:
            params['daysOldModifier'] = days_old_modifier
        if days_old:
            params['daysOld'] = days_old
        if days_old_comments_modifier:
            params['daysOldCommentsModifier'] = days_old_comments_modifier
        if days_old_comments:
            params['daysOldComments'] = days_old_comments
        if hours_old_comments_modifier:
            params['hoursOldCommentsModifier'] = hours_old_comments_modifier
        if hours_old_comments:
            params['hoursOldComments'] = hours_old_comments
        if commented_by_user:
            params['commentedByUser'] = commented_by_user
        if vulnerabilities:
            for i in range(len(vulnerabilities)):
                params['vulnerabilities[{}].id'.format(i)] = vulnerabilities[i]
        if cves_list:
            for i in range(len(cves_list)):
                params['cvesList[{}].CVE'.format(i)] = cves_list[i]
        if export_type:
            params['exportType'] = export_type
        if tags:
            for i in range(len(tags)):
                params['tags[{}].id'.format(i)] = tags[i]
        if vuln_tags:
            for i in range(len(vuln_tags)):
                params['vulnTags[{}].id'.format(i)] = vuln_tags[i]
        if defect_id:
            params['defectId'] = defect_id
        if native_id:
            params['nativeId'] = native_id
        if assign_to_user:
            params['assignToUser'] = assign_to_user
        if show_shared_vuln_found:
            params['showSharedVulnFound'] = show_shared_vuln_found
        if show_shared_vuln_not_found:
            params['showSharedVulnNotFound'] = show_shared_vuln_not_found
        return self._request('POST', 'rest/latest/vulnerabilities', params)

    def add_comment_to_vulnerability(self, vuln_id, comment, comment_tag_ids=None):
        """
        Adds a comment to the vulnerability with the given vulnId
        :param vuln_id: Vulnerability identifier
        :param comment: The message for the comment
        :param comment_tag_ids: A comma-separated list of the Ids for any comment tags you want to attach to the comment
        """
        params = {'comment' : comment}
        if comment_tag_ids:
            params['commentTagIds'] = comment_tag_ids
        return self._request('POST', 'rest/vulnerabilities/' + str(vuln_id) + '/addComment', params=params)

    def list_severities(self):
        """
        Returns a list of severity levels in ThreadFix and their custom names
        """
        return self._request('GET', 'rest/severities')
    
    def update_vulnerability_severity(self, vulnerability_id, severity_name):
        """
        Changes the severity of the specified vulnerability to the specified severity
        :param vulnerability_id: Vulnerability identifier
        :param severity_name: Name of severity that the vulnerability is being changed to
        """
        return self._request('POST', 'rest/vulnerabilities/' + str(vulnerability_id) + '/severity/' + str(severity_name))

    def close_vulnerabilities(self, vulnerability_id):
        """
        Closes the specified vulnerability
        :param vulnerability_id: Vulnerabilities' identifiers
        """
        params = {'vulnerabilityIds' : vulnerability_id}
        return self._request('POST', 'rest/vulnerabilities/close', params)
        
    def get_document_attached_to_a_vulnerability(self, document_id):
        """
        Displays content of document files
        :param document_id: Document identifier
        """
        return self._request('GET', 'rest/documents/' + str(document_id) + '/download')

    def attach_file_to_vulnerability(self, vuln_id, file_path, new_file_name=None):
        """
        Attaches a file to a vulnerability
        :param vuln_id: Vulnerability identifier
        :param file_path: Path to the file you want to attach to the vulnerability
        :param new_file_name: A name to override the filename when it is attached to the vulnerability
        """
        params = {}
        if new_file_name:
            params['filename'] = new_file_name
        files = {'file' : open(file_path, 'rb')}
        return self._request('POST',  'rest/documents/vulnerabilities/' + str(vuln_id) + '/upload', params, files)

    def mark_vulnerability_as_false_positive(self, vulnerability_id):
        """
        Marks the specified vulnerability as a false positive
        :param vulnerability_id: Vulnerability identifier
        """
        return self._request('POST', 'rest/vulnerabilities/' + str(vulnerability_id) + '/setFalsePositive')

    def add_tag_to_vulnerability(self, vulnerability_id, tag_id):
        """
        Adds specified tag to specified vulnerability
        :param vulnerability_id: Vulnerability identifier
        :param tag_id: Tag identifier
        """
        return self._request('POST', 'rest/vulnerabilities/' + str(vulnerability_id) + '/tags/' + str(tag_id) + '/add')

    def remove_tag_to_vulnerability(self, vulnerability_id, tag_id):
        """
        Removes specified tag to specified vulnerability
        :param vulnerability_id: Vulnerability identifier
        :param tag_id: Tag identifier
        """
        return self._request('POST', 'rest/vulnerabilities/' + str(vulnerability_id) + '/tags/remove/' + str(tag_id))

    def list_vulnerabilities_for_a_tag(self, tag_id):
        """
        Returns a list of all vulnerabilities associated with a tag
        :params tag_id: Tag identifier
        """
        return self._request('GET', 'rest/tags/' + str(tag_id) + '/listVulnerabilities')

    def mark_vulnerability_as_exploitable(self, vulnerability_id):
        """
        Change the specified vulnerability to exploitable
        :param vulnerability_id: Vulnerability identifer
        """
        return self._request('POST', 'rest/vulnerabilities/' + str(vulnerability_id) + '/setExploitable')

    def mark_vulnerability_as_contested(self, vulnerability_id):
        """
        Change the specified vulnerability to contested
        :param vulnerability_id: Vulnerability identifer
        """
        return self._request('POST', 'rest/vulnerabilities/' + str(vulnerability_id) + '/setContested')

    def mark_vulnerability_as_verified(self, vulnerability_id):
        """
        Change the specified vulnerability to verified
        :param vulnerability_id: Vulnerability identifer
        """
        return self._request('POST', 'rest/vulnerabilities/' + str(vulnerability_id) + '/setVerified')

    def get_defect_details(self, defect_id):
        """
        Returns details about the selected defect
        :param defect_id: Defect identifier
        """
        return self._request('GET', 'rest/defects/' + str(defect_id))
    
    def defect_search(self, paging=None, max_results=None, days_old=None, hours_old=None, aging_modifier=None, aging_date_type=None, start_date=None, end_date=None,
                        status_updated_start_date=None, status_updated_end_date=None, defects=None, application_defect_tracker=None, statuses=None, show_active=None,
                        show_open=None, show_closed=None):
        """
        Returns a filtered list of defects
        :param paging: By default defects are displayed 10 to a page. Changing this value will allow user to display the next set of 10 defects and so on
        :param max_results: Maximum number of defects to be returned. By default this method will only return up to 10 defects
        :param days_old: Age in days of defect(s)
        :param hours_old: Age in hours of defect(s)
        :param aging_modifier: 	Applies modifier to either daysOld or hoursOld parameter. Accepted values are "less" and "more"
        :param aging_date_type: Entering "created" will apply the search to the defect created date. Entering "status" will apply the search to the defect status updated date
        :param start_date: Lower bound on defect dates. Format: yyyy-MM-dd or Epoch time (in milliseconds)
        :param end_date: Upper bound on defect dates. Format: yyyy-MM-dd or Epoch time (in milliseconds)
        :param status_updated_start_date: Lower bound on defect updated dates. Format: yyyy-MM-dd or Epoch time (in milliseconds)
        :param status_updated_end_date: Upper bound on defect updated dates. Format: yyyy-MM-dd or Epoch time (in milliseconds)
        :param defects: Serialized list of defects by id
        :param application_defect_tracker: Serialized list of application defect trackers by id
        :param statuses: Serialized list of defects by status
        :param show_active: Flag to show only active defects
        :param show_open: Flag to show only open defects
        :param show_closed: Flag to show only closed defects
        """
        params = {}
        if paging:
            params['paging'] = paging
        if max_results:
            params['maxResults'] = max_results
        if days_old:
            params['daysOld'] = days_old
        if hours_old:
            params['hoursOld'] = hours_old
        if aging_modifier:
            params['agingModifier'] = aging_modifier
        if aging_date_type:
            params['agingDateType'] = aging_date_type
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        if status_updated_start_date:
            params['statusUpdatedStartDate'] = status_updated_start_date
        if status_updated_end_date:
            params['statusUpdatedEndDate'] = status_updated_end_date
        if defects:
            for i in range(len(defects)):
                params['defects[{}].id'.format(i)] = defects[i]
        if application_defect_tracker:
            for i in range(len(application_defect_tracker)):
                params['applicationDefectTracker[{}].id'.format(i)] = application_defect_tracker[i]
        if statuses:
            for i in range(len(statuses)):
                params['statuses[{}].status'.format(i)] = statuses[i]
        if show_active:
            params['showActive'] = show_active
        if show_open:
            params['showOpen'] = show_open
        if show_closed:
            params['showClosed'] = show_closed
        return self._request('POST', 'rest/defects/search', params)

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
