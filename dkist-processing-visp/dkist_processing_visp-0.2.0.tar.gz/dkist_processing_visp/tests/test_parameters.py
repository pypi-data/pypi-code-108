from dataclasses import asdict
from random import choice

import numpy as np
import pytest
from hypothesis import example
from hypothesis import given
from hypothesis import HealthCheck
from hypothesis import settings
from hypothesis import strategies as st

from dkist_processing_visp.tasks.visp_base import VispScienceTask
from dkist_processing_visp.tests.conftest import FakeVispConstants
from dkist_processing_visp.tests.conftest import VispTestingParameters


@pytest.fixture(scope="function")
def basic_science_task_with_parameter_mixin(assign_input_dataset_doc_to_task, apply_mock_constants):
    class Task(VispScienceTask):
        def run(self):
            ...

    apply_mock_constants(FakeVispConstants())
    task = Task(
        recipe_run_id=choice(range(1000000)),
        workflow_name="parse_visp_input_data",
        workflow_version="VX.Y",
    )
    try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
        assign_input_dataset_doc_to_task(task)
        yield task, VispTestingParameters()
    except:
        raise
    finally:
        task._constants_db.purge()


def test_non_wave_parameters(basic_science_task_with_parameter_mixin):
    """
    Given: A Science task with the parameter mixin
    When: Accessing properties for parameters that do not depend on wavelength
    Then: The correct value is returned
    """
    task, expected = basic_science_task_with_parameter_mixin
    task_param_attr = task.parameters
    for pn, pv in asdict(expected).items():
        if type(pv) is not dict:  # Don't test wavelength dependent parameters
            assert getattr(task_param_attr, pn.replace("visp_", "")) == pv


@given(wave=st.floats(min_value=500.0, max_value=2000.0))
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@example(wave=492.5)
def test_wave_parameters(basic_science_task_with_parameter_mixin, wave):
    """
    Given: A Science task with the paramter mixin
    When: Accessing properties for parameters that depend on wavelength
    Then: The correct value is returned
    """
    task, expected = basic_science_task_with_parameter_mixin
    task_param_attr = task.parameters
    task_param_attr._wavelength = wave
    pwaves = np.array(expected.visp_solar_zone_normalization_percentile.wavelength)
    midpoints = 0.5 * (pwaves[1:] + pwaves[:-1])
    idx = np.sum(midpoints < wave)
    for pn, pv in asdict(expected).items():
        if type(pv) is dict:
            assert getattr(task_param_attr, pn.replace("visp_", "")) == pv["values"][idx]
