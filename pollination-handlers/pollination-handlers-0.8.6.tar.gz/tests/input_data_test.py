import json
import os

from pollination_handlers.inputs.data import value_or_data_to_str
from ladybug.datacollection import HourlyDiscontinuousCollection
from ladybug.header import Header
from ladybug.analysisperiod import AnalysisPeriod
from ladybug.dt import DateTime
from ladybug.datatype.temperature import Temperature


def test_read_ddy_str():
    res = value_or_data_to_str('5')
    assert res == '5'
    res = value_or_data_to_str('[5, 6, 7]')
    assert res == '[5, 6, 7]'

    a_per = AnalysisPeriod(6, 21, 12, 6, 21, 13)
    dt1, dt2 = DateTime(6, 21, 12), DateTime(6, 21, 13)
    values = [20, 25]
    dc1 = HourlyDiscontinuousCollection(Header(Temperature(), 'C', a_per),
                                        values, [dt1, dt2])
    res = value_or_data_to_str(dc1)
    assert res == '[20, 25]'
