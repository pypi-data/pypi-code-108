import os
import json
import numpy as np
import SimpleITK as sitk


class Dcm2Masks(object):

    def __init__(self):
        self._input_dicom_file_path = None
        self._label_map = None
        self._output_dir = None
        self._output_file_paths = None
        self._overwrite_output = False

    # INTERFACE

    def set_input_dicom_file_path(self, file_path):
        self._input_dicom_file_path = file_path

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

    # INTERNAL METHODS

    @staticmethod
    def _get_int16_label_map(label_map):
        lm = {}
        for label in label_map.keys():
            label_int16 = np.int16(label)
            lm[label_int16] = label_map[label]
        return lm

    @staticmethod
    def _threshold_image(image, label):
        image = sitk.BinaryThreshold(image, float(label), float(label))
        return image

    @staticmethod
    def extract_pixels_by_label(pixels, label):
        pixels_copy = np.copy(pixels)
        pixels_copy[pixels_copy != label] = np.uint16(0)
        pixels_copy[pixels_copy == label] = np.uint16(1)
        return pixels_copy

    def execute(self):
        os.makedirs(self._output_dir, exist_ok=True)
        file_base_name = os.path.splitext(self._input_dicom_file_path)[0]
        label_map = self._get_int16_label_map(self._label_map)
        file_paths = {}
        for label in label_map.keys():

            # f = open(self._input_dicom_file_path, 'rb')
            # p = pydicom.read_file(f)
            # f.close()
            # pixels = p.pixel_array.flat
            # pixels = self.extract_pixels_by_label(pixels, label)
            # p.PixelData = pixels.tobytes()
            # file_path = os.path.join(self._output_dir, '{}_{}.dcm'.format(file_base_name, label_map[label]))
            # try:
            #     os.stat(file_path)
            #     if not self._overwrite_output:
            #         print('Error: file {} already exists!'.format(file_path))
            #         return
            # except FileNotFoundError:
            #     pass
            # p.save_as(file_path)
            # file_paths[label_map[label]] = file_path

            reader = sitk.ImageFileReader()
            reader.SetImageIO('GDCMImageIO')
            reader.SetFileName(self._input_dicom_file_path)
            image = reader.Execute()
            image_new = self._threshold_image(image, label)
            writer = sitk.ImageFileWriter()
            file_path = os.path.join(self._output_dir, '{}_{}.dcm'.format(file_base_name, label_map[label]))
            try:
                os.stat(file_path)
                if not self._overwrite_output:
                    print('Error: file {} already exists!'.format(file_path))
                    return
            except FileNotFoundError:
                pass
            writer.SetFileName(file_path)
            file_paths[label_map[label]] = file_path
            writer.SetImageIO('GDCMImageIO')
            writer.Execute(image_new)

        self._output_file_paths = file_paths


if __name__ == '__main__':
    node = Dcm2Masks()
    node.set_input_dicom_file_path('/Volumes/USB_SECURE1/data/radiomics/projects/004_ovarium/data/test/out/IM_1_tag.dcm')
    node.set_label_map_tomovision()
    node.set_output_dir('/Volumes/USB_SECURE1/data/radiomics/projects/004_ovarium/data/test/out')
    node.set_overwrite_output(True)
    node.execute()
    print(json.dumps(node.get_output_file_paths(), indent=4))
