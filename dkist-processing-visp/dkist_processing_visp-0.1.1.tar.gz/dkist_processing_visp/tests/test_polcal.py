from datetime import datetime
from unittest.mock import PropertyMock

import numpy as np
import pytest
from astropy.io import fits
from dkist_header_validator import spec122_validator
from dkist_processing_common._util.scratch import WorkflowFileSystem

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.tasks.instrument_polarization import InstrumentPolarizationCalibration
from dkist_processing_visp.tests.conftest import FakeGQLClient
from dkist_processing_visp.tests.conftest import generate_fits_frame
from dkist_processing_visp.tests.conftest import VispHeadersValidPolcalFrames


@pytest.fixture(scope="function")
def instrument_polarization_calibration_task(tmp_path, recipe_run_id, mocker):

    with InstrumentPolarizationCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="instrument_polarization_calibration",
        workflow_version="VX.Y",
    ) as task:

        num_beams = 2
        num_modstates = 2
        num_cs_steps = 2
        exposure_time = 0.01  # From VispHeadersValidPolcalFrames fixture
        all_zeros = np.zeros((10, 10))
        all_ones = np.ones((10, 10))
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)

        mocker.patch(
            "dkist_processing_visp.visp_base.VispScienceTask.num_modulator_states",
            new_callable=PropertyMock,
            return_value=num_modstates,
        )
        mocker.patch(
            "dkist_processing_visp.visp_base.VispScienceTask.num_cs_steps",
            new_callable=PropertyMock,
            return_value=num_cs_steps,
        )
        mocker.patch(
            "dkist_processing_visp.visp_base.VispScienceTask.polcal_exposure_times",
            new_callable=PropertyMock,
            return_value=[exposure_time],
        )
        mocker.patch(
            "dkist_processing_visp.visp_base.VispScienceTask.correct_for_polarization",
            new_callable=PropertyMock,
            return_value=True,
        )
        mocker.patch(
            "dkist_processing_pac.GenerateDemodMatrices.DC_main",
            new_callable=PropertyMock,
            return_value=np.ones((1, 1, 1, 4, num_modstates)),
        )
        mocker.patch(
            "dkist_processing_pac.FittingFramework.run_core",
            new_callable=PropertyMock,
            return_value=(object(), object(), object()),
        )

        # Create fake geometric objects
        angle = np.array([0.0])
        offset = np.array([0.0, 0.0])
        spec_shift = np.zeros(10)
        for beam in range(1, num_beams + 1):
            task.write_intermediate_arrays(arrays=angle, beam=beam, task="GEOMETRIC_ANGLE")
            task.write_intermediate_arrays(
                arrays=spec_shift, beam=beam, task="GEOMETRIC_SPEC_SHIFTS"
            )
            for modstate in range(1, num_modstates + 1):
                task.write_intermediate_arrays(
                    arrays=offset, beam=beam, modstate=modstate, task="GEOMETRIC_OFFSET"
                )

        # Create fake dark intermediate arrays
        for beam in range(1, num_beams + 1):
            task.write_intermediate_arrays(
                all_zeros, beam=beam, task="DARK", exposure_time=exposure_time
            )

        start_time = datetime.now()
        for beam in range(1, num_beams + 1):
            # Create a fake solar gain array for this beam and modstate
            for modstate in range(1, num_modstates + 1):
                gain_hdul = fits.HDUList([fits.PrimaryHDU(data=all_ones)])
                task.fits_data_write(
                    hdu_list=gain_hdul,
                    tags=[
                        VispTag.intermediate(),
                        VispTag.frame(),
                        VispTag.task("SOLAR_GAIN"),
                        VispTag.beam(beam),
                        VispTag.modstate(modstate),
                    ],
                )
                ds = VispHeadersValidPolcalFrames(
                    dataset_shape=(num_cs_steps, 10, 10),
                    array_shape=(1, 10, 10),
                    time_delta=10,
                    num_modstates=num_modstates,
                    modstate=modstate,
                    start_time=start_time,
                )
                header_generator = (
                    spec122_validator.validate_and_translate_to_214_l0(
                        d.header(), return_type=fits.HDUList
                    )[0].header
                    for d in ds
                )
                # cs_step does not map to a single keyword, so not needed in the fake headers
                for cs_step in range(num_cs_steps):
                    hdul = generate_fits_frame(header_generator=header_generator)
                    task.fits_data_write(
                        hdu_list=hdul,
                        tags=[
                            VispTag.beam(beam),
                            VispTag.task("POLCAL"),
                            VispTag.modstate(modstate),
                            VispTag.cs_step(cs_step),
                            VispTag.input(),
                            VispTag.frame(),
                            VispTag.exposure_time(exposure_time),
                        ],
                    )

        yield task
        task.scratch.purge()
        task.constants.purge()


def test_instrument_polarization_calibration_task(instrument_polarization_calibration_task, mocker):
    """
    Given: A ScienceCalibration task
    When: Calling the task instance
    Then: Only one average intermediate dark frame exists
    """

    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )

    # When
    task = instrument_polarization_calibration_task
    task()

    # Then
    for beam in range(1, 2 + 1):
        tags = [
            VispTag.intermediate(),
            VispTag.task("DEMOD_MATRICES"),
            VispTag.beam(beam),
        ]
        assert len(list(task.read(tags=tags))) == 1
