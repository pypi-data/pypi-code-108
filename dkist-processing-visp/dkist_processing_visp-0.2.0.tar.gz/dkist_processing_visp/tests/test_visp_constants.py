from dataclasses import asdict
from dataclasses import dataclass
from random import choice
from typing import Tuple

import pytest

from dkist_processing_visp.models.constants import VispConstants
from dkist_processing_visp.tasks.visp_base import VispScienceTask


@dataclass
class testing_constants:
    num_modstates: int = 10
    num_beams: int = 2
    num_cs_steps: int = 18
    num_raster_steps: int = 1000
    polarimeter_mode: bool = "observe_polarimetric"
    num_spatial_bins: int = 1
    num_spectral_bins: int = 1
    wavelength: float = 666.6
    lamp_exposure_times: Tuple[float] = (100.0,)
    solar_exposure_times: Tuple[float] = (1.0,)
    observe_exposure_times: Tuple[float] = (0.01,)
    # We don't need all the common ones, but let's put one just to check
    instrument: str = "CHECK_OUT_THIS_INSTRUMENT"


@pytest.fixture(scope="session")
def expected_constant_dict() -> dict:
    lower_dict = asdict(testing_constants())
    return {k.upper(): v for k, v in lower_dict.items()}


@pytest.fixture(scope="function")
def visp_science_task_with_constants(expected_constant_dict, apply_mock_constants):
    class Task(VispScienceTask):
        def run(self):
            ...

    apply_mock_constants(testing_constants())
    task = Task(
        recipe_run_id=choice(range(1000000)),
        workflow_name="parse_visp_input_data",
        workflow_version="VX.Y",
    )
    task.constants = VispConstants(expected_constant_dict)

    yield task

    task._constants_db.purge()


def test_visp_constants(visp_science_task_with_constants, expected_constant_dict):

    task = visp_science_task_with_constants
    for k, v in expected_constant_dict.items():
        if k == "POLARIMETER_MODE":
            continue
        assert getattr(task.constants, k.lower()) == v
    assert task.constants.correct_for_polarization == True
