import numpy as np
from astropy.visualization import ZScaleInterval
from dkist_processing_common.tasks.assemble_movie import AssembleMovie
from matplotlib import cm
from PIL import ImageDraw

from dkist_processing_vbi.parsers.vbi_l1_fits_access import VbiL1FitsAccess


class AssembleVbiMovie(AssembleMovie):
    """
    Class for assembling pre-made movie frames (as FITS/numpy) into a L1 movie file (mp4)
    """

    @property
    def fits_parsing_class(self):
        return VbiL1FitsAccess

    def apply_colormap(self, array: np.ndarray) -> np.ndarray:
        """
        Convert floats to RGB colors using the ZScale normalization scheme
        """
        color_mapper = cm.get_cmap(self.MPL_COLOR_MAP)
        scaled_array = ZScaleInterval()(array)
        return color_mapper(scaled_array, bytes=True)[
            :, :, :-1
        ]  # Drop the last (alpha) color dimension

    def write_overlay(self, draw: ImageDraw, fits_obj: VbiL1FitsAccess) -> None:
        """
        Add simple overlay of just instrument, wavelength, and time stamp
        """
        self.write_line(
            draw, f"INSTRUMENT: {self.constants.instrument}", 3, "right", font=self.font_18
        )
        self.write_line(draw, f"WAVELENGTH: {fits_obj.wavelength}", 2, "right", font=self.font_15)
        self.write_line(draw, f"DATE OBS: {fits_obj.time_obs}", 1, "right", font=self.font_15)
