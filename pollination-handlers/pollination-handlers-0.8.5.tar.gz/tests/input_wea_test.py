import json
import os

from pollination_handlers.inputs.wea import wea_handler
from ladybug.wea import Wea
from ladybug.epw import EPW


def test_read_wea_str():
    res = wea_handler('./tests/assets/in.wea')
    assert res.replace('\\', '/').endswith('tests/assets/in.wea')


def test_read_wea_object():
    wea_object = Wea.from_file('./tests/assets/in.wea')

    res = wea_handler(wea_object)
    assert os.path.isfile(res)
    assert res.endswith('.wea')


def test_read_epw_str():
    res = wea_handler('./tests/assets/in.epw')
    assert os.path.isfile(res)
    assert res.endswith('.wea')


def test_read_epw_object():
    epw_object = EPW('./tests/assets/in.epw')

    res = wea_handler(epw_object)
    assert os.path.isfile(res)
    assert res.endswith('.wea')
