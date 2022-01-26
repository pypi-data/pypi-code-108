#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020, 2021.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""Subpackage to load images and tables."""

import typing as t
from pathlib import Path

import fsspec
import numpy as np
import pandas as pd
from astropy.io import fits
from PIL import Image

from pyxel.options import global_options


def load_image(filename: t.Union[str, Path]) -> np.ndarray:
    """Load a 2D image.

    Parameters
    ----------
    filename : str or Path
        Filename to read an image.
        {.npy, .fits, .txt, .data, .jpg, .jpeg, .bmp, .png, .tiff} are accepted.

    Returns
    -------
    array : ndarray
        A 2D array.

    Raises
    ------
    FileNotFoundError
        If an image is not found.
    ValueError
        When the extension of the filename is unknown or separator is not found.

    Examples
    --------
    >>> from pyxel.inputs_outputs import load_image
    >>> load_image("frame.fits")
    array([[-0.66328494, -0.63205819, ...]])

    >>> load_image("https://hostname/folder/frame.fits")
    array([[-0.66328494, -0.63205819, ...]])

    >>> load_image("another_frame.npy")
    array([[-1.10136521, -0.93890239, ...]])

    >>> load_image("rgb_frame.jpg")
    array([[234, 211, ...]])
    """
    # Extract suffix (e.g. '.txt', '.fits'...)
    suffix = Path(filename).suffix.lower()  # type: str

    if isinstance(filename, Path):
        full_filename = filename.expanduser().resolve()  # type: Path
        if not full_filename.exists():
            raise FileNotFoundError(f"Input file '{full_filename}' can not be found.")

        url_path = str(full_filename)  # type: str

    else:
        url_path = filename

    # Define extra parameters to use with 'fsspec'
    extras = {}
    if global_options.cache_enabled:
        url_path = f"simplecache::{url_path}"

        if global_options.cache_folder:
            extras["simplecache"] = {"cache_storage": global_options.cache_folder}

    if suffix.startswith(".fits"):
        with fsspec.open(url_path, mode="rb", **extras) as file_handler:

            # Fix for fsspec version 0.9
            if isinstance(file_handler, fsspec.implementations.local.LocalFileOpener):
                try:
                    _ = file_handler.fileno()
                except OSError:
                    file_handler.fileno = file_handler.f.fileno

            data_2d = fits.getdata(file_handler)  # type: np.ndarray

    elif suffix.startswith(".npy"):
        with fsspec.open(url_path, mode="rb", **extras) as file_handler:
            data_2d = np.load(file_handler)

    elif suffix.startswith(".txt") or suffix.startswith(".data"):
        for sep in ["\t", " ", ",", "|", ";"]:
            try:
                with fsspec.open(url_path, mode="r", **extras) as file_handler:
                    data_2d = np.loadtxt(file_handler, delimiter=sep, ndmin=2)
                break
            except ValueError:
                pass
        else:
            raise ValueError(f"Cannot find the separator for filename '{url_path}'.")

    elif suffix.startswith((".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif")):
        with fsspec.open(url_path, mode="rb", **extras) as file_handler:
            image_2d = Image.open(file_handler)
            image_2d_converted = image_2d.convert("LA")  # RGB to grayscale conversion

        data_2d = np.array(image_2d_converted)[:, :, 0]

    else:
        raise ValueError(
            "Image format not supported. List of supported image formats: "
            ".npy, .fits, .txt, .data, .jpg, .jpeg, .bmp, .png, .tiff, .tif."
        )

    return data_2d


def load_table(filename: t.Union[str, Path]) -> pd.DataFrame:
    """Load a table from a file and returns a pandas dataframe. No header is expected in xlsx.

    Parameters
    ----------
    filename: str or Path
        Filename to read the table.
        {.npy, .xlsx, .csv, .txt., .data} are accepted.

    Returns
    -------
    table: DataFrame

    Raises
    ------
    FileNotFoundError
        If an image is not found.
    ValueError
        When the extension of the filename is unknown or separator is not found.

    """
    suffix = Path(filename).suffix.lower()  # type: str

    if isinstance(filename, Path):
        full_filename = Path(filename).expanduser().resolve()
        if not full_filename.exists():
            raise FileNotFoundError(f"Input file '{full_filename}' can not be found.")

        url_path = str(full_filename)  # type: str
    else:
        url_path = filename

    # Define extra parameters to use with 'fsspec'
    extras = {}
    if global_options.cache_enabled:
        url_path = f"simplecache::{url_path}"

        if global_options.cache_folder:
            extras["simplecache"] = {"cache_storage": global_options.cache_folder}

    if suffix.startswith(".npy"):
        with fsspec.open(url_path, mode="rb", **extras) as file_handler:
            table = pd.DataFrame(np.load(file_handler), dtype="float")

    elif suffix.startswith(".xlsx"):
        with fsspec.open(url_path, mode="rb", **extras) as file_handler:
            table = pd.read_excel(
                file_handler,
                header=None,
                convert_float=False,
            )

    elif suffix.startswith(".csv"):
        for sep in ["\t", " ", ",", "|", ";"]:
            try:
                # numpy will return ValueError with a wrong delimiter
                with fsspec.open(url_path, mode="r", **extras) as file_handler:
                    table = pd.read_csv(
                        file_handler, delimiter=sep, header=None, dtype="float"
                    )
                    break
            except ValueError:
                pass
        else:
            raise ValueError("Cannot find the separator.")

    elif suffix.startswith(".txt") or suffix.startswith(".data"):
        for sep in ["\t", " ", ",", "|", ";"]:
            try:
                with fsspec.open(url_path, mode="r", **extras) as file_handler:
                    table = pd.read_table(
                        file_handler, delimiter=sep, header=None, dtype="float"
                    )
                    break
            except ValueError:
                pass
        else:
            raise ValueError("Cannot find the separator.")

    else:
        raise ValueError("Only .npy, .xlsx, .csv, .txt and .data implemented.")

    return table
