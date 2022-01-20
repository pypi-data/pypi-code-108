from random import randint
from typing import Optional
from typing import Tuple

import numpy as np
import pytest
from astropy.io import fits
from dkist_data_simulator.spec122 import Spec122Dataset
from dkist_header_validator.translator import translate_spec122_to_spec214_l0


@pytest.fixture()
def recipe_run_id():
    return randint(0, 99999)


class S122Headers(Spec122Dataset):
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
