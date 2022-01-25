def test_import():
    import preheat_open
    from preheat_open import (
        api,
        building,
        building_unit,
        component,
        control_unit,
        data,
        helpers,
        logging,
        price,
        setpoints,
        singleton,
        unit,
        unit_graph,
        weather,
        zone,
    )

    assert isinstance(preheat_open.__version__, str)
    assert isinstance(preheat_open.__name__, str)

    assert isinstance(api.__name__, str)
    assert isinstance(building.__name__, str)
    assert isinstance(building_unit.__name__, str)
    assert isinstance(component.__name__, str)
    assert isinstance(control_unit.__name__, str)
    assert isinstance(data.__name__, str)
    assert isinstance(helpers.__name__, str)
    assert isinstance(logging.__name__, str)
    assert isinstance(price.__name__, str)
    assert isinstance(setpoints.__name__, str)
    assert isinstance(singleton.__name__, str)
    assert isinstance(unit.__name__, str)
    assert isinstance(unit_graph.__name__, str)
    assert isinstance(weather.__name__, str)
    assert isinstance(zone.__name__, str)
