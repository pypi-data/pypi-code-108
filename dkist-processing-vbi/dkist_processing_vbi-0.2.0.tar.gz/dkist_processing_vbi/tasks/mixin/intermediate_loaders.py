from typing import Generator

import numpy as np
from dkist_processing_common.tasks.base import tag_type_hint

from dkist_processing_vbi.models.tags import VbiTag


class IntermediateLoaderMixin:
    """
    Mixin for methods that allow easy loading of intermediate frame's numpy arrays
    """

    def load_intermediate_arrays(self, tags: tag_type_hint) -> Generator[np.ndarray, None, None]:
        if VbiTag.intermediate() not in tags:
            tags += [VbiTag.intermediate()]
        for path, hdu in self.fits_data_read_hdu(tags=tags):
            yield hdu.data

    def intermediate_dark_array(self, spatial_step: int, exposure_time: float) -> np.ndarray:
        tags = [
            VbiTag.task("DARK"),
            VbiTag.spatial_step(spatial_step),
            VbiTag.exposure_time(exposure_time),
        ]
        return next(self.load_intermediate_arrays(tags=tags))

    def intermediate_gain_array(self, spatial_step: int) -> np.ndarray:
        tags = [VbiTag.task("GAIN"), VbiTag.spatial_step(spatial_step)]
        return next(self.load_intermediate_arrays(tags=tags))
