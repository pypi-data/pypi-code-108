import unittest
from univer_db.models import StructureDivision

from . import Session


class TestStructureDivision(unittest.TestCase):
    def test_get_obj(self):
        session = Session()
        division = session.query(StructureDivision).first()
        print("division: %s" % division)

    def test_get_parent(self):
        session = Session()
        division = session.query(StructureDivision).filter(
            StructureDivision.parent_id != 0).first()
        print("division: %s" % division)
        print("division.parent_id: %s" % division.parent_id)
        print("division.parent: %s" % division.parent)
