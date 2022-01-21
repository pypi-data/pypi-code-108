from itertools import chain

import pytest
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.tags import Tag

from dkist_processing_visp.tasks.parse import ParseL0VispInputData
from dkist_processing_visp.tests.conftest import FakeGQLClient
from dkist_processing_visp.tests.conftest import generate_fits_frame
from dkist_processing_visp.tests.conftest import VispHeadersValidDarkFrames
from dkist_processing_visp.tests.conftest import VispHeadersValidLampGainFrames
from dkist_processing_visp.tests.conftest import VispHeadersValidObserveFrames
from dkist_processing_visp.tests.conftest import VispHeadersValidPolcalFrames
from dkist_processing_visp.tests.conftest import VispHeadersValidSolarGainFrames


@pytest.fixture(scope="function")
def parse_inputs_valid_task(tmp_path, recipe_run_id, assign_input_dataset_doc_to_task):
    with ParseL0VispInputData(
        recipe_run_id=recipe_run_id,
        workflow_name="parse_visp_input_data",
        workflow_version="VX.Y",
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            task._scratch = WorkflowFileSystem(
                scratch_base_path=tmp_path, recipe_run_id=recipe_run_id
            )
            assign_input_dataset_doc_to_task(task)
            ds1 = VispHeadersValidDarkFrames(
                dataset_shape=(2, 2, 2), array_shape=(1, 2, 2), time_delta=10
            )
            ds2 = VispHeadersValidLampGainFrames(
                dataset_shape=(2, 2, 2),
                array_shape=(2, 2, 1),
                time_delta=10,
                num_modstates=2,
                modstate=1,
            )
            ds3 = VispHeadersValidSolarGainFrames(
                dataset_shape=(2, 2, 2),
                array_shape=(2, 2, 1),
                time_delta=10,
                num_modstates=2,
                modstate=1,
            )
            ds4 = VispHeadersValidPolcalFrames(
                dataset_shape=(2, 2, 2),
                array_shape=(2, 2, 1),
                time_delta=30,
                num_modstates=2,
                modstate=1,
            )
            ds5 = VispHeadersValidObserveFrames(
                dataset_shape=(8, 2, 2),
                array_shape=(1, 2, 2),
                time_delta=10,
                num_dsps_repeats=2,
                dsps_repeat=1,
                num_raster_steps=2,
                raster_step=1,
                num_modstates=2,
                modstate=1,
                polarimeter_mode="observe_polarimetric",
            )
            ds = chain(ds1, ds2, ds3, ds4, ds5)
            header_generator = (d.header() for d in ds)
            for i in range(16):
                hdul = generate_fits_frame(header_generator=header_generator)
                task.fits_data_write(hdu_list=hdul, tags=[Tag.input(), Tag.frame()])
            yield task
        except:
            raise
        finally:
            task.scratch.purge()
            task._constants_db.purge()


def test_parse_visp_input_data(parse_inputs_valid_task, mocker):
    """
    Given: A ParseVispInputData task
    When: Calling the task instance
    Then: The correct number of translated files are tagged with input and have correct filenames
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    # When
    parse_inputs_valid_task()
    # Then
    translated_input_files = parse_inputs_valid_task.read(tags=[Tag.input()])
    for i in range(16):
        filepath = next(translated_input_files)
        assert filepath.exists()
    with pytest.raises(StopIteration):
        next(translated_input_files)


def test_parse_visp_input_data_constants(parse_inputs_valid_task, mocker):
    """
    Given: A ParseVispInputData task
    When: Calling the task instance
    Then: Constants are in the constants object as expected
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    # When
    parse_inputs_valid_task()
    # Then
    assert parse_inputs_valid_task._constants_db["NUM_MODSTATES"] == 2
    assert parse_inputs_valid_task._constants_db["NUM_DSPS_REPEATS"] == 2
    assert parse_inputs_valid_task._constants_db["NUM_RASTER_STEPS"] == 2
    assert parse_inputs_valid_task._constants_db["WAVELENGTH"] == 656.28
    assert parse_inputs_valid_task._constants_db["SPECTRAL_LINE"] == "VISP H alpha"
    assert parse_inputs_valid_task._constants_db["DARK_EXPOSURE_TIMES"] == [1.0]
    assert parse_inputs_valid_task._constants_db["LAMP_EXPOSURE_TIMES"] == [10.0]
    assert parse_inputs_valid_task._constants_db["SOLAR_EXPOSURE_TIMES"] == [20.0]
    assert parse_inputs_valid_task._constants_db["POLCAL_EXPOSURE_TIMES"] == [0.01]
    assert parse_inputs_valid_task._constants_db["OBSERVE_EXPOSURE_TIMES"] == [0.02, 0.03]


def test_parse_visp_input_data_darks_found(parse_inputs_valid_task, mocker):
    """
    Given: A valid parse input task
    When: Calling the task instance
    Then: Input files are tagged as dark
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    parse_inputs_valid_task()
    assert list(parse_inputs_valid_task.read(tags=[Tag.input(), Tag.task("DARK")]))


def test_parse_visp_input_data_lamp_gains_found(parse_inputs_valid_task, mocker):
    """
    Given: A valid parse input task
    When: Calling the task instance
    Then: Input files are tagged as lamp gain
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    parse_inputs_valid_task()
    assert list(parse_inputs_valid_task.read(tags=[Tag.input(), Tag.task("LAMP_GAIN")]))


def test_parse_visp_input_data_solar_gains_found(parse_inputs_valid_task, mocker):
    """
    Given: A valid parse input task
    When: Calling the task instance
    Then: Input files are tagged as solar gain
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    parse_inputs_valid_task()
    assert list(parse_inputs_valid_task.read(tags=[Tag.input(), Tag.task("SOLAR_GAIN")]))


def test_parse_visp_input_data_polcals_found(parse_inputs_valid_task, mocker):
    """
    Given: A valid parse input task
    When: Calling the task instance
    Then: Input files are tagged as polcal
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    parse_inputs_valid_task()
    assert list(parse_inputs_valid_task.read(tags=[Tag.input(), Tag.task("POLCAL")]))


def test_parse_visp_input_data_observes_found(parse_inputs_valid_task, mocker):
    """
    Given: A valid parse input task
    When: Calling the task instance
    Then: Input files are tagged as observe
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    parse_inputs_valid_task()
    assert list(parse_inputs_valid_task.read(tags=[Tag.input(), Tag.task("OBSERVE")]))


def test_parse_visp_values(parse_inputs_valid_task, mocker):
    """
    :Given: A valid parse input task
    :When: Calling the task instance
    :Then: Values are correctly loaded into the constants mutable mapping
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    parse_inputs_valid_task()
    assert parse_inputs_valid_task.constants.instrument == "VISP"
    assert parse_inputs_valid_task.constants.average_cadence == 10
    assert parse_inputs_valid_task.constants.maximum_cadence == 10
    assert parse_inputs_valid_task.constants.minimum_cadence == 10
    assert parse_inputs_valid_task.constants.variance_cadence == 0
