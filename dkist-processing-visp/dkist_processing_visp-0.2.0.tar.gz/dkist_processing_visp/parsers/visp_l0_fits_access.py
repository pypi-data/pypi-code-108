from typing import Optional
from typing import Union

from astropy.io import fits
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess


class VispL0FitsAccess(L0FitsAccess):
    def __init__(
        self,
        hdu: Union[fits.ImageHDU, fits.PrimaryHDU, fits.CompImageHDU],
        name: Optional[str] = None,
        auto_squeeze: bool = True,
    ):
        super().__init__(hdu=hdu, name=name, auto_squeeze=auto_squeeze)

        self.number_of_modulator_states: int = self.header.get("VSPNUMST")
        self.beam_match_id: str = self.header.get("FRAMEID")
        self.raster_scan_step: int = self.header.get("VSPSTP")
        self.total_raster_steps: int = self.header.get("VSPNSTP")
        self.modulator_state: int = self.header.get("VSPSTNUM")
        self.polarimeter_mode: str = self.header.get("VISP_006")
