# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

import logging
from unittest import TestCase
from uw_pws.models import Position, Entity, Person


class TestModels(TestCase):

    def test_position(self):
        pos = Position.from_json({
            "EWPDept": "University of Washington",
            "EWPTitle": "Retiree",
            "Primary": True})
        self.assertEquals(
            pos.json_data(),
            {'department': "University of Washington",
             'title': "Retiree",
             'is_primary': True})
        self.assertTrue(pos.is_retiree())

    def test_person(self):
        person = Person.from_json(
            {"WhitepagesPublish": True,
             "DisplayName": "Bill Teacher",
             "UWRegID": "FBB38FE46A7C11D5A4AE0004AC494FFE",
             "UWNetID": "bill",
             "PriorUWNetIDs": [],
             "PriorUWRegIDs": [],
             "RegisteredFirstMiddleName": "Bill Average",
             "PreferredMiddleName": None,
             "PreferredFirstName": None,
             "PreferredSurname": None,
             "RegisteredName": "Bill Average Teacher",
             "IsTestEntity": False,
             "RegisteredSurname": "Teacher",
             "EduPersonAffiliations": [
                 "member",
                 "alum",
                 "faculty",
                 "staff",
                 "employee"],
             "PersonAffiliations": {
                 "StudentPersonAffiliation": {
                     "StudentNumber": "0111111",
                     "StudentSystemKey": "000111111",
                     "StudentAffiliationState": "prior",
                     "StudentWhitePages": {
                         "Name": "Teacher, Bill",
                         "Phone": None,
                         "Email": None,
                         "PublishInDirectory": False,
                         "Class": None,
                         "Departments": []}},
                 "AlumPersonAffiliation": {
                     "DevelopmentID": "0000111111",
                     "AlumAffiliationState": "current"},
                 "EmployeePersonAffiliation": {
                     "EmployeeAffiliationState": "current",
                     "EmployeeWhitePages": {
                         "Name": "Teacher, Bill",
                         "Positions": [
                             {"EWPDept": "Family Medicine",
                              "EWPTitle": "Associate Professor",
                              "Primary": True},
                             {"EWPDept": "Family Medicine",
                              "EWPTitle": "Associate Professor - Non Salaried",
                              "Primary": False}],
                         "VoiceMails": ["+1 425 222-2222"],
                         "EmailAddresses": ["bill@uw.edu"],
                         "PublishInDirectory": True,
                         "Pagers": [],
                         "Faxes": ["+1 425 111-1111"],
                         "Addresses": ["Seattle, WA 98105"],
                         "Phones": ["+1 206 333-3333",
                                    "+1 425 555-1236"],
                         "Mobiles": ["+1 425 666-6666"]
                     },
                     "MailStop": "354744",
                     "EmployeeID": "123456782",
                     "HomeDepartment": "Family Medicine"}
             }}
        )
        self.assertEqual(person.display_name, "Bill Teacher")
        self.assertEqual(person.get_formatted_name(), "Bill Teacher")
        self.assertEquals(person.employee_state, "current")
        self.assertEquals(person.alumni_state, "current")
        self.assertTrue(person == person)
        self.assertEqual(
            person.json_data(),
            {'uwnetid': 'bill',
             'uwregid': 'FBB38FE46A7C11D5A4AE0004AC494FFE',
             'is_test_entity': False,
             'first_name': 'Bill Average',
             'surname': 'Teacher',
             'full_name': 'Bill Average Teacher',
             'display_name': 'Bill Teacher',
             'pronouns': None,
             'whitepages_publish': True,
             'employee_id': '123456782',
             'addresses': ["Seattle, WA 98105"],
             'email_addresses': ['bill@uw.edu'],
             'faxes': ["+1 425 111-1111"],
             'mobiles': ["+1 425 666-6666"],
             'pagers': [],
             'phones': ["+1 206 333-3333",
                        "+1 425 555-1236"],
             'voice_mails': ["+1 425 222-2222"],
             'touch_dials': None,
             'positions': [
                 {'department': 'Family Medicine',
                  'is_primary': True,
                  'title': 'Associate Professor'},
                 {'department': 'Family Medicine',
                  'is_primary': False,
                  'title': 'Associate Professor - Non Salaried'},
             ],
             'mailstop': '354744',
             'home_department': 'Family Medicine',
             'publish_in_emp_directory': True,
             'student_number': '0111111',
             'student_system_key': '000111111',
             'student_class': None,
             'student_departments': [],
             'publish_in_stu_directory': False,
             'development_id': '0000111111',
             'alumni_state': 'current',
             'employee_state': 'current',
             'student_state': 'prior'})
        self.assertIsNotNone(str(person))

        self.assertTrue(person.is_alum_state_current())
        self.assertFalse(person.is_alum_state_prior())
        person.alumni_state = "prior"
        self.assertTrue(person.is_alum_state_prior())
        self.assertFalse(person.is_alum_state_current())
        person.alumni_state = None
        self.assertFalse(person.is_alum_state_prior())
        self.assertFalse(person.is_alum_state_current())

        self.assertTrue(person.is_emp_state_current())
        self.assertFalse(person.is_emp_state_prior())
        person.employee_state = "prior"
        self.assertTrue(person.is_emp_state_prior())
        self.assertFalse(person.is_emp_state_current())
        person.employee_state = None
        self.assertFalse(person.is_emp_state_prior())
        self.assertFalse(person.is_emp_state_current())

        self.assertFalse(person.is_stud_state_current())
        self.assertTrue(person.is_stud_state_prior())
        person.student_state = None
        self.assertFalse(person.is_stud_state_prior())
        self.assertFalse(person.is_stud_state_current())
        person.student_state = "current"
        self.assertFalse(person.is_stud_state_prior())
        self.assertTrue(person.is_stud_state_current())

        self.assertFalse(person.is_retiree())
        person.positions = []
        self.assertFalse(person.is_retiree())

    def test_entity(self):
        en = Entity.from_json(
            {"UWRegID": "9136CCB8F66711D5BE060004AC494FFE",
             "PriorUWRegIDs": [],
             "UWNetID": "javerage",
             "PriorUWNetIDs": [],
             "IsTestEntity": False,
             "DisplayName": "James McMiddle Average"})
        self.assertEqual(en.json_data(),
                         {'uwnetid': "javerage",
                          'uwregid': "9136CCB8F66711D5BE060004AC494FFE",
                          'display_name': "James McMiddle Average",
                          'is_person': False,
                          'is_test_entity': False})
        self.assertTrue(en == en)
