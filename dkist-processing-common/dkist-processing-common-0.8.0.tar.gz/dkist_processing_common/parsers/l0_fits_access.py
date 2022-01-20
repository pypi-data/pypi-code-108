"""
By-frame 214 L0 header keywords that are not instrument specific
"""
from typing import Optional
from typing import Union

from astropy.io import fits

from dkist_processing_common.parsers.l1_fits_access import L1FitsAccess


class L0FitsAccess(L1FitsAccess):
    def __init__(
        self,
        hdu: Union[fits.ImageHDU, fits.PrimaryHDU, fits.CompImageHDU],
        name: Optional[str] = None,
        auto_squeeze: bool = True,
    ):
        super().__init__(hdu=hdu, name=name, auto_squeeze=auto_squeeze)
        self.ip_task_type: str = self.header["IPTASK"]
        self.ip_start_time: str = self.header["DKIST011"]
        self.ip_end_time: str = self.header["DKIST012"]
