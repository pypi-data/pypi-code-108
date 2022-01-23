import os
import pydicom

from .utils import create_fake_dicom
from .tag2npy import Tag2Numpy


class Tag2Dicom:

    def __init__(self, tag_file_path, dcm_file_path):
        self.tag_file_path = tag_file_path
        self.dcm_file_path = dcm_file_path
        self.output_dir = '.'
        self.tag_dcm_file_name = None
        self.tag_dcm_file_path = None

    def set_output_dir(self, output_dir):
        self.output_dir = output_dir

    def execute(self):
        p = pydicom.dcmread(self.dcm_file_path)
        t2n = Tag2Numpy(self.tag_file_path, (p.Rows, p.Columns))
        pixels_tag = t2n.execute()
        p_new = create_fake_dicom(pixels_tag, p)
        self.tag_dcm_file_name = os.path.split(self.tag_file_path)[1] + '.dcm'
        self.tag_dcm_file_path = os.path.join(self.output_dir, self.tag_dcm_file_name)
        p_new.save_as(self.tag_dcm_file_path)
