import json
from random import choice

import numpy as np
import pytest
from astropy.io import fits
from dkist_header_validator import spec122_validator
from dkist_processing_common._util.scratch import WorkflowFileSystem

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.tests.conftest import generate_fits_frame
from dkist_processing_visp.tests.conftest import VispHeadersValidDarkFrames
from dkist_processing_visp.visp_base import VispScienceTask

NUM_BEAMS = 2
NUM_MODSTATES = 8
NUM_CS_STEPS = 6
NUM_RASTER_STEPS = 10


@pytest.fixture(scope="function")
def visp_science_task(input_dataset_document_with_simple_parameters):
    class Task(VispScienceTask):
        def run(self):
            ...

    task = Task(
        recipe_run_id=choice(range(1000000)),
        workflow_name="parse_visp_input_data",
        workflow_version="VX.Y",
    )
    doc_path = task.scratch.workflow_base_path / "dataset_doc.json"
    with open(doc_path, "w") as f:
        f.write(json.dumps(input_dataset_document_with_simple_parameters))
    task.tag(doc_path, VispTag.input_dataset())

    task.constants["NUM_MODSTATES"] = NUM_MODSTATES
    task.constants["NUM_CS_STEPS"] = NUM_CS_STEPS
    task.constants["NUM_RASTER_STEPS"] = NUM_RASTER_STEPS
    task.constants["POLARIMETER_MODE"] = "observe_polarimetric"

    yield task

    task.constants.purge()


@pytest.fixture(scope="function")
def visp_intensity_task():
    class Task(VispScienceTask):
        def run(self):
            ...

    task = Task(
        recipe_run_id=choice(range(1000000)),
        workflow_name="parse_visp_input_data",
        workflow_version="VX.Y",
    )

    task.constants["POLARIMETER_MODE"] = "Stokes-I"

    yield task

    task.constants.purge()


# TODO: This isn't used anywhere and doesn't work(?) get rid of it
@pytest.fixture(scope="function")
def create_generic_intermediate_frames(tmp_path):
    scratch = WorkflowFileSystem(scratch_base_path=tmp_path)
    ds = VispHeadersValidDarkFrames(
        dataset_shape=(5, 512, 512), array_shape=(1, 512, 512), time_delta=10
    )
    header_generator = (
        spec122_validator.validate_and_translate_to_214_l0(d.header(), return_type=fits.HDUList)[
            0
        ].header
        for d in ds
    )
    for i in range(3):
        hdul = generate_fits_frame(header_generator=header_generator)
        task.fits_data_write(
            hdu_list=hdul,
            tags=[
                VispTag.input(),
                VispTag.frame(),
                VispTag.task("DARK"),
                VispTag.beam(1),
            ],
        )
    for i in range(2):
        hdul = generate_fits_frame(header_generator=header_generator)
        task.fits_data_write(
            hdu_list=hdul,
            tags=[
                VispTag.input(),
                VispTag.frame(),
                VispTag.task("DARK"),
                VispTag.beam(2),
            ],
        )
    yield task
    task.scratch.purge()
    task.constants.purge()


def test_num_modulator_states(visp_science_task):
    """
    Given: A VispScienceTask task
    When: Checking the number of modulator states
    Then: The value from the correct constant in the constants object is retrieved
    """
    assert visp_science_task.num_modulator_states == NUM_MODSTATES


def test_num_cs_steps(visp_science_task):
    """
    Given: A VispScienceTask task
    When: Checking the number of cs steps
    Then: The value from the correct constant in the constants object is retrieved
    """
    assert visp_science_task.num_cs_steps == NUM_CS_STEPS


def test_num_raster_steps(visp_science_task):
    """
    Given: A VispScienceTask task
    When: Checking the number of raster steps
    Then: The value from the correct constant in the constants object is retrieved
    """
    assert visp_science_task.num_raster_steps == NUM_RASTER_STEPS


def test_correct_for_polarization(visp_science_task):
    """
    Given: A VispScienceTask task
    When: Checking whether correction for polarization is required
    Then: The value from the correct constant in the constants object is retrieved
          and the property correct_for_polarization returns the correct boolean value
    """
    assert visp_science_task.correct_for_polarization


def test_not_correct_for_polarization(visp_intensity_task):
    """
    Given: A VispScienceTask task
    When: Checking whether correction for polarization is not required
    Then: The value from the correct constant in the constants object is retrieved
          and the property correct_for_polarization returns the correct boolean value
    """
    assert not visp_intensity_task.correct_for_polarization


def test_beam_border(visp_science_task):
    """
    Given: A VispScienceTask task
    When: Checking the beam border location
    Then: The value from the correct constant in input dataset parameters is retrieved
    """
    # Is there a better way to test this? I testing against the default value used in the property
    assert visp_science_task.beam_border == 1000


# Note: matching_beam_2_fits_access is tested in test_split.py


def test_write_intermediate_arrays(visp_science_task):
    """
    Given: A VispScienceTask task
    When: Using the helper to write a single intermediate array
    Then: The array is written and tagged correctly
    """
    data = np.random.random((10, 10))
    head = fits.Header()
    head["TEST"] = "foo"
    visp_science_task.write_intermediate_arrays(
        arrays=data, headers=head, beam=1, dsps_repeat=2, raster_step=3, task="BAR"
    )
    loaded_list = list(
        visp_science_task.fits_data_read_hdu(
            tags=[
                VispTag.intermediate(),
                VispTag.frame(),
                VispTag.beam(1),
                VispTag.dsps_repeat(2),
                VispTag.raster_step(3),
                VispTag.task("BAR"),
            ]
        )
    )
    assert len(loaded_list) == 1
    hdu = loaded_list[0][1]
    np.testing.assert_equal(hdu.data, data)
    assert hdu.header["TEST"] == "foo"


def test_write_intermediate_arrays_none_header(visp_science_task):
    """
    Given: A VispScienceTask task
    When: Using the helper to write a single intermediate array with no header
    Then: The array is written and tagged correctly
    """
    data = np.random.random((10, 10))
    visp_science_task.write_intermediate_arrays(
        arrays=data, headers=None, beam=1, dsps_repeat=2, raster_step=3, task="BAR"
    )
    loaded_list = list(
        visp_science_task.fits_data_read_hdu(
            tags=[
                VispTag.intermediate(),
                VispTag.frame(),
                VispTag.beam(1),
                VispTag.dsps_repeat(2),
                VispTag.raster_step(3),
                VispTag.task("BAR"),
            ]
        )
    )
    assert len(loaded_list) == 1
    hdu = loaded_list[0][1]
    np.testing.assert_equal(hdu.data, data)


@pytest.fixture
def visp_science_task_with_tagged_intermediates(tmpdir_factory):
    class Task(VispScienceTask):
        def run(self):
            ...

    task = Task(
        recipe_run_id=choice(range(1000000)),
        workflow_name="parse_visp_input_data",
        workflow_version="VX.Y",
    )
    task._scratch = WorkflowFileSystem(scratch_base_path=tmpdir_factory.mktemp("data"))
    tag_names = [["beam"], ["exposure_time", "task"], ["modstate"]]
    tag_vals = [[1], [10.23, "dark"], [3]]
    tag_fcns = [[getattr(VispTag, n) for n in nl] for nl in tag_names]
    tag_list = [[f(v) for f, v in zip(fl, vl)] for fl, vl in zip(tag_fcns, tag_vals)]
    for i, tags in enumerate(tag_list):
        hdul = fits.HDUList([fits.PrimaryHDU(data=np.ones((2, 2)) * i)])
        fname = task.scratch.workflow_base_path / f"file{i}.fits"
        hdul.writeto(fname)
        task.tag(fname, tags + [VispTag.intermediate(), VispTag.frame()])

    yield task, tag_names, tag_vals

    task.constants.purge()
    task.scratch.purge()


def test_load_intermediate_arrays(visp_science_task_with_tagged_intermediates):

    task, tag_names, tag_vals = visp_science_task_with_tagged_intermediates
    kwarg_list = [{k: v for k, v in zip(kl, vl)} for kl, vl in zip(tag_names, tag_vals)]
    for i, kwargs in enumerate(kwarg_list):
        arrays = list(task.load_intermediate_arrays(**kwargs))
        assert len(arrays) == 1
        np.testing.assert_equal(arrays[0], np.ones((2, 2)) * i)


def test_load_intermediate_dark_array():
    pass


def test_load_intermediate_lamp_gain_array():
    pass


def test_load_intermediate_solar_gain_array():
    pass


def test_load_intermediate_geometric_hdu_list():
    pass


def test_load_intermediate_demodulated_arrays():
    pass
