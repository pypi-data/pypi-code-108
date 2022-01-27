from .ImageVolume import ImageVolume
from vpv.common import read_image
import tempfile
from PIL import Image
import numpy as np


class VirtualStackVolume(ImageVolume):
    def __init__(self, *args):
        super(VirtualStackVolume, self).__init__(*args)

    def _load_data(self, file_paths, memap=True):
        """

        Parameters
        ----------
        file_paths

        Raises
        ------
        ValueError
            If an image in the stack is of the icorrect dimensions

        """
        # self.worker = LoadVirtualStackWorker(file_paths)
        # self.model.updating_started_signal.emit()
        # self.worker.progress_signal.connect(self.model.updating_msg_signal)
        # self.worker.finished.connect(self.loading_finsihed)
        # self.worker.start()

    # def loading_finsihed(self):
    #     self.model.updating_finished_signal.emit()
    #     return self.worker.memmap_result

        def sitk_load(p):
            return read_image(str(p))

        def pil_load(p):
            im = Image.open(p)
            return np.array(im)

        # SimpleITK reads in 2D bmps as 3D. So use PIL instead
        if file_paths[0].lower().endswith('.bmp'):
            reader = pil_load
        else:
            reader = sitk_load

        arr = reader(file_paths[0])
        dtype = arr.dtype
        zyx = list(arr.shape)
        zyx.insert(0, len(file_paths))
        t = tempfile.TemporaryFile()
        m = np.memmap(t, dtype=str(dtype), mode='w+', shape=tuple(zyx))
        for i, path in enumerate(sorted(file_paths)):
            img_arr = reader(path)
            m[i] = img_arr
        return m