import os
import shutil
import pydicom
import numpy as np
import matplotlib.pyplot as plt

from barbell2light.dicom import is_dicom_file, is_tag_file, is_numpy_file, get_tag_file_for_dicom, \
    get_numpy_file_for_dicom, tag2numpy, decompress


class Tag2Dcm:

    def __init__(self):
        self.dcm_file = None
        self.tag_file = None
        self.numpy_file = None
        self.output_dir = '.'
        self.output_dcm_file = None
        self.output_tag_file = None
        self.output_tag_dcm_file = None
        self.output_dcm_png_file = None
        self.output_tag_dcm_png_file = None
        self.copy_original_dcm_file_to_output_dir = False
        self.copy_original_tag_file_to_output_dir = False
        self.png_figure_size = (10, 10)
        self.create_pngs = False
        self.verbose = False

    def set_dicom_and_tag_file(self, dcm_file, tag_file):
        if not is_dicom_file(dcm_file):
            raise RuntimeError(f'File {dcm_file} is not a DICOM file')
        if not is_tag_file(tag_file):
            raise RuntimeError(f'File {tag_file} does not have .tag extension')
        if get_tag_file_for_dicom(dcm_file) != tag_file:
            # Just print a warning since it's suspicious. It might happen though that the TAG file
            # name is not the same as the DICOM file
            print(f'Files {dcm_file} and {tag_file} do not seem to belong together')
        self.dcm_file = dcm_file
        self.tag_file = tag_file

    def set_dicom_and_numpy_file(self, dcm_file, numpy_file):
        if not is_dicom_file(dcm_file):
            raise RuntimeError(f'File {dcm_file} is not a DICOM file')
        if not is_numpy_file(numpy_file):
            raise RuntimeError(f'File {numpy_file} does not have .npy extension')
        self.dcm_file = dcm_file
        self.numpy_file = numpy_file

    def set_output_dir(self, output_dir):
        if not os.path.isdir(output_dir):
            print(f'Output directory {output_dir} does not exist, creating it...')
            os.makedirs(output_dir, exist_ok=False)
        self.output_dir = output_dir

    def get_output_dir(self):
        return self.output_dir

    def set_copy_original_dcm_file_to_output_dir(self, copy_original_dcm_file_to_output_dir):
        self.copy_original_dcm_file_to_output_dir = copy_original_dcm_file_to_output_dir

    def set_copy_original_tag_file_to_output_dir(self, copy_original_tag_file_to_output_dir):
        self.copy_original_tag_file_to_output_dir = copy_original_tag_file_to_output_dir

    def set_png_figure_size(self, png_figure_size):
        self.png_figure_size = png_figure_size

    def get_png_figure_size(self):
        return self.png_figure_size

    def set_create_pngs(self, create_pngs):
        self.create_pngs = create_pngs

    def set_verbose(self, verbose):
        self.verbose = verbose

    @staticmethod
    def apply_ct_window(pix, window):
        result = (pix - window[1] + 0.5 * window[0])/window[0]
        result[result < 0] = 0
        result[result > 1] = 1
        return result

    @staticmethod
    def get_color_map():
        color_map = []
        for i in range(256):
            if i == 1:  # muscle
                color_map.append([255, 0, 0])
            elif i == 2:  # inter-muscular adipose tissue
                color_map.append([0, 255, 0])
            elif i == 5:  # visceral adipose tissue
                color_map.append([255, 255, 0])
            elif i == 7:  # subcutaneous adipose tissue
                color_map.append([0, 255, 255])
            elif i == 12:  # unknown
                color_map.append([0, 0, 255])
            else:
                color_map.append([0, 0, 0])
        return color_map

    def execute(self):
        p = pydicom.dcmread(self.dcm_file)
        if p.file_meta.TransferSyntaxUID.is_compressed:
            p.decompress()
        pixels = p.pixel_array
        pixels = pixels * p.RescaleSlope + p.RescaleIntercept
        pixels = self.apply_ct_window(pixels, [400, 50])
        pixels = pixels.astype(float)
        pixels_org = pixels.copy()
        if self.tag_file is not None:
            converter = tag2numpy.Tag2NumPy(pixels.shape)
            converter.set_input_tag_file_path(self.tag_file)
            converter.execute()
            pixels_tag = converter.get_output_numpy_array()
        else:
            pixels_tag = np.load(self.numpy_file)
        pixels_new = np.zeros((*pixels_tag.shape, 3), dtype=np.uint8)
        np.take(self.get_color_map(), pixels_tag, axis=0, out=pixels_new)
        p.PhotometricInterpretation = 'RGB'
        p.SamplesPerPixel = 3
        p.BitsAllocated = 8
        p.BitsStored = 8
        p.HighBit = 7
        p.add_new(0x00280006, 'US', 0)
        p.is_little_endian = True
        p.fix_meta_info()
        p.PixelData = pixels_new.tobytes()
        p.SOPInstanceUID = '{}.9999'.format(p.SOPInstanceUID)
        self.output_dcm_file = os.path.join(self.output_dir, os.path.split(self.dcm_file)[1])
        if self.copy_original_dcm_file_to_output_dir:
            shutil.copy(self.dcm_file, self.output_dir)
        self.output_tag_file = os.path.join(self.output_dir, os.path.split(self.tag_file)[1])
        if self.copy_original_tag_file_to_output_dir:
            shutil.copy(self.tag_file, self.output_dir)
        self.output_tag_dcm_file = os.path.join(self.output_dir, os.path.split(self.tag_file)[1] + '.dcm')
        p.save_as(self.output_tag_dcm_file)
        if self.create_pngs:
            fig = plt.figure(figsize=self.png_figure_size)
            ax = fig.add_subplot(1, 1, 1)
            plt.imshow(pixels_org, cmap='gray')
            ax.axis('off')
            self.output_dcm_png_file = os.path.join(self.output_dir, self.get_output_dcm_file_name() + '.png')
            plt.savefig(self.output_dcm_png_file, bbox_inches='tight')
            fig = plt.figure(figsize=self.png_figure_size)
            ax = fig.add_subplot(1, 1, 1)
            plt.imshow(pixels_new)
            ax.axis('off')
            self.output_tag_dcm_png_file = os.path.join(self.output_dir, self.get_output_tag_dcm_file_name() + '.png')
            plt.savefig(self.output_tag_dcm_png_file, bbox_inches='tight')
            plt.close('all')

    def get_output_dcm_file(self):
        return self.output_dcm_file

    def get_output_dcm_file_name(self):
        return os.path.split(self.get_output_dcm_file())[1]

    def get_output_dcm_png_file(self):
        return self.output_dcm_png_file

    def get_output_dcm_png_file_name(self):
        return os.path.split(self.get_output_dcm_png_file())[1]

    def get_output_tag_file(self):
        return self.output_tag_file

    def get_output_tag_file_name(self):
        return os.path.split(self.get_output_tag_file())[1]

    def get_output_tag_dcm_file(self):
        return self.output_tag_dcm_file

    def get_output_tag_dcm_file_name(self):
        return os.path.split(self.get_output_tag_dcm_file())[1]

    def get_output_tag_dcm_png_file(self):
        return self.output_tag_dcm_png_file

    def get_output_tag_dcm_png_file_name(self):
        return os.path.split(self.get_output_tag_dcm_png_file())[1]


if __name__ == '__main__':
    t2d = Tag2Dcm()
    t2d.set_dicom_and_tag_file(
        dcm_file='../../data/10.dcm',
        tag_file='../../data/10.tag',
    )
    t2d.set_output_dir(output_dir='../../data')
    t2d.set_copy_original_dcm_file_to_output_dir(False)
    t2d.set_copy_original_tag_file_to_output_dir(False)
    t2d.execute()


# import os
# import numpy as np
# import binascii
# import struct
# import SimpleITK as sitk
#
#
# class Tag2Dcm(object):
#
#     def __init__(self):
#         self._input_dicom_file_path = None
#         self._input_tag_file_path = None
#         self._output_dir = '.'
#         self._output_file_path = None
#         self._overwrite_output = False
#         self._shape = None
#         self._spacing = None
#         self._origin = None
#         self._direction = None
#         self._verbose = True
#
#     # INTERFACE
#
#     def set_input_dicom_file_path(self, file_path):
#         self._input_dicom_file_path = file_path
#
#     def set_input_tag_file_path(self, file_path):
#         self._input_tag_file_path = file_path
#
#     def set_output_dir(self, output_dir):
#         self._output_dir = output_dir
#
#     def get_output_file_path(self):
#         return self._output_file_path
#
#     def set_overwrite_output(self, value):
#         self._overwrite_output = value
#
#     def set_verbose(self, verbose):
#         self._verbose = verbose
#
#     # INTERNAL METHODS
#
#     def _get_info_from_dicom(self, f, verbose):
#         reader = sitk.ImageFileReader()
#         reader.SetImageIO('GDCMImageIO')
#         reader.SetFileName(f)
#         image = reader.Execute()
#         self._shape = image.GetSize()
#         self._spacing = image.GetSpacing()
#         self._origin = image.GetOrigin()
#         self._direction = image.GetDirection()
#         min_max_filter = sitk.MinimumMaximumImageFilter()
#         min_max_filter.Execute(image)
#         minimum = min_max_filter.GetMinimum()
#         maximum = min_max_filter.GetMaximum()
#         # p = pydicom.read_file(f)
#         # # Make sure to put the 1 at the front because the NumPy indexing is differently ordered than
#         # # SimpleITK pixel indexing
#         # self._shape = (1, p.Rows, p.Columns)
#         # self._spacing = (float(p.PixelSpacing[0]), float(p.PixelSpacing[1]), 1.0)
#         # self._origin = (
#         #     float(p.ImagePositionPatient[0]),
#         #     float(p.ImagePositionPatient[1]),
#         #     float(p.ImagePositionPatient[2])
#         # )
#         # self._direction = (
#         #     float(p.ImageOrientationPatient[0]),
#         #     float(p.ImageOrientationPatient[1]),
#         #     float(p.ImageOrientationPatient[2]),
#         #     float(p.ImageOrientationPatient[3]),
#         #     float(p.ImageOrientationPatient[4]),
#         #     float(p.ImageOrientationPatient[5]),
#         #     0, 0, 1,
#         # )
#         if verbose:
#             print('File: {}, Size: {}, Spacing: {}, Origin: {}, Direction: {}, Min: {}, Max: {}'.format(
#                 f, self._shape, self._spacing, self._origin, self._direction, minimum, maximum))
#
#     @staticmethod
#     def _get_pixels(tag_file_path):
#         f = open(tag_file_path, 'rb')
#         f.seek(0)
#         byte = f.read(1)
#         # Make sure to check the byte-value in Python 3!!
#         while byte != b'':
#             byte_hex = binascii.hexlify(byte)
#             if byte_hex == b'0c':
#                 break
#             byte = f.read(1)
#         values = []
#         f.read(1)
#         while byte != b'':
#             v = struct.unpack('b', byte)
#             values.append(v)
#             byte = f.read(1)
#         values = np.asarray(values)
#         values = values.astype(np.uint16)
#         return values
#
#     # EXECUTE
#
#     def execute(self):
#         os.makedirs(self._output_dir, exist_ok=True)
#         self._get_info_from_dicom(self._input_dicom_file_path, self._verbose)
#         pixels = self._get_pixels(self._input_tag_file_path)
#
#         # pixels.shape = self._shape
#         pixels.shape = (1, self._shape[1], self._shape[0])
#         image = sitk.GetImageFromArray(pixels)
#         image.SetSpacing(self._spacing)
#         image.SetOrigin(self._origin)
#         image.SetDirection(self._direction)
#         # print(image)
#
#         # f = open(self._input_dicom_file_path, 'rb')
#         # p = pydicom.read_file(f)
#         # p.pixel_array.setflags(write=True)
#         # p.pixel_array.flat = pixels
#         # p.PixelData = p.pixel_array.tobytes()
#         # p.RescaleIntercept = 0
#         # p.RescaleSlope = 1
#
#         file_name = os.path.split(self._input_tag_file_path)
#         file_name = file_name[1]
#         file_name = os.path.splitext(file_name)
#         file_name = file_name[0]
#         file_name = '{}_tag.dcm'.format(file_name)
#         file_path = os.path.join(self._output_dir, file_name)
#
#         try:
#             os.stat(file_path)
#             if not self._overwrite_output:
#                 print('Error: file {} already exists!'.format(file_path))
#                 return
#         except FileNotFoundError:
#             pass
#
#         self._output_file_path = file_path
#
#         writer = sitk.ImageFileWriter()
#         writer.SetFileName(self._output_file_path)
#         writer.SetImageIO('GDCMImageIO')
#         writer.Execute(image)
#         # p.save_as(file_path)
#         # f.close()
#         # print(self._output_file_path)
#
#
# if __name__ == '__main__':
#     node = Tag2Dcm()
#     node.set_input_dicom_file_path('/Volumes/USB_SECURE1/data/radiomics/projects/004_ovarium/data/test/IM_1.dcm')
#     node.set_input_tag_file_path('/Volumes/USB_SECURE1/data/radiomics/projects/004_ovarium/data/test/IM_1.tag')
#     node.set_output_dir('/Volumes/USB_SECURE1/data/radiomics/projects/004_ovarium/data/test/out')
#     node.set_overwrite_output(True)
#     node.execute()
