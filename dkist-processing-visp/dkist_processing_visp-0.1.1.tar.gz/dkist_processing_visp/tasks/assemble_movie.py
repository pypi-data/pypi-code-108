from dkist_processing_common.tasks.assemble_movie import AssembleMovie
from PIL import ImageDraw

from dkist_processing_visp.visp_l0_fits_access import VispL0FitsAccess
from dkist_processing_visp.visp_l1_fits_access import VispL1FitsAccess


class AssembleVispMovie(AssembleMovie):
    @property
    def fits_parsing_class(self):
        return VispL1FitsAccess

    def write_overlay(self, draw: ImageDraw, fits_obj: VispL0FitsAccess) -> None:
        self.write_line(draw=draw, text=f"INSTRUMENT: {self.instrument}", line=1, column="right")
        self.write_line(
            draw=draw, text=f"WAVELENGTH: {fits_obj.wavelength}", line=2, column="right"
        )
        self.write_line(draw=draw, text=f"OBS TIME: {fits_obj.time_obs}", line=3, column="right")
