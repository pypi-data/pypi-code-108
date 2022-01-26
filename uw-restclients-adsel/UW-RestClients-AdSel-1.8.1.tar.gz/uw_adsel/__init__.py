"""
This is the interface for interacting with the AdSel Web Service.
"""

import json
import logging
from restclients_core.exceptions import DataFailureException
from restclients_core.dao import MockDAO
from uw_adsel.dao import ADSEL_DAO
from uw_adsel.models import Major, Cohort, Quarter, Activity, Application, \
    Decision, AdminMajor, AdminCohort
import dateutil.parser
from datetime import datetime
import urllib.parse


logger = logging.getLogger(__name__)

# max page size 300
PAGE_SIZE = 300
MAJOR_TYPE = "major"
COHORT_TYPE = "cohort"


class AdSel(object):
    """
    The AdSel object has methods for interacting with the AdSel API.
    """
    API = '/api/v1'

    def __init__(self, config={}):
        self.DAO = ADSEL_DAO()

    def assign_majors(self, major_assignment):
        url = "{}/assignments/major".format(self.API)
        request = major_assignment.json_data()
        response = self._post_resource(url, request)
        return {"response": response, "request": request}

    def assign_cohorts_bulk(self, cohort_assignment):
        url = "{}/assignments/cohort/bulk".format(self.API)
        request = cohort_assignment.json_data()
        response = self._post_resource(url, request)
        return {"response": response, "request": request}

    def assign_cohorts_manual(self, cohort_assignment):
        url = "{}/assignments/cohort".format(self.API)
        request = cohort_assignment.json_data()
        response = self._post_resource(url, request)
        return {"response": response, "request": request}

    def assign_purple_gold(self, pg_assignments):
        url = "{}/assignments/purpleAndGold".format(self.API)
        request = pg_assignments.json_data()
        response = self._post_resource(url, request)
        return {"response": response, "request": request}

    def assign_decisions(self, decision_assignment):
        url = "{}/assignments/departmentalDecision".format(self.API)
        request = decision_assignment.json_data()
        response = self._post_resource(url, request)
        return {"response": response, "request": request}

    def get_quarters(self, **kwargs):
        url = "{}/academicqtr".format(self.API)
        response = self._get_resource(url)
        quarters = self._quarters_from_json(response)
        return quarters

    def get_now(self):
        return datetime.now()

    def _quarters_from_json(self, response):
        quarters = []
        for quarter in response:
            qtr = Quarter()
            qtr.id = quarter["academicQtrKeyId"]
            qtr.begin = dateutil.parser.parse(quarter["activeQtrBeginDttm"])
            qtr.end = dateutil.parser.parse(quarter["activeQtrEndDttm"])
            qtr.active_ind = quarter["activeInd"]
            qtr.appl_yr = quarter["appl_yr"]
            qtr.appl_qtr = quarter["appl_qtr"]
            qtr.is_current = (qtr.begin < self.get_now() < qtr.end)
            quarters.append(qtr)
        return quarters

    def get_all_applications_by_qtr(self, quarter_id):
        url = "{}/applications/{}/all".format(self.API, quarter_id)
        response = self._get_resource(url)
        applications = self._get_applications_from_json(response)
        return applications

    def get_applications_by_qtr_syskey(self, quarter_id, syskey):
        url = "{}/applications/{}/{}".format(self.API, quarter_id, syskey)
        response = self._get_resource(url)
        application = self._get_applications_from_json(response)
        return application

    def get_applications_by_qtr_syskey_list(self, quarter_id, syskey_list):
        if isinstance(self.DAO.get_implementation(), MockDAO):
            all_applications = self._get_live_apps_by_qtr_syskey_list(
                quarter_id,
                syskey_list)
            return [app for app in all_applications
                    if app.system_key in syskey_list]
        else:
            return self._get_live_apps_by_qtr_syskey_list(quarter_id,
                                                          syskey_list)

    def _get_live_apps_by_qtr_syskey_list(self, quarter_id, syskey_list):
        url = "{}/applications/SystemKeys/{}".format(self.API, quarter_id)
        response = self._post_resource(url, syskey_list)
        applications = self._get_applications_from_json(response)
        return applications

    def _get_applications_from_json(self, response):
        applications = []
        for app in response:
            application = Application()
            application.adsel_id = app['admissionsSelectionId']
            application.application_number = app['applicationNbr']
            application.system_key = app['systemKey']
            application.campus = app['campus']
            application.quarter_id = app['academicQtrKeyId']
            application.assigned_cohort = app['assignedCohort']
            application.assigned_major = app['assignedMajor']
            application.major_program_code = app['majorProgramCode']
            application.application_type = app['applicationType']
            applications.append(application)
        return applications

    def get_filtered_activities(self,
                                netid=None,
                                assignment_type=None,
                                cohort=None,
                                major=None,
                                start_date=None,
                                end_date=None,
                                system_key=None,
                                adsel_id=None,
                                collection_type=None,
                                assignment_period=None,
                                comment=None,
                                assingment_category=None,
                                application_type=None):
        url = "{}/activities".format(self.API)
        filters = {}
        if netid is not None:
            filters['netid'] = netid
        if assignment_type is not None:
            filters['assignmentType'] = assignment_type
        if application_type is not None:
            filters['applicationType'] = assignment_type
        if cohort is not None:
            filters['cohort'] = cohort
        if major is not None:
            filters['major'] = major
        if start_date is not None:
            filters['startDate'] = start_date
        if end_date is not None:
            filters['endDate'] = end_date
        if system_key is not None:
            filters['systemKey'] = system_key
        if adsel_id is not None:
            filters['admissionSelectionId'] = adsel_id
        if collection_type is not None:
            filters['collectionType'] = collection_type
        if assignment_period is not None:
            filters['assignmentPeriod'] = assignment_period
        if comment is not None:
            filters['comment'] = comment
        if assingment_category is not None:
            filters['assignmentCategory'] = assingment_category
        filter_url = urllib.parse.urlencode(filters)
        if len(filter_url) > 0:
            url = url + "?" + filter_url
        try:
            response = self._get_resource(url)
            return self._activities_from_json(response)
        except DataFailureException:
            return []

    def get_activities(self, **kwargs):
        return self.get_filtered_activities()

    def _activities_from_json(self, response):
        activities = []
        for activity in response['decisions']:
            acty = Activity()
            acty.assignment_date = \
                dateutil.parser.parse(activity['assignmentMadeOn'])
            acty.comment = activity['comment']
            acty.user = activity['assignmentMadeBy']
            acty.assignment_type = activity['assignmentType']
            acty.cohort_number = activity['cohortNbr']
            acty.major_abbr = activity['majorAbbr']
            acty.major_program_code = activity['majorProgramCode']
            acty.total_submitted = activity['totalSubmitted']
            acty.total_assigned = activity['totalAssigned']
            acty.assignment_category = activity['assignmentCategory']
            acty.decision_import_id = activity['decisionImportID']
            acty.application_type = activity['applicationType']
            activities.append(acty)
        return activities

    def get_cohorts_by_qtr(self, quarter_id, **kwargs):
        url = "{}/cohorts/{}".format(self.API, quarter_id)
        response = self._get_resource(url)
        cohorts = self._cohorts_from_json(response)
        return cohorts

    def _cohorts_from_json(self, response):
        cohorts = []
        for cohort in response['cohorts']:
            cohort_model = Cohort()
            cohort_model.academic_qtr_id = cohort['academicQtrKeyId']
            cohort_model.cohort_number = cohort['cohortNbr']
            cohort_model.cohort_description = cohort['cohortDescription']
            cohort_model.cohort_residency = cohort['cohortResidency']
            cohort_model.admit_decision = cohort['admitDecision']
            cohort_model.protected_group = cohort['protectedGroupInd']
            cohort_model.active_cohort = cohort['activeCohortInd']
            cohort_model.assigned_count = cohort['assignedCount']
            cohort_model.assigned_freshman = cohort['freshmanCount']
            cohort_model.assigned_transfer = cohort['transferCount']
            cohort_model.assigned_postbac = cohort['postBacCount']
            cohorts.append(cohort_model)
        return cohorts

    def get_decisions(self, quarter_id, **kwargs):
        url = "{}/departmentaldecisions/GetWithCounts?academicQtrKeyId={}"\
            .format(self.API, quarter_id)
        response = self._get_resource(url)
        decisions = self._decisions_from_json(response)
        return decisions

    def _decisions_from_json(self, response):
        decisions = []
        for decision in response:
            decision_model = Decision()
            decision_model.decision_name = decision['departmentalDecision']
            decision_model.decision_id = decision['departmentalDecisionId']
            decision_model.assigned_count1 = decision['assignedCount1']
            decision_model.assigned_count2 = decision['assignedCount2']
            decisions.append(decision_model)
        return decisions

    def get_major_details_by_qtr_major(self, quarter_id, major_program_code):
        url = "{}/majors/details/{}/{}".format(self.API,
                                               quarter_id,
                                               major_program_code)
        response = self._get_resource(url)
        major = self._major_from_json(response)
        return major

    def get_majors_by_qtr(self, quarter_id, **kwargs):
        majors = self._get_majors_by_page(quarter_id, 1, [])
        return majors

    def _get_majors_by_page(self, quarter_id, page, major_list=[]):
        url = "{}/majors/details/{}?Page={}&Limit=100".format(self.API,
                                                              quarter_id,
                                                              page)
        response = self._get_resource(url)
        majors = self._majors_from_json(response)
        major_list += majors
        if response['nextPage'] is not None:
            self._get_majors_by_page(quarter_id, page+1, major_list)
        return major_list

    def _majors_from_json(self, response):
        majors = []
        for major_data in response['majors']:
            major = self._major_from_json(major_data)
            majors.append(major)
        return majors

    def _major_from_json(self, major_data):
        major = Major()
        major.major_abbr = major_data['majorAbbr']
        major.program_code = major_data['majorProgramCode']
        major.academic_qtr_key_id = major_data['academicQtrKeyId']
        major.major_pathway = major_data['majorPathway']
        major.display_name = major_data['displayName']
        major.college = major_data['college']
        major.division = major_data['division']
        major.dtx = major_data['dtx']
        major.assigned_count = major_data['assignedCount']
        try:
            major.assigned_international = major_data['internationalCount']
            major.assigned_resident = major_data['residentCount']
            major.assigned_nonresident = major_data['nonResidentCount']
        except KeyError:
            pass
        try:
            major.assigned_freshman = major_data['freshmanCount']
            major.assigned_transfer = major_data['transferCount']
            major.assigned_postbac = major_data['postBacCount']
        except KeyError:
            pass
        return major

    def get_admin_majors(self):
        url = "{}/admin/majors".format(self.API)
        response = self._get_resource(url)
        majors = self._majors_from_admin_majors(response)
        return majors

    def get_admin_major_by_id(self, id):
        url = "{}/admin/major/{}".format(self.API, id)
        response = self._get_resource(url)
        major = self._major_from_admin_major(response)
        return major

    def _majors_from_admin_majors(self, response):
        majors = []
        for major in response:
            majors.append(self._major_from_admin_major(major))
        return majors

    def _major_from_admin_major(self, response):
        major_data = {'major_id': response['id'],
                      'major_abbr': response['majorAbbr'],
                      'begin_academic_qtr_key_id':
                          response['beginAcademicQtrKeyId'],
                      'end_academic_qtr_key_id':
                          response['endAcademicQtrKeyId'],
                      'major_pathway': response['majorPathway'],
                      'display_name': response['displayName'],
                      'college': response['collegeCode'],
                      'division': response['collegeDivision'],
                      'dtx': response['directToXType'],
                      'dtx_desc': response['directToXDesc'],
                      'directToMajorInd': response['directToMajorInd'],
                      'directToCollegeInd': response['directToCollegeInd'],
                      'majorDegreeLevel': response['majorDegreeLevel'],
                      'majorDegreeType': response['majorDegreeType'],
                      'assignedMajorAbbr': response['assignedMajorAbbr'],
                      'assignedMajorDegreeLevel':
                          response['assignedMajorDegreeLevel'],
                      'assignedMajorDegreeType':
                          response['assignedMajorDegreeType'],
                      'majorAssignedName': response['majorAssignedName'],
                      'assignedMajorPathway': response['assignedMajorPathway'],
                      }
        return AdminMajor(**major_data)

    def get_admin_majorvalues(self):
        url = "{}/admin/majorvalues".format(self.API)
        response = self._get_resource(url)
        return response

    def post_admin_major(self, major):
        url = "{}/admin/major".format(self.API)
        return self._post_resource(url, major.json_data())

    def put_admin_major(self, major):
        url = "{}/admin/major".format(self.API)
        return self._put_resource(url, major.json_data())

    def get_admin_cohorts_by_qtr(self, qtr):
        url = "{}/admin/cohorts/{}".format(self.API, qtr)
        response = self._get_resource(url)
        cohorts = self._cohorts_from_admin_cohorts(response)
        return cohorts

    def get_admin_cohort_by_qtr_id(self, qtr, id):
        url = "{}/admin/cohorts/{}/{}".format(self.API, qtr, id)
        response = self._get_resource(url)
        cohort = self._cohort_from_admin_cohort(response)
        return cohort

    def _cohorts_from_admin_cohorts(self, response):
        cohorts = []
        for cohort in response:
            cohorts.append(self._cohort_from_admin_cohort(cohort))
        return cohorts

    def _cohort_from_admin_cohort(self, response):
        cohort_data = {"academic_qtr_id": response['academicQtrKeyId'],
                       "cohort_number": response['cohortNbr'],
                       "cohort_description": response['cohortDescription'],
                       "cohort_residency": response['cohortResidency'],
                       "cohort_campus": response['cohortCampus'],
                       "cohort_application_type":
                           response['cohortApplicationType'],
                       "admit_decision": response['admitDecision'],
                       "protected_group": response['protectedGroupInd'],
                       "enforce_exceptions": response['enforceExceptionsInd'],
                       "active_cohort": response['activeCohortInd'],
                       "record_updated": response['recordUpdateDateTime'],
                       "record_update_user": response['recordUpdateUser'],
                       }
        return AdminCohort(**cohort_data)

    def post_admin_cohort(self, cohort):
        url = "{}/admin/cohort".format(self.API)
        return self._post_resource(url, cohort.json_data())

    def put_admin_cohort(self, cohort):
        url = "{}/admin/cohort".format(self.API)
        return self._put_resource(url, cohort.json_data())

    def copy_cohort(self, from_cohort_id, to_cohort_id):
        url = "{}/admin/cohort/copy/{}/{}".format(self.API,
                                                  from_cohort_id,
                                                  to_cohort_id)
        return self._post_resource(url, {})

    def _get_resource(self, url):
        response = self.DAO.getURL(url, self._headers())

        if response.status != 200:
            self._log_error(url, response)
            raise DataFailureException(url, response.status, response.data)

        return json.loads(response.data)

    def _post_resource(self, url, request):
        response = self.DAO.postURL(url,
                                    self._post_headers(),
                                    body=json.dumps(request))
        if response.status not in [200, 201]:
            self._log_error(url, response)
            raise DataFailureException(url, response.status, response.data)

        return json.loads(response.data)

    def _put_resource(self, url, request):
        response = self.DAO.putURL(url,
                                   self._post_headers(),
                                   body=json.dumps(request))
        if response.status not in [200, 201]:
            self._log_error(url, response)
            raise DataFailureException(url, response.status, response.data)

        return json.loads(response.data)

    def _headers(self):
        headers = {"Accept": "application/json"}
        return headers

    def _post_headers(self):
        headers = {'Content-Type': 'application/json'}
        return headers

    def _log_error(self, url, response):
        logger.error("{0} ==> status:{1} data:{2}".format(
            url, response.status, response.data))
