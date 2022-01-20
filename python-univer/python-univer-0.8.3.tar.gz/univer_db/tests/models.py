import unittest
from univer_db.models import EducPlan, EducPlanPos, Cycle

from . import Session


class TestEducPlan(unittest.TestCase):
    def test_get_list(self):
        session = Session()
        educ_plans = session.query(EducPlan).filter()
        print("educ_plans: %s" % educ_plans.count())
        self.assertTrue(educ_plans.count())
    
    def test_get_obj(self):
        session = Session()
        educ_plan = session.query(EducPlan).first()
        self.assertTrue(educ_plan)
        print('educ_plan.min_cred_total: %s' % educ_plan.min_cred_total)


class TestEducPlanPos(unittest.TestCase):
    def test_get_list(self):
        session = Session()
        educ_plan_pos_list = session.query(EducPlanPos).filter()
        print('educ_plan_pos_list: %s' % educ_plan_pos_list.count())
        self.assertTrue(educ_plan_pos_list.count())
    
    def test_get_obj(self):
        session = Session()
        educ_plan_pos = session.query(EducPlanPos).first()
        self.assertTrue(educ_plan_pos)
        print('educ_plan_pos.credit: %s' % educ_plan_pos.credit)
    
    def test_get_cycle(self):
        session = Session()
        educ_plan_pos = session.query(EducPlanPos).first()
        print('educ_plan_pos.cycle: %s' % educ_plan_pos.cycle)
        self.assertTrue(educ_plan_pos.cycle)


class TestCycle(unittest.TestCase):
    def test_get_obj(self):
        session = Session()
        cycles = session.query(Cycle).filter()
        for cycle in cycles:
            print('cycle: %s' % cycle)
        self.assertTrue(cycles.count())