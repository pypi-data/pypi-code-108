import pytest

from simses.system.power_electronics.acdc_converter.notton import NottonAcDcConverter

charge = list((10.0, v, v) for v in range(0, 10, 1))
discharge = list((10.0, v, v) for v in range(-10, 0, 1))
charge_fail = list((10.0, v, 0.0) for v in range(0, 10, 1))
discharge_fail = list((10.0, v, 0.0) for v in range(-10, 0, 1))


@pytest.fixture(scope="function")
def uut(max_power: float):
    return NottonAcDcConverter(max_power)


@pytest.mark.parametrize('max_power, power, result', charge)
def test_to_dc(result, power, uut: NottonAcDcConverter):
    res = uut.to_dc(power, 0)
    print(res)
    assert result >= res >= result - 1.0


@pytest.mark.parametrize('max_power, power, result', discharge)
def test_to_ac(result, power, uut: NottonAcDcConverter):
    res = uut.to_ac(power, 0)
    print(res)
    assert result >= res >= result - 1.0


@pytest.mark.parametrize('max_power, power, result', charge)
def test_to_dc_reverse(result, power, uut: NottonAcDcConverter):
    res = uut.to_dc_reverse(power, 0)
    print(res)
    assert result + 1.0 >= res >= result


@pytest.mark.parametrize('max_power, power, result', discharge)
def test_to_ac_reverse(result, power, uut: NottonAcDcConverter):
    res = uut.to_ac_reverse(power, 0)
    print(res)
    assert result + 1.0 >= res >= result


@pytest.mark.parametrize('max_power, power, result', discharge_fail)
def test_to_dc_fail(result, power, uut: NottonAcDcConverter):
    res = uut.to_dc(power, 0)
    print(res)
    assert result >= res >= result - 1.0


@pytest.mark.parametrize('max_power, power, result', charge_fail)
def test_to_ac_fail(result, power, uut: NottonAcDcConverter):
    res = uut.to_ac(power, 0)
    print(res)
    assert result >= res >= result - 1.0


@pytest.mark.parametrize('max_power, power, result', discharge_fail)
def test_to_dc_reverse_fail(result, power, uut: NottonAcDcConverter):
    res = uut.to_dc_reverse(power, 0)
    print(res)
    assert result + 1.0 >= res >= result


@pytest.mark.parametrize('max_power, power, result', charge_fail)
def test_to_ac_reverse_fail(result, power, uut: NottonAcDcConverter):
    res = uut.to_ac_reverse(power, 0)
    print(res)
    assert result + 1.0 >= res >= result
