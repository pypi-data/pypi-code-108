import os

from pollination_handlers.inputs.schedule import schedule_to_csv

from ladybug.datatype.fraction import Fraction
from ladybug.analysisperiod import AnalysisPeriod
from ladybug.header import Header
from ladybug.datacollection import HourlyContinuousCollection
from honeybee_energy.schedule.fixedinterval import ScheduleFixedInterval
from honeybee_energy.lib.schedules import schedule_by_identifier
import honeybee_energy.lib.scheduletypelimits as schedule_types


def test_read_schedule_ruleset():
    schedule = schedule_by_identifier('Generic Office Occupancy')
    res = schedule_to_csv(schedule)
    assert os.path.isfile(res)
    assert res.endswith('.csv')


def test_read_schedule_fixedinterval():
    trans_sched = ScheduleFixedInterval(
        'Custom Transmittance', [x / 8760 for x in range(8760)],
        schedule_types.fractional)
    res = schedule_to_csv(trans_sched)
    assert os.path.isfile(res)
    assert res.endswith('.csv')


def test_read_schedule_id():
    res = schedule_to_csv('Generic Office Lighting')
    assert os.path.isfile(res)
    assert res.endswith('.csv')


def test_read_data_collection():
    header = Header(Fraction(), 'fraction', AnalysisPeriod())
    values = [1] * 8760
    dc1 = HourlyContinuousCollection(header, values)
    res = schedule_to_csv(dc1)
    assert os.path.isfile(res)
    assert res.endswith('.csv')
