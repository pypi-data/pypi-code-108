import os
import numpy as np

from pydicom._dicom_dict import DicomDictionary
from .tag2numpy import Tag2NumPy


def is_dicom_file(file_path_or_obj):
    file_obj = file_path_or_obj
    if isinstance(file_obj, str):
        if not os.path.isfile(file_obj):
            return False
        if file_obj.startswith('._'):
            return False
        file_obj = open(file_obj, "rb")
    try:
        result = file_obj.read(132).decode('ASCII')[-4:] == 'DICM'
        file_obj.seek(0)
        return result
    except UnicodeDecodeError:
        return False


def is_tag_file(file_path):
    return file_path.endswith('.tag') and not file_path.startswith('._')


def get_tag_file_for_dicom(dcm_file, ext='.tag'):
    tag_file = os.path.splitext(dcm_file)[0] + ext
    if not os.path.isfile(tag_file):
        tag_file = dcm_file + ext
        if not os.path.isfile(tag_file):
            print(f'Could not find TAG file for DICOM file {dcm_file}')
            return None
        return tag_file
    return tag_file


def is_numpy_file(file_path):
    return file_path.endswith('.npy') and not file_path.startswith('._')


def get_numpy_file_for_dicom(dcm_file):
    return get_tag_file_for_dicom(dcm_file, ext='.npy')


def get_dicom_tag_for_name(name):
    for key, value in DicomDictionary.items():
        if name == value[4]:
            return hex(int(key))
    return None


def get_dictionary_items():
    return DicomDictionary.items()


def get_pixels(p, normalize=False):
    pixels = p.pixel_array
    if not normalize:
        return pixels
    if normalize is True:
        return p.RescaleSlope * pixels + p.RescaleIntercept
    if isinstance(normalize, int):
        return (pixels + np.min(pixels)) / (np.max(pixels) - np.min(pixels)) * normalize
    if isinstance(normalize, list):
        return (pixels + np.min(pixels)) / (np.max(pixels) - np.min(pixels)) * normalize[1] + normalize[0]
    return pixels


def get_tag_pixels(f, shape=None):
    converter = Tag2NumPy(shape)
    converter.set_input_tag_file_path(f)
    converter.execute()
    return converter.get_output_numpy_array()


def is_compressed(p):
    try:
        p.convert_pixel_data()
        return False
    except RuntimeError:
        return True


def decompress(f, reuse_name=False):
    result = os.system('which gdcmconv>/dev/null')
    if result > 0:
        raise RuntimeError('Tool "gdcmconv" is not installed')
    items = os.path.splitext(f)
    base_name, extension = items[0], items[1]
    f_target = base_name + '_raw' + extension
    command = 'gdcmconv --raw {} {}'.format(f, f_target)
    os.system(command)
    return f_target
