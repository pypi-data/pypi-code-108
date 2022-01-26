from restclients_core import models


class Major(models.Model):
    major_abbr = models.CharField(max_length=32)
    program_code = models.CharField(max_length=128)
    academic_qtr_key_id = models.IntegerField()
    major_pathway = models.IntegerField()
    display_name = models.CharField(max_length=255)
    college = models.CharField(max_length=255)
    division = models.CharField(max_length=255)
    dtx = models.CharField(max_length=255)
    assigned_count = models.IntegerField()
    assigned_resident = models.IntegerField(null=True)
    assigned_nonresident = models.IntegerField(null=True)
    assigned_international = models.IntegerField(null=True)
    assigned_freshman = models.IntegerField(null=True)
    assigned_transfer = models.IntegerField(null=True)
    assigned_postbac = models.IntegerField(null=True)


class Cohort(models.Model):
    academic_qtr_id = models.IntegerField()
    cohort_number = models.IntegerField()
    cohort_description = models.TextField()
    cohort_residency = models.CharField(max_length=255)
    admit_decision = models.CharField(max_length=255)
    protected_group = models.BooleanField()
    active_cohort = models.BooleanField()
    assigned_count = models.IntegerField()
    assigned_freshman = models.IntegerField(null=True)
    assigned_transfer = models.IntegerField(null=True)
    assigned_postbac = models.IntegerField(null=True)


class Decision(models.Model):
    decision_name = models.CharField(max_length=255)
    decision_id = models.CharField(max_length=128)
    assigned_count1 = models.IntegerField()
    assigned_count2 = models.IntegerField()


class Quarter(models.Model):
    id = models.IntegerField()
    begin = models.DateTimeField()
    end = models.DateTimeField()
    active_ind = models.CharField(max_length=32)
    appl_yr = models.CharField(max_length=4)
    appl_qtr = models.CharField(max_length=1)
    is_current = models.BooleanField()


class Activity(models.Model):
    assignment_date = models.DateTimeField()
    comment = models.TextField()
    user = models.CharField(max_length=12)
    assignment_type = models.TextField()
    cohort_number = models.IntegerField()
    major_abbr = models.CharField(max_length=32)
    major_program_code = models.CharField(max_length=32)
    total_submitted = models.IntegerField()
    total_assigned = models.IntegerField()
    application_type = models.CharField(max_length=128)


class Application(models.Model):
    adsel_id = models.IntegerField()
    application_number = models.IntegerField()
    system_key = models.IntegerField()
    campus = models.IntegerField()
    quarter_id = models.IntegerField()
    assigned_cohort = models.IntegerField()
    assigned_major = models.CharField(max_length=32)
    major_program_code = models.CharField(max_length=255)
    application_type = models.CharField(max_length=255)

    def json_data(self):
        return {'admissionSelectionId': int(self.adsel_id),
                'applicationNbr': self.application_number,
                'systemKey': int(self.system_key),
                'applicationType': self.application_type}


class PurpleGoldApplication(Application):
    award_amount = models.IntegerField()

    def json_data(self):
        return {'admissionSelectionId': int(self.adsel_id),
                'awardAmount': self.award_amount}


class DepartmentalDecisionApplication(Application):
    decision_id = models.IntegerField()

    def json_data(self):
        return {'admissionSelectionId': int(self.adsel_id),
                'departmentalDecisionId': self.decision_id}


class Assignment(models.Model):
    assignment_type = models.CharField()
    quarter = models.IntegerField()
    campus = models.IntegerField()
    comments = models.TextField()
    user = models.CharField(max_length=12)
    applicants = []


class CohortAssignment(Assignment):
    cohort_number = models.IntegerField()
    override_previous = models.BooleanField()
    override_protected = models.BooleanField()

    def json_data(self):
        applicant_json = []
        for application in self.applicants:
            applicant_json.append(application.json_data())
        return {'applicants': applicant_json,
                'cohortNbr': int(self.cohort_number),
                'overridePreviousCohort': self.override_previous,
                'overridePreviousProtectedCohort': self.override_protected,
                'assignmentDetail': {'assignmentType': self.assignment_type,
                                     'academicQtrKeyId': self.quarter,
                                     'campus': int(self.campus),
                                     'comments': self.comments,
                                     'decisionImportUser': self.user}
                }


class MajorAssignment(Assignment):
    major_code = models.CharField()

    def json_data(self):
        applicant_json = []
        for application in self.applicants:
            applicant_json.append(application.json_data())
        return {'applicants': applicant_json,
                'majorProgramCode': self.major_code,
                'assignmentDetail': {'assignmentType': self.assignment_type,
                                     'academicQtrKeyId': self.quarter,
                                     'campus': int(self.campus),
                                     'comments': self.comments,
                                     'decisionImportUser': self.user}
                }


class PurpleGoldAssignment(Assignment):
    def json_data(self):
        applicant_json = []
        for application in self.applicants:
            applicant_json.append(application.json_data())
        return {'applicants': applicant_json,
                'assignmentDetail': {'assignmentType': self.assignment_type,
                                     'academicQtrKeyId': self.quarter,
                                     'comments': self.comments,
                                     'decisionImportUser': self.user}
                }


class DecisionAssignment(Assignment):
    decision = models.CharField()
    decision_number = models.IntegerField()

    def json_data(self):
        applicant_json = []
        for application in self.applicants:
            applicant_json.append(application.json_data())
        return {'applicants': applicant_json,
                'assignmentDetail': {'assignmentType': self.assignment_type,
                                     'assignmentCategory':
                                         "DepartmentalDecision",
                                     'academicQtrKeyId': self.quarter,
                                     'campus': int(self.campus),
                                     'comments': self.comments,
                                     'decisionImportUser': self.user,
                                     'decisionNumber': self.decision_number}
                }


class AdminMajor(models.Model):
    major_id = models.IntegerField()
    major_abbr = models.CharField(max_length=32)
    begin_academic_qtr_key_id = models.IntegerField()
    end_academic_qtr_key_id = models.IntegerField()
    major_pathway = models.IntegerField()
    display_name = models.CharField(max_length=255)
    college = models.CharField(max_length=255)
    division = models.CharField(max_length=255)
    dtx = models.CharField(max_length=255)
    dtx_desc = models.CharField(max_length=255)
    directToMajorInd = models.BooleanField()
    directToCollegeInd = models.IntegerField()
    majorDegreeLevel = models.IntegerField()
    majorDegreeType = models.IntegerField()
    assignedMajorAbbr = models.CharField(max_length=255)
    assignedMajorDegreeLevel = models.IntegerField()
    assignedMajorDegreeType = models.IntegerField()
    majorAssignedName = models.CharField(max_length=255)
    assignedMajorPathway = models.IntegerField()

    def json_data(self):
        return {
            "id": self.major_id,
            "majorAbbr": self.major_abbr,
            "beginAcademicQtrKeyId": self.begin_academic_qtr_key_id,
            "endAcademicQtrKeyId": self.end_academic_qtr_key_id,
            "majorPathway": self.major_pathway,
            "displayName": self.display_name,
            "collegeCode": self.college,
            "collegeDivision": self.division,
            "directToXType": self.dtx,
            "directToXDesc": self.dtx_desc,
            "directToMajorInd": self.directToMajorInd,
            "directToCollegeInd": self.directToCollegeInd,
            "majorDegreeLevel": self.majorDegreeLevel,
            "majorDegreeType": self.majorDegreeType,
            "assignedMajorAbbr": self.assignedMajorAbbr,
            "assignedMajorDegreeLevel": self.assignedMajorDegreeLevel,
            "assignedMajorDegreeType": self.assignedMajorDegreeType,
            "majorAssignedName": self.majorAssignedName,
            "assignedMajorPathway": self.assignedMajorPathway
        }


class AdminCohort(models.Model):
    academic_qtr_id = models.IntegerField()
    cohort_number = models.IntegerField()
    cohort_description = models.TextField()
    cohort_residency = models.CharField(max_length=255)
    cohort_campus = models.IntegerField()
    cohort_application_type = models.IntegerField()
    admit_decision = models.CharField(max_length=255)
    protected_group = models.BooleanField()
    enforce_exceptions = models.BooleanField()
    active_cohort = models.BooleanField()
    record_updated = models.DateTimeField()
    record_update_user = models.CharField(max_length=255)

    def json_data(self):
        return {
            "academic_qtr_id": self.academic_qtr_id,
            "cohort_number": self.cohort_number,
            "cohort_description": self.cohort_description,
            "cohort_residency": self.cohort_residency,
            "cohort_campus": self.cohort_campus,
            "cohort_application_type": self.cohort_application_type,
            "admit_decision": self.admit_decision,
            "protected_group": self.protected_group,
            "enforce_exceptions": self.enforce_exceptions,
            "active_cohort": self.active_cohort,
            "record_updated": self.record_updated,
            "record_update_user": self.record_update_user
        }
