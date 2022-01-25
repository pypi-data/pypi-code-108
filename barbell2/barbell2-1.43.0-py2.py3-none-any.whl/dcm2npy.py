import pydicom

from barbell2.utils import apply_window


class Dicom2Numpy:

    def __init__(self, dcm_file_path):
        self.dcm_file_path = dcm_file_path
        self.npy_array = None
        self.window = None
        self.normalize_enabled = True

    def set_window(self, window):
        self.window = window

    def set_normalize_enabled(self, normalize_enabled):
        self.normalize_enabled = normalize_enabled

    def is_normalize_enabled(self):
        return self.normalize_enabled

    def execute(self):
        self.npy_array = None
        p = pydicom.dcmread(self.dcm_file_path)
        pixels = p.pixel_array
        self.npy_array = pixels.reshape(p.Rows, p.Columns)
        if self.window is not None:
            self.npy_array = apply_window(self.npy_array, self.window)
        if self.is_normalize_enabled():
            b = p.RescaleIntercept
            m = p.RescaleSlope
            self.npy_array = m * self.npy_array + b
        return self.npy_array


if __name__ == '__main__':
    d2n = Dicom2Numpy('/Users/Ralph/Desktop/output-segmentl3/1.dcm')
    d2n.set_window((400, 50))
    pixels = d2n.execute()
    print(pixels)
