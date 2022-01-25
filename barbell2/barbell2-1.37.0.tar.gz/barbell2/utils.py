import os
import time
import math
import datetime
import struct
import binascii
import numpy as np


class Logger(object):

    def __init__(self, prefix='log', to_dir='.', timestamp=True):
        self.f = None
        self.timestamp = timestamp
        os.makedirs(to_dir, exist_ok=True)
        now = datetime.datetime.now()
        if not prefix.endswith('_'):
            prefix = prefix + '_'
        file_name = '{}{}.txt'.format(prefix, now.strftime('%Y%m%d%H%M%S'))
        self.f = open(os.path.join(to_dir, file_name), 'w')

    def print(self, message):
        now = datetime.datetime.now()
        if self.timestamp:
            message = '[' + now.strftime('%Y-%m-%d %H:%M:%S.%f') + '] ' + str(message)
        else:
            message = str(message)
        print(message)
        if self.f:
            self.f.write(message + '\n')

    def close(self):
        self.f.close()

    def __del__(self):
        self.close()


def current_time_millis():
    return int(round(time.time() * 1000))


def current_time_secs():
    return int(round(current_time_millis() / 1000.0))


def elapsed_millis(start_time_millis):
    return current_time_millis() - start_time_millis


def elapsed_secs(start_time_secs):
    return current_time_secs() - start_time_secs


def duration(seconds):
    h = int(math.floor(seconds/3600.0))
    remainder = seconds - h * 3600
    m = int(math.floor(remainder/60.0))
    remainder = remainder - m * 60
    s = int(math.floor(remainder))
    return '{} hours, {} minutes, {} seconds'.format(h, m, s)


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


def get_tag_pixels(tag_file_path):
    f = open(tag_file_path, 'rb')
    f.seek(0)
    byte = f.read(1)
    # Make sure to check the byte-value in Python 3!!
    while byte != b'':
        byte_hex = binascii.hexlify(byte)
        if byte_hex == b'0c':
            break
        byte = f.read(1)
    values = []
    f.read(1)
    while byte != b'':
        v = struct.unpack('b', byte)
        values.append(v)
        byte = f.read(1)
    values = np.asarray(values)
    values = values.astype(np.uint16)
    return values


def get_alberta_color_map():
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


def apply_window(pix, window):
    result = (pix - window[1] + 0.5 * window[0])/window[0]
    result[result < 0] = 0
    result[result > 1] = 1
    return result


def apply_color_map(pixels, color_map):
    pixels_new = np.zeros((*pixels.shape, 3), dtype=np.uint8)
    np.take(color_map, pixels, axis=0, out=pixels_new)
    return pixels_new


def create_fake_dicom(pixels, dcm_obj):
    pixels_new = apply_color_map(pixels, get_alberta_color_map())
    dcm_obj.PhotometricInterpretation = 'RGB'
    dcm_obj.SamplesPerPixel = 3
    dcm_obj.BitsAllocated = 8
    dcm_obj.BitsStored = 8
    dcm_obj.HighBit = 7
    dcm_obj.add_new(0x00280006, 'US', 0)
    dcm_obj.is_little_endian = True
    dcm_obj.fix_meta_info()
    dcm_obj.PixelData = pixels_new.tobytes()
    dcm_obj.SOPInstanceUID = '{}.9999'.format(dcm_obj.SOPInstanceUID)
    return dcm_obj
