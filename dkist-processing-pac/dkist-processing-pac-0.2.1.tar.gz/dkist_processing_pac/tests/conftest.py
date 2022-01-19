from typing import Tuple, List, Union

import numpy as np
import pytest
from astropy.io import fits
from dkist_data_simulator.dataset import key_function
from dkist_data_simulator.spec122 import Spec122Dataset
from dkist_header_validator import spec122_validator
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess


class CalibrationSequenceDataset(Spec122Dataset):
    def __init__(
        self,
        array_shape: Tuple[int, ...],
        time_delta: float,
        pol_status: List[str],
        pol_theta: List[float],
        ret_status: List[str],
        ret_theta: List[float],
        dark_status: List[str],
        instrument: str = "visp",
        num_mod: int = 3,
    ):
        self.num_mod = num_mod

        # Make up a Calibration sequence. Mostly random except for two clears and two darks at start and end, which
        # we want to test
        self.pol_status = pol_status
        self.pol_theta = pol_theta
        self.ret_status = ret_status
        self.ret_theta = ret_theta
        self.dark_status = dark_status
        self.num_steps = len(self.pol_theta)
        dataset_shape = (self.num_steps * self.num_mod,) + array_shape[1:]
        super().__init__(dataset_shape, array_shape, time_delta, instrument=instrument)
        self.add_constant_key("DKIST004", "polcal")
        self.add_constant_key("WAVELNTH", 666.)

    @property
    def cs_step(self) -> int:
        return self.index // self.num_mod

    @key_function("VISP_011")
    def modstate(self, key: str) -> int:
        return (self.index % self.num_mod) + 1

    @key_function("VISP_010")
    def nummod(self, key: str) -> int:
        return self.num_mod

    @key_function("PAC__004")
    def polarizer_status(self, key: str) -> str:
        return self.pol_status[self.cs_step]

    @key_function("PAC__005")
    def polarizer_angle(self, key: str) -> str:
        return str(self.pol_theta[self.cs_step])

    @key_function("PAC__006")
    def retarter_status(self, key: str) -> str:
        return self.ret_status[self.cs_step]

    @key_function("PAC__007")
    def retarder_angle(self, key: str) -> str:
        return str(self.ret_theta[self.cs_step])

    @key_function("PAC__008")
    def gos_level3_status(self, key: str) -> str:
        return self.dark_status[self.cs_step]

class InstAccess(L0FitsAccess):
    def __init__(self, hdu: Union[fits.ImageHDU, fits.PrimaryHDU, fits.CompImageHDU]):
        super().__init__(hdu, auto_squeeze=False)
        self.modulator_state = self.header["VSPSTNUM"]
        self.number_of_modulator_states = self.header["VSPNUMST"]

@pytest.fixture(scope="session")
def general_cs():
    # Make up a Calibration sequence. Mostly random except for two clears and two darks at start and end, which
    # we want to test
    pol_status = [
            "clear",
            "clear",
            "Sapphire Polarizer",
            "Sapphire Polarizer",
            "Sapphire Polarizer",
            "clear",
            "clear",
        ]
    pol_theta = [0.0, 0.0, 60.0, 60.0, 120.0, 0.0, 0.0]
    ret_status = ["clear", "clear", "clear", "SiO2 SAR", "clear", "clear", "clear"]
    ret_theta = [0.0, 0.0, 0.0, 45.0, 0.0, 0.0, 0.0]
    dark_status = [
            "DarkShutter",
            "FieldStop (5arcmin)",
            "FieldStop (5arcmin)",
            "FieldStop (5arcmin)",
            "FieldStop (5arcmin)",
            "FieldStop (5arcmin)",
            "DarkShutter",
        ]
    ds = CalibrationSequenceDataset(array_shape=(1, 2, 2), time_delta=2.0, pol_status=pol_status, pol_theta=pol_theta,
                                    ret_status=ret_status, ret_theta=ret_theta, dark_status=dark_status)
    header_list = [
        spec122_validator.validate_and_translate_to_214_l0(d.header(), return_type=fits.HDUList)[0].header
        for d in ds
    ]
    out_dict = dict()
    for n in range(ds.num_steps):
        hdu_list = []
        for m in range(ds.num_mod):
            hdu_list.append(fits.PrimaryHDU(data=np.ones((3, 4, 1)) * n + 100 * m, header=fits.Header(header_list.pop(0))))

        out_dict[n] = [InstAccess(h) for h in hdu_list]

    return out_dict, pol_status, pol_theta, ret_status, ret_theta, dark_status
