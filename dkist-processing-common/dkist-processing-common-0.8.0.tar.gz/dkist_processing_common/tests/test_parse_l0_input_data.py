from typing import Tuple
from unittest.mock import PropertyMock

import numpy as np
import pytest
from astropy.io import fits
from dkist_data_simulator.dataset import key_function
from dkist_data_simulator.spec122 import Spec122Dataset

from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.fits_access import FitsAccessBase
from dkist_processing_common.models.flower_pot import SpilledDirt
from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.models.tags import StemName
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.parsers.single_value_single_key_flower import (
    SingleValueSingleKeyFlower,
)
from dkist_processing_common.parsers.unique_bud import UniqueBud
from dkist_processing_common.tasks.parse_l0_input_data import ParseL0InputData


class VispHeaders(Spec122Dataset):
    def __init__(
        self,
        num_mod: int,
        num_files_per_mod: int,
        array_shape: Tuple[int, ...],
        time_delta: float,
        instrument="visp",
    ):
        self.num_frames = num_mod * num_files_per_mod
        super().__init__(
            (self.num_frames, *array_shape[1:]), array_shape, time_delta, instrument=instrument
        )
        self.num_mod = num_mod
        self.add_constant_key("WAVELNTH")
        self.add_constant_key("TELSCAN")
        self.add_constant_key("CAM__001")
        self.add_constant_key("CAM__002")
        self.add_constant_key("CAM__003")
        self.add_constant_key("CAM__004")
        self.add_constant_key("CAM__005")
        self.add_constant_key("CAM__006")
        self.add_constant_key("CAM__007")
        self.add_constant_key("CAM__008")
        self.add_constant_key("CAM__009")
        self.add_constant_key("CAM__010")
        self.add_constant_key("CAM__011")
        self.add_constant_key("CAM__012")
        self.add_constant_key("CAM__013")
        self.add_constant_key("CAM__014")
        self.add_constant_key("CAM__015")
        self.add_constant_key("CAM__016")
        self.add_constant_key("CAM__017")
        self.add_constant_key("CAM__018")
        self.add_constant_key("CAM__019")
        self.add_constant_key("CAM__020")
        self.add_constant_key("CAM__021")
        self.add_constant_key("CAM__022")
        self.add_constant_key("CAM__023")
        self.add_constant_key("CAM__024")
        self.add_constant_key("CAM__025")
        self.add_constant_key("CAM__026")
        self.add_constant_key("CAM__027")
        self.add_constant_key("CAM__028")
        self.add_constant_key("CAM__029")
        self.add_constant_key("CAM__030")
        self.add_constant_key("CAM__031")
        self.add_constant_key("CAM__032")
        self.add_constant_key("PAC__002")
        self.add_constant_key("PAC__004")
        self.add_constant_key("PAC__006")
        self.add_constant_key("PAC__008")
        self.add_constant_key("VISP_002")
        self.add_constant_key("VISP_007")
        self.add_constant_key("VISP_010", self.num_mod)
        self.add_constant_key("VISP_016")
        self.add_constant_key("VISP_019")

    @key_function("VISP_011")
    def modstate(self, key: str) -> str:
        return self.index % self.num_mod


class ViSPFitsAccess(FitsAccessBase):
    def __init__(self, hdu, name, auto_squeeze=False):
        super().__init__(hdu, name, auto_squeeze=auto_squeeze)
        self.num_mod: int = self.header["VISP_010"]
        self.modstate: int = self.header["VISP_011"]
        self.ip_task_type: str = self.header["DKIST004"]
        self.name = name


@pytest.fixture(scope="function")
def visp_flowers():
    return [
        SingleValueSingleKeyFlower(tag_stem_name=StemName.modstate.value, metadata_key="modstate")
    ]


@pytest.fixture(scope="function")
def visp_buds():
    return [UniqueBud(constant_name=BudName.num_modstates.value, metadata_key="num_mod")]


@pytest.fixture(scope="function")
def empty_flowers():
    class EmptyFlower(Stem):
        def __init__(self):
            super().__init__(stem_name="EMPTY_FLOWER")

        def setter(self, value):
            return SpilledDirt

        def getter(self, key):
            pass  # We'll never get here because we spilled the dirt

    return [EmptyFlower()]


@pytest.fixture(scope="function")
def empty_buds():
    class EmptyBud(Stem):
        def __init__(self):
            super().__init__(stem_name="EMPTY_BUD")

        def setter(self, value):
            return SpilledDirt

        def getter(self, key):
            pass  # We'll never get here because we spilled the dirt

    return [EmptyBud()]


@pytest.fixture(scope="function")
def parse_inputs_task(tmp_path, visp_flowers, visp_buds, empty_flowers, empty_buds, recipe_run_id):
    class TaskClass(ParseL0InputData):
        @property
        def tag_flowers(self):
            return visp_flowers + empty_flowers

        @property
        def constant_flowers(self):
            return visp_buds + empty_buds

        @property
        def fits_parsing_class(self):
            return ViSPFitsAccess

        def run(self):
            pass

    with TaskClass(
        recipe_run_id=1, workflow_name="parse_visp_input_data", workflow_version="VX.Y"
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        task._num_mod = 2
        task._num_files_per_mod = 3
        ds = VispHeaders(
            num_mod=task._num_mod,
            num_files_per_mod=task._num_files_per_mod,
            array_shape=(1, 512, 512),
            time_delta=10,
        )
        header_generator = (d.header() for d in ds)
        for i in range(ds.num_frames):
            generated_header = next(header_generator)
            hdu = fits.PrimaryHDU(
                data=np.zeros(shape=(1, 10, 10)), header=fits.Header(generated_header)
            )
            hdul = fits.HDUList([hdu])
            task.fits_data_write(
                hdu_list=hdul,
                tags=[Tag.input(), Tag.frame()],
                relative_path=f"input/input_{i}.fits",
            )
        yield task
        task.scratch.purge()
        task._constants_db.purge()


@pytest.fixture()
def visp_parse_inputs_task(tmp_path, visp_flowers, visp_buds):
    class TaskClass(ParseL0InputData):
        @property
        def tag_flowers(self):
            return super().tag_flowers + visp_flowers

        @property
        def constant_flowers(self):
            return super().constant_flowers + visp_buds

        @property
        def fits_parsing_class(self):
            return ViSPFitsAccess

        def run(self):
            pass

    with TaskClass(
        recipe_run_id=1, workflow_name="parse_visp_input_data", workflow_version="VX.Y"
    ) as task:
        yield task
        task.scratch.purge()
        task._constants_db.purge()


def test_make_flowerpots(parse_inputs_task):
    """
    Given: ParseInputData task with constant and tag Flowers
    When: Constructing constant and tag FlowerPots
    Then: The Flowers associated with the Task are correctly placed in either FlowerPot
    """

    tag_pot, constant_pot = parse_inputs_task.make_flower_pots()

    assert len(tag_pot.flowers) == 2
    assert len(constant_pot.flowers) == 2
    assert tag_pot.flowers[0].stem_name == StemName.modstate.value
    assert tag_pot.flowers[1].stem_name == "EMPTY_FLOWER"
    assert constant_pot.flowers[0].stem_name == BudName.num_modstates.value
    assert constant_pot.flowers[1].stem_name == "EMPTY_BUD"


def test_subclass_flowers(visp_parse_inputs_task, mocker, max_cs_step_time_sec):
    """
    Given: ParseInputData child class with custom flowers
    When: Making the flower pots
    Then: Both the base and custom flowers are placed in the correct FlowerPots
    """
    tag_pot, constant_pot = visp_parse_inputs_task.make_flower_pots()

    assert len(tag_pot.flowers) == 1
    assert len(constant_pot.flowers) == 8
    assert sorted([f.stem_name for f in tag_pot.flowers]) == sorted([StemName.modstate.value])
    assert sorted([f.stem_name for f in constant_pot.flowers]) == sorted(
        [
            BudName.instrument.value,
            BudName.num_modstates.value,
            BudName.proposal_id.value,
            BudName.average_cadence.value,
            BudName.maximum_cadence.value,
            BudName.minimum_cadence.value,
            BudName.variance_cadence.value,
            BudName.dark_exposure_times.value,
        ]
    )


def test_constants_correct(parse_inputs_task):
    """
    Given: ParseInputData task with a populated constant FlowerPot
    When: Updating pipeline constants
    Then: Pipeline constants are correctly populated
    """
    _, constant_pot = parse_inputs_task.make_flower_pots()
    parse_inputs_task.update_constants(constant_pot)
    assert parse_inputs_task._constants_db == {
        BudName.num_modstates.value: parse_inputs_task._num_mod
    }


def test_tags_correct(parse_inputs_task):
    """
    Given: ParseInputData task with a populated tag FlowerPot
    When: Tagging files with group information
    Then: All files are correctly tagged
    """
    tag_pot, _ = parse_inputs_task.make_flower_pots()
    parse_inputs_task.tag_petals(tag_pot)
    num_mod = parse_inputs_task._num_mod
    files_per_mod = parse_inputs_task._num_files_per_mod
    expected_tag_set = {Tag.input(), Tag.frame()}
    for m in range(num_mod):
        expected_tag_set.add(Tag.modstate(m))
        expected_mod_files = [
            parse_inputs_task.scratch.absolute_path(f"input/input_{i}.fits")
            for i in range(num_mod * files_per_mod)[m::num_mod]
        ]
        assert sorted(list(parse_inputs_task.read(tags=Tag.modstate(m)))) == expected_mod_files

    # To make sure the empty flower didn't make it in to the tags
    assert set(parse_inputs_task.scratch._tag_db.tags) == expected_tag_set
