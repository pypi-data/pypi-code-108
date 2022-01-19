from typing import Optional
from typing import Union

from astropy.io import fits
from dkist_processing_common.parsers.quality import L1QualityFitsAccess


class VispL1QualityFitsAccess(L1QualityFitsAccess):
    def __init__(
        self,
        hdu: Union[fits.ImageHDU, fits.PrimaryHDU, fits.CompImageHDU],
        name: Optional[str] = None,
        auto_squeeze: bool = True,
    ):
        super().__init__(hdu=hdu, name=name, auto_squeeze=auto_squeeze)

        self.spectral_index: int = self.header["DINDEX5"]
