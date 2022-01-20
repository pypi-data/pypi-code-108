"""
Global test fixtures
"""
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from random import randint
from typing import Dict
from typing import List
from typing import Tuple
from uuid import uuid4

import pytest
from astropy.io import fits
from dkist_data_simulator.dataset import key_function
from dkist_data_simulator.spec122 import Spec122Dataset
from dkist_header_validator import spec122_validator
from dkist_header_validator.translator import sanitize_to_spec214_level1

from dkist_processing_common._util.constants import ConstantsDb
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common._util.tags import TagDB
from dkist_processing_common.models.graphql import InputDatasetResponse
from dkist_processing_common.models.graphql import RecipeInstanceResponse
from dkist_processing_common.models.graphql import RecipeRunResponse
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess
from dkist_processing_common.tasks import WorkflowDataTaskBase
from dkist_processing_common.tasks.mixin.input_dataset import InputDatasetMixin


@pytest.fixture()
def recipe_run_id():
    return randint(0, 99999)


@pytest.fixture()
def tag_db(recipe_run_id) -> TagDB:
    t = TagDB(recipe_run_id=recipe_run_id, task_name="test_tags")
    yield t
    t.purge()
    t.close()


@pytest.fixture()
def tag_db2(recipe_run_id) -> TagDB:
    """
    Another instance of a tag db in the same redis db
    """
    recipe_run_id = recipe_run_id + 15  # same db number but different namespace
    t = TagDB(recipe_run_id=recipe_run_id, task_name="test_tags2")
    yield t
    t.purge()
    t.close()


@pytest.fixture(params=[None, "use_tmp_path"])
def workflow_file_system(request, recipe_run_id, tmp_path) -> Tuple[WorkflowFileSystem, int, Path]:
    if request.param == "use_tmp_path":
        path = tmp_path
    else:
        path = request.param
    wkflow_fs = WorkflowFileSystem(
        recipe_run_id=recipe_run_id,
        task_name="wkflow_fs_test",
        scratch_base_path=path,
    )
    yield wkflow_fs, recipe_run_id, tmp_path
    wkflow_fs.purge(ignore_errors=True)
    tmp_path.rmdir()
    wkflow_fs.close()


@pytest.fixture()
def constants_db(recipe_run_id) -> ConstantsDb:
    constants = ConstantsDb(recipe_run_id=recipe_run_id, task_name="test_constants")
    yield constants
    constants.purge()
    constants.close()


class CommonDataset(Spec122Dataset):
    def __init__(self):
        super().__init__(
            array_shape=(1, 10, 10),
            time_delta=1,
            dataset_shape=(2, 10, 10),
            instrument="visp",
            start_time=datetime(2020, 1, 1, 0, 0, 0),
        )

        self.add_constant_key("TELEVATN", 6.28)
        self.add_constant_key("TAZIMUTH", 3.14)
        self.add_constant_key("TTBLANGL", 1.23)
        self.add_constant_key("INST_FOO", "bar")
        self.add_constant_key("DKIST004", "observe")
        self.add_constant_key("ID___005", "ip id")
        self.add_constant_key("PAC__004", "Sapphire Polarizer")
        self.add_constant_key("PAC__005", "31.2")
        self.add_constant_key("PAC__006", "clear")
        self.add_constant_key("PAC__007", "6.66")
        self.add_constant_key("PAC__008", "DarkShutter")
        self.add_constant_key("INSTRUME", "VISP")
        self.add_constant_key("WAVELNTH", 1080.0)
        self.add_constant_key("DATE-OBS", "2020-01-02T00:00:00.000")
        self.add_constant_key("DATE-END", "2020-01-03T00:00:00.000")
        self.add_constant_key("ID___013", "PROPOSAL_ID1")
        self.add_constant_key("PAC__002", "clear")
        self.add_constant_key("PAC__003", "on")
        self.add_constant_key("TELSCAN", "Raster")
        self.add_constant_key("DKIST008", 1)
        self.add_constant_key("DKIST009", 1)
        self.add_constant_key("BZERO", 0)
        self.add_constant_key("BSCALE", 1)


@pytest.fixture()
def complete_common_header():
    """
    A header with some common by-frame keywords
    """
    ds = CommonDataset()
    header_list = [
        spec122_validator.validate_and_translate_to_214_l0(d.header(), return_type=fits.HDUList)[
            0
        ].header
        for d in ds
    ]

    return header_list[0]


@pytest.fixture()
def complete_l1_only_header(complete_common_header):
    """
    A header with only 214 L1 keywords
    """
    complete_common_header["DAAXES"] = 1
    complete_common_header["DEAXES"] = 1
    complete_common_header["DNAXIS"] = 2
    l1_header = sanitize_to_spec214_level1(complete_common_header)

    return l1_header


class CalibrationSequenceDataset(Spec122Dataset):
    def __init__(
        self,
        array_shape: Tuple[int, ...],
        time_delta: float,
        instrument="visp",
    ):
        self.num_frames_per_CS_step = 5

        # Make up a Calibration sequence. Mostly random except for two clears and two darks at start and end, which
        # we want to test
        self.pol_status = [
            "clear",
            "clear",
            "Sapphire Polarizer",
            "Fused Silica Polarizer",
            "Sapphire Polarizer",
            "clear",
            "clear",
        ]
        self.pol_theta = ["0.0", "0.0", "60.0", "60.0", "120.0", "0.0", "0.0"]
        self.ret_status = ["clear", "clear", "clear", "SiO2 SAR", "clear", "clear", "clear"]
        self.ret_theta = ["0.0", "0.0", "0.0", "45.0", "0.0", "0.0", "0.0"]
        self.dark_status = [
            "DarkShutter",
            "FieldStop (2.8arcmin)",
            "FieldStop (2.8arcmin)",
            "FieldStop (2.8arcmin)",
            "FieldStop (2.8arcmin)",
            "FieldStop (2.8arcmin)",
            "DarkShutter",
        ]

        self.num_steps = len(self.pol_theta)
        dataset_shape = (self.num_steps * self.num_frames_per_CS_step,) + array_shape[1:]
        super().__init__(
            dataset_shape,
            array_shape,
            time_delta,
            instrument=instrument,
            start_time=datetime(2020, 1, 1, 0, 0, 0),
        )
        self.add_constant_key("DKIST004", "polcal")
        self.add_constant_key("TELEVATN", 6.28)
        self.add_constant_key("ID___013", "PROPOSAL_ID1")
        self.add_constant_key("PAC__002", "clear")
        self.add_constant_key("PAC__003", "on")

    @property
    def cs_step(self) -> int:
        return self.index // self.num_frames_per_CS_step

    @key_function("PAC__004")
    def polarizer_status(self, key: str) -> str:
        return self.pol_status[self.cs_step]

    @key_function("PAC__005")
    def polarizer_angle(self, key: str) -> str:
        return str(self.pol_theta[self.cs_step])

    @key_function("PAC__006")
    def retarder_status(self, key: str) -> str:
        return self.ret_status[self.cs_step]

    @key_function("PAC__007")
    def retarder_angle(self, key: str) -> str:
        return str(self.ret_theta[self.cs_step])

    @key_function("PAC__008")
    def gos_level3_status(self, key: str) -> str:
        return self.dark_status[self.cs_step]


class NonPolCalDataset(Spec122Dataset):
    def __init__(self):
        super().__init__(
            dataset_shape=(4, 2, 2),
            array_shape=(1, 2, 2),
            time_delta=1,
            instrument="visp",
            start_time=datetime(2020, 1, 1, 0, 0, 0),
        )  # Instrument doesn't matter
        self.add_constant_key("DKIST004", "dark")  # Anything that's not polcal
        self.add_constant_key("ID___013", "PROPOSAL_ID1")
        self.add_constant_key("TELEVATN", 6.28)
        self.add_constant_key("PAC__002", "clear")
        self.add_constant_key("PAC__003", "on")
        self.add_constant_key("PAC__004", "clear")
        self.add_constant_key("PAC__005", "0.0")
        self.add_constant_key("PAC__006", "clear")
        self.add_constant_key("PAC__007", "0.0")
        self.add_constant_key("PAC__008", "DarkShutter")


@pytest.fixture(scope="session")
def grouped_cal_sequence_headers() -> Dict[int, List[L0FitsAccess]]:
    ds = CalibrationSequenceDataset(array_shape=(1, 2, 2), time_delta=2.0)
    header_list = [
        spec122_validator.validate_and_translate_to_214_l0(d.header(), return_type=fits.HDUList)[
            0
        ].header
        for d in ds
    ]
    expected_cs_dict = defaultdict(list)
    for i in range(ds.num_steps):
        for j in range(ds.num_frames_per_CS_step):
            expected_cs_dict[i].append(L0FitsAccess.from_header(header_list.pop(0)))

    return expected_cs_dict


@pytest.fixture(scope="session")
def non_polcal_headers() -> List[L0FitsAccess]:
    ds = NonPolCalDataset()
    header_list = [
        spec122_validator.validate_and_translate_to_214_l0(d.header(), return_type=fits.HDUList)[
            0
        ].header
        for d in ds
    ]
    obj_list = [L0FitsAccess.from_header(h) for h in header_list]
    return obj_list


@pytest.fixture(scope="session")
def max_cs_step_time_sec() -> float:
    """ Max CS step time in seconds """
    return 20.0


class InputDatasetTask(WorkflowDataTaskBase, InputDatasetMixin):
    def run(self):
        pass


@pytest.fixture
def construct_task_with_input_dataset(tmp_path, recipe_run_id):
    def construct_task(input_dataset_dict):
        with InputDatasetTask(
            recipe_run_id=recipe_run_id,
            workflow_name="workflow_name",
            workflow_version="workflow_version",
        ) as task:
            task.scratch = WorkflowFileSystem(
                recipe_run_id=recipe_run_id,
                scratch_base_path=tmp_path,
            )
            task.scratch.workflow_base_path = tmp_path / str(recipe_run_id)
            file_path = task.scratch.workflow_base_path / Path(f"{uuid4().hex[:6]}.ext")
            file_path.write_text(data=json.dumps(input_dataset_dict))
            task.tag(path=file_path, tags=Tag.input_dataset())
            input_dataset_object = json.loads(json.dumps(input_dataset_dict))
            yield task, input_dataset_object
            task.scratch.purge()
            task.constants.purge()

    return construct_task


class FakeGQLClient:
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def execute_gql_query(**kwargs):
        query_base = kwargs["query_base"]

        if query_base == "recipeRuns":
            return [
                RecipeRunResponse(
                    recipeInstanceId=1,
                    recipeInstance=RecipeInstanceResponse(
                        recipeId=1,
                        inputDataset=InputDatasetResponse(
                            inputDatasetId=1,
                            isActive=True,
                            inputDatasetDocument='{"bucket": "bucket-name", "parameters": [{"parameterName": "", "parameterValues": [{"parameterValueId": 1, "parameterValue": "[[1,2,3],[4,5,6],[7,8,9]]", "parameterValueStartDate": "1/1/2000"}]}], "frames": ["objectKey1", "objectKey2", "objectKeyN"]}',
                        ),
                    ),
                )
            ]

    @staticmethod
    def execute_gql_mutation(**kwargs):
        ...
