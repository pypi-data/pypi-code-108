""" Collection of dicom related functions.
"""

import pathlib
from typing import Tuple, Generator

import numpy as np


def read_meta(dcm_filename: str) -> Tuple[int, int, int, int]:
    """ Reads the meta data from the DICOM file and returns the width, height
    and the minimum and maximum pixel values.
    :param dcm_filename: path to DICOM file to read meta data from
    :return: (width, height, minPixelValue, maxPixelValue)
    """
    from pydicom import dcmread
    dcm = dcmread(dcm_filename, stop_before_pixels=True)
    return dcm.Columns, dcm.Rows, dcm.SmallestImagePixelValue, dcm.LargestImagePixelValue


def list_files(dir: str, recursive: bool = False) -> Generator[pathlib.Path, None, None]:
    """ List all DICOM files the the given directory, optionally recursively.
    :param dir: Path to a directory to look for DICOM files in
    :param recursive: If true: search in subdirectories
    :return: Generator over pathlib.Path objects
    """
    path = pathlib.Path(dir)
    pattern = '**/*.dcm' if recursive else '*.dcm'
    for p in path.glob(pattern):
        yield p


def list_meta(dir: str, recursive: bool = False) -> Generator[Tuple[str, int, int, int, int], None, None]:
    """
    List meta data (width, size, min and max pixel values) for all DICOM files
    inside the given directory (optionally including sub directories).
    :param dir: Path to a directory to look for DICOM files in
    :param recursive: If true: search in subdirectories
    :return: Generator of Tuples of (filename, width, height, minPixelValue, maxPixelValue)
    """
    for file in list_files(dir, recursive):
        meta = (file.name, *read_meta(str(file)))
        yield meta


def is_corrupted(dcm_filename: str) -> bool:
    """
    Checks if the given DICOM file is corrupted ot not, i.e. if the data array can be read or not/
    :param fcm_filename: path to the DICOM file to check for corruption
    :return: True iff the data array could NOT be read
    """
    from pydicom import dcmread
    import numpy as np
    try:
        dcm = dcmread(dcm_filename, stop_before_pixels=False)
        # access pixel array
        _ = dcm.pixel_array.astype(np.int16)
        return False
    except:
        return True


def find_corrupted(dir: str, recursive: bool = False) -> Generator[Tuple[bool, str], None, None]:
    """
    List all corrupted DICOM files inside the given directory (optionally including sub directories).
    :param dir: Path to a directory to look for corrupted DICOM files in
    :param recursive: If True: search in subdirectories
    :return: Generator of (is_corrupted, filename) pairs.
    """
    for file in list_files(dir, recursive):
        yield is_corrupted(str(file)), file.name


def read_image(dcm_filename: str) -> np.array:
    """ Read the pixel data from the given DICOM file
    :param dcm_filename: path to DICOM file to read the pixel data from
    :return: numpy array containing the pixel data
    """
    from pydicom import dcmread

    dcm = dcmread(dcm_filename)
    return dcm.pixel_array
