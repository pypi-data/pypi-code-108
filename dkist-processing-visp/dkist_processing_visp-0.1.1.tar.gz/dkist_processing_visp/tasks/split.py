import logging
from typing import List
from typing import Tuple
from uuid import uuid4

import numpy as np
from astropy.io import fits

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.visp_base import VispScienceTask
from dkist_processing_visp.visp_l0_fits_access import VispL0FitsAccess


class SplitBeams(VispScienceTask):
    """
    Task class for splitting the two ViSP beams
    """

    def run(self) -> None:
        with self.apm_step("Gather input frames"):
            input_objects = self.fits_data_read_fits_access(
                tags=[VispTag.input(), VispTag.frame()], cls=VispL0FitsAccess
            )

        with self.apm_step("Split beams and save"):
            logging.info("Splitting input data into two beams")
            for full_beam_object in input_objects:
                logging.info(f"Splitting file {full_beam_object.name}")
                beam1_data, beam2_data = self.split_beam(full_beam_object.data)
                all_tags = list(self.scratch.tags(full_beam_object.name))
                header = full_beam_object.header
                beam_match_id = str(uuid4())
                header["FRAMEID"] = beam_match_id
                for i, beam in enumerate([beam1_data, beam2_data]):
                    self.write_single_beam(
                        data=np.expand_dims(beam, axis=0),
                        header=header,
                        beam_num=i + 1,
                        tags=all_tags,
                    )

                # Finally, delete the full-beam file
                logging.info(f"Deleting {full_beam_object.name}")
                self.scratch.delete(full_beam_object.name)

    def split_beam(self, data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Actually do the split. Simple now but maybe more complicated at some point.
        """
        beam1_data = data[: self.beam_border, ...]
        beam2_data = data[self.beam_border :, ...][::-1, :]

        return beam1_data, beam2_data

    def write_single_beam(
        self,
        data: np.ndarray,
        header: fits.Header,
        beam_num: int,
        tags: List[str],
    ) -> None:
        """
        Construct an HDU list with the correct header and write it with a new BEAM_? tag
        """
        hdl = fits.HDUList([fits.PrimaryHDU(data=data, header=header)])
        full_tags = tags + [VispTag.beam(beam_num)]
        self.fits_data_write(hdu_list=hdl, tags=full_tags)
