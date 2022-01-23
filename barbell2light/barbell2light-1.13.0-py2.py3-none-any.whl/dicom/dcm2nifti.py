import os
import SimpleITK as sitk


class Dcm2Nifti(object):

    def __init__(self):
        self._input_dicom_file_path = None
        self._output_dir = None
        self._output_file_path = None
        self._shape = None
        self._spacing = None
        self._origin = None
        self._direction = None
        self._overwrite_output = False

    def set_input_dicom_file_path(self, file_path):
        self._input_dicom_file_path = file_path

    def set_output_dir(self, output_dir):
        self._output_dir = output_dir

    def set_overwrite_output(self, value):
        self._overwrite_output = value

    def get_output_file_path(self):
        return self._output_file_path

    def execute(self):
        os.makedirs(self._output_dir, exist_ok=True)
        reader = sitk.ImageFileReader()
        reader.SetFileName(self._input_dicom_file_path)
        reader.SetImageIO('GDCMImageIO')
        image = reader.Execute()
        file_name = os.path.split(self._input_dicom_file_path)
        file_name = file_name[1]
        file_name = os.path.splitext(file_name)
        file_name = file_name[0]
        file_name = '{}.nii.gz'.format(file_name)
        file_path = os.path.join(self._output_dir, file_name)
        try:
            os.stat(file_path)
            if not self._overwrite_output:
                print('Error: file {} already exists!'.format(file_path))
                return
        except FileNotFoundError:
            pass
        self._output_file_path = file_path
        writer = sitk.ImageFileWriter()
        writer.SetFileName(self._output_file_path)
        writer.SetImageIO('NiftiImageIO')
        writer.Execute(image)
        print('Written {}'.format(self._output_file_path))


if __name__ == '__main__':
    node = Dcm2Nifti()
    node.set_input_dicom_file_path('/Volumes/USB_SECURE1/data/radiomics/projects/004_ovarium/data/test/IM_1.dcm')
    node.set_output_dir('/Volumes/USB_SECURE1/data/radiomics/projects/004_ovarium/data/test/out')
    node.set_overwrite_output(True)
    node.execute()
