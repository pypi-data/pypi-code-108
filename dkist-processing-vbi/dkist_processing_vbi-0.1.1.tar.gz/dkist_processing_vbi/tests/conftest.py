from random import randint
from typing import Generator
from typing import Optional
from typing import Tuple

import numpy as np
import pytest
from astropy.io import fits
from dkist_data_simulator.dataset import key_function
from dkist_data_simulator.spec122 import Spec122Dataset
from dkist_header_validator.translator import sanitize_to_spec214_level1
from dkist_header_validator.translator import translate_spec122_to_spec214_l0
from dkist_processing_common.models.graphql import InputDatasetResponse
from dkist_processing_common.models.graphql import RecipeInstanceResponse
from dkist_processing_common.models.graphql import RecipeRunResponse


@pytest.fixture()
def recipe_run_id():
    return randint(0, 99999)


class VbiS122Headers(Spec122Dataset):
    def __init__(
        self,
        array_shape: Tuple[int, ...],
        num_steps: int = 4,
        num_exp_per_step: int = 1,
        num_dsps_repeats: int = 5,
        time_delta: float = 10.0,
        instrument: str = "vbi",
    ):
        dataset_shape = (num_exp_per_step * num_steps * num_dsps_repeats,) + array_shape[-2:]
        super().__init__(
            dataset_shape=dataset_shape,
            array_shape=array_shape,
            time_delta=time_delta,
            instrument=instrument,
        )
        self.num_steps = num_steps
        self.num_exp_per_step = num_exp_per_step
        self.num_dsps_repeats = num_dsps_repeats
        self.add_constant_key("WAVELNTH", 656.282)
        self.add_constant_key("TELSCAN", "None")
        self.add_constant_key("ID___004")
        self.add_constant_key("ID___013")
        self.add_constant_key("CAM__001", "test")
        self.add_constant_key("CAM__002", "test")
        self.add_constant_key("CAM__003", 1)
        self.add_constant_key("CAM__004", 1.0)
        self.add_constant_key("CAM__005", 1.0)
        self.add_constant_key("CAM__006", 1.0)
        self.add_constant_key("CAM__007", 1)
        self.add_constant_key("CAM__008", 1)
        self.add_constant_key("CAM__009", 1)
        self.add_constant_key("CAM__010", 1)
        self.add_constant_key("CAM__011", 1)
        self.add_constant_key("CAM__012", 1)
        self.add_constant_key("CAM__013", 1)
        self.add_constant_key("CAM__014", 1)
        self.add_constant_key("CAM__015", 1)
        self.add_constant_key("CAM__016", 1)
        self.add_constant_key("CAM__017", 1)
        self.add_constant_key("CAM__018", 1)
        self.add_constant_key("CAM__019", 1)
        self.add_constant_key("CAM__020", 1)
        self.add_constant_key("CAM__021", 1)
        self.add_constant_key("CAM__022", 1)
        self.add_constant_key("CAM__023", 1)
        self.add_constant_key("CAM__024", 1)
        self.add_constant_key("CAM__025", 1)
        self.add_constant_key("CAM__026", 1)
        self.add_constant_key("CAM__027", 1)
        self.add_constant_key("CAM__028", 1)
        self.add_constant_key("CAM__029", 1)
        self.add_constant_key("CAM__030", 1)
        self.add_constant_key("CAM__031", 1)
        self.add_constant_key("CAM__032", 1)
        self.add_constant_key("VBI__003", num_steps)
        self.add_constant_key("DKIST008", num_dsps_repeats)

    @key_function("VBI__004")
    def spatial_step(self, key: str) -> int:
        return ((self.index // self.num_exp_per_step) % self.num_steps) + 1

    @key_function("DKIST009")
    def dsps_num(self, key: str) -> int:
        return (self.index // (self.num_steps * self.num_exp_per_step * self.num_dsps_repeats)) + 1


class Vbi122DarkFrames(VbiS122Headers):
    def __init__(self, array_shape: Tuple[int, ...], num_steps: int = 4, num_exp_per_step: int = 1):
        super().__init__(
            array_shape, num_steps=num_steps, num_exp_per_step=num_exp_per_step, num_dsps_repeats=1
        )
        self.add_constant_key("DKIST004", "dark")


class Vbi122GainFrames(VbiS122Headers):
    def __init__(self, array_shape: Tuple[int, ...], num_steps: int = 4, num_exp_per_step: int = 1):
        super().__init__(
            array_shape, num_steps=num_steps, num_exp_per_step=num_exp_per_step, num_dsps_repeats=1
        )
        self.add_constant_key("DKIST004", "gain")
        self.add_constant_key("PAC__002", "Clear")
        self.add_constant_key("TELSCAN", "Raster")


class Vbi122ObserveFrames(VbiS122Headers):
    def __init__(
        self,
        array_shape: Tuple[int, ...],
        num_steps: int = 4,
        num_exp_per_step: int = 1,
        num_dsps_repeats: int = 5,
    ):
        super().__init__(
            array_shape,
            num_steps=num_steps,
            num_exp_per_step=num_exp_per_step,
            num_dsps_repeats=num_dsps_repeats,
        )
        self.add_constant_key("DKIST004", "observe")


class Vbi122SummitObserveFrames(VbiS122Headers):
    def __init__(
        self,
        array_shape: Tuple[int, ...],
        num_steps: int = 4,
        num_exp_per_step: int = 1,
        num_dsps_repeats: int = 1,
    ):
        super().__init__(
            array_shape,
            num_steps=num_steps,
            num_exp_per_step=num_exp_per_step,
            num_dsps_repeats=num_dsps_repeats,
        )
        self.add_constant_key("DKIST004", "observe")
        self.add_constant_key("VBI__005", "SpeckleImaging")


def generate_214_l0_fits_frame(
    s122_header: fits.Header, data: Optional[np.ndarray] = None
) -> fits.HDUList:
    """ Convert S122 header into 214 L0 """
    if data is None:
        data = np.ones((1, 10, 10))
    translated_header = translate_spec122_to_spec214_l0(s122_header)
    del translated_header["COMMENT"]
    hdu = fits.PrimaryHDU(data=data, header=fits.Header(translated_header))
    return fits.HDUList([hdu])


def generate_214_l1_fits_frame(
    s122_header: fits.Header, data: Optional[np.ndarray] = None
) -> fits.HDUList:
    """Convert S122 header into 214 L1 only.

    This does NOT include populating all L1 headers, just removing 214 L0 only headers

    NOTE: The stuff you care about will be in hdulist[1]
    """
    l0_s214_hdul = generate_214_l0_fits_frame(s122_header, data)
    l0_header = l0_s214_hdul[0].header
    l0_header["DNAXIS"] = 3
    l0_header["DAAXES"] = 2
    l0_header["DEAXES"] = 1
    l1_header = sanitize_to_spec214_level1(input_headers=l0_header)
    hdu = fits.CompImageHDU(header=l1_header, data=l0_s214_hdul[0].data)

    return fits.HDUList([fits.PrimaryHDU(), hdu])


def ensure_all_inputs_used(header_generator: Generator) -> None:
    try:
        _ = next(header_generator)
        raise ValueError("Did not write all of the input data!")
    except StopIteration:
        return


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
        pass
