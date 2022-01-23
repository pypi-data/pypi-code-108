import pydicom


class Dicom2Numpy:

    def __init__(self, dcm_file_path):
        self.dcm_file_path = dcm_file_path
        self.npy_array = None
        self.normalize_enabled = False

    def set_normalize_enabled(self, normalize_enabled):
        self.normalize_enabled = normalize_enabled

    def is_normalize_enabled(self):
        return self.normalize_enabled

    def execute(self):
        self.npy_array = None
        p = pydicom.dcmread(self.dcm_file_path)
        pixels = p.pixel_array
        self.npy_array = pixels.reshape(p.Rows, p.Columns)
        if self.is_normalize_enabled():
            b = p.RescaleIntercept
            m = p.RescaleSlope
            self.npy_array = m * self.npy_array + b
        return self.npy_array
