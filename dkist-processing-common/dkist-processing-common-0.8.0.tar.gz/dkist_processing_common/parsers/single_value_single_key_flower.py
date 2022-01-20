"""
Pre-made flower that produces tag based on a single header key
"""
from dkist_processing_common.models.flower_pot import Stem
from dkist_processing_common.parsers.l0_fits_access import L0FitsAccess


class SingleValueSingleKeyFlower(Stem):
    """ Flower that just passes through a single header value """

    def __init__(self, tag_stem_name: str, metadata_key: str):
        super().__init__(stem_name=tag_stem_name)
        self.metadata_key = metadata_key

    def setter(self, fits_obj: L0FitsAccess):
        return getattr(fits_obj, self.metadata_key)

    def getter(self, key):
        return self.key_to_petal_dict[key]
