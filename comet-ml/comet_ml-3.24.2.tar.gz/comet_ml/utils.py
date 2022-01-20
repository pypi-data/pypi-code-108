# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2021 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

from __future__ import print_function

import atexit
import calendar
import getpass
import io
import json
import logging
import math
import numbers
import os
import os.path
import random
import re
import sys
import tempfile
import time
import uuid
from datetime import datetime

import six
from pkg_resources import DistributionNotFound, get_distribution
from requests.models import PreparedRequest
from six.moves.urllib.parse import urlparse, urlunparse

from ._typing import (
    IO,
    Any,
    Callable,
    Dict,
    Generator,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Union,
)
from .compat_utils import Mapping, StringIO, json_dump
from .convert_utils import convert_tensor_to_numpy
from .json_encoder import NestedEncoder
from .logging_messages import (
    CONVERT_DATAFRAME_INVALID_FORMAT,
    CONVERT_TABLE_INVALID_FORMAT,
    DATAFRAME_CONVERSION_ERROR,
    DATAFRAME_PROFILE_ERROR,
    MISSING_PANDAS_PROFILING,
)

LOGGER = logging.getLogger(__name__)
LOG_ONCE_CACHE = set()  # type: Set[str]


if hasattr(time, "monotonic"):
    get_time_monotonic = time.monotonic
else:
    # Python2 just won't have accurate time durations
    # during clock adjustments, like leap year, etc.
    get_time_monotonic = time.time

try:
    import numpy

    HAS_NUMPY = True
except ImportError:
    LOGGER.warning("numpy not installed; some functionality will be unavailable")
    HAS_NUMPY = False
    numpy = None


INFINITY = float("inf")


def fix_special_floats(value, _inf=INFINITY, _neginf=-INFINITY):
    """Fix out of bounds floats (like infinity and -infinity) and Not A
    Number.
    Returns either a fixed value that could be JSON encoded or the original
    value.
    """

    try:
        value = convert_tensor_to_numpy(value)

        # Check if the value is Nan, equivalent of math.isnan
        if math.isnan(value):
            return "NaN"

        elif value == _inf:
            return "Infinity"

        elif value == _neginf:
            return "-Infinity"

    except Exception:
        # Value cannot be compared
        return value

    return value


def log_once_at_level(logging_level, message, *args, **kwargs):
    """
    Log the given message once at the given level then at the DEBUG
    level on further calls.

    This is a global log-once-per-session, as ooposed to the
    log-once-per-experiment.
    """
    global LOG_ONCE_CACHE

    if message not in LOG_ONCE_CACHE:
        LOG_ONCE_CACHE.add(message)
        LOGGER.log(logging_level, message, *args, **kwargs)
    else:
        LOGGER.debug(message, *args, **kwargs)


def merge_url(url, params):
    # type: (str, Dict[Any, Any]) -> str
    """
    Given an URL that might have query strings,
    combine with additional query strings.

    Args:
        url - a url string (perhaps with a query string)
        params - a dict of additional query key/values

    Returns: a string
    """
    req = PreparedRequest()
    req.prepare_url(url, params)
    return req.url


def is_iterable(value):
    try:
        iter(value)
        return True

    except TypeError:
        return False


def is_list_like(value):
    """Check if the value is a list-like"""
    if is_iterable(value) and not isinstance(value, six.string_types):
        return True

    else:
        return False


def to_utf8(str_or_bytes):
    if hasattr(str_or_bytes, "decode"):
        return str_or_bytes.decode("utf-8", errors="replace")

    return str_or_bytes


def local_timestamp():
    # type: () -> int
    """Return a timestamp in a format expected by the backend (milliseconds)"""
    now = datetime.utcnow()
    timestamp_in_seconds = calendar.timegm(now.timetuple()) + (now.microsecond / 1e6)
    timestamp_in_milliseconds = int(timestamp_in_seconds * 1000)
    return timestamp_in_milliseconds


def wait_for_done(check_function, timeout, progress_callback=None, sleep_time=1):
    """Wait up to TIMEOUT seconds for the check function to return True"""
    end_time = time.time() + timeout
    while check_function() is False and time.time() < end_time:
        if progress_callback is not None:
            progress_callback()
        # Wait a max of sleep_time, but keep checking to see if
        # check_function is done. Allows wait_for_empty to end
        # before sleep_time has elapsed:
        end_sleep_time = time.time() + sleep_time
        while check_function() is False and time.time() < end_sleep_time:
            time.sleep(sleep_time / 20.0)


def read_unix_packages(package_status_file="/var/lib/dpkg/status"):
    # type: (str) -> Optional[List[str]]
    if os.path.isfile(package_status_file):
        package = None
        os_packages = []
        with open(package_status_file, "rb") as fp:
            for binary_line in fp:
                line = binary_line.decode("utf-8", errors="ignore").strip()
                if line.startswith("Package: "):
                    package = line[9:]
                if line.startswith("Version: "):
                    version = line[9:]
                    if package is not None:
                        os_packages.append((package, version))
                    package = None
        os_packages_list = sorted(
            [("%s=%s" % (package, version)) for (package, version) in os_packages]
        )
        return os_packages_list
    else:
        return None


def image_data_to_file_like_object(
    image_data,
    file_name,
    image_format,
    image_scale,
    image_shape,
    image_colormap,
    image_minmax,
    image_channels,
):
    # type: (Union[IO[bytes], Any], Optional[str], str, float, Optional[Sequence[int]], Optional[str], Optional[Sequence[float]], str) -> Union[IO[bytes], None, Any]
    """
    Ensure that the given image_data is converted to a file_like_object ready
    to be uploaded
    """
    try:
        import PIL.Image
    except ImportError:
        PIL = None

    ## Conversion from standard objects to image
    ## Allow file-like objects, numpy arrays, etc.
    if hasattr(image_data, "numpy"):  # pytorch tensor
        array = convert_tensor_to_numpy(image_data)
        fp = array_to_image_fp(
            array,
            image_format,
            image_scale,
            image_shape,
            image_colormap,
            image_minmax,
            image_channels,
        )

        return fp
    elif hasattr(image_data, "eval"):  # tensorflow tensor
        array = image_data.eval()
        fp = array_to_image_fp(
            array,
            image_format,
            image_scale,
            image_shape,
            image_colormap,
            image_minmax,
            image_channels,
        )

        return fp
    elif PIL is not None and isinstance(image_data, PIL.Image.Image):  # PIL.Image
        ## filename tells us what format to use:
        if file_name is not None and "." in file_name:
            _, image_format = file_name.rsplit(".", 1)
        fp = image_to_fp(image_data, image_format)

        return fp
    elif image_data.__class__.__name__ == "ndarray":  # numpy array
        fp = array_to_image_fp(
            image_data,
            image_format,
            image_scale,
            image_shape,
            image_colormap,
            image_minmax,
            image_channels,
        )

        return fp
    elif hasattr(image_data, "read"):  # file-like object
        return image_data
    elif isinstance(image_data, (tuple, list)):  # list or tuples
        if not HAS_NUMPY:
            LOGGER.error("The Python library numpy is required for this operation")
            return None
        array = numpy.array(image_data)
        fp = array_to_image_fp(
            array,
            image_format,
            image_scale,
            image_shape,
            image_colormap,
            image_minmax,
            image_channels,
        )
        return fp
    else:
        LOGGER.error("invalid image file_type: %s", type(image_data))
        if PIL is None:
            LOGGER.error("Consider installing the Python Image Library, PIL")
        return None


def array_to_image_fp(
    array,
    image_format,
    image_scale,
    image_shape,
    image_colormap,
    image_minmax,
    image_channels,
):
    # type: (Any, str, float, Optional[Sequence[int]], Optional[str], Optional[Sequence[float]], str) -> Optional[IO[bytes]]
    """
    Convert a numpy array to an in-memory image
    file pointer.
    """
    image = array_to_image(
        array, image_scale, image_shape, image_colormap, image_minmax, image_channels
    )
    if not image:
        return None
    return image_to_fp(image, image_format)


def array_to_image(
    array,
    image_scale=1.0,
    image_shape=None,
    image_colormap=None,
    image_minmax=None,
    image_channels=None,
    mode=None,
):
    # type: (Any, float, Optional[Sequence[int]], Optional[str], Optional[Sequence[float]], Optional[str], Optional[str]) -> Optional[Any]
    """
    Convert a numpy array to an in-memory image.
    """
    try:
        import numpy
        import PIL.Image
        from matplotlib import cm
    except ImportError:
        LOGGER.error(
            "The Python libraries PIL, numpy, and matplotlib are required for converting a numpy array into an image"
        )
        return None

    array = numpy.array(array)

    ## Handle image transformations here
    ## End up with a 0-255 PIL Image
    if image_minmax is not None:
        minmax = image_minmax
    else:  # auto minmax
        flatten_array = flatten(array)
        min_array = min(flatten_array)
        max_array = max(flatten_array)
        if min_array == max_array:
            min_array = min_array - 0.5
            max_array = max_array + 0.5
        min_array = math.floor(min_array)
        max_array = math.ceil(max_array)
        minmax = [min_array, max_array]

    ## if a shape is given, try to reshape it:
    if image_shape is not None:
        try:
            ## array shape is opposite of image size(width, height)
            if len(image_shape) == 2:
                array = array.reshape(image_shape[1], image_shape[0])
            elif len(image_shape) == 3:
                array = array.reshape(image_shape[1], image_shape[0], image_shape[2])
            else:
                raise Exception(
                    "invalid image_shape: %s; should be 2D or 3D" % image_shape
                )
        except Exception:
            LOGGER.info("WARNING: invalid image_shape; ignored", exc_info=True)

    if image_channels == "first" and len(array.shape) == 3:
        array = numpy.moveaxis(array, 0, -1)
    ## If 3D, but last array is flat, make it 2D:
    if len(array.shape) == 3:
        if array.shape[-1] == 1:
            array = array.reshape((array.shape[0], array.shape[1]))
        elif array.shape[0] == 1:
            array = array.reshape((array.shape[1], array.shape[2]))
    elif len(array.shape) == 1:
        ## if 1D, make it 2D:
        array = numpy.array([array])

    ### Ok, now let's colorize and scale
    if image_colormap is not None:
        ## Need to be in range (0,1) for colormapping:
        array = rescale_array(array, minmax, (0, 1), "float")
        try:
            cm_hot = cm.get_cmap(image_colormap)
            array = cm_hot(array)
        except Exception:
            LOGGER.info("WARNING: invalid image_colormap; ignored", exc_info=True)
        ## rescale again:
        array = rescale_array(array, (0, 1), (0, 255), "uint8")
        ## Convert to RGBA:
        image = PIL.Image.fromarray(array, "RGBA")
    else:
        ## Rescale (0, 255)
        array = rescale_array(array, minmax, (0, 255), "uint8")
        image = PIL.Image.fromarray(array)

    if image_scale != 1.0:
        image = image.resize(
            (int(image.size[0] * image_scale), int(image.size[1] * image_scale))
        )

    ## Put in a standard mode:
    if mode:
        image = image.convert(mode)
    elif image.mode not in ["RGB", "RGBA"]:
        image = image.convert("RGB")
    return image


def dataset_to_sprite_image(
    matrix,
    size,
    preprocess_function=None,
    transparent_color=None,
    background_color_function=None,
):
    # type: (Any, Sequence[int], Optional[Callable], Optional[Sequence[int]], Optional[Callable]) -> Any
    """
    Convert a dataset (array of arrays) into a giant image of
    images (a sprite sheet).

    Args:
        matrix: array of vectors or Images
        size: (width, height) of each thumbnail image
        preprocess_function: function to preprocess image values
        transparent_color: color to mark as transparent
        background_color_function: function that takes index, returns a color

    Returns: image
    """
    try:
        from PIL import Image
    except ImportError:
        LOGGER.error("The Python library PIL is required for this operation")
        return None

    length = len(matrix)
    sprite_size = math.ceil(math.sqrt(length))

    sprite_image = Image.new(
        mode="RGBA",
        size=(int(sprite_size * size[0]), int(sprite_size * size[1])),
        color=(0, 0, 0, 0),
    )
    if preprocess_function is not None:
        matrix = preprocess_function(matrix)
    for i, array in enumerate(matrix):
        if isinstance(array, Image.Image):
            image = array
        else:
            image = array_to_image(
                array,
                image_scale=1.0,
                image_shape=size,
                image_colormap=None,
                image_minmax=(0, 255),
                image_channels="last",
                mode="RGBA",
            )

            if not image:
                return None

        if transparent_color is not None:
            image = image_transparent_color(image, transparent_color, threshold=1)
        if background_color_function is not None:
            color = background_color_function(i)
            image = image_background_color(image, color)
        if image.mode != "RGBA":
            image = image.convert("RGBA")
        location = (int((i % sprite_size) * size[0]), int((i // sprite_size) * size[1]))
        sprite_image.paste(image, location)
    return sprite_image


def image_background_color(image, color):
    # type: (Any, Sequence[int]) -> Optional[Any]
    """
    Given an image with some transparency, add a background color to it.

    Args:
        image: a PIL image
        color: a red, green, blue color tuple
    """
    try:
        from PIL import Image
    except ImportError:
        LOGGER.error("The Python library PIL is required for this operation")
        return None

    if image.mode != "RGBA":
        raise ValueError(
            "image must have an alpha channel in order to set a background color"
        )

    new_image = Image.new("RGB", image.size, color)
    new_image.paste(image, (0, 0), image)
    return new_image


def image_transparent_color(image, color, threshold=1):
    # type: (Any, Tuple[int, int, int], int) -> Any
    """
    Given a color, make that be the transparent color.

    Args:
        image: a PIL image
        color: a red, green, blue color tuple
        threshold: the max difference in each color component
    """
    try:
        import numpy
        from PIL import Image
    except ImportError:
        LOGGER.error(
            "The Python libraries PIL and numpy are required for this operation"
        )
        return

    image = image.convert("RGBA")
    array = numpy.array(numpy.asarray(image))
    r, g, b, a = numpy.rollaxis(array, axis=-1)
    mask = (
        (numpy.abs(r - color[0]) < threshold)
        & (numpy.abs(g - color[1]) < threshold)
        & (numpy.abs(b - color[2]) < threshold)
    )
    array[mask, 3] = 0
    return Image.fromarray(array, mode="RGBA")


def image_to_fp(image, image_format):
    # type: (Any, str) -> IO[bytes]
    """
    Convert a PIL.Image into an in-memory file
    pointer.
    """
    fp = io.BytesIO()
    image.save(fp, format=image_format)  # save the content to fp
    fp.seek(0)
    return fp


def rescale_array(array, old_range, new_range, dtype):
    """
    Given a numpy array in an old_range, rescale it
    into new_range, and make it an array of dtype.
    """
    if not HAS_NUMPY:
        LOGGER.error("The Python library numpy is required for this operation")
        return

    old_min, old_max = old_range
    if array.min() < old_min or array.max() > old_max:
        ## truncate:
        array = numpy.clip(array, old_min, old_max)
    new_min, new_max = new_range
    old_delta = float(old_max - old_min)
    new_delta = float(new_max - new_min)
    if old_delta == 0:
        return ((array - old_min) + (new_min + new_max) / 2.0).astype(dtype)
    else:
        return (new_min + (array - old_min) * new_delta / old_delta).astype(dtype)


def write_file_like_to_tmp_file(file_like_object, tmpdir):
    # type: (IO, str) -> str
    # Copy of `shutil.copyfileobj` with binary / text detection

    buf = file_like_object.read(1)

    tmp_file = tempfile.NamedTemporaryFile(mode="w+b", dir=tmpdir, delete=False)

    encode = False

    # Detect binary/text
    if not isinstance(buf, bytes):
        encode = True
        buf = buf.encode("utf-8")

    tmp_file.write(buf)

    # Main copy loop
    while True:
        buf = file_like_object.read(16 * 1024)

        if not buf:
            break

        if encode:
            buf = buf.encode("utf-8")

        tmp_file.write(buf)

    tmp_file.close()

    return tmp_file.name


def table_to_fp(tabular_data, delim, headers):
    # type: (Any, str, Union[Sequence[str], bool]) -> IO
    if isinstance(headers, bool):
        add_headers = headers
    else:
        add_headers = True
    fp = StringIO()
    for row in tabular_data:
        if isinstance(row, (numbers.Number, six.string_types)):
            if add_headers:
                if isinstance(headers, bool):
                    fp.write('"column1"\n')
                else:
                    fp.write('"%s"\n' % (headers[0],))
                add_headers = False
            fp.write(str(row) + "\n")
        else:
            columns = flatten(row)
            if add_headers:
                for i, column in enumerate(columns):
                    if isinstance(headers, bool):
                        column = '"column%s"' % (i + 1)
                    else:
                        column = '"%s"' % (headers[i],)
                    if i == len(columns) - 1:
                        fp.write(column)
                    else:
                        fp.write(column + delim)
                fp.write("\n")
                add_headers = False
            for i, column in enumerate(columns):
                if i == len(columns) - 1:
                    fp.write(str(column))
                else:
                    fp.write(str(column) + delim)
            fp.write("\n")
    fp.seek(0)
    return fp


def data_to_fp(data):
    # type: (Union[bytes, str, Any]) -> Optional[IO]
    if isinstance(data, str):
        fp = StringIO()
        fp.write(data)
    elif isinstance(data, bytes):
        fp = io.BytesIO()
        fp.write(data)
    else:
        fp = StringIO()
        try:
            json.dump(data, fp)
        except Exception:
            LOGGER.error("Failed to log asset data as JSON", exc_info=True)
            return None
    fp.seek(0)
    return fp


ONE_KBYTE = float(1024)
ONE_MBYTE = float(1024 * 1024)
ONE_GBYTE = float(1024 * 1024 * 1024)


def format_bytes(size):
    # type: (float) -> str
    """
    Given a size in bytes, return a sort string representation.
    """
    if size >= ONE_GBYTE:
        return "%.2f %s" % (size / ONE_GBYTE, "GB")
    elif size >= ONE_MBYTE:
        return "%.2f %s" % (size / ONE_MBYTE, "MB")
    elif size >= ONE_KBYTE:
        return "%.2f %s" % (size / ONE_KBYTE, "KB")
    else:
        return "%d %s" % (size, "bytes")


class Embedding(object):
    """
    Data structure for holding embedding template info.
    """

    def __init__(
        self,
        vector_url,
        vector_shape,
        metadata_url,
        sprite_url=None,
        image_size=None,
        title="Comet Embedding",
    ):
        """
        The URL's and sizes for all of the Embedding'
        resources.
        """
        self.vector_url = vector_url
        self.vector_shape = vector_shape
        self.metadata_url = metadata_url
        self.sprite_url = sprite_url
        self.image_size = image_size
        self.title = title

    def to_json(self):
        """
        Return a JSON representation of the embedding
        """
        template = {
            "tensorName": self.title,
            "tensorShape": list(self.vector_shape),
            "tensorPath": self.vector_url,
            "metadataPath": self.metadata_url,
        }
        if self.sprite_url is not None:
            template["sprite"] = {
                "imagePath": self.sprite_url,
                "singleImageDim": list(self.image_size),
            }
        return template


class Histogram(object):
    """
    Data structure for holding a counts of values. Creates an
    exponentially-distributed set of bins.

    See also [`Experiment.log_histogram`](#experimentlog_histogram)
    """

    def __init__(self, start=1e-12, stop=1e20, step=1.1, offset=0):
        """
        Initialize the values of bins and data structures.

        Args:
            start: float (optional, deprecated), value of start range. Default 1e-12
            stop: float (optional, deprecated), value of stop range. Default 1e20
            step: float (optional, deprecated), value of step. Creates an
                exponentially-distributed set of bins. Must be greater
                than 1.0. Default 1.1
            offset: float (optional), center of distribution. Default is zero.
        """
        if start != 1e-12 or stop != 1e20 or step != 1.1:
            log_once_at_level(
                logging.WARNING,
                "Histogram will deprecate changing start, stop, or step values in a future version",
            )

        if step <= 1.0:
            raise ValueError("Histogram step must be greater than 1.0")

        if start <= 0:
            raise ValueError("Histogram start must be greater than 0.0")

        if stop <= start:
            raise ValueError("Histogram stop must be greater than start")

        self.start = start
        self.stop = stop
        self.step = step
        self.offset = offset
        self.values = tuple(self.create_bin_values())
        self.clear()

    def __sub__(self, other):
        if (
            isinstance(other, Histogram)
            and (self.start == other.start)
            and (self.stop == other.stop)
            and (self.step == other.step)
            and (self.offset == other.offset)
        ):

            histogram = Histogram(self.start, self.stop, self.step, self.offset)
            histogram.counts = [
                abs(c2 - c1) for c1, c2 in zip(self.counts, other.counts)
            ]
            return histogram
        else:
            raise TypeError("Can't subtract Histograms of different regions")

    def clear(self):
        """
        Clear the counts, initializes back to zeros.
        """
        self.counts = [0] * len(self.values)
        if HAS_NUMPY:
            self.counts = numpy.array(self.counts)

    def get_bin_index(self, value):
        """
        Given a value, return the bin index where:

            values[index] <= value < values[index + 1]
        """
        midpoint = len(self.counts) // 2
        if value >= self.stop:
            return len(self.values) - 2  # slight asymmetry
        elif value <= -self.stop:
            return 0
        base = self.step
        if value - self.offset == 0:
            return midpoint
        elif value - self.offset < 0:
            return (
                midpoint
                - 1
                - int(math.ceil(math.log(abs(value - self.offset) / self.start, base)))
            )
        else:
            return (
                int(math.ceil(math.log((value - self.offset) / self.start, base)))
                + midpoint
            )

    def _add_via_python(self, values, counts=None, max_skip_count=None):
        # type: (List, Optional[List], int) -> None
        """
        Values is a Python list. Only used
        when numpy is not available.
        """
        max_skip_count = max_skip_count if max_skip_count is not None else 10

        # Sort for speed of inserts
        if counts is None:
            values.sort()

        # Find initial bin:
        bucket = self.get_bin_index(values[0])

        # Avoid attributes lookup at every loop
        self_values = self.values
        self_counts = self.counts

        for i, value in enumerate(values):
            skip_count = 0
            while not (
                (bucket == 0 and value <= self_values[1])
                or (self_values[bucket] <= value < self_values[bucket + 1])
            ):
                skip_count += 1
                if skip_count > max_skip_count:
                    # if too many skips
                    bucket = self.get_bin_index(value)
                    break
                else:
                    bucket += 1

            if counts is not None:
                self_counts[bucket] += int(counts[i])
            else:
                self_counts[bucket] += 1

    def _add_via_numpy(self, values, counts=None):
        # type: (numpy.ndarray, Optional[numpy.ndarray]) -> None
        """
        Assumes numpy values (and counts).
        """
        midpoint = len(self.counts) // 2
        base = numpy.log(self.step)

        # Positive values (values > offset)

        # The filter is an array of boolean same size as values
        positive_values_filter = numpy.bitwise_and(
            values > self.offset, values < self.stop
        )

        # This is a numpy array with only positive values and we center them
        # around the offset (default 0 so no-op)
        positive_values = values[positive_values_filter] - self.offset

        # Then we transform all values to the suite index, and we add the
        # midpoint as we are storing positives (values > offset) at the end of
        # the self.values array
        positive_indices = (
            numpy.ceil(numpy.log(positive_values / self.start) / base).astype(int)
            + midpoint
        )

        # Negative values (values > offset)

        # The filter is an array of boolean same size as values
        negative_values_filter = numpy.bitwise_and(
            values < self.offset, values > -self.stop
        )

        # This is a numpy array with only negatives values and we center them
        # around the offset (default 0 so no-op)
        negative_values = values[negative_values_filter] - self.offset

        # Then we transform all values to the suite index, and substract the
        # index from the midpoint as we are storing positives (values > offset)
        # at the end of the self.values array
        negative_indices = (
            midpoint
            - 1
            - numpy.ceil(
                numpy.log(numpy.absolute(negative_values) / self.start) / base
            ).astype(int)
        )

        # Values equals to the offset
        zero_values = values[values == self.offset]

        if counts is not None:
            for i, match in enumerate(positive_values_filter):
                if match:
                    self.counts[positive_indices[i]] += counts[i]
            for i, match in enumerate(negative_values_filter):
                if match:
                    self.counts[negative_indices[i]] += counts[i]
        else:
            numpy.add.at(self.counts, positive_indices, 1)
            numpy.add.at(self.counts, negative_indices, 1)

        self.counts[midpoint] += len(zero_values)

    def add(self, values, counts=None, max_skip_count=None):
        """
        Add the value(s) to the count bins.

        Args:
            values: a list, tuple, or array of values (any shape)
                to count
            counts: a list of counts for each value in values. Triggers
                special mode for conversion from Tensorboard
                saved format. Assumes values are in order (min to max).
            max_skip_count: int, (optional) maximum number of missed
                bins that triggers get_bin_index() (only used
                when numpy is not available).

         Counting values in bins can be expensive, so this method uses
        numpy where possible.
        """
        try:
            values = [float(values)]
        except Exception:
            pass

        # Returns numpy array, if possible:
        values = fast_flatten(values)

        if len(values) == 0:
            return

        if HAS_NUMPY:
            if counts is not None:
                counts = numpy.array(counts)
            self._add_via_numpy(values, counts)
        else:
            self._add_via_python(values, counts, max_skip_count)

    def counts_compressed(self):
        """
        Convert list of counts to list of [(index, count), ...].
        """
        return [[i, int(count)] for (i, count) in enumerate(self.counts) if count > 0]

    @classmethod
    def from_json(cls, data, verbose=True):
        """
        Given histogram JSON data, returns either a Histogram object (in
        the case of a 2D histogram) or a list of Histogram objects (in
        the case of a 3D histogram).

        Args:
            data: histogram filename or JSON data
            verbose: optional, bool, if True, display the Histogram
                after conversion

        Returns: a Histogram, or list of Histograms.

        Example:

        ```python
        In[1]: histogram = Histogram.from_json("histogram.json")

        Histogram 3D:
        Step: 0
        Histogram
        =========
        Range Start      Range End          Count           Bins
        -----------------------------------------------------------
            -0.1239        -0.1003        63.7810      [506-508]
            -0.1003        -0.0766      1006.1836      [508-511]
            -0.0766        -0.0530      1824.0884      [511-514]
            -0.0530        -0.0293     11803.4008      [514-521]
            -0.0293        -0.0056     13118.4797      [521-538]
            -0.0056         0.0180     13059.5624     [538-1023]
             0.0180         0.0417     13133.6479    [1023-1032]
             0.0417         0.0654      5865.2828    [1032-1037]
             0.0654         0.0890      1616.2949    [1037-1040]
             0.0890         0.1127       275.2784    [1040-1042]
             0.1127         0.1363         0.0000    [1042-1044]
        -----------------------------------------------------------
        Total:     61766.0000
        Out[1]:
        <comet_ml.utils.Histogram at 0x7fac8f3819b0>
        ```
        """
        if isinstance(data, str):
            filename = os.path.expanduser(data)
            if os.path.isfile(filename):
                with open(filename) as fp:
                    histogram_json = json.load(fp)
                    return Histogram.from_json(histogram_json, verbose=verbose)
            else:
                LOGGER.error("Histogram.from_json: no such file %r", filename)
                return
        elif "histograms" in data:
            retval = []
            if verbose:
                print("Histogram 3D:")
            for datum in data["histograms"]:
                histogram_json = datum["histogram"]
                if verbose:
                    print("Step:", datum["step"])
                histogram = Histogram.from_json(histogram_json, verbose=verbose)
                retval.append(histogram)
            return retval
        else:
            histogram = Histogram(
                data["start"], data["stop"], data["step"], data["offset"]
            )
            for (i, count) in data["index_values"]:
                histogram.counts[i] = count
            if verbose:
                histogram.display()
            return histogram

    def to_json(self):
        """
        Return histogram as JSON-like dict.
        """
        return {
            "version": 2,
            "index_values": self.counts_compressed(),
            "values": None,
            "offset": self.offset,
            "start": self.start,
            "stop": self.stop,
            "step": self.step,
        }

    def is_empty(self):
        # type: () -> bool
        """Check if the Histogram is empty. Return True if empty, False otherwise"""
        # If the Histogram contains at least one value, at least one element of
        # self.counts will be not null
        return not any(self.counts)

    def create_bin_values(self):
        """
        Create exponentially distributed bin values
        [-inf, ..., offset - start, offset, offset + start, ..., inf)
        """
        values = [-float("inf"), self.offset, float("inf")]
        value = self.start
        while self.offset + value <= self.stop:
            values.insert(1, self.offset - value)
            values.insert(-1, self.offset + value)
            value *= self.step
        return values

    def get_count(self, min_value, max_value):
        """
        Get the count (can be partial of bin count) of a range.
        """
        index = self.get_bin_index(min_value)
        current_start_value = self.values[index]
        current_stop_value = self.values[index + 1]
        count = 0
        # Add total in this area:
        count += self.counts[index]
        if current_start_value != -float("inf"):
            # Remove proportion before min_value:
            current_total_range = current_stop_value - current_start_value
            percent = (min_value - current_start_value) / current_total_range
            count -= self.counts[index] * percent
        if max_value < current_stop_value:
            # stop is inside this area too, so remove after max
            if current_start_value != -float("inf"):
                percent = (current_stop_value - max_value) / current_total_range
                count -= self.counts[index] * percent
            return count
        # max_value is beyond this area, so loop until last area:
        index += 1
        while max_value > self.values[index + 1]:
            # add the whole count
            count += self.counts[index]
            index += 1
        # finally, add the proportion in last area before max_value:
        current_start_value = self.values[index]
        current_stop_value = self.values[index + 1]
        if current_stop_value != float("inf"):
            current_total_range = current_stop_value - current_start_value
            percent = (max_value - current_start_value) / current_total_range
            count += self.counts[index] * percent
        else:
            count += self.counts[index]
        return count

    def get_counts(self, min_value, max_value, span_value):
        """
        Get the counts between min_value and max_value in
        uniform span_value-sized bins.
        """
        counts = []

        if max_value == min_value:
            max_value = min_value * 1.1 + 1
            min_value = min_value / 1.1 - 1

        bucketPos = 0
        binLeft = min_value

        while binLeft < max_value:
            binRight = binLeft + span_value
            count = 0.0
            # Don't include last as bucketLeft, which is infinity:
            while bucketPos < len(self.values) - 1:
                bucketLeft = self.values[bucketPos]
                bucketRight = min(max_value, self.values[bucketPos + 1])
                intersect = min(bucketRight, binRight) - max(bucketLeft, binLeft)

                if intersect > 0:
                    if bucketLeft == -float("inf"):
                        count += self.counts[bucketPos]
                    else:
                        count += (intersect / (bucketRight - bucketLeft)) * self.counts[
                            bucketPos
                        ]

                if bucketRight > binRight:
                    break

                bucketPos += 1

            counts.append(count)
            binLeft += span_value

        return counts

    def display(
        self, start=None, stop=None, step=None, format="%14.4f", show_empty=False
    ):
        """
        Show counts between start and stop by step increments.

        Args:
            start: optional, float, start of range to display
            stop: optional, float, end of range to display
            step: optional, float, amount to increment each range
            format: str (optional), format of numbers
            show_empty: bool (optional), if True, show all
                entries in range

        Example:

        ```
        >>> from comet_ml.utils import Histogram
        >>> import random
        >>> history = Histogram()
        >>> values = [random.random() for x in range(10000)]
        >>> history.add(values)
        >>> history.display()

        Histogram
        =========
           Range Start      Range End          Count           Bins
        -----------------------------------------------------------
               -0.0000         0.1000       983.4069     [774-1041]
                0.1000         0.2000       975.5574    [1041-1049]
                0.2000         0.3000      1028.8666    [1049-1053]
                0.3000         0.4000       996.2112    [1053-1056]
                0.4000         0.5000       979.5836    [1056-1058]
                0.5000         0.6000      1010.4522    [1058-1060]
                0.6000         0.7000       986.1284    [1060-1062]
                0.7000         0.8000      1006.5811    [1062-1063]
                0.8000         0.9000      1007.7881    [1063-1064]
                0.9000         1.0000      1025.4245    [1064-1065]
        -----------------------------------------------------------
        Total:     10000.0000
        """
        collection = self.collect(start, stop, step)
        print("Histogram")
        print("=========")
        size = len(format % 0)
        sformat = "%" + str(size) + "s"
        columns = ["Range Start", "Range End", "Count", "Bins"]
        formats = [sformat % s for s in columns]
        print(*formats)
        print("-" * (size * 4 + 3))
        total = 0.0
        for row in collection:
            count = row["count"]
            total += count
            if show_empty or count > 0:
                print(
                    format % row["value_start"],
                    format % row["value_stop"],
                    format % count,
                    (
                        sformat
                        % ("[%s-%s]" % (row["bin_index_start"], row["bin_index_stop"]))
                    ),
                )
        print("-" * (size * 4 + 3))
        print(("Total: " + format) % total)

    def collect(self, start=None, stop=None, step=None):
        """
        Collect the counts for the given range and step.

        Args:
            start: optional, float, start of range to display
            stop: optional, float, end of range to display
            step: optional, float, amount to increment each range

        Returns a list of dicts containing details on each
        virtual bin.
        """
        counts_compressed = self.counts_compressed()
        if start is None:
            if len(counts_compressed) > 0:
                start = self.values[counts_compressed[0][0]]
            else:
                start = -1.0
        if stop is None:
            if len(counts_compressed) > 1:
                stop = self.values[counts_compressed[-1][0]]
            else:
                stop = 1.0
        if step is None:
            step = (stop - start) / 10.0

        counts = self.get_counts(start, stop + step, step)
        current = start
        bins = []
        next_one = current + step
        i = 0
        while next_one <= stop + (step) and i < len(counts):
            start_bin = self.get_bin_index(current)
            stop_bin = self.get_bin_index(next_one)
            bin = {
                "value_start": current,
                "value_stop": next_one,
                "bin_index_start": start_bin,
                "bin_index_stop": stop_bin,
                "count": counts[i],
            }
            bins.append(bin)
            current = next_one
            next_one = current + step
            i += 1
        return bins


def write_numpy_array_as_wav(numpy_array, sample_rate, file_object):
    # type: (Any, int, IO) -> None
    """Convert a numpy array to a WAV file using the given sample_rate and
    write it to the file object
    """
    try:
        import numpy
        from scipy.io.wavfile import write
    except ImportError:
        LOGGER.error(
            "The Python libraries numpy, and scipy are required for this operation"
        )
        return

    array_max = numpy.max(numpy.abs(numpy_array))

    scaled = numpy.int16(numpy_array / array_max * 32767)

    write(file_object, sample_rate, scaled)


def get_file_extension(file_path):
    if file_path is None:
        return None

    ext = os.path.splitext(file_path)[1]
    if not ext:
        return None

    # Get rid of the leading "."
    return ext[1::]


def encode_metadata(metadata):
    # type: (Optional[Dict[Any, Any]]) -> Optional[str]
    if metadata is None:
        return None

    if type(metadata) is not dict:
        LOGGER.info("invalid metadata, expecting dict type", exc_info=True)
        return None

    if metadata == {}:
        return None

    try:
        json_encoded = json.dumps(metadata, separators=(",", ":"), sort_keys=True)
        return json_encoded
    except Exception:
        LOGGER.info("invalid metadata, expecting JSON-encodable object", exc_info=True)
        return None


def get_comet_version():
    # type: () -> str
    try:
        return get_distribution("comet_ml").version
    except DistributionNotFound:
        return "Please install comet with `pip install comet_ml`"


def get_user():
    # type: () -> str
    try:
        return getpass.getuser()
    except KeyError:
        # We are in a system with no user, like Docker container with custom UID
        return "unknown"
    except Exception:
        LOGGER.debug("Unkown exception getting the user from the system", exc_info=True)
        return "unknown"


def log_asset_folder(folder, recursive=False, extension_filter=None):
    # type: (str, bool, Optional[List[str]]) -> Generator[Tuple[str, str], None, None]
    extension_filter_set = None

    if extension_filter is not None:
        extension_filter_set = set(extension_filter)

    if recursive:
        for dirpath, _, file_names in os.walk(folder):
            for file_name in file_names:

                if extension_filter_set:
                    file_extension = os.path.splitext(file_name)[1]

                    if file_extension not in extension_filter_set:
                        continue

                file_path = os.path.join(dirpath, file_name)
                yield (file_name, file_path)
    else:
        file_names = sorted(os.listdir(folder))
        for file_name in file_names:
            file_path = os.path.join(folder, file_name)
            if os.path.isfile(file_path):

                if extension_filter_set:
                    file_extension = os.path.splitext(file_name)[1]
                    if file_extension not in extension_filter_set:
                        continue

                yield (file_name, file_path)


def parse_version_number(raw_version_number):
    # type: (str) -> Tuple[int, int, int]
    """
    Parse a valid "INT.INT.INT" string, or raise an
    Exception. Exceptions are handled by caller and
    mean invalid version number.
    """
    converted_version_number = [int(part) for part in raw_version_number.split(".")]

    if len(converted_version_number) != 3:
        raise ValueError(
            "Invalid version number %r, parsed as %r",
            raw_version_number,
            converted_version_number,
        )

    # Make mypy happy
    version_number = (
        converted_version_number[0],
        converted_version_number[1],
        converted_version_number[2],
    )
    return version_number


def format_version_number(version_number):
    # type: (Tuple[int, int, int]) -> str
    return ".".join(map(str, version_number))


def valid_ui_tabs(tab=None, preferred=False):
    """
    List of valid UI tabs in browser.
    """
    mappings = {
        "artifacts": "artifacts",
        "assets": "assets",
        "audio": "audio",
        "charts": "chart",
        "code": "code",
        "confusion-matrices": "confusionMatrix",
        "graphics": "images",
        "histograms": "histograms",
        "installed-packages": "installedPackages",
        "metrics": "metrics",
        "notes": "notes",
        "parameters": "params",
        "system-metrics": "systemMetrics",
        "text": "text",
        "output": "stdout",
        "panels": "panels",
        "graph": "graph",
        "other": "other",
        "html": "html",
    }
    preferred_names = list(mappings.keys())
    # Additional keys:
    mappings.update(
        {
            "assetStorage": "assets",
            "chart": "chart",
            "confusion-matrix": "confusionMatrix",
            "confusionMatrix": "confusionMatrix",
            "images": "images",
            "installedPackages": "installedPackages",
            "params": "params",
            "systemMetrics": "systemMetrics",
            "graph-def": "graph",
            "graph-definition": "graph",
            "stdout": "stdout",
        }
    )
    if preferred:
        return preferred_names
    elif tab is None:
        return list(mappings.keys())
    elif tab in mappings:
        return mappings[tab]
    else:
        raise ValueError("invalid tab name; tab should be in %r" % preferred_names)


def shape(data):
    """
    Given a nested list or a numpy array,
    return the shape.
    """
    if hasattr(data, "shape"):
        return list(data.shape)
    else:
        try:
            length = len(data)
            return [length] + shape(data[0])
        except TypeError:
            return []


def tensor_length(data):
    """
    Get the length of a tensor/list.
    """
    if hasattr(data, "shape"):
        return data.shape[0]
    else:
        try:
            length = len(data)
        except TypeError:
            length = 0
    return length


def lazy_flatten(iterable):
    if hasattr(iterable, "flatten"):
        iterable = iterable.flatten()
    iterator, sentinel, stack = iter(iterable), object(), []
    while True:
        value = next(iterator, sentinel)
        if value is sentinel:
            if not stack:
                break
            iterator = stack.pop()
        elif isinstance(value, (numbers.Number, six.string_types)):
            yield value
        else:
            if hasattr(value, "flatten"):
                value = value.flatten()  # type: ignore
            try:
                new_iterator = iter(value)
            except TypeError:
                yield value
            else:
                stack.append(iterator)
                iterator = new_iterator


def flatten(items):
    """
    Given a nested list or a numpy array,
    return the data flattened.
    """
    if isinstance(items, (numbers.Number, six.string_types)):
        return items
    return list(lazy_flatten(items))


def fast_flatten(items):
    """
    Given a nested list or a numpy array,
    return the data flattened.
    """
    if isinstance(items, (numbers.Number, six.string_types)):
        return items

    try:
        items = convert_tensor_to_numpy(items)
    except Exception:
        LOGGER.debug("unable to convert tensor; continuing", exc_info=True)

    if HAS_NUMPY:
        try:
            # Vector, Matrix conversion:
            items = numpy.array(items, dtype=float)
            # Return numpy array:
            return items.reshape(-1)
        except Exception:
            try:
                # Uneven conversion, 2 deep:
                items = numpy.array([numpy.array(item) for item in items], dtype=float)
                return items.reshape(-1)
            except Exception:
                # Fall through
                LOGGER.debug(
                    "numpy unable to convert items in fast_flatten", exc_info=True
                )
                return numpy.array(flatten(items))
    else:
        log_once_at_level(
            logging.INFO,
            "numpy not installed; using a slower flatten",
        )
        return flatten(items)


def convert_dict_to_string(user_data):
    # type: (Dict) -> str
    try:
        return json.dumps(user_data, sort_keys=True)
    except TypeError:
        retval = {}
        for key in user_data:
            try:
                value = convert_to_string(user_data[key])
            except Exception:
                value = str(user_data[key])
            retval[key] = value
        return str(retval)


def convert_to_string(user_data):
    # type: (Any) -> str
    """
    Given an object, return it as a string.
    """
    if isinstance(user_data, Mapping):
        return convert_dict_to_string(user_data)

    # hydra ConfigNode special case:
    if hasattr(user_data, "node"):
        return convert_dict_to_string(user_data.node)

    if hasattr(user_data, "numpy"):
        user_data = convert_tensor_to_numpy(user_data)

    if isinstance(user_data, bytes) and not isinstance(user_data, str):
        user_data = user_data.decode("utf-8")

    return str(user_data)


def convert_to_string_truncated(user_data, size):
    # type: (Any, int) -> str
    value = convert_to_string(user_data)
    if len(value) > size:
        LOGGER.warning("truncated string; too long: '%s'...", value)
        indicator = " [truncated]"
        if size < len(indicator):
            value = value[:size]
        else:
            value = value[: size - len(indicator)] + indicator
    return value


def convert_to_string_key(user_data):
    # type: (Any) -> str
    return convert_to_string_truncated(user_data, 100)


def convert_to_string_value(user_data):
    # type: (Any) -> str
    return convert_to_string_truncated(user_data, 1000)


def makedirs(name, exist_ok=False):
    """
    Replacement for Python2's version lacking exist_ok
    """
    if not os.path.exists(name) or not exist_ok:
        os.makedirs(name)


def clean_and_check_root_relative_path(root, relative_path):
    # type: (str, str) -> str
    """
    Given a root and a relative path, resolve the relative path to get an
    absolute path and make sure the resolved path is a child to root. Cases
    where it could not be the case would be if the `relative_path` contains `..`
    or if one part of the relative path is a symlink going above the root.

    Return the absolute resolved path and raises a ValueError if the root path
    is not absolute or if the resolved relative path goes above the root.
    """
    if not os.path.isabs(root):
        raise ValueError("Root parameter %r should an absolute path" % root)

    if not root.endswith(os.sep):
        root = root + os.sep

    real_root = os.path.realpath(root)

    joined_path = os.path.join(real_root, relative_path)
    resolved_path = os.path.realpath(joined_path)

    if not resolved_path.startswith(real_root):
        raise ValueError("Final path %r is outside of %r" % (resolved_path, real_root))

    return resolved_path


def check_if_path_relative_to_root(root, absolute_path):
    # type: (str, str) -> bool
    if not os.path.isabs(root):
        raise ValueError("Root parameter %r should an absolute path" % root)

    root_full_path = os.path.realpath(root) + os.sep
    full_path = os.path.realpath(absolute_path)

    return full_path.startswith(root_full_path)


def verify_data_structure(datatype, data):
    # Raise an error if anything wrong
    if datatype == "curve":
        if (
            ("x" not in data)
            or ("y" not in data)
            or ("name" not in data)
            or (not isinstance(data["name"], str))
            or (len(data["x"]) != len(data["y"]))
        ):
            raise ValueError(
                "'curve' requires lists 'x' and 'y' of equal lengths, and string 'name'"
            )
    else:
        raise ValueError("invalid datatype %r: datatype must be 'curve'" % datatype)


def proper_registry_model_name(name):
    """
    A proper registry model name is:
        * lowercase
        * replaces all non-alphanumeric with dashes
        * removes leading and trailing dashes
        * limited to 1 dash in a row
    """
    name = "".join([(char if char.isalnum() else "-") for char in name])
    while name.startswith("-"):
        name = name[1:]
    while name.endswith("-"):
        name = name[:-1]
    name = name.lower()
    while "--" in name:
        name = name.replace("--", "-")
    return name


def is_interactive():
    """
    Returns True if in interactive mode
    """
    return bool(getattr(sys, "ps1", sys.flags.interactive))


def safe_filename(filename):
    """
    Given a value, turn it into a valid filename.

    1. Remove the spaces
    2. Replace anything not alpha, '-', '_', or '.' with '_'
    3. Remove duplicate '_'
    """
    string = str(filename).strip().replace(" ", "_")
    string = re.sub(r"(?u)[^-\w.]", "_", string)
    return re.sub(r"_+", "_", string)


def convert_model_to_string(model):
    # type: (Any) -> str
    """
    Given a model of some kind, convert to a string.
    """
    if type(model).__name__ == "Graph":  # Tensorflow Graph Definition
        try:
            from google.protobuf import json_format

            graph_def = model.as_graph_def()
            model = json_format.MessageToJson(graph_def, sort_keys=True)
        except Exception:
            LOGGER.warning("Failed to convert Tensorflow graph to JSON", exc_info=True)

    if hasattr(model, "to_json"):
        # First, try with sorted keys:
        try:
            model = model.to_json(sort_keys=True)
        except Exception:
            model = model.to_json()
    elif hasattr(model, "to_yaml"):
        model = model.to_yaml()

    try:
        return str(model)
    except Exception:
        LOGGER.warning("Unable to convert model to a string")
        return "Unable to convert model to a string"


def convert_object_to_dictionary(obj):
    # type: (Any) -> Dict[str, str]
    """
    This function takes an object and turns it into
    a dictionary. It turns all properties (including
    computed properties) into a {property_name: string, ...}
    dictionary.
    """
    # hydra ConfigStore special case:
    if obj.__class__.__module__.startswith("hydra.core") and hasattr(obj, "repo"):
        return obj.repo

    dic = {}
    for attr in dir(obj):
        # Python 2 exposed some "internal" functions attributed as `func_X`. They were renamed in
        # `__X__` in Python 3.
        if attr.startswith("__") or attr.startswith("to_") or attr.startswith("func_"):
            continue
        value = getattr(obj, attr)
        if callable(value):
            continue
        try:
            dic[attr] = str(value)
        except Exception:
            pass
    return dic


def check_is_pandas_dataframe(dataframe):
    # type: (Any) -> Optional[bool]
    """
    Is it like a dataframe? For example, does it have
    to_markdown(), to_html() methods?
    """
    try:
        from pandas.core.dtypes.generic import ABCDataFrame, ABCSeries
    except ImportError:
        return None

    return isinstance(dataframe, (ABCDataFrame, ABCSeries))


def get_dataframe_profile_html(dataframe, minimal):
    # type: (Any, Optional[bool]) -> Optional[str]
    """
    Log a pandas dataframe profile.
    """
    try:
        import pandas_profiling

    except ImportError:
        LOGGER.warning(MISSING_PANDAS_PROFILING)
        return None
    except Exception:
        LOGGER.warning(MISSING_PANDAS_PROFILING, exc_info=True)
        return None

    try:
        if minimal:  # earlier versions of pandas_profiling did not support minimal
            profile = pandas_profiling.ProfileReport(dataframe, minimal=minimal)
        else:
            profile = pandas_profiling.ProfileReport(dataframe)
        html = profile.to_html()  # type: str
        html = html.replace("http:", "https:")
        return html
    except Exception:
        LOGGER.warning(DATAFRAME_PROFILE_ERROR, exc_info=True)

        return None


def prepare_dataframe(dataframe, asset_format, **kwargs):
    # type: (Any, Optional[str], Optional[dict]) -> Optional[StringIO]
    """
    Log a pandas dataframe.
    """
    fp = StringIO()
    if asset_format == "json":
        dataframe.to_json(fp, **kwargs)
    elif asset_format == "csv":
        dataframe.to_csv(fp, **kwargs)
    elif asset_format == "md":
        dataframe.to_markdown(fp, **kwargs)
    elif asset_format == "html":
        dataframe.to_html(fp, **kwargs)
    else:
        LOGGER.warning(
            "invalid asset_format %r; should be 'json', "
            + "'csv', 'md', or 'html'; ignoring",
            asset_format,
        )
        return None

    fp.seek(0)
    return fp


def clean_string(string):
    if string:
        return "".join([char for char in string if char not in ["'", '"', " "]])
    else:
        return ""


def get_api_key_from_user():
    """
    Get the Comet API key fromthe user.
    """
    from .config import get_config

    client_url = get_config("comet.url_override")
    root_url = sanitize_url(get_root_url(client_url))

    print(
        "Please enter your Comet API key from {root_url}api/my/settings/".format(
            root_url=root_url
        )
    )
    print("(api key may not show as you type)")
    api_key = clean_string(getpass.getpass("Comet API key: "))
    return api_key


def parse_remote_uri(uri):
    # type: (Optional[str]) -> Optional[str]
    if not uri:
        return None

    try:
        parsed = urlparse(uri)
        if parsed.path:
            # Split the path
            return parsed.path.split("/")[-1]
        else:
            return None
    except Exception:
        LOGGER.debug("Failure parsing URI %r", uri, exc_info=True)
        return None


def make_template_filename(group=None):
    if group is None:
        group = random.randint(0, 10000000)

    return "template_projector_config-%s.json" % group


class ImmutableDict(dict):
    def _immutable(self, *args, **kws):
        raise TypeError("object is immutable")

    __setitem__ = _immutable
    __delitem__ = _immutable
    clear = _immutable
    update = _immutable
    setdefault = _immutable
    pop = _immutable
    popitem = _immutable


class IterationProgressCallback(object):
    def __init__(self, iterable, callback, frequency):
        self._iterable = iterable
        self._callback = callback
        self._frequency = frequency

    def __iter__(self):
        last = get_time_monotonic()

        for obj in self._iterable:
            yield obj

            now = get_time_monotonic()
            diff = now - last
            if diff > self._frequency:
                last = now
                try:
                    self._callback()
                except Exception:
                    LOGGER.debug("Error calling the progress callback", exc_info=True)


def atexit_unregister(func):
    # type: (Any) -> None
    if six.PY2:
        to_delete = []

        # First iterate to detect exithandlers to remove
        for exithandlers in atexit._exithandlers:
            if exithandlers[0] == func:
                to_delete.append(exithandlers)

        # Then remove them but we cannot assume that the list hasn't changed, so uses remove which is inefficient
        for exithandler_to_delete in to_delete:
            try:
                atexit._exithandlers.remove(exithandler_to_delete)
            except ValueError:
                pass
    else:
        return atexit.unregister(func)


def generate_guid():
    # type: () -> str
    """Generate a GUID"""
    return uuid.uuid4().hex


def compact_json_dump(data, fp):
    return json_dump(data, fp, sort_keys=True, separators=(",", ":"), cls=NestedEncoder)


def get_root_url(url):
    # type: (str) -> str
    """Remove the path, params, query and fragment from a given URL"""
    parts = urlparse(url)
    scheme, netloc, path, params, query, fragment = parts

    return urlunparse((scheme, netloc, "", "", "", ""))


def sanitize_url(url):
    # type: (str) -> str
    """Sanitize an URL, checking that it is a valid URL and ensure it contains an ending slash /"""
    parts = urlparse(url)
    scheme, netloc, path, params, query, fragment = parts

    # TODO: Raise an exception if params, query and fragment are not empty?

    # Ensure the leading slash
    if path and not path.endswith("/"):
        path = path + "/"
    elif not path and not netloc.endswith("/"):
        netloc = netloc + "/"

    return urlunparse((scheme, netloc, path, params, query, fragment))


def metric_name(name, prefix=None):
    # type: (str, Optional[str]) -> str
    if prefix:
        return "%s.%s" % (prefix, name)
    else:
        return name


def convert_log_table_input_to_io(
    filename, tabular_data, headers, format_kwargs, catch_exception=True
):
    # type: (str, Optional[Any], Union[Sequence[str], bool], Dict[str, Any], bool) -> Optional[Tuple[IO, str]]

    # Get the extension
    if "." in filename:
        format = filename.rsplit(".", 1)[-1]
    else:
        format = ""

    if check_is_pandas_dataframe(tabular_data):
        if format not in ["json", "csv", "md", "html"]:
            if catch_exception:
                LOGGER.error(CONVERT_DATAFRAME_INVALID_FORMAT, format)
                return None
            else:
                raise ValueError(CONVERT_DATAFRAME_INVALID_FORMAT % format)

        try:
            dataframe_fp = prepare_dataframe(tabular_data, format, **format_kwargs)
        except Exception:
            if catch_exception is False:
                raise

            LOGGER.error(DATAFRAME_CONVERSION_ERROR, format, exc_info=True)
            return None

        if dataframe_fp:
            return (dataframe_fp, "dataframe")
        else:
            return None

    else:
        if format not in ["tsv", "csv"]:
            if catch_exception:
                LOGGER.error(CONVERT_TABLE_INVALID_FORMAT, format)
                return None
            else:
                raise ValueError(CONVERT_TABLE_INVALID_FORMAT % format)

        if format == "tsv":
            delim = "\t"
        elif format == "csv":
            delim = ","
        fp = table_to_fp(tabular_data, delim, headers)
        return (fp, "asset")
