# -*- coding: utf-8 -*-
import os
from collections import namedtuple
from io import BytesIO
from math import ceil

import requests
from PIL import Image
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from arkindex_worker import logger

# See http://docs.python-requests.org/en/master/user/advanced/#timeouts
DOWNLOAD_TIMEOUT = (30, 60)

BoundingBox = namedtuple("BoundingBox", ["x", "y", "width", "height"])


def open_image(path, mode="RGB", rotation_angle=0, mirrored=False):
    """
    Open an image from a path or a URL
    """
    if (
        path.startswith("http://")
        or path.startswith("https://")
        or not os.path.exists(path)
    ):
        image = download_image(path)
    else:
        try:
            image = Image.open(path)
        except (IOError, ValueError):
            image = download_image(path)

    if image.mode != mode:
        image = image.convert(mode)

    if mirrored:
        image = image.transpose(Image.FLIP_LEFT_RIGHT)

    if rotation_angle:
        image = image.rotate(-rotation_angle, expand=True)

    return image


def download_image(url):
    """
    Download an image and open it with Pillow
    """
    assert url.startswith("http"), "Image URL must be HTTP(S)"

    # Download the image
    # Cannot use stream=True as urllib's responses do not support the seek(int) method,
    # which is explicitly required by Image.open on file-like objects
    try:
        resp = requests.get(url, timeout=DOWNLOAD_TIMEOUT)
    except requests.exceptions.SSLError:
        logger.warning(
            "An SSLError occurred during image download, retrying with a weaker and unsafe SSL configuration"
        )

        # Saving current ciphers
        previous_ciphers = requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS

        # Downgrading ciphers to download the image
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = "ALL:@SECLEVEL=1"
        resp = requests.get(url, timeout=DOWNLOAD_TIMEOUT)

        # Restoring previous ciphers
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = previous_ciphers

    resp.raise_for_status()

    # Preprocess the image and prepare it for classification
    image = Image.open(BytesIO(resp.content))
    logger.info(
        "Downloaded image {} - size={}x{}".format(url, image.size[0], image.size[1])
    )

    return image


def polygon_bounding_box(polygon):
    x_coords, y_coords = zip(*polygon)
    x, y = min(x_coords), min(y_coords)
    width, height = max(x_coords) - x, max(y_coords) - y
    return BoundingBox(x, y, width, height)


def _retry_log(retry_state, *args, **kwargs):
    logger.warning(
        f"Request to {retry_state.args[0]} failed ({repr(retry_state.outcome.exception())}), "
        f"retrying in {retry_state.idle_for} seconds"
    )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2),
    retry=retry_if_exception_type(requests.RequestException),
    before_sleep=_retry_log,
    reraise=True,
)
def _retried_request(url):
    resp = requests.get(url, timeout=DOWNLOAD_TIMEOUT)
    resp.raise_for_status()
    return resp


def download_tiles(url):
    """
    Reconstruct a full IIIF image on servers that cannot serve the full-sized image using tiles.
    """
    if not url.endswith("/"):
        url += "/"
    logger.debug("Downloading image information")
    info = _retried_request(url + "info.json").json()

    image_width, image_height = info.get("width"), info.get("height")
    assert image_width and image_height, "Missing image dimensions in info.json"
    assert info.get(
        "tiles"
    ), "Image cannot be retrieved at full size and tiles are not supported"

    # Take the biggest available tile size
    tile = sorted(info["tiles"], key=lambda tile: tile.get("width", 0), reverse=True)[0]
    tile_width = tile["width"]
    # Tile height is optional and defaults to the width
    tile_height = tile.get("height", tile_width)

    full_image = Image.new("RGB", (image_width, image_height))

    for tile_x in range(ceil(image_width / tile_width)):
        for tile_y in range(ceil(image_height / tile_height)):
            region_x = tile_x * tile_width
            region_y = tile_y * tile_height

            # Prevent trying to crop outside the bounds of an image
            region_width = min(tile_width, image_width - region_x)
            region_height = min(tile_height, image_height - region_y)

            logger.debug(f"Downloading tile {tile_x},{tile_y}")
            resp = _retried_request(
                f"{url}{region_x},{region_y},{region_width},{region_height}/full/0/default.jpg"
            )

            tile_img = Image.open(BytesIO(resp.content))

            # Some bad IIIF image server implementations may sometimes return tiles with a few pixels of difference
            # with the expected sizes, causing Pillow to raise ValueError('images do not match').
            actual_width, actual_height = tile_img.size
            if actual_width < region_width or actual_height < region_height:
                # Fail when tiles are too small
                raise ValueError(
                    f"Expected size {region_width}×{region_height} for tile {tile_x},{tile_y}, "
                    f"but got {actual_width}×{actual_height}"
                )

            if actual_width > region_width or actual_height > region_height:
                # Warn and crop when tiles are too large
                logger.warning(
                    f"Cropping tile {tile_x},{tile_y} from {actual_width}×{actual_height} "
                    f"to {region_width}×{region_height}"
                )
                tile_img = tile_img.crop((0, 0, region_width, region_height))

            full_image.paste(
                tile_img,
                box=(
                    region_x,
                    region_y,
                    region_x + region_width,
                    region_y + region_height,
                ),
            )

    return full_image
