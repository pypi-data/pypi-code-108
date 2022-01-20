#  Copyright (c) 2021 Caliber Data Labs.
#  All rights reserved.
#
from typing import NamedTuple, Optional
import requests
from PIL import Image, ImageFile
from ..custom_exceptions import ResponseError

from .logger import get_logger

logger = get_logger(__name__)


class ImageProperties(NamedTuple):
    width: int
    height: int
    format: str


def get_image_attributes(image_url: Optional[str] = None,
                         image_path: Optional[str] = None,
                         image_bytes: Optional[bytes] = None):
    # get file size *and* image size (None if not known)
    if image_url:
        # TODO is this safe to do?
        resp = requests.get(image_url, stream=True)
        if not resp.ok:
            raise ResponseError(
                "Could not find an image in {}".format(image_url))
        else:
            p = ImageFile.Parser()
            for data in resp.iter_content(chunk_size=1024):
                p.feed(data)
                if p.image:
                    return ImageProperties(
                        width=p.image.width,
                        height=p.image.height,
                        format=p.image.format
                    )

    elif image_path:
        with Image.open(image_path) as image_file:
            width, height = image_file.size
            format = image_file.format
            return ImageProperties(
                width=width,
                height=height,
                format=format)
    elif image_bytes:
        image = Image.open(image_bytes)
        width, height = image.size
        format = image.format
        return ImageProperties(
            width=width,
            height=height,
            format=format)
    else:
        raise NotImplementedError(
            "Either image url or image path must be provided")
