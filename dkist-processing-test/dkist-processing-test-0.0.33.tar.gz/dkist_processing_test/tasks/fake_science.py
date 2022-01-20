"""
Fake science task
"""
from astropy.io import fits
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks import ScienceTaskL0ToL1Base


class GenerateCalibratedData(ScienceTaskL0ToL1Base):
    def run(self):
        count = 1  # keep a running count to increment the dsps repeat number
        for path, hdu in self.fits_data_read_hdu(tags=Tag.input()):
            header = hdu.header
            header["DSPSNUM"] = count
            data = hdu.data
            output_hdu = fits.PrimaryHDU(data=data, header=header)
            output_hdul = fits.HDUList([output_hdu])
            self.fits_data_write(
                hdu_list=output_hdul,
                tags=[
                    Tag.calibrated(),
                    Tag.frame(),
                    Tag.stokes("I"),
                    Tag.dsps_repeat(count),
                ],
            )
            count += 1
