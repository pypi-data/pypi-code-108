from pollination_handlers.outputs.eui import eui_json_from_path


def test_eui_json_from_path():
    res = eui_json_from_path('./tests/assets/eui.json')
    assert 'total: 83.91' in res
    assert 'heating: 29.43' in res
    assert 'cooling: 4.925' in res
