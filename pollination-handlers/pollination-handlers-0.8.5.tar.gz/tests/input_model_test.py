import json
import os
import pytest

from pollination_handlers.inputs.model import model_to_json, model_to_json_grid_check, \
    model_to_json_grid_room_check, model_to_json_view_check, model_dragonfly_to_json, \
    model_to_json_room_check
from honeybee.model import Model
from dragonfly.model import Model as ModelDF


def test_read_model_str():
    res = model_to_json('./tests/assets/two_rooms.hbjson')
    assert res.replace('\\', '/').endswith('tests/assets/two_rooms.hbjson')


def test_read_model_object():
    with open('./tests/assets/two_rooms.hbjson') as hb_model:
        data = hb_model.read()
    data = json.loads(data)
    model = Model.from_dict(data)

    res = model_to_json(model)
    assert os.path.isfile(res)

    res2 = model_to_json_grid_check(model)
    assert os.path.isfile(res2)

    res3 = model_to_json_grid_room_check(model)
    assert os.path.isfile(res3)

    res4 = model_to_json_room_check(model)
    assert os.path.isfile(res4)

    with pytest.raises(ValueError):
        model_to_json_view_check(model)


def test_read_model_dragonfly_str():
    res = model_to_json('./tests/assets/model_complete_simple.dfjson')
    assert res.replace('\\', '/').endswith('tests/assets/model_complete_simple.dfjson')


def test_read_model_dragonfly_object():
    with open('./tests/assets/model_complete_simple.dfjson') as df_model:
        data = df_model.read()
    data = json.loads(data)
    model = ModelDF.from_dict(data)

    res = model_dragonfly_to_json(model)
    assert os.path.isfile(res)
