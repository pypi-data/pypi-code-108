import json
import logging
import os
from pathlib import Path
from typing import Tuple
import uuid

import validators  # To validate that a certain string is a url
from dotenv import load_dotenv  # Use of environment variables
from validators.utils import ValidationFailure


def is_url_image(url: str) -> Tuple[str, bool]:
    """
    [Check if an url is an image]

    Args:
        url (str): [The url to check]

    Returns:
        str: [The content type of the url image]
        bool: [A boolean that indicates if the url is an image]
    """
    load_dotenv()
    image_formats = json.loads(str(os.getenv("IMAGE_FORMATS")))
    if not is_string_an_url(url):
        return "Not a url", False
    else:
        r = requests.head(url, timeout=1)  # type: ignore
        if r.headers["content-type"] in image_formats:
            return str(r.headers["content-type"]), True
        return str(r.headers), False


def is_string_an_url(url_string: str) -> bool:
    """
    [Check if a string is a valid url]

    Args:
        url_string (str): [the string to validate]

    Returns:
        bool: [a boolean indicating if the string is a valid url]
    """
    result = validators.url(url_string)  # type: ignore

    if isinstance(result, ValidationFailure):
        return False
    else:
        return True


def store_image_to_temp(image_folder: str, url: str) -> str:
    """
    [Store an image to a temporary folder]

    Args:
        image_folder (str): [The temporary folder to save the image to]
        url (str): [The url to fetch the image from]

    Returns:
        str: [The location of the image]
    """
    logging.info(
        f"Downloading badge image from location {url} to folder {image_folder}"
    )
    header, valid_url = is_url_image(url)
    if valid_url:
        img_data = requests.get(url, timeout=1).content  # type: ignore
        with open(Path(image_folder, str(uuid.uuid4())), "wb") as file:
            file.write(img_data)
        return file.name
    else:
        raise ValueError(
            f"The url '{url}' does not contain a valid image url. (Header type: {header})"
        )
