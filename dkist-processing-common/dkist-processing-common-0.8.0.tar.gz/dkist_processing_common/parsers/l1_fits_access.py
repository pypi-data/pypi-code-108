"""
By-frame 214 L1 only header keywords that are not instrument specific
"""
from typing import Optional
from typing import Union

from astropy.io import fits

from dkist_processing_common.models.fits_access import FitsAccessBase


class L1FitsAccess(FitsAccessBase):
    def __init__(
        self,
        hdu: Union[fits.ImageHDU, fits.PrimaryHDU, fits.CompImageHDU],
        name: Optional[str] = None,
        auto_squeeze: bool = False,  # Because L1 data should always have the right form, right?
    ):
        super().__init__(hdu=hdu, name=name, auto_squeeze=auto_squeeze)

        self.elevation: float = self.header["ELEV_ANG"]
        self.azimuth: float = self.header["TAZIMUTH"]
        self.table_angle: float = self.header["TTBLANGL"]
        self.gos_level3_status: str = self.header["LVL3STAT"]
        self.gos_level3_lamp_status: str = self.header["LAMPSTAT"]
        self.scanning_mode: str = self.header["TELSCAN"]
        self.gos_polarizer_status: str = self.header["LVL2STAT"]
        self.gos_retarder_status: str = self.header["LVL1STAT"]
        self.gos_level0_status: str = self.header["LVL0STAT"]
        self.time_obs: str = self.header["DATE-BEG"]
        self.ip_id: str = self.header["IP_ID"]
        self.instrument: str = self.header["INSTRUME"]
        self.wavelength: float = self.header["LINEWAV"]
        self.proposal_id: str = self.header["PROP_ID"]
        self.num_dsps_repeats: int = self.header["DSPSREPS"]
        self.current_dsps_repeat: int = self.header["DSPSNUM"]
        self.fpa_exposure_time_sec: float = self.header["XPOSURE"]

    @property
    def gos_polarizer_angle(self) -> Union[float, str]:
        """
        Convert the polarizer angle to a float if possible before returning
        """
        try:
            return float(self.header["POLANGLE"])
        except ValueError:
            return self.header["POLANGLE"]

    @property
    def gos_retarder_angle(self) -> Union[float, str]:
        """
        Convert the retarder angle to a float if possible before returning
        """
        try:
            return float(self.header["RETANGLE"])
        except ValueError:
            return self.header["RETANGLE"]
