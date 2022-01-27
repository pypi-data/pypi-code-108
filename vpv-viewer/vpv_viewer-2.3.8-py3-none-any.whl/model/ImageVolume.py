from .volume import Volume
from vpv.annotations.annotations_model import SpecimenAnnotations


class ImageVolume(Volume):
    def __init__(self, *args):
        super(ImageVolume, self).__init__(*args)

        # We have annotations only on ImageVolumes
        self.annotations = SpecimenAnnotations(self.shape_xyz(), self.vol_path)
        self.levels = [float(self._arr_data.min()), float(self._arr_data.max())]

