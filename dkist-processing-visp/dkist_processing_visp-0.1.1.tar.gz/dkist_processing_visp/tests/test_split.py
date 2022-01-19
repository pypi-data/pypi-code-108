import json
from random import choice
from typing import Tuple

import numpy as np
import pytest
from astropy.io import fits
from dkist_data_simulator.dataset import key_function
from dkist_header_validator import spec122_validator
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.tags import Tag

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.tasks.split import SplitBeams
from dkist_processing_visp.tests.conftest import FakeGQLClient
from dkist_processing_visp.tests.conftest import generate_full_visp_fits_frame
from dkist_processing_visp.tests.conftest import VispHeaders
from dkist_processing_visp.visp_l0_fits_access import VispL0FitsAccess


class VispBeamTestHeaders(VispHeaders):
    def __init__(
        self, dataset_shape: Tuple[int, ...], array_shape: Tuple[int, ...], time_delta: float
    ):
        super().__init__(dataset_shape, array_shape, time_delta)

    @key_function("TEST_KEY")
    def test_key(self, key: str):
        return self.index


@pytest.fixture(scope="function")
def split_beams_task(tmp_path, input_dataset_document_with_simple_parameters, recipe_run_id):
    with SplitBeams(
        recipe_run_id=choice(range(1000000)),
        workflow_name="split_visp_beams",
        workflow_version="VX.Y",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        doc_path = task.scratch.workflow_base_path / "dataset_doc.json"
        with open(doc_path, "w") as f:
            f.write(json.dumps(input_dataset_document_with_simple_parameters))
        task.tag(doc_path, VispTag.input_dataset())
        task.num_files = 6
        ds = VispBeamTestHeaders(
            dataset_shape=(task.num_files, 2000, 2560), array_shape=(1, 2000, 2560), time_delta=10
        )
        header_generator = (
            spec122_validator.validate_and_translate_to_214_l0(
                d.header(), return_type=fits.HDUList
            )[0].header
            for d in ds
        )
        for i in range(task.num_files):
            hdul = generate_full_visp_fits_frame(header_generator=header_generator)
            task.fits_data_write(
                hdu_list=hdul,
                tags=[VispTag.input(), VispTag.frame(), f"FOO_{i % task.num_files // 2}"],
            )
        yield task
        task.scratch.purge()
        task.constants.purge()


def compare_split_headers(head1: fits.Header, head2: fits.Header) -> bool:
    """ Needed b/c checksum and naxis2 will change when splitting beams """
    exclude_keys = ["NAXIS2", "CHECKSUM", "DATASUM", "FRAMEID"]
    head1_keys = sorted(head1.keys())
    head2_keys = sorted(head2.keys())
    try:
        head1_keys.remove("FRAMEID")  # B/c this key is added _after_ the split
    except ValueError:
        pass
    try:
        head2_keys.remove("FRAMEID")
    except ValueError:
        pass
    if head1_keys != head2_keys:
        print(f"Header keys are not the same: {head1_keys} != {head2_keys}")
        return False
    for k in head1.keys():
        if k not in exclude_keys and head1[k] != head2[k]:
            print(f"{k}: {head1[k]} != {head2[k]}")
            return False

    return True


def test_split_visp_beams(split_beams_task, mocker):
    """
    Given: A SplitBeams task
    When: Running the task
    Then: All input data produce 2 split beam files, the split happened in the correct place, and the original file is removed
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )

    split_beams_task()
    beam_1_read = split_beams_task.fits_data_read_hdu(tags=[VispTag.beam(1)])
    beam_1_expected = np.ones((1, 1000, 2560))
    for _ in range(split_beams_task.num_files):
        beam_1_file, beam_1_hdu = next(beam_1_read)
        assert beam_1_file.exists()
        np.testing.assert_array_equal(beam_1_expected, beam_1_hdu.data)
    with pytest.raises(StopIteration):
        next(beam_1_read)

    beam_2_read = split_beams_task.fits_data_read_hdu(tags=[VispTag.beam(2)])
    beam_2_expected = np.ones((1, 1000, 2560)) * np.arange(1000)[None, :, None]
    for _ in range(split_beams_task.num_files):
        beam_2_file, beam_2_hdu = next(beam_2_read)
        assert beam_2_file.exists()
        np.testing.assert_array_equal(beam_2_expected, beam_2_hdu.data)
    with pytest.raises(StopIteration):
        next(beam_2_read)

    all_input_paths = list(split_beams_task.read(tags=[Tag.input()]))
    assert len(all_input_paths) == 2 * split_beams_task.num_files


def test_headers_preserved(split_beams_task, mocker):
    """
    Given: A SplitBeams task
    When: Running the task
    Then: The headers from the OG files are carried over to each beam
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    OG_headers_dict = dict()
    for _, hdu in split_beams_task.fits_data_read_hdu(tags=[Tag.input()]):
        foo_num = hdu.header["TEST_KEY"]
        OG_headers_dict[foo_num] = hdu.header

    split_beams_task()
    for _, hdu in split_beams_task.fits_data_read_hdu(tags=[VispTag.beam(1)]):
        foo_num = hdu.header["TEST_KEY"]
        assert compare_split_headers(OG_headers_dict[foo_num], hdu.header)

    for _, hdu in split_beams_task.fits_data_read_hdu(tags=[VispTag.beam(2)]):
        foo_num = hdu.header["TEST_KEY"]
        assert compare_split_headers(OG_headers_dict[foo_num], hdu.header)


def test_tags_preserved(split_beams_task, mocker):
    """
    Given: A SplitBeams task
    When: Running the task
    Then: The tags associated with each input file are carried over to each beam
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    OG_tags_dict = dict()
    for path, hdu in split_beams_task.fits_data_read_hdu(tags=[Tag.input()]):
        foo_num = hdu.header["TEST_KEY"]
        OG_tags_dict[foo_num] = split_beams_task.scratch.tags(path)

    split_beams_task()
    for path, hdu in split_beams_task.fits_data_read_hdu(tags=[VispTag.beam(1)]):
        foo_num = hdu.header["TEST_KEY"]
        assert sorted(OG_tags_dict[foo_num] + [VispTag.beam(1)]) == sorted(
            split_beams_task.scratch.tags(path)
        )

    for path, hdu in split_beams_task.fits_data_read_hdu(tags=[VispTag.beam(2)]):
        foo_num = hdu.header["TEST_KEY"]
        assert sorted(OG_tags_dict[foo_num] + [VispTag.beam(2)]) == sorted(
            split_beams_task.scratch.tags(path)
        )


def test_get_beam_2_object(split_beams_task, mocker):
    """
    Given: A SplitBeam task
    When: Splitting beams
    Then: A Frame ID is assigned to each beam that allows a beam 2 corresponding to a beam 1 to be found
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    split_beams_task()

    beam_1_objects = list(
        split_beams_task.fits_data_read_fits_access(tags=[VispTag.beam(1)], cls=VispL0FitsAccess)
    )
    assert len(beam_1_objects) == split_beams_task.num_files
    for b1 in beam_1_objects:
        b2 = split_beams_task.matching_beam_2_fits_access(b1)
        assert compare_split_headers(b1.header, b2.header)

    split_beams_task.scratch.delete(b2.name)
    with pytest.raises(FileNotFoundError):
        _ = split_beams_task.matching_beam_2_fits_access(b1)
