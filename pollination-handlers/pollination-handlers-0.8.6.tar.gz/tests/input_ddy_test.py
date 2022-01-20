import json
import os

from pollination_handlers.inputs.ddy import ddy_handler
from ladybug.ddy import DDY
from ladybug.epw import EPW


def test_read_ddy_str():
    res = ddy_handler('./tests/assets/in.ddy')
    assert res.replace('\\', '/').endswith('tests/assets/in.ddy')


def test_read_ddy_object():
    ddy_object = DDY.from_ddy_file('./tests/assets/in.ddy')

    res = ddy_handler(ddy_object)
    assert os.path.isfile(res)
    assert res.endswith('.ddy')


def test_read_epw_str():
    res = ddy_handler('./tests/assets/in.epw')
    assert os.path.isfile(res)
    assert res.endswith('.ddy')


def test_read_epw_object():
    epw_object = EPW('./tests/assets/in.epw')

    res = ddy_handler(epw_object)
    assert os.path.isfile(res)
    assert res.endswith('.ddy')
