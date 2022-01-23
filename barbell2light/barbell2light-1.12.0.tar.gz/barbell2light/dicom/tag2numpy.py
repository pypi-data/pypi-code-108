import numpy as np
import binascii
import struct


class Tag2NumPy(object):

    def __init__(self, shape):
        self._input_tag_file_path = None
        self._output_dir = '.'
        self._output_numpy_array = None
        self._shape = shape

    def set_input_tag_file_path(self, file_path):
        self._input_tag_file_path = file_path

    def get_output_numpy_array(self):
        return self._output_numpy_array

    @staticmethod
    def _get_pixels(tag_file_path):
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

    def execute(self):
        self._output_numpy_array = self._get_pixels(self._input_tag_file_path)
        try:
            if self._shape:
                self._output_numpy_array = self._output_numpy_array.reshape(self._shape)
        except ValueError:
            self._output_numpy_array = None


if __name__ == '__main__':
    tag2numpy = Tag2NumPy((512, 512))
    tag2numpy.set_input_tag_file_path('/Volumes/USB_SECURE1/data/radiomics/projects/deepseg/data/mega/lung_len/org/LUNG1-001_20180209_CT.tag')
    tag2numpy.execute()
    print(tag2numpy.get_output_numpy_array())
