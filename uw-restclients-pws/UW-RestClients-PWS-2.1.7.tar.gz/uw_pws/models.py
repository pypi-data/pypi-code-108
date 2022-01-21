# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from nameparser import HumanName
from restclients_core import models


class Position(models.Model):
    RETIREE = "retiree"
    department = models.CharField(max_length=250)
    title = models.CharField(max_length=250)
    is_primary = models.NullBooleanField()

    def is_retiree(self):
        return (self.title is not None and
                self.title.lower() == Position.RETIREE)

    def json_data(self):
        return {
            'department': self.department,
            'title': self.title,
            'is_primary': self.is_primary,
        }

    @staticmethod
    def from_json(data):
        position = Position()
        position.department = data.get("EWPDept")
        position.title = data.get("EWPTitle")
        position.is_primary = data.get("Primary")
        return position


class Person(models.Model):
    CURRENT = "current"
    PRIOR = "prior"

    uwregid = models.CharField(max_length=32)
    uwnetid = models.CharField(max_length=128)
    first_name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    full_name = models.CharField(max_length=250)
    display_name = models.CharField(max_length=250)
    preferred_first_name = models.CharField(max_length=250)
    preferred_middle_name = models.CharField(max_length=250)
    preferred_surname = models.CharField(max_length=250)
    pronouns = models.CharField(max_length=128)
    whitepages_publish = models.NullBooleanField()

    # Affiliation flags
    is_student = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)
    is_alum = models.BooleanField(default=False)
    is_faculty = models.BooleanField(default=False)
    is_test_entity = models.BooleanField(default=False)

    # Employee attributes
    employee_id = models.CharField(max_length=9, default=None)
    mailstop = models.CharField(max_length=255, default=None)
    home_department = models.CharField(max_length=255, default=None)
    employee_state = models.CharField(max_length=16, default=None)
    publish_in_emp_directory = models.NullBooleanField()

    # Student attributes
    student_number = models.CharField(max_length=9, default=None)
    student_system_key = models.SlugField(max_length=10, default=None)
    student_class = models.CharField(max_length=255, default=None)
    student_state = models.CharField(max_length=16, default=None)
    publish_in_stu_directory = models.NullBooleanField()

    # Alum attributes
    development_id = models.CharField(max_length=30, default=None)
    alumni_state = models.CharField(max_length=16, default=None)

    def __init__(self, *args, **kwargs):
        super(Person, self).__init__(*args, **kwargs)
        self.prior_uwnetids = []
        self.prior_uwregids = []
        self.addresses = []
        self.email_addresses = []
        self.faxes = []
        self.mobiles = []
        self.pagers = []
        self.phones = []
        self.touch_dials = []
        self.voice_mails = []
        self.positions = []
        self.student_departments = []

    def __eq__(self, other):
        return self.uwregid == other.uwregid

    def get_primary_position(self):
        for position in self.positions:
            if position.is_primary:
                return position
        return None

    def is_alum_state_current(self):
        return (self.alumni_state is not None and
                self.alumni_state == Person.CURRENT)

    def is_emp_state_current(self):
        # including retiree, visiting scholars, affiliate employees, and
        # contract individuals, who have active worker or contract
        # contingent worker records in Workday
        return (self.employee_state is not None and
                self.employee_state == Person.CURRENT)

    def is_stud_state_current(self):
        # including applicant and student
        return (self.student_state is not None and
                self.student_state == Person.CURRENT)

    def is_alum_state_prior(self):
        return (self.alumni_state is not None and
                self.alumni_state == Person.PRIOR)

    def is_emp_state_prior(self):
        return (self.employee_state is not None and
                self.employee_state == Person.PRIOR)

    def is_stud_state_prior(self):
        return (self.student_state is not None and
                self.student_state == Person.PRIOR)

    def is_retiree(self):
        primary_pos = self.get_primary_position()
        return (self.is_emp_state_current() and
                primary_pos is not None and
                primary_pos.is_retiree())

    def json_data(self):
        return {
            'uwnetid': self.uwnetid,
            'uwregid': self.uwregid,
            'is_test_entity': self.is_test_entity,
            'first_name': self.first_name,
            'surname': self.surname,
            'full_name': self.full_name,
            'display_name': self.display_name,
            'pronouns': self.pronouns,
            'whitepages_publish': self.whitepages_publish,
            'employee_id': self.employee_id,
            'addresses': self.addresses,
            'email_addresses': self.email_addresses,
            'faxes': self.faxes,
            'mobiles': self.mobiles,
            'pagers': self.pagers,
            'phones': self.phones,
            'voice_mails': self.voice_mails,
            'touch_dials': self.touch_dials,
            'positions': [p.json_data() for p in self.positions],
            'mailstop': self.mailstop,
            'home_department': self.home_department,
            'publish_in_emp_directory': self.publish_in_emp_directory,
            'student_number': self.student_number,
            'student_system_key': self.student_system_key,
            'student_class': self.student_class,
            'student_departments': self.student_departments,
            'publish_in_stu_directory': self.publish_in_stu_directory,
            'development_id': self.development_id,
            'alumni_state': self.alumni_state,
            'employee_state': self.employee_state,
            'student_state': self.student_state
        }

    def get_formatted_name(self, string_format='{first} {middle} {last}'):
        if (self.display_name is not None and len(self.display_name) and
                not self.display_name.isupper()):
            return self.display_name
        else:
            name = HumanName("{} {}".format(self.first_name, self.surname))
            name.capitalize()
            name.string_format = string_format
            return str(name)

    def get_first_last_name(self):
        """
        Returns a tuple containing first_name, last_name, using preferred name
        if available, otherwise institutional name.
        """
        if (self.preferred_first_name is not None and
                len(self.preferred_first_name) and
                self.preferred_surname is not None and
                len(self.preferred_surname)):
            return self.preferred_first_name, self.preferred_surname

        return self.first_name, self.surname

    @staticmethod
    def from_json(data):
        person = Person()
        person.uwnetid = data.get("UWNetID")
        person.uwregid = data.get("UWRegID")
        person.is_test_entity = data.get("IsTestEntity")
        person.prior_uwnetids = data.get("PriorUWNetIDs", [])
        person.prior_uwregids = data.get("PriorUWRegIDs", [])
        person.whitepages_publish = data.get("WhitepagesPublish")
        person.surname = data.get("RegisteredSurname")
        person.first_name = data.get("RegisteredFirstMiddleName")
        person.full_name = data.get("RegisteredName")
        person.display_name = data.get("DisplayName")
        person.preferred_first_name = data.get("PreferredFirstName")
        person.preferred_middle_name = data.get("PreferredMiddleName")
        person.preferred_surname = data.get("PreferredSurname")
        person.pronouns = data.get("Pronouns")

        for affiliation in data.get("EduPersonAffiliations", []):
            if affiliation == "student":
                person.is_student = True
            elif affiliation == "alum":
                person.is_alum = True
            elif affiliation == "staff":
                person.is_staff = True
            elif affiliation == "faculty":
                person.is_faculty = True
            elif affiliation == "employee":
                person.is_employee = True

        person_affiliations = data.get('PersonAffiliations', {})
        if 'EmployeePersonAffiliation' in person_affiliations:
            emp_affil = person_affiliations.get('EmployeePersonAffiliation')
            person.employee_id = emp_affil.get('EmployeeID')
            person.mailstop = emp_affil.get('MailStop')
            person.home_department = emp_affil.get('HomeDepartment')
            person.employee_state = emp_affil.get(
                "EmployeeAffiliationState")
            e_pages = emp_affil.get('EmployeeWhitePages', {})
            for pos_data in e_pages.get("Positions", []):
                person.positions.append(Position.from_json(pos_data))
            person.publish_in_emp_directory = e_pages.get("PublishInDirectory")
            if person.publish_in_emp_directory:
                person.addresses = e_pages.get("Addresses")
                person.email_addresses = e_pages.get("EmailAddresses")
                person.faxes = e_pages.get("Faxes")
                person.mobiles = e_pages.get("Mobiles")
                person.pagers = e_pages.get("Pagers")
                person.phones = e_pages.get("Phones")
                person.touch_dials = e_pages.get("TouchDials")
                person.voice_mails = e_pages.get("VoiceMails")

        if 'StudentPersonAffiliation' in person_affiliations:
            stu_affil = person_affiliations.get('StudentPersonAffiliation')
            person.student_number = stu_affil.get('StudentNumber')
            person.student_system_key = stu_affil.get('StudentSystemKey')
            person.student_state = stu_affil.get("StudentAffiliationState")
            s_pages = stu_affil.get("StudentWhitePages", {})
            person.publish_in_stu_directory = s_pages.get("PublishInDirectory")
            person.student_class = s_pages.get("Class")
            person.student_departments = s_pages.get("Departments")

        if 'AlumPersonAffiliation' in person_affiliations:
            alum_affil = person_affiliations.get('AlumPersonAffiliation')
            person.development_id = alum_affil.get('DevelopmentID')
            person.alumni_state = alum_affil.get("AlumAffiliationState")
        return person


class Entity(models.Model):
    uwregid = models.CharField(max_length=32)
    uwnetid = models.CharField(max_length=128)
    display_name = models.CharField(max_length=250)
    is_test_entity = models.BooleanField(default=False)
    is_person = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super(Entity, self).__init__(*args, **kwargs)
        self.prior_uwnetids = []
        self.prior_uwregids = []

    def __eq__(self, other):
        return self.uwregid == other.uwregid

    def json_data(self):
        return {
            'uwnetid': self.uwnetid,
            'uwregid': self.uwregid,
            'display_name': self.display_name,
            'is_test_entity': self.is_test_entity,
            'is_person': self.is_person,
        }

    @staticmethod
    def from_json(data):
        entity = Entity()
        entity.uwnetid = data.get("UWNetID")
        entity.uwregid = data.get("UWRegID")
        entity.display_name = data.get("DisplayName")
        entity.is_test_entity = data.get("IsTestEntity")
        entity.prior_uwnetids = data.get("PriorUWNetIDs", [])
        entity.prior_uwregids = data.get("PriorUWRegIDs", [])

        entity_affiliations = data.get("EntityAffiliations")
        if (entity_affiliations and "PersonURI" in entity_affiliations):
            entity.is_person = True

        return entity
