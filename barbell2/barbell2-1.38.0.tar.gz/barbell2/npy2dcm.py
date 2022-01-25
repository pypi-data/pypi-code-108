import os
import pydicom
import numpy as np

from .utils import get_alberta_color_map, create_fake_dicom


class Numpy2Dicom:

    def __init__(self, npy_array_or_file_path, dcm_file_path):
        self.npy_array_or_file_path = npy_array_or_file_path
        self.dcm_file_path = dcm_file_path
        self.color_map = get_alberta_color_map()
        self.npy_dcm_file_name = 'npy_array.dcm'
        self.npy_dcm_file_path = None
        self.output_dir = '.'

    def set_color_map(self, color_map):
        self.color_map = color_map

    def set_output_dir(self, output_dir):
        self.output_dir = output_dir

    def set_npy_dcm_file_name(self, npy_dcm_file_name):
        self.npy_dcm_file_name = npy_dcm_file_name

    def execute(self):
        if isinstance(self.npy_array_or_file_path, str):
            npy_array = np.load(self.npy_array_or_file_path)
        else:
            npy_array = self.npy_array_or_file_path
        p = pydicom.dcmread(self.dcm_file_path)
        if p.file_meta.TransferSyntaxUID.is_compressed:
            p.decompress()
        p_new = create_fake_dicom(npy_array, p)
        self.npy_dcm_file_path = os.path.join(self.output_dir, self.npy_dcm_file_name)
        p_new.save_as(self.npy_dcm_file_path)
