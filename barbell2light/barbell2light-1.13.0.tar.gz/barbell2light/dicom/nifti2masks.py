import os
import json
import numpy as np
import SimpleITK as sitk


class Nifti2Masks(object):

    def __init__(self):
        self._input_nifti_file_path = None
        self._label_map = None
        self._output_dir = None
        self._output_file_paths = None
        self._overwrite_output = False

    def set_input_nifti_file_path(self, file_path):
        self._input_nifti_file_path = file_path

    def set_label_map(self, label_map):
        self._label_map = label_map

    def set_label_map_tomovision(self):
        self._label_map = {1: 'muscle', 5: 'SAT', 7: 'VAT'}

    def set_output_dir(self, output_dir):
        self._output_dir = output_dir

    def set_overwrite_output(self, value):
        self._overwrite_output = value

    def get_output_file_paths(self):
        return self._output_file_paths

    @staticmethod
    def _threshold_image(image, label):
        image = sitk.BinaryThreshold(image, float(label), float(label))
        return image

    @staticmethod
    def _get_int16_label_map(label_map):
        lm = {}
        for label in label_map.keys():
            label_int16 = np.int16(label)
            lm[label_int16] = label_map[label]
        return lm

    @staticmethod
    def _get_file_base_name(file_path):
        x = os.path.split(file_path)
        x = x[1]
        x = os.path.splitext(x)
        x = x[0]
        if x.endswith('.nii'):
            x = os.path.splitext(x)
            x = x[0]
        return x

    def execute(self):
        file_base_name = self._get_file_base_name(self._input_nifti_file_path)
        label_map = self._get_int16_label_map(self._label_map)
        file_paths = {}
        for label in label_map.keys():
            reader = sitk.ImageFileReader()
            reader.SetImageIO('NiftiImageIO')
            reader.SetFileName(self._input_nifti_file_path)
            image = reader.Execute()
            image_new = self._threshold_image(image, label)
            writer = sitk.ImageFileWriter()
            file_path = os.path.join(self._output_dir, '{}_{}.nii.gz'.format(file_base_name, label_map[label]))
            try:
                os.stat(file_path)
                if not self._overwrite_output:
                    print('Error: file {} already exists!'.format(file_path))
                    return
            except FileNotFoundError:
                pass
            writer.SetFileName(file_path)
            file_paths[label_map[label]] = file_path
            writer.SetImageIO('NiftiImageIO')
            writer.Execute(image_new)
        self._output_file_paths = file_paths
        print(self._output_file_paths)


if __name__ == '__main__':
    node = Nifti2Masks()
    node.set_input_nifti_file_path('/Volumes/USB_SECURE1/data/radiomics/projects/004_ovarium/data/test/out/IM_1_tag.nii.gz')
    node.set_label_map_tomovision()
    node.set_output_dir('/Volumes/USB_SECURE1/data/radiomics/projects/004_ovarium/data/test/out')
    node.set_overwrite_output(True)
    node.execute()
    print(json.dumps(node.get_output_file_paths(), indent=4))
