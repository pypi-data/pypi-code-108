from random import randint

import numpy as np
import pytest
from astropy.io import fits
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.fits_access import FitsAccessBase

from dkist_processing_vbi.models.constants import VbiBudName
from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.parsers.vbi_l1_fits_access import VbiL1FitsAccess
from dkist_processing_vbi.tasks.make_movie_frames import MakeVbiMovieFrames
from dkist_processing_vbi.tests.conftest import ensure_all_inputs_used
from dkist_processing_vbi.tests.conftest import FakeGQLClient
from dkist_processing_vbi.tests.conftest import generate_214_l1_fits_frame
from dkist_processing_vbi.tests.conftest import Vbi122ObserveFrames


@pytest.fixture(scope="function")
def raw_make_movie_frames_task(tmp_path, recipe_run_id):
    with MakeVbiMovieFrames(
        recipe_run_id=recipe_run_id, workflow_name="vbi_make_movie_frames", workflow_version="VX.Y"
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        task.num_steps = 4
        task.num_exp_per_step = 2
        task.testing_num_dsps_repeats = 2
        task.constants[VbiBudName.num_spatial_steps.value] = task.num_steps
        task.constants[BudName.num_dsps_repeats.value] = task.testing_num_dsps_repeats
        ds = Vbi122ObserveFrames(
            array_shape=(1, 10, 10),
            num_steps=task.num_steps,
            num_exp_per_step=task.num_exp_per_step,
            num_dsps_repeats=task.testing_num_dsps_repeats,
        )
        header_generator = (d.header() for d in ds)
        for s in range(1, task.num_steps + 1):
            for e in range(1, task.num_exp_per_step + 1):
                for d in range(1, task.testing_num_dsps_repeats + 1):
                    value = (s - 1) + (e - 1) * 2 + (d - 1)
                    data = np.ones((10, 10)) * value
                    header = next(header_generator)
                    hdl = generate_214_l1_fits_frame(data=data, s122_header=header)
                    hdl[1].header["CRVAL1"] = 0.0
                    hdl[1].header["CRVAL2"] = 0.0
                    hdl[1].header["CDELT1"] = 1.0
                    hdl[1].header["CDELT2"] = 1.0
                    hdl[1].header["CRPIX1"] = (s % 2) * 7
                    hdl[1].header["CRPIX2"] = -1 * ((s - 1) // 2 - 1) * 7
                    hdl[1].header["DSPSNUM"] = d
                    hdl[1].header["VBISTP"] = s
                    task.fits_data_write(
                        hdu_list=hdl,
                        tags=[
                            VbiTag.output(),
                            VbiTag.frame(),
                            VbiTag.spatial_step(s),
                            VbiTag.dsps_repeat(d),
                        ],
                    )
        ensure_all_inputs_used(header_generator)
        yield task
        task.scratch.purge()
        task.constants.purge()


@pytest.fixture(scope="module")
def make_movie_frames_task_with_averages(tmp_path_factory):
    recipe_run_id = randint(0, 99999)
    with MakeVbiMovieFrames(
        recipe_run_id=recipe_run_id,
        workflow_name="vbi_make_movie_frames",
        workflow_version="VX.Y",
    ) as task:
        task.scratch = WorkflowFileSystem(
            scratch_base_path=tmp_path_factory.mktemp("scratch"), recipe_run_id=recipe_run_id
        )
        task.num_steps = 4
        task.num_exp_per_step = 1
        task.testing_num_dsps_repeats = 2
        task.constants[VbiBudName.num_spatial_steps.value] = task.num_steps
        task.constants[BudName.num_dsps_repeats.value] = task.testing_num_dsps_repeats
        ds = Vbi122ObserveFrames(
            array_shape=(1, 10, 10),
            num_steps=task.num_steps,
            num_exp_per_step=task.num_exp_per_step,
            num_dsps_repeats=task.testing_num_dsps_repeats,
        )
        header_generator = (d.header() for d in ds)
        for s in range(1, task.num_steps + 1):
            for d in range(1, task.testing_num_dsps_repeats + 1):
                header = next(header_generator)
                value = s - 1 + d - 1
                data = np.ones((10, 10)) * value
                hdl = generate_214_l1_fits_frame(s122_header=header, data=data)
                hdl[1].header["CRVAL1"] = 0.0
                hdl[1].header["CRVAL2"] = 0.0
                hdl[1].header["CDELT1"] = 1.0
                hdl[1].header["CDELT2"] = 1.0
                hdl[1].header["CRPIX1"] = (s % 2) * 7
                hdl[1].header["CRPIX2"] = -1 * ((s - 1) // 2 - 1) * 7
                hdl[1].header["DSPSNUM"] = d
                hdl[1].header["VBISTP"] = s
                task.fits_data_write(
                    hdu_list=hdl,
                    tags=[
                        VbiTag.intermediate(),
                        VbiTag.task("AVG_MOVIE_FRAME"),
                        VbiTag.spatial_step(s),
                        VbiTag.dsps_repeat(d),
                    ],
                )
        ensure_all_inputs_used(header_generator)
        yield task
        task.scratch.purge()
        task.constants.purge()


@pytest.fixture(scope="module")
def place_pos_arguments():
    ref_header = fits.Header()
    ref_header["CRPIX1"] = 8
    ref_header["CRPIX2"] = 8
    data = np.ones((10, 10)) * 7  # No reason this is 7. Nice to have it be different than 1
    hdu = fits.PrimaryHDU(data=data)
    hdu.header["CRPIX1"] = 7.5
    hdu.header["CRPIX2"] = 0.5
    access = FitsAccessBase(hdu=hdu, name=None, auto_squeeze=True)

    output = np.zeros((17, 17))
    px_count = np.zeros((17, 17))

    return access, ref_header, output, px_count


def test_make_movie_frames_task(raw_make_movie_frames_task, mocker):
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    base_expected = np.zeros((17, 17))
    base_counts = np.zeros((17, 17))

    # Step 1
    base_expected[:10, :10] += 1
    base_counts[:10, :10] += 1
    # Step 2
    base_expected[:10, 7:] += 2
    base_counts[:10, 7:] += 1
    # Step 3
    base_expected[7:, :10] += 3
    base_counts[7:, :10] += 1
    # Step 4
    base_expected[7:, 7:] += 4
    base_counts[7:, 7:] += 1

    base_expected /= base_counts

    raw_make_movie_frames_task()

    frame_access_list = list(
        raw_make_movie_frames_task.fits_data_read_fits_access(
            tags=[VbiTag.movie_frame()], cls=VbiL1FitsAccess
        )
    )
    assert len(frame_access_list) == raw_make_movie_frames_task.testing_num_dsps_repeats

    frame_access_list = sorted(frame_access_list, key=lambda x: x.current_dsps_repeat)
    assert [o.current_dsps_repeat for o in frame_access_list] == list(
        range(1, raw_make_movie_frames_task.testing_num_dsps_repeats + 1)
    )
    for i in range(raw_make_movie_frames_task.testing_num_dsps_repeats):
        np.testing.assert_almost_equal(frame_access_list[i].data, base_expected + i)


def test_average_all_exposures(raw_make_movie_frames_task):
    raw_make_movie_frames_task.average_all_exposures()
    for s in range(1, raw_make_movie_frames_task.num_steps + 1):
        for d in range(1, raw_make_movie_frames_task.testing_num_dsps_repeats + 1):
            hdus = list(
                raw_make_movie_frames_task.fits_data_read_hdu(
                    tags=[
                        VbiTag.intermediate(),
                        VbiTag.task("AVG_MOVIE_FRAME"),
                        VbiTag.spatial_step(s),
                        VbiTag.dsps_repeat(d),
                    ]
                )
            )
            assert len(hdus) == 1
            data = hdus[0][1].data
            expected = np.ones((10, 10)) * (s + d - 1)
            np.testing.assert_equal(data, expected)


def test_find_ref_pos(make_movie_frames_task_with_averages):
    access_list = list(
        make_movie_frames_task_with_averages.fits_data_read_fits_access(
            tags=[VbiTag.intermediate(), VbiTag.task("AVG_MOVIE_FRAME"), VbiTag.dsps_repeat(2)],
            cls=VbiL1FitsAccess,
        )
    )
    assert make_movie_frames_task_with_averages.find_ref_pos(access_list) == 1


def test_get_fov_size(make_movie_frames_task_with_averages):
    access_list = list(
        make_movie_frames_task_with_averages.fits_data_read_fits_access(
            tags=[VbiTag.intermediate(), VbiTag.task("AVG_MOVIE_FRAME"), VbiTag.dsps_repeat(1)],
            cls=VbiL1FitsAccess,
        )
    )
    assert make_movie_frames_task_with_averages.get_fov_size(
        access_list, access_list[0].header
    ) == (17, 17)


def test_place_pos_in_full_fov(make_movie_frames_task_with_averages, place_pos_arguments):
    access, ref_header, output, px_count = place_pos_arguments
    make_movie_frames_task_with_averages.place_pos_in_full_fov(*place_pos_arguments)

    expected_output = np.zeros((17, 17))
    expected_counts = np.zeros((17, 17))
    expected_output[8:, 1:10] += 7
    expected_counts[8:, 1:10] += 1

    np.testing.assert_almost_equal(expected_output, output)
    np.testing.assert_almost_equal(expected_counts, px_count)
