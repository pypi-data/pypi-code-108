import unittest
from univer_db.models import TeacherChairLink, OfficeRegistrator, OfficeRegistratorFacultyLink

from . import Session


class TestTeacherChairLink(unittest.TestCase):
    def test_get_obj(self):
        session = Session()
        links = session.query(TeacherChairLink).filter()
        print("links: %s" % links.count())
        self.assertTrue(links.count())


class TestOfficeRegistrator(unittest.TestCase):
    def test_get_obj(self):
        session = Session()
        office_registrator = session.query(OfficeRegistrator).first()
        print(f'office_registrator: {office_registrator}')
        office_registrator_faculties = session.query(OfficeRegistratorFacultyLink).filter(
            OfficeRegistratorFacultyLink.office_registrator_id == office_registrator.id)

        for office_registrator in office_registrator_faculties:
            print(f'faculty: {office_registrator.faculty}')
