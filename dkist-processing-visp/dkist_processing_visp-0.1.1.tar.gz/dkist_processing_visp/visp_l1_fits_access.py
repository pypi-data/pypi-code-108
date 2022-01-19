from typing import Optional
from typing import Union

from astropy.io import fits
from dkist_processing_common.parsers.l1_fits_access import L1FitsAccess


class VispL1FitsAccess(L1FitsAccess):
    def __init__(
        self,
        hdu: Union[fits.ImageHDU, fits.PrimaryHDU, fits.CompImageHDU],
        name: Optional[str] = None,
        auto_squeeze: Optional[bool] = True,
    ):
        super().__init__(hdu=hdu, name=name, auto_squeeze=auto_squeeze)
