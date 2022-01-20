import pytest
from copy import deepcopy
from module_placeholder.config import read_config
from module_placeholder.workflows import common, business_case

config = read_config("config.yml")
target = config['target']


@pytest.mark.unit
def test_business_case_pass(calibration_results):
    challenger_calibration_results = deepcopy(calibration_results)
    champion_calibration_results = deepcopy(calibration_results)

    challenger_calibration_results[target]['automation_overall']['automation'] += 0.05

    should_publish, reason = business_case.should_publish(challenger_calibration_results, champion_calibration_results)

    assert should_publish
    assert reason.startswith("The challenger savings are ")


@pytest.mark.unit
def test_business_case_pass_no_champion(calibration_results):
    challenger_calibration_results = deepcopy(calibration_results)

    should_publish, reason = business_case.should_publish(challenger_calibration_results, None)

    assert should_publish
    assert reason.startswith("There is no current champion. Publishing the model is recommended. The challenger accuracy ")


@pytest.mark.unit
def test_business_target_not_achieved(calibration_results):
    challenger_calibration_results = deepcopy(calibration_results)
    champion_calibration_results = deepcopy(calibration_results)

    challenger_calibration_results[target]['automation_overall']['accuracy'] -= 0.05

    should_publish, reason = business_case.should_publish(challenger_calibration_results, champion_calibration_results)

    assert not should_publish
    assert reason.startswith("The accuracy for the challenger model accuracy ")


@pytest.mark.unit
def test_business_target_not_meaningfully_improved(calibration_results):
    challenger_calibration_results = deepcopy(calibration_results)
    champion_calibration_results = deepcopy(calibration_results)

    should_publish, reason = business_case.should_publish(challenger_calibration_results, champion_calibration_results)

    assert not should_publish
    assert reason.startswith("The challenger model does not meaningfully improve the ")
