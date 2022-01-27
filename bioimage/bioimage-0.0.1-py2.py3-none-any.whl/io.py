from datetime import datetime
from pathlib import Path
from typing import Union
import skimage
from skimage.exposure import rescale_intensity
from skimage import util, filters, morphology
import matplotlib.pyplot as plt
import numpy as np
import pims
from functional import seq
from pims import *
from pycomfort.files import *


def load_bio_image(from_file: Path):
    """
    Load microscopy image
    :param from_file:
    :return:
    """
    return pims.Bioformats(str(from_file))


def load_frame(from_file: Path):
    return load_bio_image(from_file).get_frame_2D()


def file_image(from_file: Path):
    return (from_file, load_bio_image(from_file))



def get_date(image, verbose=False):
    """
    Get date of the microscopy image
    :param i:
    :param verbose:
    :return:
    """
    d = image.metadata.ImageAcquisitionDate(0)
    if(verbose):
        print(d)
    return datetime.strptime(d[0:d.index("T")], '%Y-%m-%d')

def gray2color(u: np.ndarray, channel: int = 1) -> np.ndarray:
    """

    :param u:  fluorescence image
    :param channel: Channel to code the image in (0: Red, 1: Green, 2: Blue).
    :return: The computed output image in color. Green by default
    """
    return np.dstack((
        rescale_intensity(u if channel == 0 else np.zeros_like(u), out_range='float'),
        rescale_intensity(u if channel == 1 else np.zeros_like(u), out_range='float'),
        rescale_intensity(u if channel == 2 else np.zeros_like(u), out_range='float'),
    ))


def image_2_tiff(image: np.ndarray, where: str, clahe: bool = False):
    img = skimage.exposure.equalize_adapthist(image, kernel_size=None, clip_limit=0.01, nbins=256) if clahe else image
    import tifffile
    tifffile.imwrite(where, img)


def frame_2_tiff(frame: pims.Frame, where: str, clahe: bool = False):
    img = skimage.exposure.equalize_adapthist(frame, kernel_size=None, clip_limit=0.01, nbins=256) if clahe else frame
    import tifffile
    tifffile.imwrite(where, img, metadata=frame.metadata)

def make_tiffs(folder: Path, overwrite: bool = False):
    for d in dirs(folder):
        tiffs: Path = (d / "tiffs")
        tiffs.mkdir(parents=True, exist_ok=True)
        print(f'creating tiffs at {tiffs.as_posix()}')
        for f in files(d):
            if "czi" in f.suffix:
                frame = load_frame(f)
                path: Path = (tiffs / (f.stem+".tiff"))
                if path.exists():
                    if overwrite:
                        print(f'\t {path.as_posix()} exists, but we are overwriting!')
                        frame_2_tiff(frame, path.as_posix(), False)
                else:
                    print(f'\t Creating tiff {path.as_posix()}')
                    frame_2_tiff(frame, path.as_posix(), False)